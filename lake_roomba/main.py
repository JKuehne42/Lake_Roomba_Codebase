#!/usr/bin/python
# Main file to run all functions of the Lake Roomba robot
import sys

# Import child files
import mapping
import travel
import movement
import connect_to_base
import communicate
import collect_algae

import argparse
import asyncio

import RPi.GPIO as GPIO

import time

class Control:

    def __init__(self):

        try:
            self.loop = asyncio.get_running_loop() # Better for running coroutines.
        except:
            print("no running event loop (main.py)")
            # loop = asyncio.get_event_loop() # get the main event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        
        
        # initialise classes
        self.map_object = mapping.Map()
        self.com_object = communicate.Communication()
        self.mov_object = movement.Movement()
        self.trav_object = travel.Travel(self.mov_object, self.map_object)
        #TODO setup rest of files and initialise



    async def main(self):
        try:
            async with asyncio.TaskGroup() as tg:
                # Run main function async loops
                t1 = tg.create_task(self.map_object.main())
                t2 = tg.create_task(self.com_object.main())
                t3 = tg.create_task(self.mov_object.main())
                t4 = tg.create_task(self.trav_object.main())
                t5 = tg.create_task(self.output_pos_data())

        except asyncio.CancelledError:
            print("Asyncio Stopped")
            GPIO.cleanup()
            self.mov_object.pwm12.stop()

        self.loop.run_forever() # run the read loop forever non-blocking


    async def output_pos_data(self):
        while True:
            # print(f"main.py initial gps data: {self.map_object.initial_gps_data}")
            # print(f"main.py gps data: {self.map_object.gps_data}")
            # print(f"main.py imu data: {self.map_object.imu_data}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Lake Roomba Communication Module')
    # parser.add_argument('--message',              default="no_message",     type=str,    help='message to send through LoRa communication module', metavar='') 

    ARGS = parser.parse_args()

    # Run code
    com = Control()

    asyncio.run(com.main())

    # com.write_lora(**vars(ARGS))
