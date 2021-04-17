SAMPLE_RATE = 44100.0;
import math
import wave
import struct
import aifc

ATTACK = 1 
DECAY = 2
SUSTAIN = 3
RELEASE = 4


def square(i, freq, rate):
    on = int((i/rate)*freq) % 3  
    if on == 0: return 1
    return -1

def sin(i, freq, rate):
    return math.sin(2 * math.pi * i / (rate / freq))

def sinpair(ratio):
    return (lambda i, freq, rate: math.sin(2 * math.pi * i / (rate / freq)) + math.sin(2 * math.pi * i / (rate / (ratio*freq))))

def saw(i, freq, rate):
    return 2*(i % ( rate/freq ) / (rate/freq)) - 1;

def sinsaw(i, freq,rate):
    return sin(i, freq, rate) + 0.2*saw(i, freq/1.9, rate)

def mkbeep(name, length, func, *notes):
    out = wave.open("%s.wav"%name, "wb")
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(SAMPLE_RATE)
    out.setnframes(len(notes)*SAMPLE_RATE*2)

    fidx = 0;
    for note in notes: 
        sample_count = length*SAMPLE_RATE*note.length;
        attack_end = note.envelope[0] * sample_count 
        decay_end = note.envelope[1] * sample_count
        decay_size = decay_end - attack_end 
        sustain_level = note.envelope[2]
        sustain_fall = 1-sustain_level
        release_start = note.envelope[3] * sample_count
        release_size = sample_count-release_start
        for i in xrange(0,int(sample_count)):
            if i < attack_end: 
                amp = float(i)/(attack_end) 
            elif i < decay_end: 
                amp = 1 - (sustain_fall * (decay_size- (decay_end-i))/decay_size)
            elif i >= release_start:
                amp = sustain_level - sustain_level*(i-release_start)/release_size
            else:
                amp = sustain_level
            gen = 0
            #generate samples in 0->1
            gen = func(i, note.freq, SAMPLE_RATE)
            #Normalize to -1->1
            gen = gen / len(notes)
            #Apply envelope
            gen = gen * amp
            #Create PCM sample
            sample = 32767 * gen;
            #<H little-endian short
            out.writeframesraw(struct.pack('<h', sample))
        fidx += 1
    out.close();
    print "release start/size: %s %s"%(release_start, release_size)
    print "samples: %s"%(sample_count)

#Envelope:
#0: The percentage in to be finished the attack (amp = 1 at this point)
#1: The percentage in to be finished the decay (amp = sustain at this point)
#2: The level to decay to (sustain level)
#3: The percentage in to start releasing (sustain -> 0)


defenvelope = [.05, .1, .9, .5]
class Note:
    def __init__(self, freq, length = 1, envelope = defenvelope):
        self.freq = freq
        self.length = length
        self.envelope = envelope

basefreq =440 
freqs = [basefreq, 3*basefreq/2, basefreq *1.2, 3*basefreq * 1.2/2]
interval = 3.0/2.0
step = 1.2
mkbeep("beepa", 0.1, square, Note(basefreq, 1), Note(basefreq*interval, 1), Note(step*basefreq, 1), Note(step*interval*basefreq, 2))
mkbeep("beepb", 0.15, sin, Note(basefreq*interval, 1), Note(basefreq, 1), Note(interval*basefreq, 1), Note(basefreq, 2, [.05, .1, .9, .1]))
mkbeep("beepc", 0.1, sinsaw, Note(basefreq*interval, 1), Note(basefreq, 1), Note(interval*basefreq, 1), Note(basefreq, 2))
