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
CRLF = '\r\n'
LINE_WIDTH = 70

MARK_CODE = '1'
SPACE_CODE = '0'

START_BIT = MARK_CODE + SPACE_CODE
STOP_BIT = MARK_CODE

__wrap = lambda symb: START_BIT + symb + STOP_BIT

# Baudot code (simplified example mapping)
BAUDOT_CODE = {
	'letters': {
		'A': __wrap('11000'), 'B': __wrap('10011'), 'C' : __wrap('01110'), 'D' : __wrap('10010'), 'E': __wrap('10000'),
		'F': __wrap('10110'), 'G': __wrap('01011'), 'H' : __wrap('00101'), 'I' : __wrap('01100'), 'J': __wrap('11010'),
		'K': __wrap('11110'), 'L': __wrap('01001'), 'M' : __wrap('00111'), 'N' : __wrap('00110'), 'O': __wrap('00011'),
		'P': __wrap('01101'), 'Q': __wrap('11101'), 'R' : __wrap('01010'), 'S' : __wrap('10100'), 'T': __wrap('00001'),
		'U': __wrap('11100'), 'V': __wrap('01111'), 'W' : __wrap('11001'), 'X' : __wrap('10111'), 'Y': __wrap('10101'),
		'Z': __wrap('10001'), ' ': __wrap('00100'), '\n': __wrap('00010'), '\r': __wrap('00000')
	},
	'figures': {
		'1': __wrap('11101'), '2' : __wrap('11001'), '3': __wrap('10000'), '4': __wrap('01010'), '5': __wrap('00001'),
		'6': __wrap('10101'), '7' : __wrap('11100'), '8': __wrap('01100'), '9': __wrap('00011'), '0': __wrap('01101'),
		'-': __wrap('11000'), '\'': __wrap('11010'), '!': __wrap('10110'), '&': __wrap('01011'), '#': __wrap('00101'),
		'(': __wrap('11110'), ')' : __wrap('01001'), '"': __wrap('10001'), '/': __wrap('10111'), ':': __wrap('01110'),
		';': __wrap('01111'), '?' : __wrap('10011'), ',': __wrap('00110'), '.': __wrap('00111'), '$': __wrap('10010'), 
		' ': __wrap('00100'), '`' : __wrap('11010'),
	},
	'LTRS': __wrap('11111'),  # Letters shift
	'FIGS': __wrap('11011')   # Figures shift
}

def text_to_baudot(text):
	"""Convert text to 5-bit Baudot code, including necessary shifts and adding appropriate start/stop bits."""
	current_mode = 'letters'  # Start in letters mode as enforced on the following line
	baudot_str = MARK_CODE * 20 + BAUDOT_CODE['LTRS']

	chars_in_this_line = ''

	for char in text.upper():  # Baudot code is case-insensitive
		for mode in ['letters', 'figures']:
			if char in BAUDOT_CODE[mode]:
				if current_mode != mode:
					# Insert the mode shift code
					baudot_str += BAUDOT_CODE['LTRS' if mode == 'letters' else 'FIGS']
					current_mode = mode
				baudot_str += BAUDOT_CODE[mode][char]

				if char == '\r' or char == '\n':
					chars_in_this_line = ''
				else:
					chars_in_this_line += char

				if len(chars_in_this_line) >= LINE_WIDTH:
					for c in CRLF:
						baudot_str += BAUDOT_CODE['letters'][c]
					chars_in_this_line = ''

				break

	return baudot_str

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE, initial_phase=0):
	"""Generate a sine wave for a given frequency and duration. Ensures phase continuity when concating sections"""
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