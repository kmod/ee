`timescale 1ns / 1ps
`default_nettype none
module memory_controller(
        output wire MemOE, MemWR,
        output wire RamAdv, RamCS, RamClk, RamCRE, RamLB, RamUB,
        input wire RamWait//,
        //output wire [25:0] MemAdr,
        //inout wire [15:0] MemDB
    );
    //
    // Think I always want these:
    assign MemOE = 1;
    assign RamCS = 0;
    assign RamCRE = 0;

    // think these are only for asynchronous mode:
    assign RamClk = 0;
    assign RamAdv = 0;

    assign MemWR = 1;
    assign RamLB = 0;
    assign RamUB = 0;
    assign MemOE = 0;
endmodule

