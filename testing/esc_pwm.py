import RPi.GPIO as GPIO
import time
import pigpio

pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)
# setup PWM
pwm_left_pin = 12 # Pin PWM is controlled on for APISQUEEN ASC
pwm_right_pin = 16
# GPIO.setup(pwm_left_pin, GPIO.OUT)
# GPIO.setup(pwm_right_pin, GPIO.OUT)
# frequency = 500 # in Hz, for a 2ms period
user_input = ""

# pwm_left = GPIO.PWM(pwm_left_pin, frequency)
# pwm_right = GPIO.PWM(pwm_right_pin, frequency)
# pwm_left.start(0)
# pwm_right.start(0)
# Use hardware PWM via pigpio for accurate microsecond pulse widths
# pip install pigpio, then sudo pigpiod


def set_pulse_us(pin, us):
    """Set PWM pulse width in microseconds."""
    pi.set_servo_pulsewidth(pin, us)
    
# Standard ESC pulse widths:
# 1000us = full reverse / min throttle
# 1500us = neutral / stop  
# 2000us = full forward / max throttle

while user_input == "":
    user_input = input("Do you wish to perform manual PWM input? (y/n)")

if user_input == "y":
    print("Entering manual PWM pulse programming")
    user_input = ""

    while(True):
        while user_input == "":
            user_input = input("Type in desired PWM pulse width in ms (500-2000), or quit (q)\n")
        try: # Valid number?
            test = float(user_input) <= 2500 and float(user_input) >= 0
        except:
            test = False

        if user_input == "q":
            print("Quiting")
            break
        elif test:
            print(f"Setting PWM value to {user_input}")
            # pwm_left.ChangeDutyCycle(float(user_input))
            # pwm_right.ChangeDutyCycle(float(user_input))
            set_pulse_us(pwm_left_pin, int(float(user_input)))  
            set_pulse_us(pwm_right_pin, int(float(user_input)))  

        else:
            print(f"Invalid input '{user_input}', try again")
        user_input = ""


else:
    print("Performing automatic PWM")
    print("Step 1: Sending full throttle — NOW power on the ESC")
    set_pulse_us(pwm_left_pin, 2000)
    set_pulse_us(pwm_right_pin, 2000)
    input("Press Enter once you have powered on the ESC...")
    time.sleep(3)  # wait for startup beeps after power-on

    print("Step 2: Drop to neutral to confirm max endpoint")
    set_pulse_us(pwm_left_pin, 1500)
    set_pulse_us(pwm_right_pin, 1500)
    time.sleep(2)

    print("Step 3: Drop to min to confirm min endpoint")
    set_pulse_us(pwm_left_pin, 1000)
    set_pulse_us(pwm_right_pin, 1000)
    time.sleep(2)
    # ESC should now beep to confirm calibration and enter programming mode

    print("Step 4: Cycling to bidirectional (parameter 1)")
    # Brief full-throttle pulse to advance the parameter selection
    set_pulse_us(pwm_left_pin, 2000)
    set_pulse_us(pwm_right_pin, 2000)
    time.sleep(0.5)

    set_pulse_us(pwm_left_pin, 1500)
    set_pulse_us(pwm_right_pin, 1500)
    time.sleep(3)  # confirm tone
