#!/usr/bin/env python

from marsyas import *
from marsyas_util import *


class FM:
    """
    Sets up and controls a marsyas network doing FM synthesis set up
    as follows:

    Fm(xt) => Env
                \\
                  => + => sink => file
                //
    Fm(yt) => Env
    """

    # Default our systems ratios, and indexes to 1
    ra1 = 1
    ra2 = 1
    in1 = 1
    in2 = 1

    def __init__(self):
        """
        Sets up the marsystem, and then calls the functions to initialize
        the audio IO, and to re-map the controls

        """
        # Set up fm network
        osc1 = ["Series/osc1",["FM/fm1","ADSR/env1","Gain/gain1"]]
        osc2 = ["Series/osc2",["FM/fm2","ADSR/env2","Gain/gain2"]]
        fms = ["Fanout/mix", [osc1, osc2]]
        gen = ["Series/fmnet",[fms,"Sum/sum",
                               "SoundFileSink/dest2","AudioSink/dest1"]]

        # Create network and intialize parameter mapping
        self.network = create(gen)
        self._init_fm()
        self._init_audio()

        # Used to calculate time based off of buffer size and rate
        self.bufferSize = self.network.getControl("mrs_natural/inSamples").to_natural()
        self.srate = self.network.getControl("mrs_real/osrate").to_real()
        self.tstep = self.bufferSize * 1.0 / self.srate

    def __call__(self):
        """
        Ticks the network when the synth is called
        """
        self.network.tick()

    def _init_fm(self):
        """
        Re-maps the controls to the mar system so that they
        are easier to access.
        """
        # Map Osc1 Controls
        Osc1 = 'Fanout/mix/Series/osc1/FM/fm1/'
        self.network.linkControl( Osc1 + "mrs_real/cFrequency", "mrs_real/Osc1cFreq")
        self.network.linkControl( Osc1 + "mrs_real/mDepth", "mrs_real/Osc1mDepth")
        self.network.linkControl( Osc1 + "mrs_real/mSpeed", "mrs_real/Osc1mSpeed")
        self.network.linkControl( Osc1 + "mrs_bool/noteon", "mrs_bool/noteon")
        # Map Osc2 Controls
        Osc2 = 'Fanout/mix/Series/osc2/FM/fm2/'
        self.network.linkControl( Osc2 + "mrs_real/cFrequency", "mrs_real/Osc2cFreq")
        self.network.linkControl( Osc2 + "mrs_real/mDepth", "mrs_real/Osc2mDepth")
        self.network.linkControl( Osc2 + "mrs_real/mSpeed", "mrs_real/Osc2mSpeed")
        self.network.linkControl( Osc2 + "mrs_bool/noteon", "mrs_bool/noteon")
        # Map ADSR1
        adsr1 = 'Fanout/mix/Series/osc1/ADSR/env1/'
        self.network.linkControl( adsr1 + "mrs_real/nton", "mrs_real/noteon")
        self.network.linkControl( adsr1 + "mrs_real/ntoff", "mrs_real/noteoff")
        self.network.linkControl( adsr1 + "mrs_real/aTime", "mrs_real/attack1")
        self.network.linkControl( adsr1 + "mrs_real/dTime", "mrs_real/decay1")
        self.network.linkControl( adsr1 + "mrs_real/rTime", "mrs_real/release1")
        # Map ADSR2
        adsr2 = 'Fanout/mix/Series/osc2/ADSR/env2/'
        self.network.linkControl( adsr2 + "mrs_real/nton", "mrs_real/noteon")
        self.network.linkControl( adsr2 + "mrs_real/ntoff", "mrs_real/noteoff")
        self.network.linkControl( adsr2 + "mrs_real/aTime", "mrs_real/attack2")
        self.network.linkControl( adsr2 + "mrs_real/dTime", "mrs_real/decay2")
        self.network.linkControl( adsr2 + "mrs_real/rTime", "mrs_real/release2")
        # Turn Oscillators on
        self.network.updControl( "mrs_bool/noteon", MarControlPtr.from_bool(True))

    def _init_audio(self, sample_rate = 44100.0, buffer_size = 128, device = 1):
        """
        Sets up the audio output for the network
        """
        self.network.updControl( "mrs_real/israte", sample_rate)
        # Set up Audio File
        self.network.updControl( "SoundFileSink/dest2/mrs_string/filename", "fm.wav")

    def update_ratios(self, ra1, ra2):
        """
        Updates the ratios of the oscillators
        """
        self.ra1 = ra1
        self.ra2 = ra2

    def update_mod_indices(self, in1, in2):
        """
        Updates the mod indexs of the oscillors
        """
        self.in1 = in1
        self.in2 = in2

    def update_oscs(self, fr1, fr2):
        """
        Updates the frequencies, ratios, and modulation indexes
        for both of the oscillators.
        """
        # Set Osc1
        self.network.updControl( "mrs_real/Osc1cFreq",  float(fr1))
        self.network.updControl( "mrs_real/Osc1mDepth", float(fr1 * self.in1))
        self.network.updControl( "mrs_real/Osc1mSpeed", float(fr1 * self.ra1))
        # Set Osc2
        self.network.updControl( "mrs_real/Osc2cFreq",  float(fr2))
        self.network.updControl( "mrs_real/Osc2mDepth", float(fr2 * self.in2))
        self.network.updControl( "mrs_real/Osc2mSpeed", float(fr2 * self.ra2))

    def set_gain(self, ga1, ga2):
        """
        Sets the gain of each oscillator in the mar system
        """
        self.network.updControl("Fanout/mix/Series/osc1/Gain/gain1/mrs_real/gain", ga1)
        self.network.updControl("Fanout/mix/Series/osc2/Gain/gain2/mrs_real/gain", ga2)

    def update_envs(self, at1, at2, de1, de2, re1, re2):
        """
        Updates the amplitude envelopes of both oscillators
        """
        #TODO: This function is a bit
        self.network.updControl( "mrs_real/attack1",   at1)
        self.network.updControl( "mrs_real/decay1",    de1)
        self.network.updControl( "mrs_real/release1",  re1)
        self.network.updControl( "mrs_real/attack2",   at2)
        self.network.updControl( "mrs_real/decay2",    de2)
        self.network.updControl( "mrs_real/release2",  re2)

    def note_on(self):
        """
        Starts a note playing
        """
        self.network.updControl( "mrs_real/noteon",  1.0)

    def note_off(self):
        """
        Turns a note off
        """
        self.network.updControl( "mrs_real/noteoff", 1.0)
