import argparse
import time
import RPi.GPIO as GPIO
import asyncio

class Movement:

    def __init__(self):

        GPIO.setmode(GPIO.BCM)
        try:

            # setup PWM
            pwm_left_pin = 12 # Pin PWM is controlled on for APISQUEEN ASC
            pwm_right_pin = 16
            GPIO.setup(pwm_left_pin, GPIO.OUT)
            GPIO.setup(pwm_right_pin, GPIO.OUT)
            frequency = 500 # in Hz, for a 2ms period
        
            self.pwm_left = GPIO.PWM(pwm_left_pin, frequency)
            self.pwm_right = GPIO.PWM(pwm_right_pin, frequency)
            self.pwm_left.start(0)
            self.pwm_right.start(0)

        except:
            print("pwm already active")


    async def main(self, example_arg=1):
        """
        Main function for lake roomba movement module.
        """

        try:
            self.loop = asyncio.get_running_loop() # Better for running coroutines.
        except:
            print("no running event loop (movement.py)")
            # loop = asyncio.get_event_loop() # get the main event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        # while loop ran in the asyncio thread to check for keyboard interrupt
        # If interrupted, clean up GPIO
        # self.loop.create_task(self.check_for_interrupt())

        print(f"Running lake roomba movement with example_arg: {example_arg}")
    



    def drive(self, linear_velocity, angular_velocity):
        """
        Function to drive the lake roomba.

        Parameters:
        linear_velocity -- desired forward velocity (m/s)
        angular_velocity -- desired angular velocity (rad/s)
        """
        print(f"Driving with velocity {linear_velocity} at angle {angular_velocity} degrees.")
        # TODO calculate desired motor torques

        left_torque = 0
        right_torque = 0
        self.command_motors(left_torque, right_torque)

    def dead_reckon(self, linear_velocity, angular_velocity, duration):
        """
        Function to drive the lake roomba for a specified duration.

        Parameters:
        linear_velocity -- desired forward velocity (m/s)
        angular_velocity -- desired angular velocity (rad/s)
        duration -- time to drive (seconds)
        """
        self.drive(linear_velocity, angular_velocity)
        time.sleep(duration)
        self.stop()
        
    def stop(self):
        """
        Function to stop the lake roomba.
        """
        print("Stopping the lake roomba.")
        self.drive(0, 0)

    def command_motors(self, left_torque, right_torque):
        """
        Function to command the lake roomba's motors directly.

        Parameters:
        left_torque -- torque for the left motor (unit unknown)
        right_torque -- torque for the right motor (unit unknown)
        """
        print(f"Setting left motor torque to {left_torque} and right motor torque to {right_torque}.")
        # TODO connect to motors and set torques

        # TODO convert torques to PWM values
        left_pwm = left_torque
        right_pwm = right_torque

        # PWM bounded from 0-100
        if left_pwm > 100:
            print(f"left_pwm over bounds with a value of {left_pwm}")
            left_pwm = 100
        if right_pwm > 100:
            print(f"right_pwm over bounds with a value of {right_pwm}")
            right_pwm = 100

        self.pwm12.ChangeDutyCycle(left_pwm)


if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Lake Roomba Movement Module')
    parser.add_argument('--example_arg',              default=1,     type=int,    help='example argument. Of no consiquence', metavar='', choices=[0,1,2])

    ARGS = parser.parse_args()

    mov = Movement()

    asyncio.run(mov.main(**vars(ARGS)))