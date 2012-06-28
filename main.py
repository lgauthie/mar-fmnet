#!/usr/bin/env python

from fm import FM
from adsr import ADSR

def main():
    # This is where we set up the synth we created
    synth = FM()
    synth.update_envs( at1 = 0.03, at2 = 0.03, de1 = 0.15, de2 = 0.3, re1 = 0.1, re2 = 0.1 )
    synth.update_ratios( 1, 1.0/6 )
    synth.set_gain( ga1 = 1.0, ga2 = 0.2 )
    synth.note_on()

    # Link the mod depth to our envelope
    modenv1 = ADSR(synth, "mrs_real/Osc1mDepth", dtime = 0.15, scale = 250 * 2.66)
    modenv2 = ADSR(synth, "mrs_real/Osc2mDepth", dtime = 0.3,  scale = 250 * 1.8)

    pitch = 250
    notes = [pitch, pitch * 2, (pitch * 3)/2.0, (pitch * 5)/3.0, pitch]

    for note in notes:
        time = 0.0
        nton = 'on'

        trig( note, note*6, synth, modenv1, modenv2 )
        while time < 0.4:
            synth()
            modenv1()
            modenv2()

            if time > 0.3 and nton == 'on':
                synth.note_off()
                modenv1.note_off()
                modenv2.note_off()
                nton = 'off'
            time = time + synth.tstep

def trig( fr1, fr2, synth, modenv1, modenv2 ):
    synth.update_oscs( fr1, fr2 )
    modenv1.__init__(synth, "mrs_real/Osc1mDepth", dtime = 0.15, scale = fr1 * 2.66)
    modenv2.__init__(synth, "mrs_real/Osc2mDepth", dtime = 0.3,  scale = fr2 * 1.8)
    synth.note_on()
    modenv1.note_on()
    modenv2.note_on()

if __name__ == "__main__":
    main()
