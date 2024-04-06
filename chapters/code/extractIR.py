# coding: utf-8


import numpy as np


def extractIR(sweep_response, invsweepfft):
    """Extract impulse response from swept-sine recording.
    
    Returns:
            irLin : numpy array with linear impulse response
            irNonLin : non linear Volterra diagonals
    """
    N = len(invsweepfft)
    sweepfft = np.fft.fft(sweep_response, N)
    # perform convolution with inverse filter
    invsweepfft = invsweepfft.reshape(sweepfft.shape)
    ir = np.fft.ifft(invsweepfft * sweepfft)
    ir = np.roll(np.transpose(ir.real), int(len(ir)/2))
    # separate linear and non linear responses
    irLin = ir[int(len(ir)/2):]
    irNonLin = ir[:int(len(ir)/2)]
    return irLin, irNonLin


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    from sys import argv
    from scipy.io import wavfile as wav
    from scipy.io import loadmat
    
    
    script, sweep, invsweep = argv
    # retrieve data
    sw_rate, sw = wav.read(sweep)
    mat = loadmat(invsweep)
    invsw = np.transpose(mat['invsw700to5j20s'])
    
    irLin, irNonLin = extractIR(sw, invsw)
    
    NFFT = 1024
    Fs = 48000
    noverlap = 900
    
    Pxx, freqs, bins, im = plt.specgram(irLin, NFFT=NFFT, Fs=Fs, noverlap=900,
                                cmap=plt.get_cmap('seismic'))
    
    plt.show()
