__author__ = 'oleh'

import math
import pyaudio


def play():
    # sudo apt-get install python-pyaudio
    py_audio = pyaudio.PyAudio
    # See http://en.wikipedia.org/wiki/Bit_rate#Audio
    bitrate = 16000  # number of frames per second/frameset.
    # See http://www.phy.mtu.edu/~suits/notefreqs.html
    frequency = 261.63  # Hz, waves per second, 261.63=C4-note.
    length = 4.2232  # seconds to play sound
    numberofframes = int(bitrate * length)
    restframes = numberofframes % bitrate
    wavedata = ''
    for x in xrange(numberofframes):
        frequency += 1
        wavedata += chr(int(math.sin(x / ((bitrate / frequency) / math.pi)) * 127 + 128))

    # fill remainder of frameset with silence
    for x in xrange(restframes):
        wavedata += chr(128)
    p = py_audio()
    stream = p.open(format=p.get_format_from_width(1),
                    channels=1,
                    rate=bitrate,
                    output=True)
    stream.write(wavedata)
    stream.stop_stream()
    stream.close()


if __name__ == '__main__':
    play()

