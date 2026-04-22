import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

pwm_pin = 12 # Pin PWM is controlled on for APISQUEEN ASC
pwm2_pin = 16

GPIO.setup(pwm_pin, GPIO.OUT)
GPIO.setup(pwm2_pin, GPIO.OUT)


# Need 2ms period, so 500Hz
frequency = 500 # in Hz 

pwm12 = GPIO.PWM(pwm_pin, frequency) # Pin and Frequency
pwm16 = GPIO.PWM(pwm2_pin, frequency) # Pin and Frequency


init_duty = 0
user_input = ""

print(f"Initial duty value of {init_duty}%")

pwm12.start(init_duty) # start PWM duty cycle at preset amount
pwm16.start(init_duty) # start PWM duty cycle at preset amount


try: 

    while user_input == "":
        user_input = input("Do you wish to perform manual PWM input? (y/n)")

    if user_input == "y":
        print("Entering manual PWM programming")
        user_input = ""

        while(True):
            while user_input == "":
                user_input = input("Type in desired PWM percentage (0-100), or quit (q)\n")
            try: # Valid number?
                test = float(user_input) <= 100 and float(user_input) >= 0
            except:
                test = False

            if user_input == "q":
                print("Quiting")
                break
            elif test:
                print(f"Setting PWM value to {user_input}%")
                pwm12.ChangeDutyCycle(float(user_input))
                pwm16.ChangeDutyCycle(float(user_input))

            else:
                print(f"Invalid input '{user_input}', try again")
            user_input = ""


    else:
        print("Performing automatic PWM")
        pass


    # time.sleep(1)
    while not user_input == "c":
        user_input = input("Type 'c' to continue: ")
    user_input = ""
    print("Program continued")


    while user_input == "":
        user_input = input("Do you wish to program throttle? (y/n)")

    if user_input == "y":
        user_input = ""
        print("Programming Throttle")
        pwm12.ChangeDutyCycle(100) # program 100% duty cycle as max
        pwm16.ChangeDutyCycle(100) # program 100% duty cycle as max

        while not user_input == "b":
            user_input = input("Type 'b' when 2 beeps heard")
    else: #
        print("Not programming throttle. Continue.")
        pass

    # PWM range is 1ms/50% for full reverse backwards
    # 2ms/100% for full ahead, 1.5ms/75% for stop
    while(True):
        for duty in range(500,1000,1): # 1% -> 100% 
            duty = duty/10 # Divide to reach decimal values using range
            print(f"Duty: {duty}")

            pwm12.ChangeDutyCycle(duty)
            pwm16.ChangeDutyCycle(duty)

            time.sleep(0.001)

        print("Pause 1")
            
        time.sleep(0.5)

        for duty in range(1000,500,-1):
            duty = duty/10
            print(f"Duty: {duty}")

            pwm12.ChangeDutyCycle(duty)
            pwm16.ChangeDutyCycle(duty)

            time.sleep(0.001)

        time.sleep(0.5)

        print("Pause 2")

except KeyboardInterrupt:
    print("\nExiting program.")
    pwm12.stop()  # Stop PWM
    pwm16.stop()  # Stop PWM

    GPIO.cleanup()  # Cleanup all GPIO
