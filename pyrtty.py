#!/usr/bin/env python3
import numpy as np
import sounddevice as sd

# Constants
MARK_FREQ = 2125
SPACE_FREQ = 2295
BAUD_RATE = 45.45
SAMPLE_RATE = 44100
BIT_DURATION = 1 / BAUD_RATE
AMPLITUDE = 1
BLOCKSIZE = 1000

# Baudot code (simplified example mapping)
BAUDOT_CODE = {
    'letters': {
        'A': '11000', 'B': '10011', 'C': '01110', 'D': '10010', 'E': '10000',
        'F': '10110', 'G': '01011', 'H': '00101', 'I': '01100', 'J': '11010',
        'K': '11110', 'L': '01001', 'M': '00111', 'N': '00110', 'O': '00011',
        'P': '01101', 'Q': '11101', 'R': '01010', 'S': '10100', 'T': '00001',
        'U': '11100', 'V': '01111', 'W': '11001', 'X': '10111', 'Y': '10101',
        'Z': '10001', ' ': '00100', '\n': '00010', '\r': '00000'
    },
    'figures': {
        '1': '11000', '2': '10011', '3': '01110', '4': '10010', '5': '10000',
        '6': '10110', '7': '01011', '8': '00101', '9': '01100', '0': '11010',
        '-': '11110', '\'': '00011', '!': '11011', '&': '01101', '#': '11101',
        '(': '01001', ')': '00111', '"': '01010', '/': '10111', ':': '10100',
        ';': '10001', '?': '00110', ',': '00001', '.': '11100', '=': '01111', ' ': '00100'
    },
    'LTRS': '11111',  # Letters shift
    'FIGS': '11011'   # Figures shift
}

def text_to_baudot(text):
    """Convert text to 5-bit Baudot code, including necessary shifts."""
    baudot_str = ''
    current_mode = 'letters'  # Start in letters mode

    for char in text.upper():  # Baudot code is case-insensitive
        for mode in ['letters', 'figures']:
            if char in BAUDOT_CODE[mode]:
                if current_mode != mode:
                    # Insert the mode shift code
                    baudot_str += BAUDOT_CODE['LTRS' if mode == 'letters' else 'FIGS']
                    current_mode = mode
                baudot_str += BAUDOT_CODE[mode][char]
                break

    return baudot_str

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE, initial_phase=0):
    """Generate a sine wave for a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t + initial_phase)
    final_phase = (initial_phase + 2 * np.pi * frequency * duration) % (2 * np.pi)
    return tone, final_phase

def baudot_to_afsk(baudot_str, mark_freq=MARK_FREQ, space_freq=SPACE_FREQ, baud_rate=BAUD_RATE):
    """Convert Baudot code string to AFSK tones."""
    afsk_signal = np.array([])
    phase = 0
    for bit in baudot_str:
        frequency = mark_freq if bit == MARK_CODE else space_freq
        tone, phase  = generate_tone(frequency, BIT_DURATION, initial_phase=phase)
        afsk_signal = np.concatenate((afsk_signal, tone))
    return afsk_signal

def play_afsk_signal(signal):
    """Play AFSK signal through the default audio device."""
    sd.play(signal, SAMPLE_RATE, blocksize=BLOCKSIZE)
    sd.wait()

# Example usage
text = "Hello, World 123!"
baudot_str = text_to_baudot(text)
afsk_signal = baudot_to_afsk(baudot_str)
play_afsk_signal(afsk_signal)