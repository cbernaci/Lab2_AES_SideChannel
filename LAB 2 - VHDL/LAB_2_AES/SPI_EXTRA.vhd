process (SD_button_count)
begin
	if (SD_button_count = DEBOUNCE_DELAY) then
		SD_button_done <= '1';
	else 
		SD_button_done <= '0';
	end if;
	end process;

process (SD_button_count)
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
			if (f_btn2 = '0') then
				SD_button_count <= (others => '0');
			elsif (SD_button_done = '1') then
				SD_button_count <= SD_button_count;
			else
				SD_button_count <= SD_button_count + 1;
			end if;
		end if;
		end process;
