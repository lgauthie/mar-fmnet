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

A tutorial on installing Marsyas and swig python bindings can
be found
[here](http://marsology.blogspot.ca/2011/09/installing-marsyas-with-python-bindings.html).

The structure
-------------

The first thing we will do is create a class to wrap our marsystem.
This is done so we can hid the marsystem from the user.

```python
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
       

The first order of business in our class is to set up our 
constructor. In python this is the __init__ method. Our method
should look like:


```python
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
```


