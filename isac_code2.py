import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.signal import chirp
from scipy.fft import fft
from scipy.fft import fftfreq
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import csv
import os

# Parameters (rest of your parameters remain the same)
fs = 1000
T = 10
N = fs * T
f0, f1 = 20, 200
t = np.linspace(0, T, N)
window_size = 80
detected_abnormal_count = 0
ABNORMAL_THRESHOLD = 1

# Realistic normal ranges
HEART_RATE_NORMAL_RANGE = (60, 100)
BREATH_RATE_NORMAL_RANGE = (12, 20)

# Dark theme colors
BACKGROUND_COLOR = "#2e2e2e"  # Dark grey
TEXT_COLOR = "#f0f0f0"      # Light grey
ACCENT_COLOR = "green"      # Green for normal
WARNING_COLOR = "orange"   # Orange for high
DANGER_COLOR = "red"    # Red for low

def setup_gui():
    root = tk.Tk()
    root.title("Vital Sign Monitor")
    root.geometry("1920x1080")
    root.configure(bg=BACKGROUND_COLOR)

    style = ttk.Style(root)
    style.theme_use('clam')

    # Configure dark theme for ttk widgets
    style.configure("TLabel", background=BACKGROUND_COLOR, foreground=TEXT_COLOR)
    style.configure("TFrame", background=BACKGROUND_COLOR)
    style.configure("TLabelframe", background=BACKGROUND_COLOR, foreground=TEXT_COLOR, bordercolor=TEXT_COLOR)
    style.configure("TLabelframe.Label", background=BACKGROUND_COLOR, foreground=TEXT_COLOR)

    # Vital Signs Box
    vital_signs_group = ttk.LabelFrame(root, padding=(15, 15))
    vital_signs_group.pack(pady=20, padx=50)

    heart_rate_label = ttk.Label(vital_signs_group, text="Heart Rate: -- bpm", font=("Arial", 28, "bold"))
    heart_rate_label.pack(pady=5)

    breath_rate_label = ttk.Label(vital_signs_group, text="Breath Rate: -- breaths/min", font=("Arial", 28, "bold"))
    breath_rate_label.pack(pady=5)

    heart_rate_status_text = ttk.Label(vital_signs_group, text="Heart Status: Normal", font=("Arial", 16))
    heart_rate_status_text.pack(pady=2)

    breath_rate_status_text = ttk.Label(vital_signs_group, text="Breath Status: Normal", font=("Arial", 16))
    breath_rate_status_text.pack(pady=2)

    # Plot Frame (Reduced size and padding)
    plot_frame = ttk.Frame(root, padding=(10, 10))
    plot_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    plot_frame.columnconfigure(0, weight=1)
    plot_frame.rowconfigure(0, weight=1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), dpi=100) # Reduced figure size
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    ax1.set_title("HR & BR Trends", fontsize=10, color=TEXT_COLOR) # Smaller font
    ax1.set_ylabel("Rate", fontsize=8, color=TEXT_COLOR) # Smaller font
    ax1.tick_params(axis='both', which='major', labelsize=7, color=TEXT_COLOR, labelcolor=TEXT_COLOR) # Smaller ticks
    ax1.grid(True, linestyle='--', alpha=0.5, color=TEXT_COLOR)
    ax1.set_facecolor(BACKGROUND_COLOR)
    ax2.set_title("FFT (Phase Diff)", fontsize=10, color=TEXT_COLOR) # Smaller font
    ax2.set_xlabel("Frequency (Hz)", fontsize=8, color=TEXT_COLOR) # Smaller font - Removed labelcolor here
    ax2.set_ylabel("Magnitude", fontsize=8, color=TEXT_COLOR) # Smaller font - Removed labelcolor here
    ax2.tick_params(axis='both', which='major', labelsize=7, color=TEXT_COLOR, labelcolor=TEXT_COLOR) # Smaller ticks
    ax2.grid(True, linestyle='--', alpha=0.5, color=TEXT_COLOR)
    ax2.set_facecolor(BACKGROUND_COLOR)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, sticky="nsew")

    return root, heart_rate_label, breath_rate_label, heart_rate_status_text, breath_rate_status_text, ax1, ax2, canvas

