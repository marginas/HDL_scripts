import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, font
import os
import re
from datetime import datetime
import tkinter.font as tkfont

class CustomText(tk.Text):
    """Text widget with syntax highlighting and line numbers"""
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        
        # Configure tags for VHDL syntax highlighting
        self.tag_configure("keyword", foreground="#569CD6")
        self.tag_configure("type", foreground="#4EC9B0")
        self.tag_configure("comment", foreground="#608B4E")
        self.tag_configure("string", foreground="#CE9178")
        self.tag_configure("number", foreground="#B5CEA8")
        self.tag_configure("operator", foreground="#D4D4D4")
        
        # VHDL keywords
        self.keywords = [
            "architecture", "begin", "case", "component", "downto", "else", "elsif", 
            "end", "entity", "exit", "for", "function", "generate", "generic", "if", 
            "in", "inout", "is", "library", "loop", "map", "next", "not", "null", 
            "of", "out", "package", "port", "process", "range", "record", "return", 
            "signal", "then", "to", "type", "use", "variable", "wait", "when", "while",
            "std_logic", "std_logic_vector", "unsigned", "signed"
        ]
        
    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        """Apply the given tag to all text that matches the given pattern"""
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "" or count.get() == 0: break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

class VHDLTestbenchGenerator:
    # [Previous VHDLTestbenchGenerator class code remains exactly the same]
    # ... [Keep all the previous code for this class]

class TestbenchGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VHDL Testbench Generator")
        self.root.geometry("1200x800")
        
        # Set dark theme
        self.style = ttk.Style()
        self.style.configure(".", background="#1E1E1E", foreground="#D4D4D4")
        self.style.configure("TButton", padding=6)
        self.style.configure("TLabelframe", background="#1E1E1E", foreground="#D4D4D4")
        self.style.configure("TLabelframe.Label", background="#1E1E1E", foreground="#D4D4D4")
        
        self.root.configure(bg="#1E1E1E")
        
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create and configure frame for buttons
        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Create select file button
        self.select_button = ttk.Button(
            self.button_frame, 
            text="Select VHDL File",
            command=self.select_file
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # Create regenerate button
        self.regenerate_button = ttk.Button(
            self.button_frame,
            text="Regenerate Testbench",
            command=self.regenerate_testbench
        )
        self.regenerate_button.pack(side=tk.LEFT, padx=5)
        
        # Create label for selected file
        self.file_label = ttk.Label(self.button_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        # Create frame for text areas
        self.left_frame = ttk.LabelFrame(root, text="Input VHDL File")
        self.left_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.right_frame = ttk.LabelFrame(root, text="Generated Testbench")
        self.right_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Configure frame grid weights
        self.left_frame.grid_columnconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        
        # Create line numbers and text areas
        self.input_line_numbers = tk.Text(
            self.left_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background='#252526',
            foreground='#858585',
            selectbackground='#252526',
            wrap=tk.NONE,
        )
        self.input_line_numbers.grid(row=0, column=0, sticky="nsew")
        
        self.input_text = CustomText(
            self.left_frame,
            wrap=tk.NONE,
            width=50,
            height=30,
            background="#1E1E1E",
            foreground="#D4D4D4",
            insertbackground="#D4D4D4",
            selectbackground="#264F78",
            selectforeground="#D4D4D4",
            relief=tk.FLAT,
            border=0
        )
        self.input_text.grid(row=0, column=1, sticky="nsew")
        
        self.output_line_numbers = tk.Text(
            self.right_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background='#252526',
            foreground='#858585',
            selectbackground='#252526',
            wrap=tk.NONE,
        )
        self.output_line_numbers.grid(row=0, column=0, sticky="nsew")
        
        self.output_text = CustomText(
            self.right_frame,
            wrap=tk.NONE,
            width=50,
            height=30,
            background="#1E1E1E",
            foreground="#D4D4D4",
            insertbackground="#D4D4D4",
            selectbackground="#264F78",
            selectforeground="#D4D4D4",
            relief=tk.FLAT,
            border=0
        )
        self.output_text.grid(row=0, column=1, sticky="nsew")
        
        # Add horizontal scrollbars
        self.input_hscrollbar = ttk.Scrollbar(
            self.left_frame,
            orient=tk.HORIZONTAL,
            command=self.input_text.xview
        )
        self.input_hscrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.input_text.configure(xscrollcommand=self.input_hscrollbar.set)
        
        self.output_hscrollbar = ttk.Scrollbar(
            self.right_frame,
            orient=tk.HORIZONTAL,
            command=self.output_text.xview
        )
        self.output_hscrollbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.output_text.configure(xscrollcommand=self.output_hscrollbar.set)
        
        # Add vertical scrollbars
        self.input_vscrollbar = ttk.Scrollbar(
            self.left_frame,
            orient=tk.VERTICAL,
            command=self.on_input_scroll
        )
        self.input_vscrollbar.grid(row=0, column=2, sticky="ns")
        self.input_text.configure(yscrollcommand=self.input_vscrollbar.set)
        
        self.output_vscrollbar = ttk.Scrollbar(
            self.right_frame,
            orient=tk.VERTICAL,
            command=self.on_output_scroll
        )
        self.output_vscrollbar.grid(row=0, column=2, sticky="ns")
        self.output_text.configure(yscrollcommand=self.output_vscrollbar.set)
        
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
        
        # Bind events for line numbers
        self.input_text.bind('<KeyPress>', lambda e: self.after_ms(10, self.update_line_numbers))
        self.input_text.bind('<KeyRelease>', lambda e: self.after_ms(10, self.update_line_numbers))
        self.output_text.bind('<KeyPress>', lambda e: self.after_ms(10, self.update_line_numbers))
        self.output_text.bind('<KeyRelease>', lambda e: self.after_ms(10, self.update_line_numbers))
        
        # Initial line numbers
        self.update_line_numbers()
        
    def after_ms(self, ms, callback):
        self.root.after(ms, callback)
        
    def on_input_scroll(self, *args):
        self.input_text.yview(*args)
        self.input_line_numbers.yview(*args)
        
    def on_output_scroll(self, *args):
        self.output_text.yview(*args)
        self.output_line_numbers.yview(*args)
        
    def update_line_numbers(self):
        def update_lines(text_widget, line_widget):
            line_widget.delete('1.0', tk.END)
            lines = text_widget.get('1.0', tk.END).count('\n')
            line_numbers = '\n'.join(str(i).rjust(3) for i in range(1, lines + 1))
            line_widget.insert('1.0', line_numbers)
            
        update_lines(self.input_text, self.input_line_numbers)
        update_lines(self.output_text, self.output_line_numbers)
        
    def apply_syntax_highlighting(self, text_widget):
        content = text_widget.get("1.0", tk.END)
        
        # Remove existing tags
        for tag in text_widget.tag_names():
            text_widget.tag_remove(tag, "1.0", tk.END)
        
        # Apply syntax highlighting
        for keyword in text_widget.keywords:
            text_widget.highlight_pattern(r'\y' + keyword + r'\y', "keyword", regexp=True)
        
        # Highlight comments
        text_widget.highlight_pattern(r'--.*$', "comment", regexp=True)
        
        # Highlight strings
        text_widget.highlight_pattern(r'"[^"]*"', "string", regexp=True)
        
        # Highlight numbers
        text_widget.highlight_pattern(r'\b\d+\b', "number", regexp=True)
        
        # Highlight operators
        text_widget.highlight_pattern(r'[<=>:&|+-/*]+', "operator", regexp=True)
        
    def regenerate_testbench(self):
        """Regenerate testbench from current input text content"""
        try:
            content = self.input_text.get('1.0', tk.END)
            self.generator.parse_vhdl_file(content)
            testbench = self.generator.generate_testbench()
            
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', testbench)
            self.apply_syntax_highlighting(self.output_text)
            
            if hasattr(self, 'current_file'):
                output_path = os.path.splitext(self.current_file)[0] + '_tb.vhd'
                with open(output_path, 'w') as file:
                    file.write(testbench)
                self.status_bar.config(
                    text=f"Testbench regenerated successfully: {os.path.basename(output_path)}"
                )
            else:
                self.status_bar.config(text="Testbench regenerated (not saved - no input file selected)")
                
        except Exception as e:
            self.status_bar.config(text=f"Error regenerating testbench: {str(e)}")
        
    def select_file(self):
        """Handle file selection and display content"""
        file_path = filedialog.askopenfilename(
            filetypes=[("VHDL files", "*.vhd *.vhdl"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_file = file_path
                # Update file label
                self.file_label.config(text=os.path.basename(file_path))
                
                # Read and display input file
                with open(file_path, 'r') as file:
                    content = file.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                self.apply_syntax_highlighting(self.input_text)
                
                # Generate and display testbench
                self.generator.parse_vhdl_file(content)
                testbench = self.generator.generate_testbench()
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert('1.0', testbench)
                self.apply_syntax_highlighting(self.output_text)
                
                # Generate output file
                output_path = os.path.splitext(file_path)[0] + '_tb.vhd'
                with open(output_path, 'w') as file:
                    file.write(testbench)
                
                self.status_bar.config(
                    text=f"Testbench generated successfully: {os.path.basename(output_path)}"
                )
                
                # Update line numbers
                self.update_line_numbers()
                
            except Exception as e:
                self.status_bar.config(text=f"Error: {str(e)}")

def main():
    root = tk.Tk()
    app = TestbenchGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()