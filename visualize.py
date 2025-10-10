import serial
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import winsound # ## NEW: Import for making sounds (Windows only)

# --- Configuration ---
SERIAL_PORT = 'COM4'      # Change this to your STM32's COM port
BAUD_RATE = 9600          # Must match your STM32 UART baud rate
MAX_POINTS = 100          # Number of points to display on the screen
HEART_RATE_FLAG = 130     # The special byte value that indicates the next byte is a heart rate
ALARM_THRESHOLD = 30      # ## NEW: Heart rate below which the alarm will sound

class ECGReceiver:
    def __init__(self, root):
        self.root = root
        self.root.title("ECG & Heart Rate Monitor")
        self.root.geometry("1200x600")
        self.running = False
        self.ser = None

        ## State variables for heart rate protocol
        self.heart_rate = 0
        self.expecting_heart_rate = False
        self.alarm_active = False # ## NEW: Flag to control the alarm thread

        # --- Data Handling ---
        self.data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
        self.x_values = np.arange(0, MAX_POINTS)

        # --- UI Setup ---
        self.setup_ui()
        self.setup_plot()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frame, text="Serial Port:").pack(side=tk.LEFT, padx=5)
        self.port_entry = ttk.Entry(frame, width=10)
        self.port_entry.insert(0, SERIAL_PORT)
        self.port_entry.pack(side=tk.LEFT)

        ttk.Label(frame, text="Baud Rate:").pack(side=tk.LEFT, padx=5)
        self.baud_entry = ttk.Entry(frame, width=10)
        self.baud_entry.insert(0, str(BAUD_RATE))
        self.baud_entry.pack(side=tk.LEFT)

        self.connect_btn = ttk.Button(frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=10)

        self.status_label = ttk.Label(frame, text="Status: Disconnected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        ## Heart Rate Display Label
        self.hr_label = ttk.Label(frame, text="Heart Rate: -- BPM", font=("Helvetica", 14, "bold"), foreground="red")
        self.hr_label.pack(side=tk.RIGHT, padx=20)

    def setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 4))
        self.line, = self.ax.plot(self.x_values, list(self.data), color='lime', linewidth=1.5)

        self.ax.set_title("Live ECG Plot", fontsize=14, fontweight='bold')
        self.ax.set_ylim(0, 255) # Y-axis for 8-bit ADC values
        self.ax.set_xlim(0, MAX_POINTS) # X-axis is now fixed
        
        self.ax.set_facecolor("black")
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#333333')
        self.ax.get_yaxis().set_visible(False)
        self.ax.get_xaxis().set_visible(False)
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_connection(self):
        if not self.running:
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        port = self.port_entry.get()
        baud = int(self.baud_entry.get())
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2) # Wait for connection to establish
            self.running = True
            self.status_label.config(text="Status: Connected", foreground="green")
            self.connect_btn.config(text="Disconnect")
            threading.Thread(target=self.read_data, daemon=True).start()
            self.update_plot()
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Could not open port {port}\nError: {e}")

    def disconnect_serial(self):
        self.running = False
        self.alarm_active = False # ## NEW: Ensure alarm stops on disconnect
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")
        self.hr_label.config(text="Heart Rate: -- BPM")


    def read_data(self):
        while self.running:
            try:
                if self.ser and self.ser.in_waiting:
                    byte_data = self.ser.read(1)
                    if byte_data:
                        value = int.from_bytes(byte_data, 'big')

                        if self.expecting_heart_rate:
                            self.heart_rate = value
                            self.expecting_heart_rate = False 
                        elif value == HEART_RATE_FLAG:
                            self.expecting_heart_rate = True
                        else:
                            self.data.append(value)
                else:
                    time.sleep(0.005) 
            except Exception as e:
                print(f"Error in read thread: {e}")
                self.running = False

    ## NEW: Function to handle the beeping in a separate thread
    def alarm_thread_func(self):
        """This function runs in a loop as long as the alarm is active."""
        while self.alarm_active:
            winsound.Beep(800, 400) # Frequency 800 Hz, Duration 400ms
            time.sleep(0.5) # Pause between beeps

    def update_plot(self):
        if self.running:
            # Update the plot line
            self.line.set_ydata(list(self.data))
            
            # Update the heart rate label
            self.hr_label.config(text=f"Heart Rate: {self.heart_rate} BPM")
            
            ## MODIFIED: Add alarm logic
            # Check if heart rate is below threshold (and not zero, to avoid alarm at start)
            if self.heart_rate < ALARM_THRESHOLD and self.heart_rate > 0:
                # If the alarm is not already active, start it
                if not self.alarm_active:
                    self.alarm_active = True
                    # Start the alarm function in a new daemon thread
                    threading.Thread(target=self.alarm_thread_func, daemon=True).start()
                    # Change HR label color to indicate alarm state
                    self.hr_label.config(foreground="orange")
            else:
                # If heart rate is normal, make sure the alarm is turned off
                if self.alarm_active:
                    self.alarm_active = False
                    # Restore HR label color
                    self.hr_label.config(foreground="red")
            
            self.canvas.draw()
        
        self.root.after(30, self.update_plot)

    def on_close(self):
        self.disconnect_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ECGReceiver(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()