# Moving Average Filter for Smoothing (remains the same)
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

# Dummy alert popup (remains the same for now)
def show_dummy_email_alert(heart_status, breath_status):
    subject = "Vital Sign Alert"
    body = (
        f"To: anirbanbofficial@gmail.com\n"
        f"From: yourvital@gmail.com\n"
        f"Subject: {subject}\n\n"
        f"Dear Caregiver,\n\n"
        f"Abnormal Vitals Detected:\n"
        f"Heart Rate: {heart_status}\n"
        f"Breath Rate: {breath_status}\n\n"
        f"Please check the patient.\n\n"
        f"Regards,\nVital Sign Monitor"
    )
    messagebox.showinfo("🚨 Alert", body)

# Generate vital signs data (simulated) (remains the same)
def generate_vital_signs(t):
    heart_rate = 75 + 8 * np.sin(2 * np.pi * 0.05 * t) + 2 * np.random.normal(size=len(t))
    breath_rate = 16 + 3 * np.sin(2 * np.pi * 0.1 * t) + 0.5 * np.random.normal(size=len(t))
    return heart_rate, breath_rate

# Prepare CSV log (remains the same)
log_file = "vital_signs_log.csv"
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "Heart Rate (bpm)", "Breath Rate (bpm)", "Heart Status", "Breath Status"])

