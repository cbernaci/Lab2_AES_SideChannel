`default_nettype none
module AES(enable, e128, d128, e192, d192, e256, d256);

output wire e128;
output wire d128;
output wire e192;
output wire d192;
output wire e256;
output wire d256;
input enable;

wire [127:0] encryptedb1, encryptedb2, encryptedb3, encryptedb4, encryptedb5, encryptedb6;
wire [127:0] encryptedc1, encryptedc2, encryptedc3, encryptedc4, encryptedc5, encryptedc6;

// The plain text used as input
//wire[127:0] in = 128'h_00112233445566778899aabbccddeeff;
// The different keys used for testing (one of each type)
//wire[127:0] key128 = 128'h_000102030405060708090a0b0c0d0e0f;

////////////////////////////////////////////////////////////////

// CB Edit - NIST Test Vectors
// From Appendix B: GFSbox Known Answer Test Values
wire[127:0] in_b1 = 128'h_f34481ec3cc627bacd5dc3fb08f273e6;   // B.1.1
wire[127:0] in_b2 = 128'h_9798c4640bad75c7c3227db910174e72;   // B.1.2
wire[127:0] in_b3 = 128'h_96ab5c2ff612d9dfaae8c31f30c42168;   // B.1.3
wire[127:0] in_b4 = 128'h_6a118a874519e64e9963798a503f1d35;   // B.1.4
wire[127:0] in_b5 = 128'h_cb9fceec81286ca3e989bd979b0cb284;   // B.1.5
wire[127:0] in_b6 = 128'h_b26aeb1874e47ca8358ff22378f09144;   // B.1.6
wire[127:0] key128 = 128'h_0;

AES_Encrypt eb1(in_b1,key128,encryptedb1);
AES_Encrypt eb2(in_b2,key128,encryptedb2);
AES_Encrypt eb3(in_b3,key128,encryptedb3);
AES_Encrypt eb4(in_b4,key128,encryptedb4);
AES_Encrypt eb5(in_b5,key128,encryptedb5);
AES_Encrypt eb6(in_b6,key128,encryptedb6);

// The expected outputs from the encryption module
wire[127:0] expectedb1 = 128'h_0336763e966d92595a567cc9ce537f5e; //B.1.1
wire[127:0] expectedb2 = 128'h_a9a1631bf4996954ebc093957b234589; //B.1.2
wire[127:0] expectedb3 = 128'h_ff4f8391a6a40ca5b25d23bedd44a597; //B.1.3
wire[127:0] expectedb4 = 128'h_dc43be40be0e53712f7e2bf5ca707209; //B.1.4
wire[127:0] expectedb5 = 128'h_92beedab1895a94faa69b632e5cc47ce; //B.1.5
wire[127:0] expectedb6 = 128'h_459264f4798f6a78bacb89c15ed3d601; //B.1.6

/////////////////////////////////////////////////////////
// From Appendix C: KeySbox Known Answer Test Values
wire[127:0] in = 128'h_0;
wire[127:0] key128_c1 = 128'h_10a58869d74be5a374cf867cfb473859;
wire[127:0] key128_c2 = 128'h_caea65cdbb75e9169ecd22ebe6e54675;
wire[127:0] key128_c3 = 128'h_a2e2fa9baf7d20822ca9f0542f764a41;
wire[127:0] key128_c4 = 128'h_b6364ac4e1de1e285eaf144a2415f7a0;
wire[127:0] key128_c5 = 128'h_64cf9c7abc50b888af65f49d521944b2;
wire[127:0] key128_c6 = 128'h_47d6742eefcc0465dc96355e851b64d9;

AES_Encrypt ec1(in,key128_c1,encryptedc1);
AES_Encrypt ec2(in,key128_c2,encryptedc2);
AES_Encrypt ec3(in,key128_c3,encryptedc3);
AES_Encrypt ec4(in,key128_c4,encryptedc4);
AES_Encrypt ec5(in,key128_c5,encryptedc5);
AES_Encrypt ec6(in,key128_c6,encryptedc6);

// The expected outputs from the encryption module
wire[127:0] expectedc1 = 128'h_6d251e6944b051e04eaa6fb4dbf78465; //C.1.1
wire[127:0] expectedc2 = 128'h_6e29201190152df4ee058139def610bb; //C.1.2
wire[127:0] expectedc3 = 128'h_c3b44b95d9d2f25670eee9a0de099fa3; //C.1.3
wire[127:0] expectedc4 = 128'h_5d9b05578fc944b3cf1ccf0e746cd581; //C.1.4
wire[127:0] expectedc5 = 128'h_f7efc89d5dba578104016ce5ad659c05; //C.1.5
wire[127:0] expectedc6 = 128'h_0306194f666d183624aa230a8b264ae7; //C.1.6

// CHECK B1 TEST VECTORS - (comment if checking C1)
//assign d128 = (encryptedb1 == expectedb1 && enable) ? 1'b1 : 1'b0;
//assign e128 = (encryptedb2 == expectedb2 && enable) ? 1'b1 : 1'b0;
//assign d192 = (encryptedb3 == expectedb3 && enable) ? 1'b1 : 1'b0;
//assign e192 = (encryptedb4 == expectedb4 && enable) ? 1'b1 : 1'b0;
//assign d256 = (encryptedb5 == expectedb5 && enable) ? 1'b1 : 1'b0;
//assign e256 = (encryptedb6 == expectedb6 && enable) ? 1'b1 : 1'b0;

// CHECK C1 TEST VECTORS - (comment if checking B1)
assign d128 = (encryptedc1 == expectedc1 && enable) ? 1'b1 : 1'b0;
assign e128 = (encryptedc2 == expectedc2 && enable) ? 1'b1 : 1'b0;
assign d192 = (encryptedc3 == expectedc3 && enable) ? 1'b1 : 1'b0;
assign e192 = (encryptedc4 == expectedc4 && enable) ? 1'b1 : 1'b0;
assign d256 = (encryptedc5 == expectedc5 && enable) ? 1'b1 : 1'b0;
assign e256 = (encryptedc6 == expectedc6 && enable) ? 1'b1 : 1'b0;

endmodule