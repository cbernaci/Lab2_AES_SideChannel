module SPI (clk, btn, data_byte, ss_dec, sck, mosi_reg, tran_counter);
input          clk;
input 			btn;
input  [63:0] data_byte;
output 			ss_dec;
output			sck;
output			mosi_reg;
output  [11:0]  tran_counter;

// Wires
wire SD_button_done, SD_click;	// Debounce Signals

// Registers
reg ss_dec, sck, mosi_reg;
reg [11:0] tran_counter;

reg spi_c_reset, start_sck;
reg f_btn1, f_btn2;
reg [15:0]spi_counter;
reg [31:0]SD_button_count;

// Integer
integer bc = 64;

// Assignments

// Parameters + Initializations
parameter DEBOUNCE_DELAY = 32'd0_500_000;   /// 20nS * 500k = 10mS

initial begin
	spi_c_reset = 0;
	spi_counter = 0;
end

// Button Trigger
always @(posedge clk) 						f_btn1 <= btn;
always @(posedge clk) 						f_btn2 <= f_btn1;

assign                                  SD_button_done = (SD_button_count == DEBOUNCE_DELAY); 
assign                                  SD_click = (SD_button_count == DEBOUNCE_DELAY - 1); 

always @(posedge clk) 
    if (!f_btn2)                     SD_button_count <= 0;
    else if (SD_button_done)         SD_button_count <= SD_button_count;
    else                             SD_button_count <= SD_button_count + 1;

// SPI Set-up
always @(posedge clk)
    if (SD_click == 1)																								 ss_dec <= 0;
	 // Change back to SD_click
	 else if ((tran_counter == 65) && (spi_counter == 40))												 ss_dec <= 1;
	 else 																											    ss_dec <= ss_dec;
	 
always @(posedge clk)
	if ((ss_dec == 0) && (spi_c_reset == 0))										spi_counter <= spi_counter + 16'b1;
	else if ((ss_dec == 1) || (spi_c_reset == 1))								spi_counter <= 0;
	else																						spi_counter <= spi_counter;
	
always @(posedge clk)
    if (spi_counter == 48)     spi_c_reset <= 1;
    else            	 			 spi_c_reset <= 0;
	
always @(posedge clk)
    if ((spi_counter == 40) && (tran_counter != 65))    					start_sck <= 1;
    else if (tran_counter == 65)	 											start_sck <= 0;
	 else 																				start_sck <= start_sck;

always @(posedge clk)
    if ((spi_counter == 0) && (start_sck == 1))      						sck <= 1;
	 else if	(spi_counter == 24)													sck <= 0;										
    else            	 										  						sck <= sck; 
	 
always @(posedge clk)
	if  (spi_counter == 24) 												tran_counter <= tran_counter + 1;
	else if (SD_click == 1)													tran_counter <= 0;
	// Change back to SD_click
	else 																			tran_counter <= tran_counter;
	
always @(posedge clk)
	if  (spi_counter == 24) 												bc <= bc - 1;
	else if (SD_click == 1)													bc <= 64;
	// Change back to SD_click
	else 																			bc <= bc;
	
always @(posedge clk) begin
	if ((tran_counter <= 64) && (tran_counter >= 1))     mosi_reg <= data_byte[bc];
	else 															  	    mosi_reg <= 0;
end

endmodule