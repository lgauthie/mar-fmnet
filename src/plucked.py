from marsyas import *
from marsyas_util import create

gen = ["Series/fmnet", ["Plucked/plucked", "SoundFileSink/dest2"]]

# Create network and intialize parameter mapping 
network = create(gen)

network.updControl("Plucked/plucked/mrs_real/frequency", 440.0)

sample_rate = 44100.0
buffer_size = 128
device = 1
"""
Sets up the audio output for the network
"""
network.updControl( "mrs_real/israte", sample_rate)

# Set up Audio File
network.updControl( "SoundFileSink/dest2/mrs_string/filename", "fm.wav")

bufferSize = network.getControl("mrs_natural/inSamples").to_natural()
srate = network.getControl("mrs_real/osrate").to_real()
tstep = bufferSize * 1.0 / srate

pitch = 250.0
notes = [pitch, pitch * 2, (pitch * 3)/2.0, (pitch * 5)/3.0, pitch]

for note in notes:
    time = 0.0
    nton = 'on'
    network.updControl("Plucked/plucked/mrs_real/frequency", note)
    network.updControl("Plucked/plucked/mrs_real/nton", 1.0)

    while time < 1.0:
        network.tick()

        if time > 0.7 and nton == 'on':
            nton = 'off'
            network.updControl("Plucked/plucked/mrs_real/nton", 0.0)
        time = time + tstep
