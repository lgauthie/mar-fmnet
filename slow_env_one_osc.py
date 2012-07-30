#!/usr/bin/env python

from fm import FM
from adsr import ADSR

def main():
    # This is where we set up the synth we created
    synth = FM()
    synth.update_envs(at1=0.00, at2=0.0, de1=0.0, de2=0.0, re1=0.0, re2=0.0)

    synth.set_ratios(1, 1.0/6)
    synth.set_gain(1.0, 0.0)
    synth.audio_file("two_osc.wav")

    # This is where we initialize the envelopes to modulate
    # the mod index 
    modenv1 = ADSR(synth, "mrs_real/Osc1mDepth")
    modenv2 = ADSR(synth, "mrs_real/Osc2mDepth")

    pitch = 250

    time = 0.0

    synth.update_oscs(pitch, 0)
    modenv1 = ADSR(synth, "mrs_real/Osc1mDepth",atime=10.0, dtime=0.15, scale=pitch * 8.0)
    synth.note_on()
    modenv1.note_on()
    while time < 10:
        synth()
        modenv1()
        time = time + synth.tstep

if __name__ == "__main__":
    main()
