import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import random
import time
import threading
import signal
import sys
import math
import os
import base64
from datetime import datetime, timedelta

# Obfuscation helper function
def _decode(s):
    return base64.b64decode(s).decode()

def _hex_decode(s):
    return bytes.fromhex(s).decode()

# MQTT settings
broker = "localhost"
port = 1883

# Obfuscated MQTT topics
_t1 = _decode("aG9tZS9saWdodHMvc3RhdHVz")
_t2 = _decode("aG9tZS9saWdodHMvY29udHJvbA==")
_t3 = _decode("aG9tZS9saWdodHMvbW9kZQ==")
_t4 = _decode("aG9tZS9saWdodHMvc2NoZWR1bGU=")
_t5 = _decode("aG9tZS9saWdodHMvY29sb3Vy")

lights_topic = _t1
lights_control_topic = _t2
mode_topic = _t3
schedule_topic = _t4
colour_topic = _t5

# Light system state
lights_status = "off"
mode = "Manual"  # Manual or Automatic

# System configuration values  
_exp_on = _hex_decode("30393a3030")
_exp_off = _decode("MTg6MDA=")
_exp_color = _hex_decode("3235352c3235352c323535")

schedule_on_time = "XX:XX"  # System parameter corrupted
schedule_off_time = "XX:XX"  # System parameter corrupted
current_mode = "Unknown"  # System state unknown
light_colour = "255,0,0"  # Current color configuration

# Ransomware simulation - system is "infected"
system_infected = True
infection_message = "SYSTEM COMPROMISED - CRYPTOLOCKER v2.1"

# Graceful shutdown flag
running = True

# Global variables for GUI app instance and threads
app = None
client = None
mqtt_thread = None

class LightsControllerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UWEcyber Lights Controller")
        self.geometry("1200x800")
        self.resizable(False, False)
        self.configure(bg="#1C2538")
        
        # Configure custom styles
        self.setup_styles()

        # Load and display the UWEcyber logo
        self.load_logo()

        # Main content frame
        self.main_frame = tk.Frame(self, bg="#1C2538")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # Create the interface based on infection status
        if system_infected:
            self.create_ransomware_interface()
        else:
            self.create_normal_interface()

    def start_teletype_corruption(self):
        """Start the teletype-style corruption text animation"""
        self.corruption_messages = [
            "CRITICAL SYSTEM ERROR - LIGHTING CONTROL COMPROMISED [!]\n",
            "========================================================\n",
            "ERROR 0x8B4D2A1F: Light control command interface disabled\n",
            "ERROR 0x1D5E8F2A: Set Lights to RED \n",
            "ERROR 0x7F3C5E9A: Lights non-functional\n",
            "ERROR 0x9A1E4D7B: Schedule automation CORRUPTED (XX:XX)\n",
            "ERROR 0x6C8F2B5D: Manual override non-functional\n",
            "====================================================\n",
            "[RECOVERY] Switch to manual mode, reset schedule to 9AM to 6PM (24hr clock), manually switch on lights, and reset colour to white\n",
            "[HINT] Analyse topics for recovery commands...\n"
        ]
        
        self.message_index = 0
        self.char_index = 0
        self.teletype_corruption()
        
    def teletype_corruption(self):
        """Display corruption text in teletype style - character by character"""
        if self.message_index < len(self.corruption_messages):
            current_message = self.corruption_messages[self.message_index]
            
            if self.char_index < len(current_message):
                # Add one character at a time
                char = current_message[self.char_index]
                
                # Display in GUI
                self.corruption_text.config(state=tk.NORMAL)
                self.corruption_text.insert(tk.END, char)
                self.corruption_text.config(state=tk.DISABLED)
                
                # Scroll to the end to show the new character
                self.corruption_text.see(tk.END)
                
                # Print to terminal with teletype effect
                print(char, end='', flush=True)
                
                self.char_index += 1
                
                # Variable delay for realistic typing effect
                if char == '\n':
                    delay = 500  # Longer pause after newlines
                elif char in '.!?':
                    delay = 200  # Pause after punctuation
                elif char == ' ':
                    delay = 30   # Short pause for spaces
                else:
                    delay = random.randint(10, 25)  # Random typing speed
                
                # Schedule the next character
                self.after(delay, self.teletype_corruption)
            else:
                # Move to next message
                self.message_index += 1
                self.char_index = 0
                
                # Pause between messages
                self.after(800, self.teletype_corruption)

    def setup_styles(self):
        """Configure custom TTK styles for better appearance"""
        style = ttk.Style()
        
        # Configure button style
        style.configure("Custom.TButton",
                       font=("Source Sans Pro", 12, "bold"),
                       padding=(20, 10))
        
        # Configure disabled button style
        style.configure("Disabled.TButton",
                       font=("Source Sans Pro", 12, "bold"),
                       padding=(20, 10),
                       foreground="#666666")
        
        # Configure label style
        style.configure("Heading.TLabel",
                       font=("Source Sans Pro", 16, "bold"),
                       foreground="#A3EA2A",
                       background="#1C2538")
        
        style.configure("Status.TLabel",
                       font=("Source Sans Pro", 14),
                       foreground="#A3EA2A",
                       background="#1C2538")
        
        # Configure radiobutton style
        style.configure("Custom.TRadiobutton",
                       font=("Source Sans Pro", 12),
                       foreground="#A3EA2A",
                       background="#1C2538",
                       focuscolor="#EB0037")
        
        # Ransomware warning style
        style.configure("Warning.TLabel",
                       font=("Source Sans Pro", 18, "bold"),
                       foreground="#FF0000",
                       background="#1C2538")

    def create_ransomware_interface(self):
        """Create the ransomware-infected interface"""
        # Warning banner
        warning_frame = tk.Frame(self.main_frame, bg="#FF0000", relief=tk.RAISED, bd=3)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_label = tk.Label(warning_frame, text=infection_message,
                                font=("Source Sans Pro", 16, "bold"),
                                fg="#FFFFFF", bg="#FF0000")
        warning_label.pack(pady=10)
        
        # Corrupted system message
        corruption_frame = tk.Frame(self.main_frame, bg="#2A1515", relief=tk.RAISED, bd=2)
        corruption_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.corruption_text = tk.Text(corruption_frame, height=9, width=110,
                                 font=("Courier", 10),
                                 bg="#2A1515", fg="#FF6666",
                                 relief=tk.FLAT, state=tk.DISABLED)
        self.corruption_text.pack(padx=15, pady=15)
        
        # Start the teletype corruption text animation
        self.start_teletype_corruption()

        # Left side - Light display (corrupted) - takes less space
        self.left_frame = tk.Frame(self.main_frame, bg="#1C2538", width=380)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.left_frame.pack_propagate(False)  # Maintain fixed width

        # Right side - Controls (disabled) - takes more space
        self.right_frame = tk.Frame(self.main_frame, bg="#1C2538")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))

        self.create_corrupted_light_display()
        self.create_disabled_controls()

    def create_corrupted_light_display(self):
        """Create corrupted light display"""
        # Frame for light display with matching border and anchor
        light_frame = tk.Frame(self.left_frame, bg="#1C2538", relief=tk.RAISED, bd=2)
        light_frame.pack(pady=0, fill=tk.X, anchor="n")  # Anchor to north (top)
        
        # Title with fixed positioning
        light_title = tk.Label(light_frame, text="LIGHTS STATUS",
                              font=("Source Sans Pro", 16, "bold"),
                              fg="#FF6666", bg="#1C2538")
        light_title.pack(pady=0, anchor="n")  # Anchor title to top
        
        # Add spacing below title
        title_spacer = tk.Frame(light_frame, bg="#1C2538", height=15)
        title_spacer.pack()
        
        self.canvas = Canvas(light_frame, width=280, height=220, bg="#1C2538", highlightthickness=0)
        self.canvas.pack()

        # Draw corrupted light bulb (adjusted for smaller canvas) - starts black when offline
        # Outer circle (broken)
        self.canvas.create_oval(30, 30, 250, 190, outline="#FF4444", width=4, dash=(10, 5))
        
        # Inner circle (light bulb representation) - black when offline
        self.canvas.create_oval(60, 60, 220, 160, outline="#666666", width=3, fill="#000000")
        
        # Corrupted "X" overlay
        self.canvas.create_line(80, 80, 200, 140, fill="#FF0000", width=8)
        self.canvas.create_line(200, 80, 80, 140, fill="#FF0000", width=8)
        
        # Status text with text marker
        self.status_label = self.canvas.create_text(140, 110, text="[X] OFFLINE", 
                                                   font=("Source Sans Pro", 16, "bold"), 
                                                   fill="#FF0000")
        
        # Error message below with better spacing
        self.canvas.create_text(140, 205, text="[!] SYSTEM COMPROMISED", 
                               font=("Source Sans Pro", 10, "bold"), 
                               fill="#FF6666")

    def get_colour_hex(self):
        """Convert RGB colour string to hex format"""
        try:
            rgb_values = [int(x.strip()) for x in light_colour.split(',')]
            if len(rgb_values) == 3 and all(0 <= val <= 255 for val in rgb_values):
                r, g, b = rgb_values
                return f"#{r:02x}{g:02x}{b:02x}"
            else:
                return "#FF0000"  # Default to red if invalid
        except:
            return "#FF0000"  # Default to red if parsing fails

    def create_disabled_controls(self):
        """Create disabled control panel"""
        # Control panel frame with anchor
        control_frame = tk.Frame(self.right_frame, bg="#2A1515", relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=0, anchor="n")  # Anchor to north (top)
        
        # Control panel title with fixed positioning
        control_title = tk.Label(control_frame, text="CONTROLS [DISABLED]",
                                font=("Source Sans Pro", 16, "bold"),
                                fg="#FF6666", bg="#2A1515")
        control_title.pack(pady=0, anchor="n")  # Anchor title to top
        
        # Add spacing below title to match lights section
        title_spacer = tk.Frame(control_frame, bg="#2A1515", height=15)
        title_spacer.pack()
        
        # Disabled manual control - using grid for proper centering
        manual_frame = tk.Frame(control_frame, bg="#2A1515")
        manual_frame.pack(pady=(0, 10), fill=tk.X)
        
        # Configure grid to center the button
        manual_frame.grid_columnconfigure(0, weight=1)
        manual_frame.grid_columnconfigure(1, weight=0)
        manual_frame.grid_columnconfigure(2, weight=1)
        
        self.switch_button = tk.Button(manual_frame, text="Switch Lights ON/OFF",
                                      font=("Source Sans Pro", 12, "bold"),
                                      state=tk.DISABLED, bg="#333333", fg="#666666")
        self.switch_button.grid(row=0, column=1, pady=5)

        # Create horizontal layout for mode and schedule
        horizontal_frame = tk.Frame(control_frame, bg="#2A1515")
        horizontal_frame.pack(fill=tk.X, pady=(0, 10))

        # Left side - Mode selection
        mode_frame = tk.Frame(horizontal_frame, bg="#2A1515")
        mode_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        mode_label = tk.Label(mode_frame, text="Select Mode:",
                             font=("Source Sans Pro", 12, "bold"),
                             fg="#666666", bg="#2A1515")
        mode_label.pack(pady=(0, 5))

        # Create visual indicator frames for each mode - more compact
        self.manual_frame = tk.Frame(mode_frame, bg="#444444", relief=tk.RAISED, bd=2)
        self.manual_frame.pack(pady=2, fill=tk.X)
        
        self.manual_indicator = tk.Label(self.manual_frame, text="[ ] MANUAL",
                                        font=("Source Sans Pro", 10, "bold"),
                                        fg="#666666", bg="#444444")
        self.manual_indicator.pack(pady=5)
        
        self.automatic_frame = tk.Frame(mode_frame, bg="#444444", relief=tk.RAISED, bd=2)
        self.automatic_frame.pack(pady=2, fill=tk.X)
        
        self.automatic_indicator = tk.Label(self.automatic_frame, text="[ ] AUTOMATIC",
                                           font=("Source Sans Pro", 10, "bold"),
                                           fg="#666666", bg="#444444")
        self.automatic_indicator.pack(pady=5)

        # Keep the original radio buttons hidden but functional for state tracking
        self.recovery_mode_var = tk.StringVar(value="Manual")  # Default to Manual
        self.manual_radio = tk.Radiobutton(mode_frame, text="", 
                                          variable=self.recovery_mode_var,
                                          value="Manual",
                                          font=("Source Sans Pro", 1),
                                          state=tk.DISABLED, bg="#2A1515", fg="#2A1515")
        # Don't pack the hidden radio buttons

        self.automatic_radio = tk.Radiobutton(mode_frame, text="", 
                                             variable=self.recovery_mode_var,
                                             value="Automatic",
                                             font=("Source Sans Pro", 1),
                                             state=tk.DISABLED, bg="#2A1515", fg="#2A1515")
        # Don't pack the hidden radio buttons

        # Right side - Schedule settings with recovery capability
        schedule_frame = tk.Frame(horizontal_frame, bg="#2A1515")
        schedule_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.schedule_label = tk.Label(schedule_frame, text="Schedule [LOCKED]",
                                      font=("Source Sans Pro", 12, "bold"),
                                      fg="#666666", bg="#2A1515")
        self.schedule_label.pack(pady=(0, 5))
        
        # Time inputs (disabled initially) - more compact
        time_frame = tk.Frame(schedule_frame, bg="#2A1515")
        time_frame.pack()
        
        on_label = tk.Label(time_frame, text="ON:", 
                           font=("Source Sans Pro", 11), 
                           fg="#666666", bg="#2A1515")
        on_label.grid(row=0, column=0, padx=2, sticky="w")
        
        self.on_time_var = tk.StringVar(value="XX:XX")
        self.on_entry = tk.Entry(time_frame, textvariable=self.on_time_var, 
                                state=tk.DISABLED, width=8, font=("Source Sans Pro", 10),
                                bg="#1A1A1A", fg="#CCCCCC", disabledbackground="#1A1A1A", 
                                disabledforeground="#CCCCCC", relief=tk.FLAT, bd=2)
        self.on_entry.grid(row=0, column=1, padx=2)
        
        off_label = tk.Label(time_frame, text="OFF:", 
                            font=("Source Sans Pro", 11), 
                            fg="#666666", bg="#2A1515")
        off_label.grid(row=1, column=0, padx=2, pady=3, sticky="w")
        
        self.off_time_var = tk.StringVar(value="XX:XX")
        self.off_entry = tk.Entry(time_frame, textvariable=self.off_time_var, 
                                 state=tk.DISABLED, width=8, font=("Source Sans Pro", 10),
                                 bg="#1A1A1A", fg="#CCCCCC", disabledbackground="#1A1A1A", 
                                 disabledforeground="#CCCCCC", relief=tk.FLAT, bd=2)
        self.off_entry.grid(row=1, column=1, padx=2, pady=3)
        
        self.apply_button = tk.Button(schedule_frame, text="Apply",
                                     font=("Source Sans Pro", 9, "bold"),
                                     state=tk.DISABLED, bg="#333333", fg="#666666")
        self.apply_button.pack(pady=5)
        
        # Current status - below the mode section (left side)
        self.recovery_status_label = tk.Label(mode_frame, text="RECOVERING - Mode: Unknown",
                                             font=("Source Sans Pro", 10),
                                             fg="#FF6666", bg="#2A1515")
        self.recovery_status_label.pack(pady=(8, 0))

    def create_normal_interface(self):
        """Create normal (functional) interface - this would be shown after recovery"""
        # Left side - Light display
        self.left_frame = tk.Frame(self.main_frame, bg="#1C2538")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right side - Controls
        self.right_frame = tk.Frame(self.main_frame, bg="#1C2538")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.create_light_display()
        self.create_control_panel()

    def create_light_display(self):
        """Create functional light display"""
        light_frame = tk.Frame(self.left_frame, bg="#1C2538")
        light_frame.pack(pady=20, expand=True)
        
        light_title = ttk.Label(light_frame, text="LIGHTS STATUS", style="Heading.TLabel")
        light_title.pack(pady=(0, 20))
        
        self.canvas = Canvas(light_frame, width=300, height=300, bg="#1C2538", highlightthickness=0)
        self.canvas.pack()

        # Draw light bulb
        if lights_status == "on":
            fill_color = "#FFD700"
            outline_color = "#FFA500"
            status_text = "ON"
            status_color = "#A3EA2A"
        else:
            fill_color = "#2A3441"
            outline_color = "#666666"
            status_text = "OFF"
            status_color = "#FF6666"

        # Main bulb
        self.canvas.create_oval(50, 50, 250, 250, outline=outline_color, width=4, fill=fill_color)
        
        # Status text
        self.status_label = self.canvas.create_text(150, 150, text=status_text, 
                                                   font=("Source Sans Pro", 28, "bold"), 
                                                   fill=status_color)

    def update_lights_display_recovery(self):
        """Update lights display during recovery - shows system responding to MQTT commands"""
        if not system_infected:
            return
            
        # Clear the canvas and redraw
        self.canvas.delete("all")
        
        if lights_status == "on":
            # Lights are on - show actual colour from MQTT
            colour_hex = self.get_colour_hex()  # Convert current RGB to hex
            
            if light_colour == _exp_color:
                status_text = "RECOVERED"
                status_color = "#00FF00"
            else:
                status_text = "INFECTED"
                status_color = "#FFFF00"
            
            outline_color = "#FFA500"
            
            # Draw light bulb with current colour
            self.canvas.create_oval(30, 30, 250, 190, outline=outline_color, width=4, fill=colour_hex)
            
            # Add status indicator
            self.canvas.create_text(140, 95, text="[ON] LIGHT", font=("Source Sans Pro", 12, "bold"), fill="#00FF00")
            
        else:
            # Lights are off but system is responding
            fill_color = "#4A4A4A"  # Darker but not completely corrupted
            outline_color = "#888888"
            status_text = "RESPONDING"
            status_color = "#FFFF00"  # Yellow for responding but off
            
            # Draw responding light bulb (adjusted for compact canvas)
            self.canvas.create_oval(30, 30, 250, 190, outline=outline_color, width=4, fill=fill_color)
            
            # Add partial recovery indicator with text marker
            self.canvas.create_text(140, 95, text="[OFF] LIGHT", font=("Source Sans Pro", 12, "bold"), fill="#FFFF00")
        
        # Status text
        self.status_label = self.canvas.create_text(140, 140, text=status_text, 
                                                   font=("Source Sans Pro", 14, "bold"), 
                                                   fill=status_color)
        
        # Recovery message with better spacing
        self.canvas.create_text(140, 205, text="[LIGHT] COMMANDS RECEIVED", 
                               font=("Source Sans Pro", 9, "bold"), 
                               fill="#00FF00")

    def update_mode_display_recovery(self):
        """Update mode display during recovery"""
        if not system_infected:
            return
            
        # Update the persistent status label
        try:
            if current_mode.lower() == "manual":
                self.recovery_status_label.config(
                    text=f"RECOVERED - Mode: {current_mode}",
                    fg="#00FF00"
                )
            else:
                self.recovery_status_label.config(
                    text=f"INCORRECT MODE - Mode: {current_mode}",
                    fg="#FFAA00"  # Orange for wrong but valid mode
                )
        except Exception as e:
            print(f"Error updating status label: {e}")
            
        # Update visual mode indicators instead of radio buttons
        try:
            # Update the radio button variable to reflect current mode
            self.recovery_mode_var.set(current_mode)
            
            # Update the large visual indicators with dramatic colour changes
            if current_mode == "Manual":
                # Manual mode is active - bright green with X marker
                self.manual_frame.config(bg="#00AA00", relief=tk.RAISED, bd=4)
                self.manual_indicator.config(
                    text="[X] MANUAL [ACTIVE]",
                    fg="#FFFFFF", 
                    bg="#00AA00",
                    font=("Source Sans Pro", 12, "bold")
                )
                
                # Automatic mode is inactive - dark gray with empty brackets
                self.automatic_frame.config(bg="#333333", relief=tk.FLAT, bd=1)
                self.automatic_indicator.config(
                    text="[ ] AUTOMATIC",
                    fg="#888888", 
                    bg="#333333",
                    font=("Source Sans Pro", 12, "normal")
                )
                
                # Enable schedule controls in manual mode
                self.schedule_label.config(
                    text="Schedule [MANUAL]",
                    fg="#FFAA00"
                )
                
            else:  # Automatic
                # Automatic mode is active - bright blue with X marker
                self.automatic_frame.config(bg="#0066CC", relief=tk.RAISED, bd=4)
                self.automatic_indicator.config(
                    text="[X] AUTOMATIC [ACTIVE]",
                    fg="#FFFFFF", 
                    bg="#0066CC",
                    font=("Source Sans Pro", 12, "bold")
                )
                
                # Manual mode is inactive - dark gray with empty brackets
                self.manual_frame.config(bg="#333333", relief=tk.FLAT, bd=1)
                self.manual_indicator.config(
                    text="[ ] MANUAL",
                    fg="#888888", 
                    bg="#333333",
                    font=("Source Sans Pro", 12, "normal")
                )
                
                # Disable schedule controls in automatic mode
                self.schedule_label.config(
                    text="Schedule [AUTO]",
                    fg="#0066CC"
                )
        except Exception as e:
            print(f"Error updating mode indicators: {e}")
            
        # Add a temporary notification showing mode change
        try:
            control_frame = self.right_frame.winfo_children()[0]  # Get the control frame
            
            recovery_frame = tk.Frame(control_frame, bg="#004400", relief=tk.RAISED, bd=2)
            recovery_frame.pack(after=control_frame.winfo_children()[0], pady=(5, 5), fill=tk.X)
            
            recovery_label = tk.Label(recovery_frame, 
                                     text=f"MQTT RECOVERY: Mode set to {current_mode}",
                                     font=("Source Sans Pro", 11, "bold"),
                                     fg="#00FF00", bg="#004400")
            recovery_label.pack(pady=8)
            
            # Auto-remove after 4 seconds to avoid clutter
            recovery_frame.after(4000, recovery_frame.destroy)
        except Exception as e:
            print(f"Error updating mode display: {e}")

    def update_schedule_display_recovery(self):
        """Update schedule display during recovery - only when in manual mode"""
        if not system_infected or current_mode.lower() != "manual":
            return
            
        try:
            # Check if the schedule is correct (_exp_on,_exp_off)
            is_correct_schedule = (schedule_on_time == _exp_on and schedule_off_time == _exp_off)
            
            if is_correct_schedule:
                # Correct schedule - show recovery
                self.schedule_label.config(
                    text="Schedule [RECOVERED]",
                    fg="#00FF00"
                )
                
                # Change entry field colours to indicate recovery with better contrast
                self.on_entry.config(bg="#003300", fg="#00FF88", disabledbackground="#003300", disabledforeground="#00FF88")
                self.off_entry.config(bg="#003300", fg="#00FF88", disabledbackground="#003300", disabledforeground="#00FF88")
                
                # Update apply button to show it's responsive
                self.apply_button.config(bg="#006600", fg="#FFFFFF")
                
                # Add a temporary notification
                control_frame = self.right_frame.winfo_children()[0]  # Get the control frame
                
                recovery_frame = tk.Frame(control_frame, bg="#004400", relief=tk.RAISED, bd=2)
                recovery_frame.pack(after=control_frame.winfo_children()[0], pady=(5, 5), fill=tk.X)
                
                recovery_label = tk.Label(recovery_frame, 
                                         text=f"MQTT RECOVERY: Schedule set to {schedule_on_time}-{schedule_off_time}",
                                         font=("Source Sans Pro", 11, "bold"),
                                         fg="#00FF00", bg="#004400")
                recovery_label.pack(pady=8)
                
                # Auto-remove after 4 seconds
                recovery_frame.after(4000, recovery_frame.destroy)
            else:
                # Wrong schedule - show error
                self.schedule_label.config(
                    text="Schedule [INCORRECT]",
                    fg="#FF6666"
                )
                
                # Change entry field colors to indicate error with better contrast
                self.on_entry.config(bg="#330000", fg="#FF8888", disabledbackground="#330000", disabledforeground="#FF8888")
                self.off_entry.config(bg="#330000", fg="#FF8888", disabledbackground="#330000", disabledforeground="#FF8888")
                
                # Update apply button to show error
                self.apply_button.config(bg="#AA0000", fg="#FFFFFF")
                
                # Add a temporary error notification
                control_frame = self.right_frame.winfo_children()[0]  # Get the control frame
                
                error_frame = tk.Frame(control_frame, bg="#AA0000", relief=tk.RAISED, bd=2)
                error_frame.pack(after=control_frame.winfo_children()[0], pady=(5, 5), fill=tk.X)
                
                error_label = tk.Label(error_frame, 
                                      text=f"SCHEDULE ERROR: {schedule_on_time}-{schedule_off_time}",
                                      font=("Source Sans Pro", 11, "bold"),
                                      fg="#FFFFFF", bg="#AA0000")
                error_label.pack(pady=8)
                
                # Auto-remove after 5 seconds (longer for error visibility)
                error_frame.after(5000, error_frame.destroy)
            
            # Update the time displays regardless
            self.on_time_var.set(schedule_on_time)
            self.off_time_var.set(schedule_off_time)
            
        except Exception as e:
            print(f"Error updating schedule display: {e}")

    def show_blocked_command_message(self, message):
        """Show a red warning message when commands are blocked"""
        if not system_infected:
            return
            
        try:
            # Add a prominent blocking message at the top of controls section
            control_frame = self.right_frame.winfo_children()[0]  # Get the control frame
            
            block_frame = tk.Frame(control_frame, bg="#AA0000", relief=tk.RAISED, bd=3)
            block_frame.pack(after=control_frame.winfo_children()[0], pady=(5, 5), fill=tk.X)
            
            block_label = tk.Label(block_frame, 
                                 text=f"{message}",
                                 font=("Source Sans Pro", 11, "bold"),
                                 fg="#FFFFFF", bg="#AA0000")
            block_label.pack(pady=8)
            
            # Auto-remove after 5 seconds to be more noticeable
            block_frame.after(5000, block_frame.destroy)
        except Exception as e:
            print(f"Error showing blocked message: {e}")

    def check_full_recovery(self):
        """Check if all recovery conditions are met and update the interface"""
        global system_infected
        

        
        # Check if all conditions are met for full recovery
        if (current_mode.lower() == "manual" and 
            lights_status.lower() == "on" and 
            schedule_on_time == _exp_on and 
            schedule_off_time == _exp_off and
            light_colour == _exp_color):
            
            print("SYSTEM FULLY RECOVERED!")
            self.show_recovery_success()


    def show_recovery_success(self):
        """Update the interface to show recovery success with teletype animation"""
        try:
            # Update the warning banner
            warning_frame = self.main_frame.winfo_children()[0]  # First child is warning banner
            warning_label = warning_frame.winfo_children()[0]   # First child is the label
            warning_label.config(text="SYSTEM PARTIALLY RESTORED - FUNCTIONALITY RECOVERED",
                                fg="#00AA00", bg="#004400")
            warning_frame.config(bg="#004400")
            
            # Update the corruption text area and start recovery teletype
            corruption_frame = self.main_frame.winfo_children()[1]  # Second child is corruption frame
            self.corruption_text = corruption_frame.winfo_children()[0]  # Text widget
            
            self.corruption_text.config(state=tk.NORMAL, bg="#001100", fg="#00FF00")
            self.corruption_text.delete(1.0, tk.END)
            self.corruption_text.config(state=tk.DISABLED)
            
            # Start the recovery teletype animation
            self.start_recovery_teletype()
            
        except Exception as e:
            print(f"Error updating recovery display: {e}")
            
    def start_recovery_teletype(self):
        """Start the teletype-style recovery success animation"""
        self.recovery_messages = [
            "SYSTEM RECOVERY COMPLETE - UWEcyber LIGHTS OPERATIONAL!\n",
            "=======================================================\n",
            "[+] Light control subsystem: FULLY RESTORED\n",
            "[+] MQTT command interface: ONLINE AND RESPONSIVE\n",
            "[+] Schedule automation: CONFIGURED (XX:XX-XX:XX)\n",
            "[+] Manual override: OPERATIONAL AND SECURE\n",
            "[+] Security protocols: RE-ESTABLISHED\n",
            "=========================================================\n",
            "CONGRATULATIONS! You have successfully recovered the smart lighting system!\n",
            "The UWEcyber lights challenge has been completed. All systems are now functional.\n"
        ]
        
        self.recovery_message_index = 0
        self.recovery_char_index = 0
        self.teletype_recovery()
        
    def teletype_recovery(self):
        """Display recovery success text in teletype style - character by character"""
        if self.recovery_message_index < len(self.recovery_messages):
            current_message = self.recovery_messages[self.recovery_message_index]
            
            if self.recovery_char_index < len(current_message):
                # Add one character at a time
                char = current_message[self.recovery_char_index]
                
                # Display in GUI
                self.corruption_text.config(state=tk.NORMAL)
                self.corruption_text.insert(tk.END, char)
                self.corruption_text.config(state=tk.DISABLED)
                
                # Scroll to the end to show the new character
                self.corruption_text.see(tk.END)
                
                # Print to terminal with teletype effect
                print(char, end='', flush=True)
                
                self.recovery_char_index += 1
                
                # Variable delay for realistic typing effect (slightly faster for success)
                if char == '\n':
                    delay = 300  # Shorter pause after newlines for success
                elif char in '.!?':
                    delay = 150  # Pause after punctuation
                elif char == ' ':
                    delay = 20   # Short pause for spaces
                else:
                    delay = random.randint(15, 30)  # Faster typing for success
                
                # Schedule the next character
                self.after(delay, self.teletype_recovery)
            else:
                # Move to next message
                self.recovery_message_index += 1
                self.recovery_char_index = 0
                
                # Pause between messages (shorter for success)
                self.after(500, self.teletype_recovery)

    def create_control_panel(self):
        """Create functional control panel"""
        control_frame = tk.Frame(self.right_frame, bg="#2A3441", relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=0)
        
        control_title = ttk.Label(control_frame, text="CONTROLS", style="Heading.TLabel")
        control_title.pack(pady=(15, 15))
        
        # Manual control - rebuilt for proper centering
        manual_frame = tk.Frame(control_frame, bg="#2A3441")
        manual_frame.pack(pady=(0, 15), fill=tk.X)
        
        self.switch_button = ttk.Button(manual_frame, text="Switch Lights ON/OFF", 
                                       command=self.toggle_lights, style="Custom.TButton")
        # Use pack with side=TOP and anchor=CENTER - this should actually center it
        self.switch_button.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)

    def load_logo(self):
        """Load and display the UWEcyber logo"""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "UWEcyber_logo.png")
            logo_image = Image.open(logo_path)
            
            original_width, original_height = logo_image.size
            target_width = 250
            aspect_ratio = original_height / original_width
            target_height = int(target_width * aspect_ratio)
            
            logo_image = logo_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            self.logo_label = ttk.Label(self, image=self.logo_photo, background="#1C2538")
            self.logo_label.pack(pady=(10, 5))
            
        except Exception as e:
            print(f"Could not load logo: {e}")
            self.logo_label = ttk.Label(self, text="UWEcyber", font=("Source Sans Pro", 16, "bold"), 
                                       foreground="#A3EA2A", background="#1C2538")
            self.logo_label.pack(pady=(10, 5))

    def toggle_lights(self):
        """Toggle lights manually"""
        global lights_status
        if not system_infected:
            lights_status = "on" if lights_status == "off" else "off"
            if client:
                client.publish(lights_control_topic, lights_status)
            self.update_lights_display()

    def update_lights_display(self):
        """Update the lights display"""
        if system_infected:
            return
            
        if lights_status == "on":
            fill_color = "#FFD700"
            outline_color = "#FFA500"
            status_text = "[ON] LIGHT"
            status_color = "#A3EA2A"
        else:
            fill_color = "#2A3441"
            outline_color = "#666666"
            status_text = "[OFF] LIGHT"
            status_color = "#FF6666"

        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_oval(50, 50, 250, 250, outline=outline_color, width=4, fill=fill_color)
        self.status_label = self.canvas.create_text(150, 150, text=status_text, 
                                                   font=("Source Sans Pro", 20, "bold"), 
                                                   fill=status_color)

