module de0cv #(
    parameter integer PERIOD=500000, BIT_CYCLES=434
)(
    input wire CLOCK_50,
    input wire [1:0] KEY,
    input wire [6:0] SW,
    output wire [9:0] LEDR,
    output wire UART_TX
);

    reg [1:0] released = 0;
    reg [7:0] sync1, sync2;
    reg key_prev, rearm_pending;
    reg [18:0] divider;
    wire rst_n = released[1];
    wire sample = divider == PERIOD-1 && !sync2[6];
    wire [9:0] a = sync2[0] ? 710 : 500;
    wire [9:0] b = sync2[1] ? 710 : 500;
    wire [9:0] c = sync2[2] ? 710 : 500;
    wire [2:0] bad, high, discrep;
    wire [1:0] mode;
    wire trip, timeout;
    wire [31:0] tick, event_tick, event_id;
    wire [9:0] event_state;
    reg [119:0] packet;
    reg [7:0] bits_left;
    reg [8:0] bit_timer;
    reg [3:0] symbol;

    always @(posedge CLOCK_50 or negedge KEY[0])
        if (!KEY[0]) released <= 0;
        else released <= {released[0],1'b1};

    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            sync1 <= 0; sync2 <= 0;
            divider <= 0; key_prev <= 0; rearm_pending <= 0;
        end else begin
            sync1 <= {~KEY[1],SW};
            sync2 <= sync1;
            key_prev <= sync2[7];
            if (sync2[7] && !key_prev) rearm_pending <= 1;
            else if (sample) rearm_pending <= 0;
            if (divider == PERIOD-1) divider <= 0;
            else divider <= divider+1'b1;
        end
    end

    vigia #(.TIMEOUT(PERIOD*4),.DIVERGENCE(300)) core(
        .clk(CLOCK_50),.rst_n(rst_n),.sample(sample),.rearm(rearm_pending),
        .a(a),.b(b),.c(c),.valid(~sync2[5:3]),
        .trip(trip),.timeout(timeout),.mode(mode),.bad(bad),.high(high),
        .discrep(discrep),.tick(tick),.event_tick(event_tick),
        .event_id(event_id),.event_state(event_state)
    );
    assign LEDR = {timeout, mode, trip, bad, high};

    function automatic [7:0] checksum(input [95:0] data);
        checksum = 0;
        for (integer i=0; i<12; i=i+1)
            checksum = checksum ^ data[i*8 +: 8];
    endfunction

    wire [95:0] snapshot = {6'b0,event_state,event_tick,event_id,16'h2102};
    // Transmit low byte first, UART 115200 8N1. One snapshot each 10 ms.
    assign UART_TX = bits_left == 0 || symbol == 9 ? 1'b1 :
                     symbol == 0 ? 1'b0 : packet[0];
    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            packet <= 0; bits_left <= 0; bit_timer <= 0; symbol <= 0;
        end else if (bits_left == 0) begin
            if (divider == 0) begin
                packet <= {16'b0,checksum(snapshot),snapshot};
                bits_left <= 130;
                bit_timer <= BIT_CYCLES-1;
                symbol <= 0;
            end
        end else if (bit_timer == 0) begin
            bit_timer <= BIT_CYCLES-1;
            bits_left <= bits_left-1'b1;
            if (symbol >= 1 && symbol <= 8) packet <= packet >> 1;
            if (symbol == 9) symbol <= 0;
            else symbol <= symbol+1'b1;
        end else bit_timer <= bit_timer-1'b1;
    end
endmodule
