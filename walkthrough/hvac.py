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

# MQTT settings
broker = "localhost"
port = 1883
temperature_topic = "home/temperature"
set_temperature_topic="home/temperature/set"
heater_topic = "home/heater"
current_temperature = random.uniform(-10.0, 30.0)  # Start with a random temperature between -10°C and 30°C
heater_status = "off"
mode = "Automatic"  # Default mode
set_temperature = 22.0  # Default set temperature for automatic mode

# Graceful shutdown flag
running = True

# Global variables for GUI app instance and threads
app = None
client = None  # Initialize client as None
sim_thread = None
mqtt_thread = None


# GUI setup
class ThermostatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UWEcyber Thermostat and Heater Controller")
        self.geometry("800x680")  # Increased height further to prevent cutoff
        self.resizable(False, False)  # Make the window non-resizable
        self.configure(bg="#1C2538")
        
        # Configure custom styles
        self.setup_styles()

        # Load and display the UWEcyber logo
        self.load_logo()

        # Main content frame with side-by-side layout
        self.main_frame = tk.Frame(self, bg="#1C2538")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))  # Added bottom padding

        # Left side - Thermostat display
        self.left_frame = tk.Frame(self.main_frame, bg="#1C2538")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right side - Controls and status
        self.right_frame = tk.Frame(self.main_frame, bg="#1C2538")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Create components in their respective frames
        self.create_thermostat_display()
        self.create_status_section()
        self.create_control_panel()

        # Set initial mode
        self.set_mode()

    def setup_styles(self):
        """Configure custom TTK styles for better appearance"""
        style = ttk.Style()
        
        # Configure button style
        style.configure("Custom.TButton",
                       font=("Source Sans Pro", 12, "bold"),
                       padding=(20, 10))
        
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

    def create_thermostat_display(self):
        """Create an enhanced circular thermostat display"""
        # Frame for thermostat - now in left frame
        thermo_frame = tk.Frame(self.left_frame, bg="#1C2538")
        thermo_frame.pack(pady=20, expand=True)
        
        # Title for the thermostat section
        thermo_title = ttk.Label(thermo_frame, text="THERMOSTAT", style="Heading.TLabel")
        thermo_title.pack(pady=(0, 20))
        
        self.canvas = Canvas(thermo_frame, width=300, height=300, bg="#1C2538", highlightthickness=0)
        self.canvas.pack()

        # Draw multiple circles for depth effect
        self.canvas.create_oval(10, 10, 290, 290, outline="#2A3441", width=3)  # Outer shadow
        self.canvas.create_oval(20, 20, 280, 280, outline="#EB0037", width=4)  # Main circle
        self.canvas.create_oval(30, 30, 270, 270, outline="#3A4651", width=2)  # Inner ring
        
        # Add temperature scale marks
        self.draw_temperature_scale()

        # Temperature label in the center with better styling
        self.temperature_label = self.canvas.create_text(150, 150, text=f"{current_temperature:.1f}°C", 
                                                        font=("Source Sans Pro", 28, "bold"), fill="#A3EA2A")
        
        # Add "TEMPERATURE" label below the reading
        self.canvas.create_text(150, 180, text="TEMPERATURE", 
                               font=("Source Sans Pro", 10), fill="#7A8A9A")

    def draw_temperature_scale(self):
        """Draw temperature scale marks around the thermostat"""
        import math
        center_x, center_y = 150, 150  # Adjusted for 300x300 canvas
        radius = 110
        
        # Draw major marks every 30 degrees (12 marks total)
        for i in range(12):
            angle = math.radians(i * 30 - 90)  # Start from top
            x1 = center_x + (radius - 15) * math.cos(angle)
            y1 = center_y + (radius - 15) * math.sin(angle)
            x2 = center_x + radius * math.cos(angle)
            y2 = center_y + radius * math.sin(angle)
            
            self.canvas.create_line(x1, y1, x2, y2, fill="#7A8A9A", width=2)

    def create_status_section(self):
        """Create an improved status section"""
        status_frame = tk.Frame(self.right_frame, bg="#2A3441", relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status title
        status_title = ttk.Label(status_frame, text="SYSTEM STATUS", style="Heading.TLabel")
        status_title.pack(pady=(15, 10))
        
        # Heater status with color coding
        self.heater_status_frame = tk.Frame(status_frame, bg="#2A3441")
        self.heater_status_frame.pack(pady=(0, 15))
        
        # Use a colored rectangle instead of unicode character
        self.indicator_canvas = Canvas(self.heater_status_frame, width=20, height=20, bg="#2A3441", highlightthickness=0)
        self.indicator_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Draw indicator circle
        indicator_color = "#FF4444" if heater_status == "off" else "#44FF44"
        self.indicator_circle = self.indicator_canvas.create_oval(2, 2, 18, 18, fill=indicator_color, outline=indicator_color)
        
        self.heater_status_label = ttk.Label(self.heater_status_frame, text=f"Heater is {heater_status.upper()}", 
                                           style="Status.TLabel")
        self.heater_status_label.pack(side=tk.LEFT)

    def create_control_panel(self):
        """Create an organized control panel"""
        # Control panel frame - remove expand=True to prevent unnecessary stretching
        control_frame = tk.Frame(self.right_frame, bg="#2A3441", relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=0)
        
        # Control panel title
        control_title = ttk.Label(control_frame, text="CONTROLS", style="Heading.TLabel")
        control_title.pack(pady=(15, 15))
        
        # Manual control section
        manual_frame = tk.Frame(control_frame, bg="#2A3441")
        manual_frame.pack(pady=(0, 15))
        
        self.switch_button = ttk.Button(manual_frame, text="TOGGLE HEATER", 
                                       command=self.toggle_heater, style="Custom.TButton")
        self.switch_button.pack()
        
        # Mode selection with better layout
        mode_frame = tk.Frame(control_frame, bg="#2A3441")
        mode_frame.pack(pady=(0, 15))
        
        self.mode_label = ttk.Label(mode_frame, text="OPERATION MODE", style="Heading.TLabel")
        self.mode_label.pack(pady=(0, 10))

        # Radio buttons in a horizontal layout
        radio_frame = tk.Frame(mode_frame, bg="#2A3441")
        radio_frame.pack()
        
        self.mode_var = tk.StringVar(value="Automatic")
        self.manual_radio = ttk.Radiobutton(radio_frame, text="Manual", variable=self.mode_var, 
                                          value="Manual", command=self.set_mode, style="Custom.TRadiobutton")
        self.manual_radio.pack(side=tk.LEFT, padx=15)

        self.automatic_radio = ttk.Radiobutton(radio_frame, text="Automatic", variable=self.mode_var, 
                                             value="Automatic", command=self.set_mode, style="Custom.TRadiobutton")
        self.automatic_radio.pack(side=tk.LEFT, padx=15)

        # Temperature setting section
        temp_frame = tk.Frame(control_frame, bg="#2A3441")
        temp_frame.pack(pady=(0, 15))
        
        self.set_temp_label = ttk.Label(temp_frame, text="TARGET TEMPERATURE", style="Heading.TLabel")
        
        # Temperature input with better styling
        self.temp_input_frame = tk.Frame(temp_frame, bg="#2A3441")
        
        self.set_temp_spinbox = ttk.Spinbox(self.temp_input_frame, from_=-20.0, to=30.0, increment=0.5, 
                                          format="%.1f", width=8, font=("Source Sans Pro", 12, "bold"))
        self.set_temp_spinbox.set(set_temperature)
        self.set_temp_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        temp_unit_label = ttk.Label(self.temp_input_frame, text="°C", style="Status.TLabel")
        temp_unit_label.pack(side=tk.LEFT)
        
        self.confirm_button = ttk.Button(temp_frame, text="SET TEMPERATURE", 
                                       command=self.confirm_temperature, style="Custom.TButton")

        # Status display - now packed normally instead of at bottom
        self.mode_status_label = ttk.Label(control_frame, text=f"Current mode: {mode}", 
                                         style="Status.TLabel")
        self.mode_status_label.pack(pady=(15, 20))

    def load_logo(self):
        """Load and display the UWEcyber logo at the top of the application"""
        try:
            # Get the path to the logo file (one directory up from walkthrough folder)
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "UWEcyber_logo.png")
            
            # Load and resize the image while maintaining aspect ratio
            logo_image = Image.open(logo_path)
            
            # Get original dimensions
            original_width, original_height = logo_image.size
            
            # Calculate aspect ratio and resize to fit width of 250px while maintaining proportions
            target_width = 250
            aspect_ratio = original_height / original_width
            target_height = int(target_width * aspect_ratio)
            
            # Resize with proper aspect ratio
            logo_image = logo_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Create and pack the logo label
            self.logo_label = ttk.Label(self, image=self.logo_photo, background="#1C2538")
            self.logo_label.pack(pady=(10, 5))
            
        except Exception as e:
            print(f"Could not load logo: {e}")
            # Create a text label as fallback
            self.logo_label = ttk.Label(self, text="UWEcyber", font=("Source Sans Pro", 16, "bold"), 
                                       foreground="#A3EA2A", background="#1C2538")
            self.logo_label.pack(pady=(10, 5))

    def update_temperature(self, temperature):
        """Update temperature label and limit it to a minimum of -20°C"""
        if temperature < -20.0:
            temperature = -20.0
        self.canvas.itemconfig(self.temperature_label, text=f"{temperature:.1f}°C")
        self.update()

    def update_heater_status(self, status):
        """Update heater status with visual indicator"""
        self.heater_status_label.config(text=f"Heater is {status.upper()}")
        print(f"Heater status changed to: {status}")
        # Update indicator color using canvas
        color = "#44FF44" if status == "on" else "#FF4444"
        self.indicator_canvas.itemconfig(self.indicator_circle, fill=color, outline=color)
        self.update()

    def update_mode(self, mode_status):
        self.mode_status_label.config(text=f"Current mode: {mode_status}")
        self.update()

    def toggle_heater(self):
        global heater_status
        # Ensure heater control works only in Manual mode
        if self.mode_var.get() == "Manual":
            if heater_status == "off":
                heater_status = "on"
            else:
                heater_status = "off"
            print(f"Heater status manually changed to: {heater_status}")
            self.update_heater_status(heater_status)
            client.publish(heater_topic, heater_status)  # Update via MQTT

    def confirm_temperature(self):
        """Confirm the set temperature and apply it in Automatic mode."""
        global set_temperature
        set_temperature = float(self.set_temp_spinbox.get())
        print(f"Set temperature confirmed: {set_temperature}°C")
        client.publish(set_temperature_topic, set_temperature)  # Send the set temperature to the MQTT broker

    def set_mode(self):
        global mode, set_temperature
        mode = self.mode_var.get()
        self.update_mode(mode)

        if mode == "Automatic":
            # Show temperature setting controls for Automatic mode
            self.set_temp_label.pack(pady=(0, 10))
            self.temp_input_frame.pack(pady=10)
            self.confirm_button.pack(pady=(10, 0))
        else:
            # Hide temperature setting controls in Manual mode
            self.set_temp_label.pack_forget()
            self.temp_input_frame.pack_forget()
            self.confirm_button.pack_forget()