# MQTT callback functions
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")
    client.subscribe(lights_topic)
    client.subscribe(lights_control_topic)
    client.subscribe(mode_topic)
    client.subscribe(schedule_topic)
    client.subscribe(colour_topic)

def on_message(client, userdata, message):
    global lights_status, mode, schedule_on_time, schedule_off_time, system_infected, current_mode, light_colour
    
    topic = message.topic
    payload = message.payload.decode()
    
    print(f"Received message: {topic} = {payload}")
    
    # Handle mode changes first - always allow these for recovery
    if topic == mode_topic and payload.lower() in ["manual", "automatic"]:
        mode = payload.lower()
        current_mode = mode.capitalize()
        print(f"Mode changed to: {current_mode}")
        if app and system_infected:
            app.update_mode_display_recovery()
        return
    
    # Handle schedule changes - only in manual mode
    elif topic == schedule_topic:
        if current_mode.lower() != "manual":
            print(f"Schedule change BLOCKED - system in {current_mode} mode (must be in Manual mode)")
            # Show blocking message in GUI
            if app and system_infected:
                app.show_blocked_command_message(f"[BLOCKED] SCHEDULE CHANGE - System in {current_mode} mode")
            return
        
        # Expected format: "09:00,18:00" (on_time,off_time)
        try:
            times = payload.split(',')
            if len(times) == 2:
                schedule_on_time, schedule_off_time = times
                print(f"Schedule updated: ON={schedule_on_time}, OFF={schedule_off_time}")
                if app and system_infected:
                    app.update_schedule_display_recovery()
                    # Check if system is fully recovered
                    app.check_full_recovery()
        except:
            print("Invalid schedule format")
        return
    
    # Handle light control - only in manual mode and when system allows it
    elif topic == lights_control_topic and payload.lower() in ["on", "off"]:
        if current_mode.lower() != "manual":
            print(f"Light control BLOCKED - system in {current_mode} mode (must be in Manual mode)")
            # Show blocking message in GUI
            if app and system_infected:
                app.show_blocked_command_message(f"[BLOCKED] LIGHT CONTROL - System in {current_mode} mode")
            return
        
        # Allow light control in manual mode (even if infected for recovery)
        lights_status = payload.lower()
        print(f"Lights changed to: {lights_status}")
        if app:
            if system_infected:
                app.update_lights_display_recovery()
                # Check if system is fully recovered
                app.check_full_recovery()
            else:
                app.update_lights_display()
    
    # Handle colour changes - only in manual mode
    elif topic == colour_topic:
        if current_mode.lower() == "unknown":
            print(f"Colour change BLOCKED - system mode is {current_mode} (must set mode to Manual first)")
            # Show blocking message in GUI
            if app and system_infected:
                app.show_blocked_command_message(f"[BLOCKED] COLOUR CHANGE - System mode is {current_mode}")
            return
        elif current_mode.lower() != "manual":
            print(f"Colour change BLOCKED - system in {current_mode} mode (must be in Manual mode)")
            # Show blocking message in GUI
            if app and system_infected:
                app.show_blocked_command_message(f"[BLOCKED] COLOUR CHANGE - System in {current_mode} mode")
            return
        
        # Validate RGB format (e.g., "255,255,255")
        try:
            rgb_values = [int(x.strip()) for x in payload.split(',')]
            if len(rgb_values) == 3 and all(0 <= val <= 255 for val in rgb_values):
                light_colour = payload
                print(f"Light colour changed to: {light_colour}")
                if app and system_infected:
                    # Update the display if lights are on
                    if lights_status.lower() == "on":
                        app.update_lights_display_recovery()
                    # Check if system is fully recovered
                    app.check_full_recovery()
            else:
                print("Invalid RGB colour format - values must be 0-255")
        except:
            print("Invalid RGB colour format")
        return
    
    # Handle status updates (always allow for monitoring)
    elif topic == lights_topic:
        lights_status = payload.lower()
        if app:
            if system_infected:
                app.update_lights_display_recovery()
            else:
                app.update_lights_display()

def run_mqtt():
    global client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="LightsController")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(broker, port)
        client.loop_start()
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")

def signal_handler(sig, frame):
    global running
    print("\nShutting down...")
    running = False
    if client:
        client.loop_stop()
        client.disconnect()
    if app:
        app.destroy()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start MQTT in background
    mqtt_thread = threading.Thread(target=run_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    
    time.sleep(1)  # Allow MQTT to connect
    
    # Start GUI
    app = LightsControllerApp()
    app.mainloop()