# Update function
def update_vital_signs_and_plot():
    global detected_abnormal_count
    global heart_rate_label, breath_rate_label, heart_rate_status_text, breath_rate_status_text, root

    heart_rate, breath_rate = generate_vital_signs(t)
    smoothed_heart_rate = moving_average(heart_rate, window_size)
    smoothed_breath_rate = moving_average(breath_rate, window_size)
    t_adjusted = t[:len(smoothed_breath_rate)]

    breath_motion = 0.05 * np.sin(2 * np.pi * smoothed_breath_rate * t_adjusted) + 0.02 * np.random.normal(size=len(t_adjusted))
    heart_motion = 0.01 * np.sin(2 * np.pi * smoothed_heart_rate * t_adjusted) + 0.01 * np.random.normal(size=len(t_adjusted))
    total_motion = breath_motion + heart_motion

    transmitted_signal = chirp(t_adjusted, f0=f0, f1=f1, t1=T, method='linear')[:len(total_motion)]
    received_signal = transmitted_signal * np.exp(1j * 2 * np.pi * total_motion)

    received_phase = np.unwrap(np.angle(received_signal))
    phase_difference = received_phase - np.polyval(np.polyfit(t_adjusted, received_phase, 1), t_adjusted)

    phase_fft = np.abs(fft(phase_difference))
    frequencies = fftfreq(len(t_adjusted), 1/fs)
    positive_freqs = frequencies[:len(t_adjusted)//2]
    positive_fft = phase_fft[:len(t_adjusted)//2]

    breath_band = (positive_freqs > 0.1) & (positive_freqs < 0.5)
    heart_band = (positive_freqs > 0.8) & (positive_freqs < 2.0)

    breath_peak_idx = np.argmax(positive_fft * breath_band)
    heart_peak_idx = np.argmax(positive_fft * heart_band)

    breath_detected = positive_freqs[breath_peak_idx] * 60 if breath_band[breath_peak_idx] else 0
    heart_detected = positive_freqs[heart_peak_idx] * 60 if heart_band[heart_peak_idx] else 0

    # Update Heart Rate Display
    heart_status = "Normal"
    heart_color = ACCENT_COLOR
    if heart_detected < HEART_RATE_NORMAL_RANGE[0]:
        heart_status = "Low"
        heart_color = DANGER_COLOR
        root.config(bg=DANGER_COLOR)
    elif heart_detected > HEART_RATE_NORMAL_RANGE[1]:
        heart_status = "High"
        heart_color = WARNING_COLOR
        root.config(bg=WARNING_COLOR)
    else:
        root.config(bg=BACKGROUND_COLOR) # Reset background if normal
    heart_rate_label.config(text=f"HR: {heart_detected:.0f} bpm", foreground=TEXT_COLOR)
    heart_rate_status_text.config(text=f"Status: {heart_status}", foreground=heart_color)

    # Update Breath Rate Display
    breath_status = "Normal"
    breath_color = ACCENT_COLOR
    if breath_detected < BREATH_RATE_NORMAL_RANGE[0]:
        breath_status = "Low"
        breath_color = DANGER_COLOR
        if root.cget('bg') == BACKGROUND_COLOR: # Only change if not already abnormal
            root.config(bg=DANGER_COLOR)
    elif breath_detected > BREATH_RATE_NORMAL_RANGE[1]:
        breath_status = "High"
        breath_color = WARNING_COLOR
        if root.cget('bg') == BACKGROUND_COLOR: # Only change if not already abnormal
            root.config(bg=WARNING_COLOR)
    elif root.cget('bg') != DANGER_COLOR and root.cget('bg') != WARNING_COLOR:
        root.config(bg=BACKGROUND_COLOR) # Reset background if both are normal
    breath_rate_label.config(text=f"BR: {breath_detected:.0f} breaths/min", foreground=TEXT_COLOR)
    breath_rate_status_text.config(text=f"Status: {breath_status}", foreground=breath_color)

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([t_adjusted[-1], heart_detected, breath_detected, heart_status, breath_status])

    ax1.cla()
    step = 20
    ax1.plot(t_adjusted[::step], smoothed_breath_rate[::step], label="BR", alpha=0.7, linewidth=1.5, color="#87CEEB") # Light Sky Blue
    ax1.plot(t_adjusted[::step], smoothed_heart_rate[::step], label="HR", alpha=0.7, linewidth=1.5, color="#FF69B4") # Hot Pink
    ax1.set_title("Heart Rate & Breath Rate Trends", fontsize=10, color=TEXT_COLOR)
    ax1.set_ylabel("Rate", fontsize=8, color=TEXT_COLOR)
    ax1.tick_params(axis='both', which='major', labelsize=7, color=TEXT_COLOR, labelcolor=TEXT_COLOR)
    ax1.grid(True, linestyle='--', alpha=0.5, color=TEXT_COLOR)
    ax1.set_facecolor(BACKGROUND_COLOR)
    ax1.legend(fontsize=8, facecolor=BACKGROUND_COLOR, edgecolor=TEXT_COLOR, labelcolor=TEXT_COLOR)

    ax2.cla()
    ax2.plot(positive_freqs, positive_fft, linewidth=1, color="#98FB98") # Pale Green
    ax2.axvspan(0.1, 0.5, color='lightcoral', alpha=0.2, label='Breath')
    ax2.axvspan(0.8, 2.0, color='lightskyblue', alpha=0.2, label='Heart')
    ax2.set_title("FFT (Phase Diff)", fontsize=10, color=TEXT_COLOR)
    ax2.set_xlabel("Frequency (Hz)", fontsize=8, color=TEXT_COLOR) # Removed labelcolor here
    ax2.set_ylabel("Magnitude", fontsize=8, color=TEXT_COLOR) # Removed labelcolor here
    ax2.tick_params(axis='both', which='major', labelsize=7, color=TEXT_COLOR, labelcolor=TEXT_COLOR)
    ax2.grid(True, linestyle='--', alpha=0.5, color=TEXT_COLOR)
    ax2.set_facecolor(BACKGROUND_COLOR)
    ax2.legend(fontsize=8, facecolor=BACKGROUND_COLOR, edgecolor=TEXT_COLOR, labelcolor=TEXT_COLOR)
    ax2.set_xlim(0, 2)

    canvas.draw()

    if heart_status != "Normal" or breath_status != "Normal":
        detected_abnormal_count += 1
        if detected_abnormal_count >= ABNORMAL_THRESHOLD:
            root.after(100, lambda: show_dummy_email_alert(heart_status, breath_status))
            detected_abnormal_count = 0
    else:
        detected_abnormal_count = 0

    root.after(1000, update_vital_signs_and_plot)

# Run GUI
root, heart_rate_label, breath_rate_label, heart_rate_status_text, breath_rate_status_text, ax1, ax2, canvas = setup_gui()
update_vital_signs_and_plot()
root.mainloop()