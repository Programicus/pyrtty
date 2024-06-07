#!/usr/bin/env python3
import argparse
import sys

import numpy as np
import sounddevice as sd

# Constants
DEFAULT_MARK_FREQ = 2125
DEFAULT_SPACE_FREQ = 2295
DEFAULT_BAUD_RATE = 45.45
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_BLOCKSIZE = 1000
DEFAULT_AMPLITUDE = 1

DEFAULT_MESSAGE = 'Hello World! This is pyrtty.py\r\n(This is the example message)\r\n12345 Text 67890\r\nRYRYRYRYRYRYRYRYRYRY\r\nAMAMAMAMAMAMAMAMAMA'

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

def generate_tone(frequency, duration, sample_rate=DEFAULT_SAMPLE_RATE, initial_phase=0):
	"""Generate a sine wave for a given frequency and duration. Ensures phase continuity when concating sections"""
	t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
	tone = np.sin(2 * np.pi * frequency * t + initial_phase)
	final_phase = (initial_phase + 2 * np.pi * frequency * duration) % (2 * np.pi)
	return tone, final_phase

def baudot_to_afsk(baudot_str, mark_freq=DEFAULT_MARK_FREQ, space_freq=DEFAULT_SPACE_FREQ, baud_rate=DEFAULT_BAUD_RATE, amp=DEFAULT_AMPLITUDE):
	"""Convert Baudot code string to AFSK tones."""
	bit_duration = 1 / baud_rate
	afsk_signal = np.array([])
	phase = 0
	for bit in baudot_str:
		frequency = mark_freq if bit == MARK_CODE else space_freq
		tone, phase  = generate_tone(frequency, bit_duration, initial_phase=phase)
		afsk_signal = np.concatenate((afsk_signal, tone))
	return afsk_signal

def play_afsk_signal(signal, sample_rate=DEFAULT_SAMPLE_RATE, blocksize=DEFAULT_BLOCKSIZE):
	"""Play AFSK signal through the default audio device."""
	sd.play(signal, sample_rate, blocksize=blocksize)
	sd.wait()


def main():
	parser = argparse.ArgumentParser(description='Generate AFSK signals from text.')
	parser.add_argument('text', nargs='*', default=[DEFAULT_MESSAGE], help='Text to convert to baudot then a AFSK signal')
	parser.add_argument('--mark-freq', type=float, default=DEFAULT_MARK_FREQ, help=f'Frequency of mark tone (default: {DEFAULT_MARK_FREQ} Hz)')
	parser.add_argument('--space-freq', type=float, default=DEFAULT_SPACE_FREQ, help=f'Frequency of space tone (default: {DEFAULT_SPACE_FREQ} Hz)')
	parser.add_argument('--baud-rate', type=float, default=DEFAULT_BAUD_RATE, help=f'Baud rate (default: {DEFAULT_BAUD_RATE})')
	parser.add_argument('--sample-rate', type=int, default=DEFAULT_SAMPLE_RATE, help=f'Sample rate (default: {DEFAULT_SAMPLE_RATE} Hz)')
	parser.add_argument('--amplitude', type=float, default=DEFAULT_AMPLITUDE, help=f'Amplitude of the waveform (default: {DEFAULT_AMPLITUDE})')
	parser.add_argument('--block-size', type=int, default=DEFAULT_BLOCKSIZE, help=f'Block size for audio playback (default: {DEFAULT_BLOCKSIZE})')
	args = parser.parse_args()
	
	text = ' '.join(args.text)
	if text == '-':
		text = sys.stdin.read()

	baudot = text_to_baudot(text)
	afsk = baudot_to_afsk(baudot, mark_freq=args.mark_freq, space_freq=args.space_freq, baud_rate=args.baud_rate, amp=args.amplitude)
	play_afsk_signal(afsk, sample_rate=args.sample_rate, blocksize=args.block_size)

if __name__ == '__main__':
	main()