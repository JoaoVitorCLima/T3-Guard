module vigia #(
    parameter integer TIMEOUT = 8,
    parameter integer CONFIRM = 3,
    parameter integer DIVERGENCE = 180
)(
    input logic clk, rst_n, sample, rearm,
    input logic [9:0] a, b, c,
    input logic [2:0] valid,
    output logic trip, timeout,
    output logic [1:0] mode,
    output logic [2:0] bad, high, discrep,
    output logic [31:0] tick, event_tick, event_id,
    output logic [9:0] event_state
);
    logic [31:0] age;
    logic [31:0] streak [0:2];
    logic [2:0] invalid_now, outlier, bad_next, high_next, discrep_next;
    logic ab, ac, bc, timeout_next, demand, trip_next;
    logic [1:0] mode_next;
    logic [9:0] state_next;
    integer healthy, votes;
    function automatic logic far(input logic [9:0] x, y);
        far = (x >= y ? x-y : y-x) > DIVERGENCE;
    endfunction
    function automatic logic threshold(input logic [9:0] value, input logic previous);
        threshold = previous ? value > 650 : value >= 700;
    endfunction
    always @* begin
        invalid_now = ~valid | {c > 1000, b > 1000, a > 1000};
        ab = far(a,b);
        ac = far(a,c);
        bc = far(b,c);
        outlier[0] = !(|invalid_now) && ab && ac && !bc;
        outlier[1] = !(|invalid_now) && ab && bc && !ac;
        outlier[2] = !(|invalid_now) && ac && bc && !ab;
        timeout_next = !sample && age >= TIMEOUT-1;
        bad_next = bad;
        high_next = high;
        discrep_next = discrep;
        if (sample) begin
            for (integer i=0; i<3; i=i+1)
                discrep_next[i] = outlier[i] && streak[i] >= CONFIRM-1;
            bad_next = invalid_now | discrep_next;
            high_next = {threshold(c,high[2]),threshold(b,high[1]),threshold(a,high[0])};
        end
        if (timeout_next) bad_next = 3'b111;
        healthy = 0;
        votes = 0;
        for (integer i=0; i<3; i=i+1) begin
            if (!bad_next[i]) begin
                healthy = healthy + 1;
                if (high_next[i]) votes = votes + 1;
            end
        end
        demand = healthy < 2 || votes >= 2 || (healthy == 2 && votes == 1);
        trip_next = demand || (trip && !(rearm && sample && healthy == 3 && high_next == 0));
        mode_next = healthy == 3 ? 2'd0 : healthy == 2 ? 2'd1 : 2'd2;
        state_next = {timeout_next, mode_next, trip_next, bad_next, high_next};
    end
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trip <= 1;
            timeout <= 1;
            mode <= 2;
            bad <= 7;
            high <= 0;
            discrep <= 0;
            age <= TIMEOUT;
            tick <= 0;
            event_tick <= 0;
            event_id <= 0;
            event_state <= {1'b1,2'd2,1'b1,3'd7,3'd0};
            for (integer i=0; i<3; i=i+1) streak[i] <= 0;
        end else begin
            tick <= tick + 1;
            trip <= trip_next;
            timeout <= timeout_next;
            mode <= mode_next;
            bad <= bad_next;
            high <= high_next;
            discrep <= discrep_next;
            if (sample) age <= 0;
            else if (age < TIMEOUT) age <= age + 1;
            for (integer i=0; i<3; i=i+1) begin
                if (timeout_next || (sample && !outlier[i])) streak[i] <= 0;
                else if (sample && streak[i] < CONFIRM) streak[i] <= streak[i] + 1;
            end
            if (state_next != event_state) begin
                event_state <= state_next;
                event_tick <= tick + 1;
                event_id <= event_id + 1;
            end
        end
    end
endmodule
