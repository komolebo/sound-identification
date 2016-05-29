__author__ = 'oleh'

from scipy.interpolate import UnivariateSpline
from scipy.io import wavfile
from pylab import *
from peakutils.plot import plot as pplot
import pywt
import peakutils
import random

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Left values less than (MIN_VAL_CLEAN * MAX)
MIN_VAL_CLEAN = 0.01

# Select values with threshold
MIN_VAL_THRES = 0.1
MAX_VAL_THRES = 0.8

# Gun shoot time characteristics
MAX_TIME_DURATION = 3.0
MIN_TIME_DURATION = 0.1


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                    Sound processing section
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# get tuple (signal, rate) from sound file
def read_signal_rate(f, wavelet='db1'):
    rat, signal = wavfile.read(f)

    # check stereo - read only one channel (they're the same)
    if signal[0].size == 2:
        signal = [el[0] for el in signal]

    ca, cd = pywt.dwt(signal, wavelet)
    return rat, [abs(el) for el in cd]


# select spectral components from signal
def select_components(wave, rat, min_t=MIN_TIME_DURATION, max_t=MAX_TIME_DURATION):
    min_val = MIN_VAL_THRES * max(wave)
    min_wid = min_t * rat

    sounds = []

    peaks = peakutils.indexes(np.array(wave), thres=MAX_VAL_THRES, min_dist=min_t * rat)  # TODO min seconds later
    for peak in peaks:
        left = []
        right = []
        zeros_number = min_t * rat / 2

        # move left and collect left part of sound
        i = peak
        rsv = zeros_number
        while i != 0 and rsv and peak - i < rat * max_t / 2:
            if wave[i] < min_val:
                rsv -= 1
            else:
                rsv = zeros_number
            left.append(wave[i])
            i -= 1

        left.reverse()

        # move right and collect right part of sound
        i = peak
        rsv = zeros_number
        while i != len(wave) and rsv and i - peak < rat * max_t / 2:
            if wave[i] < min_val:
                rsv -= 1
            else:
                rsv = zeros_number
            right.append(wave[i])
            i += 1

        sound = left[:-1] + right

        # check if this sound not is already in sounds
        if len(sound) >= min_wid and sounds.count(sound) == 0:
            sounds.append(sound)
    return sounds


# find time offset point of waves max similarity
def offset_convolution(a, b):
    n = len(a)
    max_s = 0
    off = 0

    for offset in range(-n + 1, n - 1):
        s = sum([a[i] * b[i - offset] for i in range(n) if 0 <= offset - i - offset < n])
        if s > max_s:
            max_s = s
            off = offset

    return off


# make wave smooth
def interpolate_signal(wave, new_len):
    old_values = np.arange(0, len(wave))
    new_values = np.linspace(0, len(wave) - 1, new_len)
    spl = UnivariateSpline(old_values, wave, k=3, s=0)
    return spl(new_values)


# wave output
def show_signals(waves, mes='default'):
    figure(random.random())
    for wave in waves:
        plot(wave)
    title(mes)
    show()


# wave output with peaks
def show_peaks(x, y, peaks, mes='mes'):
    pplot(x, y, peaks)
    title(mes)
    show()


def clean_signal(wave):
    min_val = MIN_VAL_CLEAN * max(wave)
    peak = max(wave)

    l = 0
    while wave[l] != peak and wave[l] < min_val:
        l += 1
    r = len(wave) - 1
    while wave[r] != peak and wave[r] < min_val:
        r -= 1

    return wave[l:r]


# normalizes and count difference between two signals
def count_similarity(w1, w2, watch=False):
    # Normalize waves
    scal = max(w2) / max(w1)
    w1 = [el * scal for el in w1]

    # Search max similarity integral
    offset = offset_convolution(w1, w2)

    # Shift graphic and fill empty values with zeros
    if offset < 0:
        shifted_w1 = w1[abs(offset):] + abs(offset) * [0]  # w1[offset] + abs(len(w2) - offset) * [0]
    else:
        shifted_w1 = (len(w2) - offset) * [0] + w1[:offset]

    assert len(shifted_w1) == len(w2)

    if watch:
        show_signals([w1, w2], 'Comparing normalized waves')
        show_signals([shifted_w1, w2], 'Shifted by (f1*f2)(x)')

    delta = sum([abs(i - j) for i, j in zip(shifted_w1, w2)])

    return 1 - delta / (len(w2) * max(w2))