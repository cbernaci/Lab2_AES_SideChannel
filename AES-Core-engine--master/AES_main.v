module AES_main(
    input CLOCK_50,
    output wire [9:0] LEDR);


wire [127:0] data_out;
wire [127:0] data_in;
wire [127:0] key;

assign data_in = 128'h_00112233445566778899aabbccddeeff;
assign key = 128'h_000102030405060708090a0b0c0d0e0f;

aes(.clk(CLOCK_50),
    .data_in(data_in),
    .key(key),
    .data_out(data_out));

assign LEDR[0] = (data_out == 128'h_69c4e0d86a7b0430d8cdb78070b4c55a) ? 1'b1 : 1'b0;
assign LEDR[1] = 1'b1;

endmodule

