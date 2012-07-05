Synthesizing trumpet tones with Marsyas using FM synthesis
=============================================
We are going to emulate a trumpet tone according to the two operator
method described by Dexter Morrill in the first edition of the
computer music journal.

```
There should be a blurb here talking about what we need to create a trumpet tone
```
```
The section talking about synthesis should explain why two pairs of
oscillators are being used.

A spectrogram should be used here to show the problem of using one
pair of oscillators with a higher modulation ration.
```
```
The "Lets talk about synthesis" section should be split up; the part
about FM synthesis should come before anything about the program or
marsyas, and the part about the code should be in an "Setting up the
oscillators" section.
```
```
Add a short section on setting the relative gain. It is talked about in
the "Putting it all together" section, but I never explain where the
method comes from.
```

Prerequisites
-------------
To follow this tutorial you will need:
+ Python ```which versions?```
+ Marsyas - compiled with the swig python bindings
+ marsyas_util - found in src/marsyas_python/ from the Marsyas svn repository
+ plot_spectrogram - from the same location

marsyas_util.py and plot_spectrogram.py should be placed in the same folder
as the code examples. ```Please define what these modules do.```

A tutorial on installing Marsyas and swig python bindings can
be found
[here](http://marsology.blogspot.ca/2011/09/installing-marsyas-with-python-bindings.html).

I'm also assuming you have some experience with classes in python, and object oriented 
programming in general.

The structure
-------------

The first thing we will do is create a class to wrap our marsystem.
This is done so we can hide the marsystem from the user.

```python
#!/usr/bin/env python

# import all the functions we need from the marsyas
# library, and marsyas_util.
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
        This method will set up the audio system, currently
        we are only using the marsyas AudioFileSink. If 
        you wanted to use the AudioSink marsystem that should
        be initialized here as well.
        """

    def set_ratios(self):
        """
        This method should be used to set the default modulation 
        ratios for the marsystem.
        """

    def set_mod_indices(self):
        """
        This method should be used to set the default modulation
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

Because we may want to re-use this system in a larger contexts linking controls like
this becomes really import; it keeps access to system parameters from becoming
completely ridiculous.

All of these parameters that are getting linked now will be discussed in later sections.

The one parameter I would like to talk about now is the "mrs_real/noteon". Both envelopes
have been linked to the same control so both can be triggered at the same time. The same
thing happens with the oscillators "mrs_bool/noteon".

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
signal. We will instead use the ADSR envelopes to control the output volume of the system.

Initializing the audio
----------------------

Here we are setting up the audio output for our mar system. Right now we are just
using the file output, but buffer_size and device are left in the method call in case
we want to add the ability to directly write to an AudioSink.

```python
def _init_audio(self, sample_rate = 44100.0, buffer_size = 128, device = 1):
    """
    Sets up the audio output for the network
    """
    self.network.updControl( "mrs_real/israte", sample_rate)
    # Set up Audio File
    self.network.updControl( "SoundFileSink/dest2/mrs_string/filename", "fm.wav")
```

Overriding defaults and ticking the network
----------------

The __call__ method is python is used to make an object callable. Here we want to
use __call__ to tick our network. This means we can call and instance of our FM
class like:
```python
fm_instance()
```
Instead of:
```python
fm_instance.tick()
```

Each call to our class will now cause audio to processed:
```python
def __call__(self):
    self.network.tick()
```

We will also set up two more methods to override the
default values for our mod ratio and mod indices.
```python
def set_ratios(self, ra1, ra2):
    self.ra1 = ra1
    self.ra2 = ra2

def set_mod_indices(self, in1, in2):
    self.in1 = in1
    self.in2 = in2
```

Lets talk about FM
------------------

Now that we have are network set up, we should talk a bit about FM synthesis.

FM is short for frequency modulation. This name is great because it literally
describes what is taking place, we are modulating the frequency of a signal. 
We could call it Chowning Synthesis, but that would be silly and not describe very
well what is happening.

The great thing about FM is that you can create many frequency sidebands from
simple waves.

The easiest and most commonly used version of FM synthesis is to have two sine wave
generators. One is called the carrier; it is where we get our output from, and
the other is called the modulator; it controls the frequency of the carrier.

Both are normally set to be in the audible range, but some neat aliasing effects can
be achieved if they are not(this also depends on the sample rate of the system).
See [this](http://en.wikipedia.org/wiki/Aliasing#Sampling_sinusoidal_functions).

The amplitude of the sidebands are controlled by:
+ Modulation Index
+ Bessel Functions

And the location of the sidebands are controlled by:
+ Modulation Ratio

The ratio is used to calculate the frequency of our modulation oscillators:
```
modulation frequency = base frequency x ratio
```

If the ratio is a whole number our sidebands will be harmonic. Otherwise we
will end up with an enharmonic spectrum.

This can be made slightly more complicated by having a carrier ratio as well,
but for trumpet tones we don't need this capability.

The modulation index is used to calculate how many hz our signal should be
modulated by:
```
modulation depth = base frequency x modulation index
```

The higher the index the more high frequencies will show up in our output.
The actual amplitude of each sideband is scaled by a Bessel function, and
the amount a sideband is scaled by will change depending on the mod index.
See [this](http://en.wikipedia.org/wiki/Bessel_functions) for a bunch of math
we don't really need to know to play with FM synthesis.

Because we already mapped these controls earlier on it is now just a matter of
making a method call that can set these parameters.

```python
def update_oscs(self, fr1, fr2):

    # Set Osc1
    self.network.updControl("mrs_real/Osc1cFreq",  float(fr1))
    self.network.updControl("mrs_real/Osc1mDepth", float(fr1 * self.in1))
    self.network.updControl("mrs_real/Osc1mSpeed", float(fr1 * self.ra1))

    # Set Osc2
    self.network.updControl("mrs_real/Osc2cFreq",  float(fr2))
    self.network.updControl("mrs_real/Osc2mDepth", float(fr2 * self.in2))
    self.network.updControl("mrs_real/Osc2mSpeed", float(fr2 * self.ra2))
```

The envelopes
-------------

Here we will be doing very much the same thing as we just did above, but
this time we will be setting the parameters for our amplitude envelopes.

An ADSR envelope like the one we are using in this system has four stages:
+ Attack - time to get to the maximum amplitude
+ Decay - time to get to the sustain amplitude
+ Sustain - holds the sustain amplitude until given note off
+ Release - time for the amplitude to reach zero after the note off

```python
def update_envs(self, at1, at2, de1, de2, re1, re2):

    # Envelope one settings
    self.network.updControl("mrs_real/attack1",   at1)
    self.network.updControl("mrs_real/decay1",    de1)
    self.network.updControl("mrs_real/release1",  re1)

    # Envelope two settings
    self.network.updControl("mrs_real/attack2",   at2)
    self.network.updControl("mrs_real/decay2",    de2)
    self.network.updControl("mrs_real/release2",  re2)
```

Note on, note off
-----------------

These two methods are used to tell our envelope when to turn on, and
when to turn off. We mapped the controls we are using now back in the
mapping controls section.

```python
def note_on(self):
    self.network.updControl("mrs_real/noteon",  1.0)

def note_off(self):
    self.network.updControl("mrs_real/noteoff", 1.0)
```

More envelopes
----------

The last ability we need to create a "Convincing" FM trumpet is the power
to modulate the index over time.

I have written an ADSR envelope in python that will allow us to modulate
any parameter of our synth. We can only update the value each time we tick
our system, but it is better then having no modulation.

This envelope can be used like:
```python
modenv = ADSR(synth, "mrs_type/parameter")
```

Each time modenv() is called it will tick the envelope, and update the parameter.

It also has the ability to scale the output, or change the times for the attack, decay,
and release.
```python
modenv = ADSR(synth, "mrs_type/parameter", dtime=something, scale=something)
```

Lets put this all together
--------------------------

The first thing we need to do is set up an instance of our synth.
```python
synth = FM()
```

And then override the envelope. For this to sound trumpet like we need a
fast attack/decay/release. The decay time for the higher oscillator should
be slightly longer.
```python
synth.update_envs(at1=0.03, at2=0.03, de1=0.15, de2=0.3, re1=0.1, re2=0.1)
```

Then we set the ratios. For our trumpet tone we need the first oscillator
to be 1 to 1, and the second to have the modulator 6 times lower.
```python
synth.set_ratios(1, 1.0/6)
```

The last thing we need to do to initialize the synth is set the relative
volume of each oscillator. The second oscillator should quieter than the first.
```python
synth.set_gain(1.0, 0.2)
```

It would be cool if we could play a little melody, so lets create a list of notes
to play.
```python
pitch = 250
notes = [pitch, pitch * 2, (pitch * 3)/2.0, (pitch * 5)/3.0, pitch]
```

We can now iterate through that list, and generate a 0.3s note for
each note in the list.
```python
for note in notes:
    time = 0.0
    nton = 'on'

    synth.update_oscs(note, note * 6)
    modenv1 = ADSR(synth, "mrs_real/Osc1mDepth", dtime=0.15, scale=note * 2.66)
    modenv2 = ADSR(synth, "mrs_real/Osc2mDepth", dtime=0.3,  scale=note * 1.8)
    synth.note_on()
    modenv1.note_on()
    modenv2.note_on()
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
```

The first thing we do is update the frequencies of the oscillators, based on 
our list. Note that the second oscillator is six times higher than the first.
This is done to have better control of the tone in the upper registers of the
trumpet sound. If we were to simply use one oscillator with a higher modulation
index to get more harmonics, it would become hard to predict and control this area
of the sound.
```python
synth.update_oscs(pitch, pitch * 6)
```

The other thing you might have noticed is that we never set the default modulation
index. This is because we are controlling that parameter via an envelope. Therefore
we have to set the modulation amout using the ADSR scale factor.
```python
modenv1 = ADSR(synth, "mrs_real/Osc1mDepth", dtime=0.15, scale=fr1 * 2.66)
modenv2 = ADSR(synth, "mrs_real/Osc2mDepth", dtime=0.3,  scale=fr2 * 1.8)
```

Limitations and improvements
----------------------------

A system could be set up such that the control values of the system are used to map
a input channel of the marsystem to various parameters, such as the modulation index,
pitch, ratio, and any other interesting parameters. This would allow for sample
accurate modulation.

There is also some other issues with the built in FM module. If the mod ratio isn't a whole
number, there will be pops and clicks in the output signal.
