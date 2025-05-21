import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import chirp, find_peaks
import tkinter as tk
from tkinter import ttk

# --- Signal Configuration ---
fs = 1000            # Sampling frequency (Hz)
T = 5                # Duration (seconds)
t = np.linspace(0, T, int(fs*T), endpoint=False)
N = len(t)

# --- 1. LFM Chirp Signal ---
f0 = 20
f1 = 200
lfm_signal = chirp(t, f0=f0, f1=f1, t1=T, method='linear')

# --- 2. Chest Movement (Heartbeat + Breathing) ---
breathing = 0.5 * np.sin(2 * np.pi * 0.25 * t)
heartbeat = 0.05 * np.sin(2 * np.pi * 1.2 * t)
chest_movement = breathing + heartbeat

# --- 3. Reflected Signal ---
reflected_signal = lfm_signal * np.cos(4 * np.pi * chest_movement)

# --- 4. OFDM Transmitter Side ---
num_subcarriers = 64
reflected_samples = reflected_signal[:num_subcarriers]
reflected_norm = (reflected_samples - np.mean(reflected_samples)) / np.std(reflected_samples)

# Bit stream generation using thresholding (synthetic)
bit_stream = (reflected_norm > 0).astype(int)[:num_subcarriers]

# QPSK-like mapping from normalized reflected signal
real_parts = reflected_norm[::2]
imag_parts = reflected_norm[1::2]
min_len = min(len(real_parts), len(imag_parts))
qpsk_like_symbols = real_parts[:min_len] + 1j * imag_parts[:min_len]

# Padding to 64 symbols
if len(qpsk_like_symbols) < num_subcarriers:
    qpsk_like_symbols = np.pad(qpsk_like_symbols, (0, num_subcarriers - len(qpsk_like_symbols)))

# IFFT to generate OFDM signal
ofdm_signal = np.fft.ifft(qpsk_like_symbols, n=num_subcarriers)
ofdm_time = np.arange(num_subcarriers) / fs

# --- 5. OFDM Receiver Side ---
received_signal = np.fft.fft(ofdm_signal, n=num_subcarriers)

# QPSK Demodulation
demodulated_real = np.real(received_signal) > 0
demodulated_imag = np.imag(received_signal) > 0
demodulated_bits = np.zeros(2 * num_subcarriers)
demodulated_bits[::2] = demodulated_real
demodulated_bits[1::2] = demodulated_imag

# Data Decoding
decoded_data = ''.join([str(int(bit)) for bit in demodulated_bits[:len(bit_stream)]])
decoded_data = np.array([int(bit) for bit in decoded_data])

# --- Heartbeat and Breathing Rate Calculation ---
# Detect peaks in the bitstream for heartbeat (faster) and breathing (slower)
def detect_rate(decoded_bits, fs, rate_type='heartbeat'):
    if rate_type == 'heartbeat':
        # Heartbeat has a higher frequency, e.g., 1.2 Hz -> 60-120 BPM
        min_distance = fs // 2  # Heartbeat has a higher frequency, so peaks are farther apart
        max_distance = fs // 1  # Heart rate will occur in a range between 60 and 120 BPM
    else:
        # Breathing has a lower frequency, e.g., 0.25 Hz -> 12-20 BPM
        min_distance = fs // 8  # Breathing has a lower frequency, so peaks are closer together
        max_distance = fs // 4  # Breathing rate will occur between 12 and 20 BPM

    # Find peaks in the decoded bitstream
    peaks, _ = find_peaks(decoded_bits, distance=min_distance, width=(min_distance, max_distance))
    peak_times = peaks / fs
    return len(peaks), peak_times

# Detect heartbeat and breathing rates
heartbeat_peaks_count, heartbeat_times = detect_rate(decoded_data, fs, rate_type='heartbeat')
breathing_peaks_count, breathing_times = detect_rate(decoded_data, fs, rate_type='breathing')

# --- Plot Functions ---
def plot_lfm():
    fig, axs = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('LFM Part: Radar Vital Sign Detection', fontsize=16, color='darkblue')

    axs[0].plot(t, lfm_signal, color='green', label='LFM Chirp Signal')
    axs[0].set_title('LFM Chirp Signal')
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('Amplitude')
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(t, chest_movement, label='Chest Movement', color='purple')
    axs[1].set_title('Chest Movement (Breathing + Heartbeat)')
    axs[1].set_ylabel('Displacement')
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(t, reflected_signal, label='Reflected Signal', color='darkred')
    axs[2].set_title('Reflected LFM Signal')
    axs[2].set_ylabel('Amplitude')
    axs[2].legend()
    axs[2].grid()

    plt.tight_layout()
    plt.show()

