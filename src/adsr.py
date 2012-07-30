class ADSR:
    """
    This class is used to modulation a marsystems parameters
    via a ADSR envelope.
    """
    state = 'off'
    val = 0

    def __init__(self, synth, param, atime = 0.03, dtime = 0.25,
                       rtime = 0.1, suslvl = 0.85, scale = 1):
        """
        Initializes the envelopes parameters
        """
        self.target = 1
        self.atime = atime
        self.dtime = dtime
        self.rtime = rtime
        self.suslvl = suslvl
        self.scale = scale
        self.arate = self.target / (self.atime / synth.tstep)
        self.drate = (self.target - self.suslvl) / (self.dtime / synth.tstep)
        self.rrate = self.suslvl / (self.rtime / synth.tstep)
        self.synth = synth
        self.param = param

    def __call__(self):
        """
        Updates the envelope, and chosen parameter each time 
        the class is called.
        """
        if self.state == 'attack':
            self.val += self.arate
            if self.val >= self.target:
                self.val = self.target
                self.target = self.suslvl
                self.state = 'decay'
        elif self.state == 'decay':
            self.val -= self.drate
            if self.val <= self.target:
                self.val = self.target
                self.state = 'sustain'
        elif self.state == 'release':
            self.val -= self.rrate
            if self.val <= 0:
                self.val = 0
                self.state = 'end'
                self.target = 1
        self.synth.network.updControl(self.param, float(self.val * self.scale))

    def note_on(self):
        """
        Used to trigger the envelope
        """
        self.state = 'attack'
        self.val = 0
        self.target = 1

    def note_off(self):
        """
        Tells the envelope when to stop playing
        """
        self.state = 'release'
