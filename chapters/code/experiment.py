#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""Plot the live microphone signal(s) with matplotlib."""
import argparse
from queue import Queue, Empty
from os import path


user = path.expanduser('~')
main_path = path.join(user, 'Documents', 'recordings')


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-w', '--window', type=float, default=200, metavar='DURATION',
    help='visible time slot (default: %(default)s ms)')
parser.add_argument(
    '-i', '--interval', type=float, default=100,
    help='minimum time between plot updates (default: %(default)s ms)')
parser.add_argument(
    '-b', '--blocksize', type=int, help='block size (in samples)')
parser.add_argument(
    '-r', '--samplerate', type=float, help='sampling rate of audio device')
parser.add_argument(
    '-n', '--downsample', type=int, default=10, metavar='N',
    help='display every Nth sample (default: %(default)s)')
parser.add_argument(
    'channels', type=int, default=[1, 2], nargs='*', metavar='CHANNEL',
    help='input channels to plot (default: the first)')
args = parser.parse_args()
if any(c < 1 for c in args.channels):
    parser.error('argument CHANNEL: must be >= 1')
mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
queue = Queue()


def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, flush=True)
    # Fancy indexing with mapping creates a (necessary!) copy:
    queue.put(indata[::args.downsample, mapping])


def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    global pause
    global record
    global recorded
    block = True  # The first read from the queue is blocking ...
    if not pause:
        while True:
            try:
                data = queue.get(block=block)
                if record:
                    recorded.append(data)
                else:
                    pass
            except Empty:
                break
            shift = len(data)
            plotdata = np.roll(plotdata, -shift, axis=0)
            plotdata[-shift:, :] = data
            block = False  # ... all further reads are non-blocking
            if gen.is_playing() == False:
                print('led off')    # debug
                # duino.led_off()
        for column, line in enumerate(lines):
            line.set_ydata(plotdata[:, column])
    return lines


def onKeyboard(event):
    """Keyboard events for experiment control.
    """
    global pause
    global record
    global recorded
    global file_
    global frec
    global amp
    global dur
    global soundfile
    k = event.key
    if k == 't':    # play tone and record
        record = True
        # duino.led_on()
        gen.play_tone(frec, dur, amp)
    elif k == 'r':  # play from file and record
        record = True
        # duino.led_on()
        gen.play_file(soundfile)
    elif k == 'v':  # record without playing tone
        record = True
    elif k == 'g':  # save recording
        if record == True:
            record = False
            with open(file.name, 'w') as thefile:
                for item in recorded:
                    thefile.write("%s\n" % item)
        else: pass
        recorded = []
    elif k == 'n':  # choose/create save file
        root = tk.Tk()
        root.withdraw()
        file_ = filedialog.asksaveasfile(mode='w', defaultextension='txt')
    elif k == 'p':  # choose parameter for tones
        root = tk.Tk()
        root.withdraw()
        frec = simpledialog.askfloat('Frecuencia', 'Frecuencia (Hz):')
        dur = simpledialog.askfloat('dur', 'Duracion (ms):') * .001
        amp = simpledialog.askfloat('Amplitud', 'Volumen (0--1):')
    elif k == 'm':  # choose sound file
        root = tk.Tk()
        root.withdraw()
        s = filedialog.askopenfile()
        soundfile = s.name
    elif k == 'q':  # play tone
        gen.play_tone(frec, dur, amp)
    else:
        print('Argument unknown')


try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    import numpy as np
    import sounddevice as sd
    import tkinter as tk
    from tkinter import filedialog, simpledialog
    from ToneGenerator import ToneGenerator
    # from arduino import Arduino


    options = '''t --> Record and play tone.\n
                 r --> Record and play from file.\n
                 v --> Record silence.\n
                 g --> Save recorded data
                 n --> Choose new file to save data.\n
                 p --> Choose tone parameters (freq, dur, amp).\n
                 m --> Choose file to play.\n
                 q --> Play test tone.'''


    pause = False
    record = False
    recorded = []
    file_ = ''
    frec = 440
    dur = .025
    amp = 1
    soundfile = 'sw1.wav'
    gen = ToneGenerator()
    # duino = Arduino()
    nchan = len(args.channels)

    if args.list_devices:
        print(sd.query_devices())
        parser.exit()
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    length = int(args.window * args.samplerate / (1000 * args.downsample))
    plotdata = np.zeros((length, nchan))

    fig, axarr = plt.subplots(nchan, sharex=True)
    lines = [axarr[n].plot(plotdata[:, n])[0] for n in range(nchan)]
    if len(args.channels) > 1:
        for i in range(nchan):
            axarr[i].legend(('channel {}'.format(args.channels[i]), ),
                            loc='lower left')
            axarr[i].axis((0, len(plotdata), -1.2, 1.2))
            axarr[i].yaxis.grid(True)
            # ax.tick_params(bottom='off', top='off', labelbottom='off',
                            # right='off', left='on', labelleft='on',
                            # direction='out', length=6, width=2, colors='r')
    fig.tight_layout(pad=0)

    stream = sd.InputStream(
        device=args.device, channels=max(args.channels),
        samplerate=args.samplerate, callback=audio_callback)
    fig.canvas.mpl_connect('key_press_event', onKeyboard)
    ani = FuncAnimation(fig, update_plot, interval=args.interval, blit=True)
    with stream:
        print(options)
        plt.show()
        print('Bye')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
