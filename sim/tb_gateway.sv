`timescale 1ns/1ps
module tb_gateway;
    localparam integer STDIN = 32'h8000_0000;
    logic clk=0, rst_n=1, sample=0, rearm=0;
    logic [9:0] a=0, b=0, c=0;
    logic [2:0] valid=7;
    wire trip, timeout;
    wire [1:0] mode;
    wire [2:0] bad, high, discrep;
    wire [31:0] tick, event_tick, event_id;
    wire [9:0] event_state;
    integer x, y, z, fields, rounds;

    vigia dut(.*);
    always #5 clk=~clk;

    initial begin
        #1 rst_n=0;
        #10 rst_n=1;
        rounds=0;
        fields=$fscanf(STDIN, "%d %d %d", x,y,z);
        while (fields == 3) begin
            if (x < 0 || x > 1000 || y < 0 || y > 1000 || z < 0 || z > 1000)
                $fatal(1,"Amostra fora da faixa do ensaio");
            @(negedge clk);
            a=x[9:0]; b=y[9:0]; c=z[9:0];
            sample=1;
            rearm=(rounds == 0);
            @(posedge clk); #1;
            rounds=rounds+1;
            $display("RTL %0d %0d %0d %0d %0d %0d", rounds, discrep, bad, mode, trip, event_id);
            fields=$fscanf(STDIN, "%d %d %d", x,y,z);
        end
        if (rounds == 0 || (fields != -1 && !(fields == 0 && $feof(STDIN))))
            $fatal(1,"Entrada incompleta ou sem rodadas");
        $finish;
    end
endmodule
