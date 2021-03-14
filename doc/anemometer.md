# Anemometer Design and Practice

This documentation is dedicated to the ultrasonic anemometer design and tuning. 

# Introduction
Anemometer is the most interesting sensor on QingStation. 
However, it is also very challenging for me since I got almost no experience 
(I don't even know how to use OP AMP at the beginning).

A very good blog I learnt from time to time is this one [Anemometer by Hardy Lau](https://www.dl1glh.de/ultrasonic-anemometer.html#advancement) 
This log is very informative and already cover most of the knowledge needed to build your own ultrasonic anemometer. 

The principle in short: the wind speed is measured by the time that the ultrasonic waves (pules) propagate forward and backwards 
between a pair of transducers. 
With 2 pairs of transducer placed perpendicular in horizontal, the wind direction can also be calculated by using trigonometry.

The advantage of ultrasonic anemometer compared to other types
- The spinning type (cup anemometer) is much larger.
- Reasonable easy and cheap to DIY, good instruction by Hardy. 
- No moving parts! Moving parts are not very easy to DIY especially when waterproofing. 

# Methods

## Basic Principle




## Practical Issues, Solution and Compromise
In reality, things normally don't work as we want, especially analog circuits. 

Here is the schematic of the second version(PCB v1.1), details will be explained in the following sections.
![](figures/anemometer-sch.png)

### Ultrasonic Transducer, Driver 

#### Transducers
I brought a few different parts for the test.
- A `40kHz` `10mm` waterproof(P/N: EU10AIF40H07T/R)
- A `200kHz` `10mm` waterproof(P/N: EU10PIF200H07T/R)
- A `40kHz` `16mm` waterproof (P/N: NU40A16TR-1)
- A few HC-SR04 type open-end transducer. None-waterproof. 

The three with part number have similar parameters. 

Transmition sound pressure `10V(0dB=0.02mPa) ≥106dB`
Receive sensitive at `40KHz (0dB=V/ubar)：≥-75dB`
Capacitive are all at a few `nF` depended on their diameter. 

I did not test the HC-SR04 because they are much larger than the `10mm` one. 

The final decision is the first one, `40kHz 10mm` waterproof(P/N: EU10AIF40H07T/R).
The size is small, which helps to reduce the overall assembly size. 
It is inexpensive compared to the `200k` (4 times the cost). 
High frequency can bring shorter pulse but thoes `40KHz` already good enough. 
It has a good spreading directivity(less than `-3dB @ 30degree`), which means that I didn't need to fix it at an angle to the plate.
Everythings lay down will be a big plus to mechanical design and assembly.

Frequency
> Ideally, the pulses should as short as possible.
> We normally send 3~4 pulses.
>
> `f=40k, λ=8.4mm` pulse width `33mm` 
> 
> `f=200k, λ=1.68mm` pulse width `6.72mm` 
>
> Both are smaller than the Height (`5cm`). 
> Shorter wavelenght always better, however, signal signal also degrade faster through propagation.


The only concern left is whether the signal pules is short enough 
to avoid mix signal between the direct sound (we don't want) and reflective sound (we need). 

I didn't consider muRata `MA40E8-2` which was used in Lau's blog because it has been discontinued and it was more expensive anyway. 

#### Driver Design
Driver design is a tricky part. A lot of pain here. 

For size and low-power consideration, I did not use a conventional driver + transformer to drive the transducer. 
Instead, like the old-style HC-SR04, I use RS-232 interface drivers to generate `-5.5V` to `+5.5V` square wave. 
It should more or less provide `10Vpp` range. 
Those 3V variances run on a 3V power supply so all  can run on the same power rail. 

These RS-232 chips have many alternatives, the driving capability is good enough (a few kohm and a few nF in parallel) for the transducers. 
The one used here is MAX3232/3222, it provides a shutdown pin that can save power compared to more often used MAX3232. 
These chips are low-cost and in a small package. 

However, this decision introduced a huge interference issue.

The MAX3222 drive the transducer through a `1uF` capacitor from one of its output channel. 
One the receiver (transducer) side using a set of clamp diodes and resistors will ensure the signal won't travel back to the driver side. 
Also, the diodes should block any noise that comes from the MAX3232. But it doesn't.

Because the MAX3232/3222 are generating negative and positive driving voltage based on charge pump method, 
it is impossible to get a smooth output voltage. 

The signal on the capacitor looks like this:

![](max3232_driver_noise.jpg)

Although after the clamp diode, the noise is "negligible" even my oscilloscope cannot detect, but somethings still pass there. 
Which results in a distortion of the receiving wave.  

Here is the wave without connecting transducer, when connected, the noise will be lower but still exist. 
The same channel means the driver (MAX3232) connected directly to the receiver. 
Cross channel means from the other MAX3232 by power or other unknown sources.
![](figures/anemometer_noise.png)

The below shows an actual signal distorted by the noise from the driver side. 
The cross channel distortion is negligible, but the same channel distortion definitely affects the shape of the beam. 
Notice that the signal shown here was collect before I glue the transducer to the frame, results in a much larger amplitude.
When the transducers were glue to the frame, the distortion effect much more. 

![](figures/anemometer_signal_distorsion.png)

I tried many methods including adding capacity to the MAX3232 charge-pump capacitors. 
This helps to reduce the ripple frequency from `6.6kHz` to `~3kHz`. 

Later I found the trigger of the charging pump is very simple, once the voltage reaches a recharge threshold, it switches.
Very much like a DC/DC converter with PDM mode, low-power, but higher noise. This kind of noise cannot be eliminated.

In the first PCB (v1.0), I cannot eliminate this noise with MAX3232 because both MAX3232's power is controlled by one P-MOS.
So I designed a second PCB (v1.1) using MAX3222 which can be placed into a shutdown mode thus to stop the charge-pump. 
Hopefully, it can eliminate the issues. 


### Echo Signal and Amplifier

(I rarely touch analog circuit since forever, this definitely does not help)

The echo signal first passes through a `4.7k` resistor then a `100nF` capacitor to block DC signal. 
Then, it passes through a analog switch (4052, Low Voltage variance), before it finally reaches the amplifier. 

Since we use a single rail power supply, the 4052 does not allow negative voltage signal to pass.
Instead, we will charge the `100nF` capacitor to the virtual ground (`1/2 Vreff`) 
before we start to send the pulses and collect measurement. 

#### Amplifiers

In the amplifier, I use the most common LMV358 dual OP AMP. 

In PCB v1.0, only a single-stage amplifier is used to amplify the echo, 
while the other one is used for generating a low impedance virtual ground. 

The OP AMP was only set to `10x`, which I cannot even see the signal in my ADC data. 
Overestimated the signal strength.
I later changed the gain to `~200x` to be able to record a clear signal. 
However, the signal reading ranges is still too small (around `100 digits/pp` in a `12bit, 4096` ADC). 

Later, until I accidently saw on tutorial on YouTube [Basics of Op Amp Gain Bandwidth Product and Slew Rate Limit](https://youtu.be/UooUGC7tNRg)
then I realized what was wrong here. The bandwidth of LMV358 (as well as all other op amps) list in datasheet is "Unit Gain" also equal to "Gain–Bandwidth Product" 
which does not cover the full frequency range. 
LMV358 will only have around maximum `1MHz/40kHz = 25x` gain no matter how much I set.  
What make things worst is I added a capacitor on the feedback loop for a RC filter.
Now I see why I could not see a signal at the beginning, the final bandwidth is too small filtered out all signals. 

Unfortunately, by the time I learnt the GBP parameter, PCB V1.1 fabrication and assembly are already finished and on its long way to me. 
In PCB v1.1, the 2 OP AMPs are all used to amplify the echo. 
The first stage was set to low impedance. 
The 2 stages OP AMPs also allow higher total gains while still let the `40KHz` signal pass. 
The virtual ground is now provided by a voltage divider and a large capacitor. 
The new circuit looks good . 
However, in this circuit, we still cannot test `200KHz` transducer, 
unless I change to a high bandwidth OP AMP and drop plenty of my LMV358 brought earlier.


#### The noise from the driver

I think the small capacitor in the clamp diodes let the driver's noise passed to the receiver side. 
This is also approved in a simulation circuit built using EasyEDA.
With clean power, I can still see small amplitude noise pass through. 
The 1N4148 cannot block the noise from the driver side completely. 
That is why I change the MAX3232 to MAX3222, the receiver's charge pump has to stop. 


### Signal Processing

#### ADC Setting 

ADC is configured to `1MHz`. I did not configure it to higher because it is not necessary.
- LMV358 only have `1MHz` GBP.
- Sub resolution accuracy can be achieved by linear interpolation (details in signal processing section). 

At each burst, the ADC sample for `1ms` exactly `1000` samples. 
It is enough for Height in range of 4CM to 10CM

When does the first echo arrive?
> Assemue Height(H)=`5cm`, Pitch(D)=`4cm`, Sound speed(C)=`336m/s`
>
> The distance that the sound travel is `S = sqrt((D/2)^2 + H^2) * 2 = 10.7cm`. 
>
> The first pulse arrives at around `t = 0.107 / 336 = 318us` after pulses sent when the wind is claim. 
> Even when H=`10cm` t=`588us`. 1000 samples is more than enough.

#### Preprocess
ADC to Float. Filter. Zeroing. 

#### Echo Pulse

#### Pulse Compression
See if needed. take times to calculate. 

#### Zero-Crossing Detection

#### Extracting Wind Speed

## Calibration