def plot_ofdm_transmitter():
    fig, axs = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle('OFDM Transmitter Workflow', fontsize=18, color='darkblue')

    # Step 1: Simulated Bit Stream from Reflected Signal
    axs[0].step(range(len(bit_stream)), bit_stream, where='mid', label='Simulated Bit Stream')
    axs[0].set_title('Step 1: Bit Stream Generation')
    axs[0].set_ylabel('Bit')
    axs[0].legend()
    axs[0].grid()

    # Step 2: QPSK-like Symbol Mapping
    axs[1].scatter(np.real(qpsk_like_symbols), np.imag(qpsk_like_symbols), color='purple')
    axs[1].set_title('Step 2: QPSK Symbols')
    axs[1].set_xlabel('In-Phase')
    axs[1].set_ylabel('Quadrature')
    axs[1].grid()
    axs[1].axhline(0, color='gray', linestyle='--')
    axs[1].axvline(0, color='gray', linestyle='--')

    # Step 3: IFFT → OFDM Modulated Signal
    axs[2].plot(ofdm_time, np.real(ofdm_signal), label='Real Part')
    axs[2].plot(ofdm_time, np.imag(ofdm_signal), label='Imag Part', linestyle='--')
    axs[2].set_title('Step 3: OFDM Time Domain Signal (IFFT Output)')
    axs[2].set_ylabel('Amplitude')
    axs[2].legend()
    axs[2].grid()

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.show()

def plot_ofdm_receiver():
    fig, axs = plt.subplots(3, 1, figsize=(14, 12))
    fig.suptitle('OFDM Receiver Workflow with QPSK Demodulation', fontsize=18, color='darkblue')

    # Step 4: FFT → Received Subcarrier Symbols
    axs[0].stem(np.real(received_signal), linefmt='g-', markerfmt='go', basefmt=' ', label='Real')
    axs[0].stem(np.imag(received_signal), linefmt='m--', markerfmt='mo', basefmt=' ', label='Imag')
    axs[0].set_title('Step 4: FFT - Received Subcarrier Symbols')
    axs[0].set_ylabel('Amplitude')
    axs[0].legend()
    axs[0].grid()

    # Step 5: QPSK Demodulation (Real/Imag Thresholding)
    axs[1].stem(demodulated_bits[::2], linefmt='c-', markerfmt='co', basefmt=' ', label='Demodulated Real')
    axs[1].stem(demodulated_bits[1::2], linefmt='r--', markerfmt='ro', basefmt=' ', label='Demodulated Imag')
    axs[1].set_title('Step 5: QPSK Demodulation (Real/Imag Thresholding)')
    axs[1].set_ylabel('Decoded Bit')
    axs[1].legend()
    axs[1].grid()

    # Step 6: Data Decoding and Bitstream
    axs[2].step(range(len(decoded_data)), decoded_data, where='mid', label='Decoded Bitstream')
    axs[2].set_title('Step 6: Data Decoding')
    axs[2].set_xlabel('Bit Index')
    axs[2].set_ylabel('Decoded Bit')
    axs[2].legend()
    axs[2].grid()

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.show()

# --- GUI to Display Heartbeat and Breathing Rates ---
def main_gui():
    root = tk.Tk()
    root.title("Radar Signal Plot Selector")

    label = tk.Label(root, text="Select which signal part to plot:", font=("Arial", 14))
    label.pack(pady=10)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    lfm_button = ttk.Button(button_frame, text="Plot LFM Part", command=plot_lfm)
    lfm_button.grid(row=0, column=0, padx=10)

    ofdm_transmitter_button = ttk.Button(button_frame, text="Plot OFDM Transmitter", command=plot_ofdm_transmitter)
    ofdm_transmitter_button.grid(row=0, column=1, padx=10)

    ofdm_receiver_button = ttk.Button(button_frame, text="Plot OFDM Receiver", command=plot_ofdm_receiver)
    ofdm_receiver_button.grid(row=0, column=2, padx=10)

    # Display Heartbeat and Breathing Rates
    heart_rate_label = tk.Label(root, text=f"Detected Heartbeat Rate: {heartbeat_peaks_count * 60} BPM", font=("Arial", 12))
    heart_rate_label.pack(pady=10)

    breathing_rate_label = tk.Label(root, text=f"Detected Breathing Rate: {breathing_peaks_count * 60} BPM", font=("Arial", 12))
    breathing_rate_label.pack(pady=10)

    root.mainloop()

# --- Run the GUI ---
main_gui()
