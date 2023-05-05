library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity spi_mod is 
	port (
		clk : in std_logic;
		rst : in std_logic;
		plaintext : in std_logic_vector(127 downto 0);
		ciphertext : in std_logic_vector(127 downto 0);
		ss_dec : out std_logic;
		sck : out std_logic;
		mosi_reg : out std_logic);
end spi_mod;

architecture behavioral of spi_mod is

-- Debounce Signals
-- signal SD_button_done : std_logic := '0';
-- signal SD_click : std_logic := '0';
signal trigger : std_logic := '0';

signal f_btn1 : std_logic := '0';
signal f_btn2 : std_logic := '0';

signal spi_counter : unsigned(15 downto 0) := (others => '0');
signal SD_button_count : unsigned(31 downto 0) := (others => '0');

signal spi_c_reset : std_logic := '0';
signal start_sck : std_logic := '0';

signal ss_dec_sig : std_logic := '0';
signal sck_sig : std_logic := '0';
signal tran_counter_sig : unsigned(11 downto 0) := (others => '0');	-- CHECK

signal bc : integer := 256;

signal plaintext_sig : std_logic_vector(127 downto 0) := (others => '0');
signal ciphertext_sig : std_logic_vector(127 downto 0) := (others => '0');
signal data_shift : std_logic_vector(255 downto 0) := (others => '0');

begin

-- Declarations
ss_dec <= ss_dec_sig;
sck <= sck_sig;

plaintext_sig(127 downto 120) <= plaintext(7 downto 0);
plaintext_sig(119 downto 112) <= plaintext(15 downto 8);
plaintext_sig(111 downto 104) <= plaintext(23 downto 16);
plaintext_sig(103 downto 96) <= plaintext(31 downto 24);
plaintext_sig(95 downto 88) <= plaintext(39 downto 32);
plaintext_sig(87 downto 80) <= plaintext(47 downto 40);
plaintext_sig(79 downto 72) <= plaintext(55 downto 48);
plaintext_sig(71 downto 64) <= plaintext(63 downto 56);
plaintext_sig(63 downto 56) <= plaintext(71 downto 64);
plaintext_sig(55 downto 48) <= plaintext(79 downto 72);
plaintext_sig(47 downto 40) <= plaintext(87 downto 80);
plaintext_sig(39 downto 32) <= plaintext(95 downto 88);
plaintext_sig(31 downto 24) <= plaintext(103 downto 96);
plaintext_sig(23 downto 16) <= plaintext(111 downto 104);
plaintext_sig(15 downto 8) <= plaintext(119 downto 112);
plaintext_sig(7 downto 0) <= plaintext(127 downto 120);

-------------------------------------------------------------
ciphertext_sig(127 downto 120) <= ciphertext(7 downto 0);
ciphertext_sig(119 downto 112) <= ciphertext(15 downto 8);
ciphertext_sig(111 downto 104) <= ciphertext(23 downto 16);
ciphertext_sig(103 downto 96) <= ciphertext(31 downto 24);
ciphertext_sig(95 downto 88) <= ciphertext(39 downto 32);
ciphertext_sig(87 downto 80) <= ciphertext(47 downto 40);
ciphertext_sig(79 downto 72) <= ciphertext(55 downto 48);
ciphertext_sig(71 downto 64) <= ciphertext(63 downto 56);
ciphertext_sig(63 downto 56) <= ciphertext(71 downto 64);
ciphertext_sig(55 downto 48) <= ciphertext(79 downto 72);
ciphertext_sig(47 downto 40) <= ciphertext(87 downto 80);
ciphertext_sig(39 downto 32) <= ciphertext(95 downto 88);
ciphertext_sig(31 downto 24) <= ciphertext(103 downto 96);
ciphertext_sig(23 downto 16) <= ciphertext(111 downto 104);
ciphertext_sig(15 downto 8) <= ciphertext(119 downto 112);
ciphertext_sig(7 downto 0) <= ciphertext(127 downto 120);

-------------------------------------------------------------

data_shift(255 downto 128) <= plaintext_sig(127 downto 0);
data_shift(127 downto 0) <= ciphertext_sig(127 downto 0);

process (clk)
	begin
		if rising_edge(clk) then
			f_btn1 <= rst;
		end if;
		end process;

process (clk)
	begin	
		if rising_edge(clk) then
			f_btn2 <= f_btn1;
		end if;
		end process;

process (clk)
	begin	
		if rising_edge(clk) then
			if ((f_btn1 = '1') AND (f_btn2 = '0')) then
				trigger <= '1';
			else 
				trigger <= '0';
			end if;
		end if;
		end process;

-- SPI CORE
process (clk)
	begin	
		if rising_edge(clk) then
			if (trigger = '1') then
				ss_dec_sig <= '0';
			elsif ((tran_counter_sig = x"101") AND (spi_counter = x"28")) then -- x"101" == 257 / x"28" == 40
				ss_dec_sig <= '1';
			else 
				ss_dec_sig <= ss_dec_sig;
			end if;
		end if;
	end process;


process (clk)
begin	
	if rising_edge(clk) then
		if ((ss_dec_sig = '0') AND (spi_c_reset = '0')) then
			spi_counter <= spi_counter + 1;
		elsif ((ss_dec_sig = '1') OR (spi_c_reset = '1')) then
			spi_counter <= (others => '0');
		else 
			spi_counter <= spi_counter;
		end if;
	end if;
end process;

process (clk)
begin	
	if rising_edge(clk) then
		if (spi_counter = x"30") then -- x"30" == 48
			spi_c_reset <= '1';
		else
			spi_c_reset <= '0';
		end if;
	end if;
	end process;

process (clk)
begin	
	if rising_edge(clk) then
		if ((spi_counter = x"28") AND (tran_counter_sig /= x"101")) then -- x"28" == 40 / x"101" == 257
			start_sck <= '1';
		elsif (tran_counter_sig = x"101") then -- x"101" == 257
			start_sck <= '0';
		else 
			start_sck <= start_sck;
		end if;
	end if;
	end process;

process (clk)
begin	
	if rising_edge(clk) then
		if ((spi_counter = x"0") AND (start_sck = '1')) then
			sck_sig <= '1';
		elsif (spi_counter = x"18") then -- 0x"18" == 24
			sck_sig <= '0';
		else
			sck_sig <= sck_sig;
		end if;
	end if;
	end process;

process (clk)
begin	
	if rising_edge(clk) then
		if (spi_counter = x"18") then --- 0x"18" == 24
			tran_counter_sig <= tran_counter_sig + 1;
		elsif (trigger = '1') then
			tran_counter_sig <= (others => '0');
		else
			tran_counter_sig <= tran_counter_sig;
		end if;
	end if;
	end process;

process (clk)
begin
	if rising_edge(clk) then
		if (spi_counter = x"18") then -- 0x"18" == 24
			bc <= bc - 1;
		elsif (trigger = '1') then
			bc <= 256;
		else
			bc <= bc;
		end if;
	end if;
	end process;

process (clk)
begin
	if rising_edge(clk) then
		if ((tran_counter_sig <= x"100") AND (tran_counter_sig >= x"1")) then
			mosi_reg <= data_shift(bc);
		else
			mosi_reg <= '0';
		end if;
	end if;
	end process;
	
end architecture behavioral;
