import re
from datetime import datetime
import os
import sys

class VHDLTestbenchGenerator:
    def __init__(self):
        self.entity_name = ""
        self.ports = []
        self.generics = []
        
    def parse_vhdl_file(self, vhdl_content):
        """Parse VHDL file content to extract entity information."""
        # Find entity declaration
        entity_match = re.search(r'entity\s+(\w+)\s+is', vhdl_content, re.IGNORECASE)
        if entity_match:
            self.entity_name = entity_match.group(1)
        
        # Extract generics
        generic_section = re.search(r'generic\s*\((.*?)\);', vhdl_content, re.IGNORECASE | re.DOTALL)
        if generic_section:
            generic_list = generic_section.group(1)
            generic_items = re.finditer(r'(\w+)\s*:\s*(\w+)\s*:=\s*([^;,]+)', generic_list)
            for item in generic_items:
                self.generics.append({
                    'name': item.group(1),
                    'type': item.group(2),
                    'default': item.group(3).strip()
                })
        
        # Extract ports
        port_section = re.search(r'port\s*\((.*?)\);', vhdl_content, re.IGNORECASE | re.DOTALL)
        if port_section:
            port_list = port_section.group(1)
            port_items = re.finditer(r'(\w+)\s*:\s*(in|out|inout)\s*(\w+(?:\s*\(\s*[\w\s\-]+\s+downto\s+[\w\s\-]+\s*\))?)', port_list)
            for item in port_items:
                self.ports.append({
                    'name': item.group(1),
                    'direction': item.group(2),
                    'type': item.group(3)
                })

    def generate_testbench(self):
        """Generate VHDL testbench code."""
        tb_name = f"{self.entity_name}_tb"
        
        # Start with the testbench template
        testbench = f"""-- Generated VHDL Testbench for {self.entity_name}
-- Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity {tb_name} is
end entity {tb_name};

architecture behavior of {tb_name} is
    -- Component Declaration
    component {self.entity_name} is"""

        # Add generics if they exist
        if self.generics:
            testbench += "\n        generic (\n"
            generic_lines = []
            for generic in self.generics:
                generic_lines.append(
                    f"            {generic['name']} : {generic['type']} := {generic['default']}"
                )
            testbench += ";\n".join(generic_lines) + "\n        );"

        # Add ports
        testbench += "\n        port (\n"
        port_lines = []
        for port in self.ports:
            port_lines.append(
                f"            {port['name']} : {port['direction']} {port['type']}"
            )
        testbench += ";\n".join(port_lines) + "\n        );\n"
        testbench += "    end component;\n\n"

        # Add signals
        testbench += "    -- Signals\n"
        for port in self.ports:
            testbench += f"    signal {port['name']}_tb : {port['type']};\n"

        # Add clock and reset if they exist
        has_clock = any(port['name'].lower().startswith(('clk', 'clock')) for port in self.ports)
        has_reset = any(port['name'].lower().startswith(('rst', 'reset')) for port in self.ports)
        
        if has_clock:
            testbench += "\n    -- Clock period definitions\n"
            testbench += "    constant clk_period : time := 10 ns;\n"

        testbench += "\nbegin\n"
        
        # Instantiate the Unit Under Test (UUT)
        testbench += "\n    -- Instantiate the Unit Under Test (UUT)\n"
        testbench += f"    UUT: {self.entity_name}"
        
        # Add generic map if generics exist
        if self.generics:
            testbench += "\n        generic map (\n"
            generic_maps = []
            for generic in self.generics:
                generic_maps.append(
                    f"            {generic['name']} => {generic['default']}"
                )
            testbench += ",\n".join(generic_maps) + "\n        )"

        # Add port map
        testbench += "\n        port map (\n"
        port_maps = []
        for port in self.ports:
            port_maps.append(
                f"            {port['name']} => {port['name']}_tb"
            )
        testbench += ",\n".join(port_maps) + "\n        );\n"

        # Add clock process if clock exists
        if has_clock:
            clock_signal = next(port['name'] for port in self.ports if port['name'].lower().startswith(('clk', 'clock')))
            testbench += f"""
    -- Clock process
    clk_process: process
    begin
        {clock_signal}_tb <= '0';
        wait for clk_period/2;
        {clock_signal}_tb <= '1';
        wait for clk_period/2;
    end process;
"""

        # Add stimulus process
        testbench += """
    -- Stimulus process
    stim_proc: process
    begin
        -- hold reset state for 100 ns
        wait for 100 ns;

        -- Insert stimulus here
        
        wait;
    end process;

end behavior;"""

        return testbench

def process_file(input_file_path):
    """Process a VHDL file and generate its testbench."""
    try:
        # Read input file
        with open(input_file_path, 'r') as file:
            vhdl_content = file.read()
        
        # Generate testbench
        generator = VHDLTestbenchGenerator()
        generator.parse_vhdl_file(vhdl_content)
        testbench = generator.generate_testbench()
        
        # Create output file path
        dir_path = os.path.dirname(input_file_path)
        file_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_path = os.path.join(dir_path, f"{file_name}_tb.vhd")
        
        # Write testbench to file
        with open(output_file_path, 'w') as file:
            file.write(testbench)
            
        print(f"Testbench generated successfully: {output_file_path}")
        return True
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error generating testbench: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_vhdl_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    process_file(input_file)

if __name__ == "__main__":
    main()
