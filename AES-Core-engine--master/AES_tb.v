module top();
    
wire [127:0] data_out;
wire [127:0] data_in;
wire [127:0] key;
logic clock;
wire [9:0] LEDR;

assign data_in = 128'h_00112233445566778899aabbccddeeff;
assign key = 128'h_000102030405060708090a0b0c0d0e0f;

aes(.clk(clock),       // in
    .data_in(data_in), // in
    .key(key),         // in
    .data_out(data_out));

aes_tb (.data_in(data_in),);

//assign LEDR[0] = (data_out == 128'h_69c4e0d86a7b0430d8cdb78070b4c55a) ? 1'b1 : 1'b0;

initial begin
  $monitor("key = %h, data_in = %h, data_out = %h, LEDR0 = %b", key, data_in, data_out, LEDR[0]);
  clock = 0;
  repeat (500) #1 clock = ~clock;
end




endmodule

