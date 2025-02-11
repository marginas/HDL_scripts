import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
import re
from datetime import datetime

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

class TestbenchGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VHDL Testbench Generator")
        self.root.geometry("1200x800")
        
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create and configure frame for button
        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Create select file button
        self.select_button = ttk.Button(
            self.button_frame, 
            text="Select VHDL File",
            command=self.select_file
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # Create label for selected file
        self.file_label = ttk.Label(self.button_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        # Create frame for text areas
        self.left_frame = ttk.LabelFrame(root, text="Input VHDL File")
        self.left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.right_frame = ttk.LabelFrame(root, text="Generated Testbench")
        self.right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Configure frame grid weights
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        
        # Create text areas
        self.input_text = scrolledtext.ScrolledText(
            self.left_frame,
            wrap=tk.NONE,
            width=50,
            height=30
        )
        self.input_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.output_text = scrolledtext.ScrolledText(
            self.right_frame,
            wrap=tk.NONE,
            width=50,
            height=30
        )
        self.output_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Add horizontal scrollbars
        self.input_hscrollbar = ttk.Scrollbar(
            self.left_frame,
            orient=tk.HORIZONTAL,
            command=self.input_text.xview
        )
        self.input_hscrollbar.grid(row=1, column=0, sticky="ew")
        self.input_text.configure(xscrollcommand=self.input_hscrollbar.set)
        
        self.output_hscrollbar = ttk.Scrollbar(
            self.right_frame,
            orient=tk.HORIZONTAL,
            command=self.output_text.xview
        )
        self.output_hscrollbar.grid(row=1, column=0, sticky="ew")
        self.output_text.configure(xscrollcommand=self.output_hscrollbar.set)
        
        # Create status bar
        self.status_bar = ttk.Label(
            root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Initialize generator
        self.generator = VHDLTestbenchGenerator()
        
    def select_file(self):
        """Handle file selection and display content"""
        file_path = filedialog.askopenfilename(
            filetypes=[("VHDL files", "*.vhd *.vhdl"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Update file label
                self.file_label.config(text=os.path.basename(file_path))
                
                # Read and display input file
                with open(file_path, 'r') as file:
                    content = file.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                
                # Generate and display testbench
                self.generator.parse_vhdl_file(content)
                testbench = self.generator.generate_testbench()
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert('1.0', testbench)
                
                # Generate output file
                output_path = os.path.splitext(file_path)[0] + '_tb.vhd'
                with open(output_path, 'w') as file:
                    file.write(testbench)
                
                self.status_bar.config(
                    text=f"Testbench generated successfully: {os.path.basename(output_path)}"
                )
                
            except Exception as e:
                self.status_bar.config(text=f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = TestbenchGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
