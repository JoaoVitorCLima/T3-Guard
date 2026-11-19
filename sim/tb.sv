`timescale 1ns/1ps
module tb;
    logic clk=0,rst_n=1,sample=0,rearm=0;
    logic [9:0] a=0,b=0,c=0;
    logic [2:0] valid=7;
    wire trip,timeout;
    wire [1:0] mode;
    wire [2:0] bad,high,discrep;
    wire [31:0] tick,event_tick,event_id;
    wire [9:0] event_state;
    integer fd, pattern;
    vigia dut(.*);
    always #5 clk=~clk;
    task automatic step(input integer x,y,z,v,s,r,expected_trip,expected_mode,expected_bad);
        @(negedge clk);
        a=x; b=y; c=z; valid=v; sample=s; rearm=r;
        @(posedge clk); #1;
        if (trip !== expected_trip[0] || mode !== expected_mode[1:0] || bad !== expected_bad[2:0])
            $fatal(1,"tick %0d: trip=%0d mode=%0d bad=%0d",tick,trip,mode,bad);
        $fdisplay(fd,"%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",tick,a,b,c,trip,mode,bad,high,timeout,event_id,event_tick);
    endtask
    initial begin
        fd=$fopen("trace.csv","w");
        if (!fd) $fatal(1,"trace.csv");
        $fdisplay(fd,"tick,a,b,c,trip,mode,bad,high,timeout,event_id,event_tick");
        #1 rst_n=0;
        #10 rst_n=1;
        step(400,410,405,7,1,1,0,0,0);
        step(400,410,750,7,1,0,0,0,0);
        step(400,410,750,7,1,0,0,0,0);
        step(400,410,750,7,1,0,0,1,4);
        step(400,410,750,3,1,0,0,1,4);
        step(400,410,750,1,1,0,1,2,6);
        step(400,410,405,7,1,0,1,0,0);
        step(400,410,405,7,1,1,0,0,0);
        step(710,720,680,7,1,0,1,0,0);
        step(680,680,680,7,1,1,1,0,0);
        step(650,650,650,7,1,1,0,0,0);
        repeat (7) step(650,650,650,7,0,0,0,0,0);
        step(650,650,650,7,0,0,1,2,7);
        step(650,650,650,7,1,1,0,0,0);
        step(710,650,1023,7,1,0,1,1,4);
        $fclose(fd);
        fd=$fopen("exhaustive.csv","w");
        for (pattern=0; pattern<8; pattern=pattern+1) begin
            step(650,650,650,7,1,1,0,0,0);
            step(pattern[0]?700:650,pattern[1]?700:650,pattern[2]?700:650,
                7,1,0,(pattern[0]+int'(pattern[1])+int'(pattern[2]))>=2,0,0);
        end
        $fclose(fd);
        $display("PASS: majority table, discrepancy, degraded, timeout, hysteresis and manual rearm");
        $finish;
    end
endmodule
