----------------------------------------------------------------
-- Rover HDL
-- File: motor_control_left.vhd
-- Entity: motor_control_left
-- Description: Circuitry to control left drivetrain motors.
--
-- Written by: David J. Morvay
-- YSU Robotics Club - NASA Lunabotics Competition
-- ECEN 4899 - Senior Design
-- Date: April 2021	                                                    
----------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity motor_control_left is
    port (
           clk : in std_logic;
	   rec_data : in std_logic_vector(7 downto 0);
	   boost : in std_logic;
	   JA : out std_logic
    );
end motor_control_left;

architecture behavior of motor_control_left is

-- Motor Signals
signal counter : unsigned(31 downto 0) := (others => '0');
signal res : std_logic := '0';
signal switch : unsigned(0 downto 0) := "0";

signal period_counter : unsigned(21 downto 0) := (others => '0');
signal period_res : std_logic := '0';

signal duty_cycle : unsigned(19 downto 0) := (others => '0');
signal motor_dc : std_logic := '0';

signal duty_cycle_follow : unsigned(19 downto 0) := (others => '0');

begin

-- Motor control --

	process (clk)
		begin
		if rising_edge(clk) then
			if (boost = '1') then
				case rec_data is
					-- Decreasing
					when "00000000"  => duty_cycle <= x"249F0"; 
					when "00000001"  => duty_cycle <= x"30D40"; 
					when "00000010"  => duty_cycle <= x"2F9B8"; 
					when "00000011"  => duty_cycle <= x"2E630"; 
					when "00000100"  => duty_cycle <= x"2D2A8"; 
					when "00000101"  => duty_cycle <= x"2BF20";
					when "00000110"  => duty_cycle <= x"2AB98"; 
					when "00000111"  => duty_cycle <= x"29810"; 
					when "00001000"  => duty_cycle <= x"28488"; 
					when "00001001"  => duty_cycle <= x"27100"; 
					when "00001010"  => duty_cycle <= x"25D78";
					when "00001011"  => duty_cycle <= x"249F0";
					when "00001100"  => duty_cycle <= x"23668";
					when "00001101"  => duty_cycle <= x"222E0";
					when "00001110"  => duty_cycle <= x"20F58";
					when "00001111"  => duty_cycle <= x"1FBD0"; 
					when "00010000"  => duty_cycle <= x"1E848"; 
					when "00010001"  => duty_cycle <= x"1D4C0";
					when "00010010"  => duty_cycle <= x"1C138"; 
					when "00010011"  => duty_cycle <= x"1ADB0";
					when "00010100"  => duty_cycle <= x"19A28";
					when "00010101"  => duty_cycle <= x"186A0"; 
					when others => duty_cycle <= duty_cycle_follow;
				end case;
			else
				case rec_data is
					-- Decreasing
					when "00000000"  => duty_cycle <= x"249F0"; 
					when "00000001"  => duty_cycle <= x"28488"; 
					when "00000010"  => duty_cycle <= x"27EAC"; 
					when "00000011"  => duty_cycle <= x"278D0"; 
					when "00000100"  => duty_cycle <= x"272F4"; 
					when "00000101"  => duty_cycle <= x"26D18";
					when "00000110"  => duty_cycle <= x"2673C"; 
					when "00000111"  => duty_cycle <= x"26160"; 
					when "00001000"  => duty_cycle <= x"25B84"; 
					when "00001001"  => duty_cycle <= x"255A8"; 
					when "00001010"  => duty_cycle <= x"24FCC";
					when "00001011"  => duty_cycle <= x"249F0";
					when "00001100"  => duty_cycle <= x"24414";
					when "00001101"  => duty_cycle <= x"23E38";
					when "00001110"  => duty_cycle <= x"2385C";
					when "00001111"  => duty_cycle <= x"23280"; 
					when "00010000"  => duty_cycle <= x"22CA4"; 
					when "00010001"  => duty_cycle <= x"226C8";
					when "00010010"  => duty_cycle <= x"220EC"; 
					when "00010011"  => duty_cycle <= x"21B10";
					when "00010100"  => duty_cycle <= x"21534";
					when "00010101"  => duty_cycle <= x"20F58"; 
					when others => duty_cycle <= duty_cycle_follow;
				end case;
			end if;
		end if;
	end process;

	duty_cycle_follow <= duty_cycle;
			

-- period Counter --
	process (clk)
        	begin
    		if rising_edge(clk) then 
			if (period_res = '1') then
				period_counter <= (others => '0');
			else
				period_counter <= period_counter + 1;
			end if;
                end if;
         end process;

	process (clk)
		begin
			if rising_edge(clk) then
				if (period_counter = x"F4240") then 
					period_res <= '1';
				else
					period_res <= '0';
				end if;
			end if;
	end process;

-- Duty-Cylce --
	process (clk)
        	begin
    		if rising_edge(clk) then
			if (period_counter = x"0") then
				motor_dc <= '1';
			elsif (period_counter = duty_cycle) then
				motor_dc <= '0';
			else
				motor_dc <= motor_dc;
			end if;
                end if;
         end process;

--------------------------------------------------------
	process (clk)
        	begin
    		if rising_edge(clk) then
			JA <= motor_dc;
                end if;
         end process;

end behavior;
