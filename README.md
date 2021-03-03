# QingStation （青站）
A compact weather station.

![](figures/qingstation-render1.png)

## About this project
Before introducing this project, I shall mention my another project **DeepPlankter**.
DeepPlankter is an tiny autonomous water drone ship which could sail in ocean for month using wave-propelled underwater wings.
Sailing alone is fun but if we can collect some meaningful data during the sailing. 

Thus, a weather station is perfect to fit this purpose! 
Imagine that the ship is measuring wind velocity on a 10 metres high wave at the centre of a storm. 

There are some requirements:

- Low-power

The electronics on the ship is supplied by solar panels so is the weather station. 
The solar panels has a peak power rating at 10W. 
However, this 10W will need to supply the main controller, GPS, satellite, rudder servos, and charge batteries for over-nights supplies.

A rough estimation is <100mA average current for the whole ship. 
The weather station should have a maximum 10mA average current. 

- Small & light weight

The drone is small, with deck width at only ~12CM. 
Idealy, the size of the weather station should be less than the deck. 
When install it on the ship, it should be placed as high as possible. 
Heavy weight will decrease the stability of the ship. 

- Versatile

Today's digital sensors are easy to use. 
We can implements as muchs as possible as long as we got space on the PCB. 

## Features and functions

For the hardware V1.1

**Features**: 
- MCU: STM32L476
- PCB dimension: Φ48 mm
- SDCard
- RTC

**Sensor Integration**:
- Anemometer (2x2 Ultrasonic transducer array 40k/200kHz)
- Rain sensor (IR Optical type)
- Lighting sensor (AS3935)
- IMU & eCampass (BMX160)
- RGBI light sensor (APDS-9250)
- Barometer, humidity, temperature sensor (BME280)

**Communication Interfaces**:
- 2x UART
- I2C
- SPI
- CAN (FDCAN)
- USB (CDC or MassStorage)

### Functions descripton

Todays digital sensors are easy to use, configure each sensor and they were all up in a short time. 

For lighting sensor (AS3935), I could not make a easy test to validate my antenna design. 

For RGBI sensor, we cannot calibrate the sensor using cosine corrector which light sensor usually used. 
I have no tools that can calibrate this sensor. 
RGBI sensor can provide colour data than a single lumen meter. 
Hopefully it will not saturated in direct sunlight.  
Otherwise i need to install a gray lens to lower the light stength. 
  
IMU and eCampass is not needed for a stationary mount weather station. 
But in sailing, its high mounted location is perfect for navigation where less inferences than in the hull (the ship's main controller). 

An additional small size GPS module can be connected to one of the UART, 
to provide clock calibration even we do not the location in stationary mount. 
It is much helpful when sailing, to provide a secondary GPS location.

The rain sensor is consist of a pair of a IR transmitter and a receiver. 
The method is to use the reflection of a piece of trapezoid glass (hand made..). 
When rain drop on the surfaces of glass, it will reduce the reflection, therefore the signal magnitude on the reciever will change.
We can either use calibrated absolute value or use the covariance. 
This sensor will not be accurate. Even when on the sea, droplets from large waves can easily keep the sensor wet all the time.  






