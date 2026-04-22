#!/usr/bin/python

import RPi.GPIO as GPIO
from time import sleep

import os

# GPIO.setmode(GPIO.BCM)

# GPIO.setup(16, GPIO.OUT)
i = 1
while i < 20:
  # print(i)
  # GPIO.output(16, GPIO.HIGH)
  # sleep(0.5)
  # GPIO.output(16, GPIO.LOW)
  # sleep(0.5)
  # i += 1
  print("on during loop ", i)
  os.system("echo 0 | sudo tee -a /sys/class/leds/led1/brightness")
  sleep(0.5)
  print("off during loop ", i)
  os.system("echo 255 | sudo tee -a /sys/class/leds/led1/brightness")
  sleep(0.5)
  i += 1
