# -*- coding: utf-8 -*-


import pyaudio
import numpy as np
import wave


class ToneGenerator(object):
 
    def __init__(self, samplerate=48000, frames_per_buffer=4800):
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.frames_per_buffer = frames_per_buffer
        self.streamOpen = False
 
    def sinewave(self):
        if self.buffer_offset + self.frames_per_buffer - 1 > self.x_max:
            xs = np.arange(self.buffer_offset, self.x_max)
            tmp = self.amplitude * np.sin(xs * self.omega)
            out = np.append(tmp, np.zeros(self.frames_per_buffer - len(tmp)))                    
        else:
            xs = np.arange(self.buffer_offset,
                           self.buffer_offset + self.frames_per_buffer)
            out = self.amplitude * np.sin(xs * self.omega)
        self.buffer_offset += self.frames_per_buffer
        return out
 
    def tone_callback(self, in_data, frame_count, time_info, status):
        if self.buffer_offset < self.x_max:
            data = self.sinewave().astype(np.float32)
            return (data.tostring(), pyaudio.paContinue)
        else:
            return (None, pyaudio.paComplete)
            
    def file_callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
 
    def is_playing(self):
        if self.streamOpen:
            if self.stream.is_active():
                return True
            else:
                if self.streamOpen:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.streamOpen = False
                return False
        else:
            pass
 
    def play_tone(self, frequency, duration, amplitude): #frecuencia normalizada
        self.omega = float(frequency) * (np.pi * 2) / self.samplerate
        self.amplitude = amplitude
        self.buffer_offset = 0
        self.streamOpen = True
        self.x_max = np.ceil(self.samplerate * duration) - 1
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=1,
                                  rate=self.samplerate,
                                  output=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.tone_callback)

    def play_file(self, file):
        self.streamOpen = True
        self.wf = wave.open(file)
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                    channels=self.wf.getnchannels(),
                    rate=self.wf.getframerate(),
                    output=True,
                    stream_callback=self.file_callback)
