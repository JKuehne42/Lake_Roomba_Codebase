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

# GPIO.setmode(GPIO.BCM)

# GPIO.setup(16, GPIO.OUT)

# GPIO.setmode(GPIO.BOARD)
# input_pin = 11 # GPIO 17

# For the SPI protocol
# These aren't used, just neat to have
# SCLK = 23 # Clock
# MISO = 21 # Main in, Sub out (NO MASTER!!!!)
# MOSI = 19 # Main out, Sub in
# CEO_N = 24 # Chip Select

# # Start SPI connection
# spi = spidev.SpiDev()
# spi.open(0,0) # (bus, dev) Only 1 bus, we use chip enable 0
# spi.max_speed_hz = 1350000
# spi.mode = 0
# spi.xfer2([0]) # Dummy transfer to start SPI


# GPIO.setup(input_pin, GPIO.IN)
Vcc = 5 #voltage input from rpi
resolution = 2**16 # 16 bit resolution ADC (good quality!)
step_change = Vcc/resolution # Voltage difference between each step

#Tutorial with other ADC
# def analogInput(channel):
#   adc = spi.xfer2([1,(8+channel)<<4,0])
#   data = ((adc[1]&3) << 8) + adc[2]
#   return data


# i = 1
while True:
  sleep(0.5)
  chan0_val = channel_0.voltage # Using channel 0 on the ADC
  print(f"Potentiometer Voltage: {chan0_val}V")

  print(f"Solar panel Voltage: {channel_1.voltage}V")

  print(f"Thermoelectric Voltage: {channel_2.voltage}V")

  print(f"Turbine Voltage: {channel_3.voltage}V\n")
  # print("on during loop ", i)
  # os.system("echo 0 | sudo tee -a /sys/class/leds/led0/brightness")
  # sleep(read_val) # sleep time depending on adc output
  # print("off during loop ", i)
  # os.system("echo 255 | sudo tee -a /sys/class/leds/led0/brightness")
  # sleep(read_val)
  # i += 1
