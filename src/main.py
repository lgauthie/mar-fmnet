#!/usr/bin/env python

from fm import FM
from adsr import ADSR

def main():
    # This is where we set up the synth we created
    synth = FM()
    synth.update_envs(at1=0.03, at2=0.03, de1=0.15, de2=0.3, re1=0.1, re2=0.1)
    synth.set_ratios(1, 1.0/6)
    synth.set_gain(1.0, 0.2)

    # This is where we initialize the envelopes to modulate
    # the mod index 
    modenv1 = ADSR(synth, "mrs_real/Osc1mDepth")
    modenv2 = ADSR(synth, "mrs_real/Osc2mDepth")

    pitch = 250
    notes = [pitch, pitch * 2, (pitch * 3)/2.0, (pitch * 5)/3.0, pitch]

    for note in notes:
        time = 0.0
        nton = 'on'

        synth.update_oscs(note, note * 6)
        modenv1 = ADSR(synth, "mrs_real/Osc1mDepth", dtime=0.15, scale=note * 2.66)
        modenv2 = ADSR(synth, "mrs_real/Osc2mDepth", dtime=0.3,  scale=note * 1.8)
        synth.note_on()
        modenv1.note_on()
        modenv2.note_on()
        while time < 1.0:
            synth()
            modenv1()
            modenv2()

            if time > 0.7 and nton == 'on':
                synth.note_off()
                modenv1.note_off()
                modenv2.note_off()
                nton = 'off'
            time = time + synth.tstep

if __name__ == "__main__":
    main()
