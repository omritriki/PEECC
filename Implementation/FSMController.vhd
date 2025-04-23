"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

Library IEEE;
Use ieee.std_logic_1164.ALL;
use ieee.std_logic_arith.ALL;
use ieee.std_logic_unsigned.ALL;

Entity FSM_controller is
	port (
			clk : IN std_logic;
			reset : IN std_logic;
			valid_in : IN std_logic;
			en_gen_data, en_gen_err, en_enc, en_bus, en_dec,en_trans_count,en_bf1,en_bf2, en_k_comp : OUT std_logic;
			trigger, done, load_seed : OUT std_logic
	);
end entity;

Architecture controller_beh of FSM_controller is
	
	type state_type is (idle, S0, S1, S2, S3, S4);
	signal state : state_type;
	signal nextstate : state_type;
	signal enable_cnt, done_cnt : std_logic;
	signal cnt : std_logic_vector (10 downto 0);
	
	begin
		
		-- proces assignment per state 
		p1 : process (clk, reset) begin
				if reset = '1' then
					state <= idle;
					enable_cnt <= '0';
				elsif rising_edge(clk) then
					state <= nextstate;
				end if;
			end process;
		
		p2 : process (state, valid_in, done_cnt) begin
				case state is
					when idle =>
						if valid_in = '1' then
							nextstate <= S0;
							enable_cnt <= '1';
							load_seed <= '1';
						else
							nextstate <= idle;
							enable_cnt <= '0';
						end if;
					when S0 =>
						if done_cnt = '1' then
							nextstate <= S1;
						else
							nextstate <= S0;
						end if;
					when S1 =>
						if done_cnt = '1' then
							nextstate <= S2;
						else
							nextstate <= S1;
						end if;
					when S2 =>
						if done_cnt = '1' then
							nextstate <= S3;
						else
							nextstate <= S2;
						end if;
					when S3 =>
						if done_cnt = '1' then
							nextstate <= S4;
						else
							nextstate <= S3;
						end if;
					when S4 =>
						if done_cnt = '1' then
							nextstate <= idle;
						else
							nextstate <= S4;
						end if;
					when others =>
						nextstate <= idle;
				end case;
			end process;
			
		p3 : process (state) begin
				case state is
					when idle =>										
						en_gen_data <= '0';
						en_enc <= '0';
						en_bus <= '0';
						en_dec <= '0';
						en_trans_count <= '0';
						done <= '0';
						en_bf1 <= '0';
						en_bf2 <= '0';
						en_k_comp <= '0';
					when S0 =>												
						en_gen_data <= '1';
						en_enc <= '0';
						en_bus <= '0';
						en_dec <= '0';
						en_trans_count <= '0';
						done <= '0';
						en_bf1 <= '0';
						en_bf2 <= '0';
						en_k_comp <= '0';
					when S1 =>					
						en_gen_data <= '1';
						en_enc <= '1';
						en_bus <= '0';
						en_dec <= '0';
						en_trans_count <= '0';
						done <= '0';
						en_bf1 <= '0';
						en_bf2 <= '0';
						en_k_comp <= '0';
					when S2 =>						
						en_gen_data <= '1';
						en_enc <= '1';
						en_bus <= '1';
						en_dec <= '0';
						en_trans_count <= '0';
						done <= '0';
						en_bf1 <= '0';
						en_bf2 <= '0';
						en_k_comp <= '0';
					when S3 =>						
						en_gen_data <= '1';
						en_enc <= '1';
						en_bus <= '1';
						en_dec <= '1';
						en_trans_count <= '0';
						done <= '0';
						en_bf1 <= '0';
						en_bf2 <= '0';
						en_k_comp <= '0';
					when S4 =>	
						enable_cnt <= '1';
						done_cnt <= '1';						
						en_gen_data <= '1';
						en_enc <= '1';
						en_bus <= '1';
						en_dec <= '1';
						en_trans_count <= '1';
						done <= '1';
						en_bf1 <= '1';
						en_bf2 <= '1';
						en_k_comp <= '1';
					when others =>
						enable_cnt <= '0';
						done_cnt <= '0';						
						en_gen_data <= '0';
						en_enc <= '0';
						en_bus <= '0';
						en_dec <= '0';
						en_trans_count <= '0';
						done <= '0';
						en_bf1 <= '0';
						en_bf2 <= '0';
						en_k_comp <= '0';
				end case;
			end process;
		
			cnt_inst : process(clk, reset, enable_cnt) begin
				if reset = '1' then
					cnt <= (others => '0');
				elsif rising_edge(clk) then
					if enable_cnt = '1' then
						if cnt = "00000000000" then
							done_cnt <= '1';
						else
							done_cnt <= '0';
						end if;
						cnt <= cnt + 1;
						if (cnt > 0) and (cnt < 4) then  --if the scope can read the trigger signal in one clk cycle we can change this range to be one cycle
							trigger <= '1';
						else
							trigger <= '0';
						end if;
					else
						cnt <= (others => '0');
					end if;
				end if;
			end process;
			
end architecture;