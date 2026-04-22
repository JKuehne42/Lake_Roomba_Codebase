#!/usr/bin/python

# Lets blink the light using an ADC connected to a potentiometer
# Change the blinking speed on boot measuring the potentiometer value
# This is to verify ADC functionality with no terminal output

import RPi.GPIO as GPIO
from time import sleep
# import spidev # To communicate with SPI devices
from numpy import interp # To scale values
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import os
import board

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
channel_0 = AnalogIn(ads, 0)
channel_1 = AnalogIn(ads, 1)
channel_2 = AnalogIn(ads, 2)
channel_3 = AnalogIn(ads, 3)

# GPIO.setup(input_pin, GPIO.IN)
Vcc = 5 #voltage input from rpi
resolution = 2**16 # 16 bit resolution ADC (good quality!)
step_change = Vcc/resolution # Voltage difference between each step

# i = 1
while True:
  sleep(0.5)
  print(f"A0 voltage: {channel_0.voltage}V")

  print(f"A1 voltage: {channel_1.voltage}V")

  print(f"A2 voltage: {channel_2.voltage}V")

  print(f"A3 voltage: {channel_3.voltage}V")

  print(f"A0-A1 current: {(chan0_val - channel_1.voltage)/10.2}A") # Using Ohms law and our 10.2 ohm resistor
  
  print(f"A2-A3 current: {(chan2_val - channel_3.voltage)/10.2}A\n") # Using Ohms law and our 10.1 ohm resistor


