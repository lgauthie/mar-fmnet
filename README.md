The first thing we will do is create a class to wrap our marsytem.
This is done so we can hid the marsystem from the user.

```python
class FM:

    def __init__(self):
        pass

    def __call__(self):
        pass

    def some_func(self, x):
        return x + x
    ...
    ...
    ...
```

<table>
    <tr>
        *note: that the self var in the function call is used to access
               member variables. This is implied, and the function can
               be called as -- fm_instance.some_func(3)
    </tr>
</table>
       

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


