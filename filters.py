__author__ = 'oleh'

import numpy
from sound_process import *

# Input component divided into groups by peaks number
PEAKS_NUM = 50


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Filters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# takes basic wave and compares it to pattern
def filter_by_form(w, pattern, thres=0.08, n=50, watch=True):
    x_wid = min(len(w), len(pattern)) / 2
    x = numpy.linspace(0, x_wid - 1, x_wid)

    pattern = interpolate_signal(pattern, x_wid)
    w = interpolate_signal(w, x_wid)

    p_peaks = peakutils.indexes(pattern, thres=thres, min_dist=len(x) / n)
    w_peaks = peakutils.indexes(w, thres=thres, min_dist=len(x) / n)

    if watch:
        show_peaks(x, w, w_peaks, 'Comparable signal peaks')
        show_peaks(x, pattern, p_peaks, 'Pattern peaks')

    new_w = interpolate_signal([w[i] for i in w_peaks], x_wid)
    new_p = interpolate_signal([pattern[i] for i in p_peaks], x_wid)

    if watch:
        show_signals([new_w], 'New comparable wav signal')
        show_signals([new_p], 'New pattern wav signal')

    return count_similarity(new_w, new_p, watch)


# Check whether the sound is duration-enough
def filter_by_duration(wave, rat, min_sec=0.01, max_sec=10):
    t = float(len(wave)) / rat
    return min_sec <= t <= max_sec


# Returns True if first half is bigger then second half in spectrum
def filter_energy(wave, min_val=1.5):
    half1 = sum(wave[:len(wave) / 2])
    half2 = sum(wave[len(wave) / 2:])
    return (half1 / half2) >= min_val


# Returns True is peak's position in selected area
def filter_by_peak(wave, area=0.2):
    peak_pos = wave.index(max(wave))
    return peak_pos <= len(wave) * area


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Run method
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def run_filters(name1, pattern='patterns/pattern.wav', watch=False):
    rat, f1 = read_signal_rate(name1)
    rat2, f2 = read_signal_rate(pattern)

    components1 = select_components(f1, rat)
    components2 = select_components(f2, rat2)

    components1 = [clean_signal(comp) for comp in components1]

    mes = str(len(components1))

    # Filter by duration
    components1 = [x for x in components1 if filter_by_duration(x, rat)]
    mes += ' d->' + str(len(components1))

    # Filter by energy
    components1 = [x for x in components1 if filter_energy(x)]
    mes += ' e->' + str(len(components1))

    # Filter by peak position
    components1 = [x for x in components1 if filter_by_peak(x)]
    mes += ' p->' + str(len(components1)) + '| '

    # Eventually analyze the form
    value = 0
    for comp in components1:
        if watch:
            show_signals([f1] + [comp], name1)
        tmp = filter_by_form(comp, components2[0], n=PEAKS_NUM, watch=watch)
        if tmp >= value:
            value = tmp

    if value >= 0.9:
        mes += 'SUPER'
    elif value >= 0.85:
        mes += 'GOOD'
    elif value >= 0.8:
        mes += 'NORM'
    elif value >= 0.7:
        mes += 'MAYBE NO'
    else:
        mes += 'NOT A GUNSHOT'
    mes += ' [' + str(value) + ']'
    print mes

    return 'SUPER' in mes or 'GOOD' in mes or 'NORM' in mes


if __name__ == '__main__':
    run_filters('patterns/gunshot1_sim-7.wav', watch=False)