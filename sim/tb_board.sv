`timescale 1ns/1ps
module tb_board;
    localparam PERIOD=2048, BIT_CYCLES=8;
    logic CLOCK_50=0;
    logic [1:0] KEY=2'b11;
    logic [6:0] SW=0;
    wire [9:0] LEDR;
    wire UART_TX;
    logic [7:0] packet [0:12];
    logic [7:0] parity;
    de0cv #(.PERIOD(PERIOD), .BIT_CYCLES(BIT_CYCLES)) dut(.*);
    always #10 CLOCK_50=~CLOCK_50;
    task automatic clocks(input integer cycles);
        repeat (cycles) @(negedge CLOCK_50);
    endtask
    task automatic receive_frame;
        parity=0;
        for (integer i=0;i<13;i=i+1) begin
            @(negedge UART_TX);
            clocks(BIT_CYCLES+BIT_CYCLES/2);
            for (integer j=0;j<8;j=j+1) begin
                packet[i][j]=UART_TX;
                clocks(BIT_CYCLES);
            end
            if (UART_TX !== 1) $fatal(1,"Missing UART stop bit");
            parity=parity^packet[i];
        end
        if (packet[0] !== 8'h02 || packet[1] !== 8'h21 || parity !== 0)
            $fatal(1,"Invalid UART framing");
    endtask
    initial begin
        clocks(2); KEY[0]=0; clocks(2); KEY[0]=1;
        receive_frame();
        if ({packet[11],packet[10]} !== 16'h0378) $fatal(1,"Wrong reset snapshot");
        KEY[1]=0; clocks(8); KEY[1]=1;
        receive_frame();
        if (LEDR !== 0 || {packet[11],packet[10]} !== 0) $fatal(1,"Rearm snapshot");
        SW=7'b0000011;
        receive_frame();
        if (!LEDR[6] || {packet[11],packet[10]} !== 16'h0043) $fatal(1,"Wrong trip snapshot");
        $display("PASS: DE0-CV switch input, rearm, trip and UART packets");
        $finish;
    end
    initial begin
        #300000;
        $fatal(1,"UART test timeout");
    end
endmodule
