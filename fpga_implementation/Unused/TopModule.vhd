"""
======================================================
    Power Efficient Error Correction Encoding for
            On-Chip Interconnection Links

            Shlomit Lenefsky & Omri Triki
                        06.2025
======================================================
"""

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.STD_LOGIC_UNSIGNED.ALL;


-- Define the type, currently manually set to 19 registers of 11 bits
type reg_array_type is array (0 to 18) of std_logic_vector(10 downto 0);

entity TopModule is
    Port ( 
		CLK : in  STD_LOGIC;
		RST : in STD_LOGIC;
		ValidIn : in STD_LOGIC;
		registers : out reg_array_type;
		IsEqual : out STD_LOGIC);
end TopModule;

architecture Behavioral of TopModule is

	component FSM_controller is
		port (	
			clk : IN std_logic;
			reset : IN std_logic;
			valid_in : IN std_logic;
			en_gen_data, en_gen_err, en_enc, en_bus, en_dec, en_trans_count, en_bf1, en_bf2, en_k_comp : OUT std_logic;
			trigger, done : OUT std_logic);
	end component FSM_controller;

	component DataPath is
		generic (	
			M : integer := 5;
			k : integer := 32;
			A : integer := 8);
		port (	
			clk : IN std_logic;
			rst : IN std_logic;
			done : IN std_logic;
			en_gen_data, en_gen_err, en_enc, en_bus, en_dec, en_trans_count, en_bf1, en_bf2, en_k_comp : IN std_logic;
≈≈≈			isequal : OUT std_logic);
	end component DataPath;

	-- SIGNALS
	signal trigger : std_logic;
	signal en_gen_data : std_logic;
	signal en_gen_err : std_logic;
	signal en_enc : std_logic;
	signal en_bus : std_logic;
	signal en_dec : std_logic;
	signal en_trans_count : std_logic;
	signal en_bf1 : std_logic;
	signal en_bf2 : std_logic;
	signal en_k_comp : std_logic;
	signal done : std_logic;

	begin
		U1 : FSM_controller
			Port map (	
				clk => CLK,
				reset => RST,
				valid_in => ValidIn,
				en_gen_data => en_gen_data,
				en_gen_err => en_gen_err,
				en_enc => en_enc,
				en_bus => en_bus,
				en_dec => en_dec,
				en_trans_count => en_trans_count,
				en_bf1 => en_bf1,
				en_bf2 => en_bf2,
				en_k_comp => en_k_comp,
				trigger => trigger,
				done => done);
					
		U2 : DataPath
			generic map ()
			port map (	
				clk => CLK,
				reset => RST,
				done => done,
				en_gen_data => en_gen_data,
				en_gen_err => en_gen_err,
				en_enc => en_enc,
				en_bus => en_bus,
				en_dec => en_dec,
				en_trans_count => en_trans_count,
				en_bf1 => en_bf1,
				en_bf2 => en_bf2,
				en_k_comp => en_k_comp,
				registers => registers,
				isequal => IsEqual);

end Behavioral;
