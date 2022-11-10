from re import S
import numpy as np
from scipy.io import wavfile

sr = 44100
freq = 440
length = 5

t = np.linspace(0, length, sr * length)
y = np.sin(2 * np.pi * freq * t)

wavfile.write('mp3/sin.wav', sr, y)