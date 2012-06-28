Synthesizing trumpet tones with FM synthesis
=============================================
We are going to emulate a trumpet tone according to the two operator
method described by Steve Saunders in the first edition of the
computer music journal.

Prerequisites
-------------
To follow this tutorial you will need:
+ Python
+ Marsyas - compiled with the swig python bindings
+ marsyas_util - found in src/marsyas_python/ from the Marsyas svn repository
+ plot_spectrogram - from the same location

marsyas_util.py and plot_spectrogram.py should be placed in the same folder
as these code examples.

A tutorial on installing Marsyas and swig python bindings can
be found
[here](http://marsology.blogspot.ca/2011/09/installing-marsyas-with-python-bindings.html).

The structure
-------------

The first thing we will do is create a class to wrap our marsystem.
This is done so we can hid the marsystem from the user.

```python
#!/usr/bin/env python

from marsyas import *
from marsyas_util import create

class FM:

    def __init__(self):
        """
        This method is where we will initialize our marsystem.

        We will also make a call to _init_fm(), and _init_audio()
        These functions could be directly in __init__(), but
        I've separated them out to help better organize the code.
        """

    def __call__(self):
        """
        This method should tick out marsystem. We override the
        __call__() method so we can use the syntax:

            fm_instance()

        To tick the marsystem.
        """

    def _init_fm(self):
        """
        This method will re-map out marsystems controls
        to something that is easier to call.
        """

    def _init_audio(self):
        """
        This method will set up the audio, for the purpose of
        generating graphs of we are only using file out. If 
        you wanted to use the AudioSink marsystem that should
        be initialized here as well.
        """

    def set_ratios(self):
        """
        This method should be used to set the default mod 
        ratios for the marsystem.
        """

    def set_mod_indices(self):
        """
        This method should be used to set the defaul mod
        indices for the marsystem.
        """

    def update_oscs(self):
        """
        This method is used to set the frequency of the
        marsystem oscillators. It will use the default
        ratios, and default mod indices for its calculations
        """

    def update_envs(self):
        """
        This method will set the default amplitude envelope
        for the marsystem.
        """
        
    def note_on(self):
        """
        This method will set the note_on message for the
        marsystem.
        """
        
    def note_off(self):
        """
        Likewise this method will set the note_off message
        for the marsystem.
        """
```

```
*note: that the self var in the function call is used to access
       member variables. This is implied, and the function can
       be called as -- fm_instance.some_func(3)
```

Setting up the system
---------------------
The first order of business in our class is to set up our 
constructor. In python this is the __init__ method. Our method
should look like:

```python
def __init__(self):

    """
    The following four lines in more graphical terms:

        osc1 = FM => ADSR => Gain
        osc2 = FM => ADSR => Gain

        fms = | osc1 =>
              | osc2 =>

        gen = | osc1 
              |    \\
              |     (+) => SoundFileSink
              |    //
              | osc2
    """
    osc1 = ["Series/osc1", ["FM/fm1", "ADSR/env1", "Gain/gain1"]]
    osc2 = ["Series/osc2", ["FM/fm2", "ADSR/env2", "Gain/gain2"]]
    fms = ["Fanout/mix", [osc1, osc2]]
    gen = ["Series/fmnet", [fms, "Sum/sum", "SoundFileSink/dest2"]]

    """
    create is a function defined in marsyas_util, it takes
    in a list of lists, and parses it to create our marsystem.
    """
    self.network = create(gen)

    """
    These methods will be discussed next, the one thing
    I would like to discuss here is the leading _ on the
    method name. This indicates that these methods are
    'private', and should not be called from out side this
    class.
    """
    self._init_fm()
    self._init_audio()

    """
    Here we set up the member variable tstep, this is used to
    get how much time has passed each time we tick the marsystem.
    """
    bufferSize = self.network.getControl("mrs_natural/inSamples").to_natural()
    srate = self.network.getControl("mrs_real/osrate").to_real()
    self.tstep = bufferSize * 1.0 / srate
```

Mapping the controls
--------------------

The following method maps our controls so that we can access them using:
```python
network.updControl("mrs_real/Osc1cFreq")
```
instead of:
```python
network.updControl("Fanout/mix/Series/osc1/FM/fm1/mrs_real/cFrequency")
```

Because we may want to re-use this system in a larger context linking controls like
this become really import so access to parameters doesn't become completely ridiculous.

```python
def _init_fm(self):
    # Map Osc1 Controls
    Osc1 = 'Fanout/mix/Series/osc1/FM/fm1/'
    self.network.linkControl(Osc1 + "mrs_real/cFrequency", "mrs_real/Osc1cFreq")
    self.network.linkControl(Osc1 + "mrs_real/mDepth", "mrs_real/Osc1mDepth")
    self.network.linkControl(Osc1 + "mrs_real/mSpeed", "mrs_real/Osc1mSpeed")
    self.network.linkControl(Osc1 + "mrs_bool/noteon", "mrs_bool/noteon")
    # Map Osc2 Controls
    Osc2 = 'Fanout/mix/Series/osc2/FM/fm2/'
    self.network.linkControl(Osc2 + "mrs_real/cFrequency", "mrs_real/Osc2cFreq")
    self.network.linkControl(Osc2 + "mrs_real/mDepth", "mrs_real/Osc2mDepth")
    self.network.linkControl(Osc2 + "mrs_real/mSpeed", "mrs_real/Osc2mSpeed")
    self.network.linkControl(Osc2 + "mrs_bool/noteon", "mrs_bool/noteon")
    # Map ADSR1
    adsr1 = 'Fanout/mix/Series/osc1/ADSR/env1/'
    self.network.linkControl(adsr1 + "mrs_real/nton", "mrs_real/noteon")
    self.network.linkControl(adsr1 + "mrs_real/ntoff", "mrs_real/noteoff")
    self.network.linkControl(adsr1 + "mrs_real/aTime", "mrs_real/attack1")
    self.network.linkControl(adsr1 + "mrs_real/dTime", "mrs_real/decay1")
    self.network.linkControl(adsr1 + "mrs_real/rTime", "mrs_real/release1")
    # Map ADSR2
    adsr2 = 'Fanout/mix/Series/osc2/ADSR/env2/'
    self.network.linkControl(adsr2 + "mrs_real/nton", "mrs_real/noteon")
    self.network.linkControl(adsr2 + "mrs_real/ntoff", "mrs_real/noteoff")
    self.network.linkControl(adsr2 + "mrs_real/aTime", "mrs_real/attack2")
    self.network.linkControl(adsr2 + "mrs_real/dTime", "mrs_real/decay2")
    self.network.linkControl(adsr2 + "mrs_real/rTime", "mrs_real/release2")
    # Turn Oscillators on
    self.network.updControl( "mrs_bool/noteon", MarControlPtr.from_bool(True))
```

The oscillators are also turned on at this point because we want them to generate a constant
signal. We will use the ADSR envelopes to control the output volume of the system.

Initializing the audio
----------------------

Here we are setting up the audio output for our mar system. Right now we are just
using the file output, but buffer_size and device are left in the call incase
we want to add direct writing to an AudioSink.

```python
    def _init_audio(self, sample_rate = 44100.0, buffer_size = 128, device = 1):
        """
        Sets up the audio output for the network
        """
        self.network.updControl( "mrs_real/israte", sample_rate)
        # Set up Audio File
        self.network.updControl( "SoundFileSink/dest2/mrs_string/filename", "fm.wav")
```
