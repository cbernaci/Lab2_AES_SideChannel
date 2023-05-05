library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.MATH_REAL.all;

entity aes_top is 
	generic(size : natural := 511);
	port (
		clk : in std_logic;
		rst : in std_logic;
		trigger_in : in std_logic;
		slow_clk : out std_logic;
		ss_dec : out std_logic;
		sck : out std_logic;
		mosi_reg : out std_logic
	);
end aes_top;

architecture behavioral of aes_top is

component aes_enc is 
	port(
		clk : in std_logic;
		rst : in std_logic;
		key : in std_logic_vector(127 downto 0);
		plaintext : in std_logic_vector(127 downto 0);
		ciphertext_comp : in std_logic_vector(127 downto 0);
		led0 : out std_logic;
		led1 : out std_logic;
		ciphertext_out : out std_logic_vector(127 downto 0)		
	);
	end component aes_enc;
	
	component spi_mod is 
	port(
		clk : in std_logic;
		rst : in std_logic;
		plaintext : in std_logic_vector(127 downto 0);
		ciphertext : in std_logic_vector(127 downto 0);
		ss_dec : out std_logic;
		sck : out std_logic;
		mosi_reg : out std_logic);
	end component spi_mod;
	
	-- Constants
	constant DEBOUNCE_DELAY : unsigned(31 downto 0) := x"0007A120";
	
	constant key : std_logic_vector(127 downto 0) := x"00000000000000000000000000000080";
	constant ciphertext_comp : std_logic_vector(127 downto 0) := x"c8be1814bad85b4546e521c6d333dd0e";
	constant test : std_logic_vector(127 downto 0) := x"FFEEDDCCBBAA99887766554433221100";
	
	signal done : std_logic := '0';
	signal led1 : std_logic := '0';
	signal rst_com : std_logic := '0';
	signal clk_div : unsigned(23 downto 0) := x"000000";
	signal clk_res : std_logic := '0';
	signal clk_one : std_logic := '0';
	signal trig_in_sig : std_logic := '0';
	signal trig_1 : std_logic := '0';
	signal trig_2 : std_logic := '0';
	signal SD_button_done : std_logic := '0';
	signal SD_click : std_logic := '0';
	signal pti_1 : std_logic := '0';
	signal pti_2 : std_logic := '0';
	signal ss_dec_sig : std_logic := '0';
	signal ciphertext_enc : std_logic_vector(127 downto 0) := x"00000000000000000000000000000000";
	signal plaintext : std_logic_vector(127 downto 0) := x"00000000000000000000000000000000";
	
	signal SD_button_count : unsigned(31 downto 0) := (others => '0');

begin
	led1 <= done;
	slow_clk <= clk_one;
	ss_dec <= ss_dec_sig;
	trig_in_sig <= (NOT trigger_in);
	
	-- Button trigger
	process (clk)
	begin
		if rising_edge(clk) then
			trig_1 <= trig_in_sig;
		end if;
	end process;
	
	process (clk)
	begin
		if rising_edge(clk) then
			trig_2 <= trig_1;
		end if;
	end process;
	
	process (SD_button_count) 
	begin
		if (SD_button_count = DEBOUNCE_DELAY) then 
			SD_button_done <= '1';
		else 
			SD_button_done <= '0';
		end if;
	end process;
	
	process (SD_button_count, done)
	begin
		if (SD_button_count = (DEBOUNCE_DELAY - 1)) then 
			SD_click <= '1';
		else
			SD_click <= '0';
		end if;
	end process;
	
	process (clk)
	begin
		if rising_edge(clk) then
			if (trig_2 = '0') then
				SD_button_count <= (others => '0');
			elsif (SD_button_done = '1') then
				 SD_button_count <= SD_button_count;
			else
				SD_button_count <= SD_button_count + 1;
			end if;
		end if;
	end process;
			
	-- Start AES Encryption based on button press OR trigger pulse
	rst_com <= ((NOT rst) OR trigger_in);
	
	-- Plaintext Increment
	process (clk)
	begin
		if rising_edge(clk) then
			pti_1 <= ss_dec_sig;
		end if;
		end process;

	process (clk)
	begin	
		if rising_edge(clk) then
			pti_2 <= pti_1;
		end if;
		end process;

	process (clk)
	begin	
		if rising_edge(clk) then
			if ((pti_1 = '1') AND (pti_2 = '0')) then
				plaintext(127 downto 0) <= ciphertext_enc(127 downto 0);
			end if;
		end if;
		end process;
	
	-- Clock Divider
	process (clk)
	begin	
		if rising_edge(clk) then
			if (clk_div = x"000000") then
				clk_one <= '1';
			elsif (clk_div = x"0061A7") then
				clk_one <= '0';
			else 
				clk_one <= clk_one;
			end if;
		end if;
		end process;
		
	process (clk)
	begin	
		if rising_edge(clk) then
			if (clk_div = x"00C34F") then
				clk_res <= '1';
			else
				clk_res <= '0';
			end if;
		end if;
		end process;
		
	process (clk)
	begin	
		if rising_edge(clk) then
			if (clk_res = '1') then
				clk_div <= (others => '0');
			else
				clk_div <= clk_div + 1;
			end if;
		end if;
		end process;

	G1 : FOR n IN 0 to 511 GENERATE
		INNERLOOP1: IF (n = 0) GENERATE
			aes_enc_1: aes_enc
				port map( clk => clk_one,
							 rst => rst_com,
							 key => key,
							 plaintext => plaintext,
							 ciphertext_comp => ciphertext_comp,
							 led0 => OPEN,
							 led1 => done,
							 ciphertext_out => ciphertext_enc);
		END GENERATE INNERLOOP1;
		INNERLOOP2: IF (n > 0) GENERATE
			aes_enc_loop: aes_enc
				port map( clk => clk_one,
							rst => rst_com,
							key => key,
							plaintext => plaintext,
							ciphertext_comp => ciphertext_comp,
							led0 => OPEN,
							led1 => OPEN,
							ciphertext_out => OPEN);
		END GENERATE INNERLOOP2;
	END GENERATE G1;		

	spi : spi_mod 
		port map(clk => clk,
					rst => done,
					plaintext => plaintext,
					ciphertext => ciphertext_enc,
					ss_dec => ss_dec_sig,
					sck => sck,
					mosi_reg => mosi_reg);
					
	
end architecture behavioral;
