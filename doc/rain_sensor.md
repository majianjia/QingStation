# Rain Sensor

This document records the development of the optical rain sensor on QingStation.

## Principle

Here we are building a Infrared Optical Rain Sensor, which is common in today's car automotive windshield wiper. 
The below diagram from wiki shows the principle of these type of rain sensor.

![Rain_sensor diagram from wikipedia](figures/Rain_sensor_en.svg)

When the glass is dry, the IR travels through will be totally reflected between top and bottom of the `2` pices of glasses. 
When there are rain drops on the glass, the IR light will not be totally reflected, so the light intensity will decrease. 
We can then use a photodiode to measure the intensity of light to read the rain. 

There a few strategies can convert the measurement to rain level. 
- Count how many drops (changes of measurement) in a time. 
- Calculate the variance of continuous measurement. 

Since our sensor is small, it is expected that the "accuracy" will be low especially in small rain. 

## Design and Practice

![rainsensor_diagram](figures/rainsensor_diagram.png)

The optical part is the most difficult part for the rain sensor. 
I did not even try to use real glasses.
The materials I selected is polycarbonate (PC), a clear and UV resistance plastic materials. 
It has better physical mechanical properties than acrylic, but only a bit more expensive. 

The optical part is assembled by `2` pieces of PC sheet. 
The top one is flat with right angle on all the side. 
The bottom one is smaller with 2 short sides in a `45` degree angle. 
Both PC sheets are glued together by clear epoxy.