import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
from vhdl_testbench_generator import VHDLTestbenchGenerator  # Assuming previous code is saved as vhdl_testbench_generator.py

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