# Graceful shutdown when CTRL+C is pressed
def signal_handler(sig, frame):
    global running
    print("\nGraceful shutdown initiated...")
    running = False

    if client:
        client.loop_stop(force=True)  # Stop the MQTT loop and force it
        client.disconnect()  # Cleanly disconnect MQTT client

    if sim_thread:
        sim_thread.join()  # Wait for the temperature simulation thread to finish

    if mqtt_thread:
        mqtt_thread.join()  # Wait for the MQTT thread to finish

    if app:
        try:
            app.after(0, app.destroy)  # Safely close the GUI from the main thread
        except Exception as e:
            print(f"Error closing GUI: {e}")
    sys.exit(0)


# MQTT callback functions
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")
    client.subscribe(temperature_topic)
    client.subscribe(set_temperature_topic)
    client.subscribe(heater_topic)


def on_message(client, userdata, message):
    global current_temperature, heater_status, mode, set_temperature

    if message.topic == temperature_topic:
        current_temperature = float(message.payload.decode())
        if app is not None:
            app.update_temperature(current_temperature)

        if mode == "Automatic":
            # Automatic heater control based on user-defined set temperature
            if current_temperature < set_temperature and heater_status == "off":
                heater_status = "on"
                client.publish(heater_topic, "on")
                if app is not None:
                    app.update_heater_status("on")
            elif current_temperature > set_temperature and heater_status == "on":
                heater_status = "off"
                client.publish(heater_topic, "off")
                if app is not None:
                    app.update_heater_status("off")
                    
    elif message.topic == set_temperature_topic:
        set_temperature=float(message.payload.decode())
       


# Simulate temperature change based on heater state
def simulate_temperature():
    global current_temperature, heater_status, running

    while running:
        if heater_status == "on":
            # Slowly increase the temperature when the heater is ON
            if current_temperature < 30.0:
                current_temperature += 1
        else:
            # Slowly decrease the temperature when the heater is OFF
            if current_temperature > -20.0:  # Don't go below -20°C
                current_temperature -= 1

        # Publish the updated temperature to the MQTT broker
        if client is not None:
            client.publish(temperature_topic, current_temperature)
        if app is not None:
            app.update_temperature(current_temperature)
        time.sleep(5)  # Adjust the speed of temperature change here


# Run the MQTT client loop in a separate thread
def run_mqtt():
    global client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="HeaterController")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_start()


# Main program starts here
if __name__ == "__main__":
    # Capture CTRL+C signal for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start the MQTT thread first
    mqtt_thread = threading.Thread(target=run_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Allow some time for the MQTT client to connect before starting temperature simulation
    time.sleep(2)

    # Start simulating temperature in the main thread
    sim_thread = threading.Thread(target=simulate_temperature)
    sim_thread.daemon = True
    sim_thread.start()

    # Run the Tkinter GUI in the main thread
    app = ThermostatApp()
    app.mainloop()

