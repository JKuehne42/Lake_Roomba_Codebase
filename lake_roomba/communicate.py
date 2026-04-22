import argparse
import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
# import adafruit_ssd1306
# Import the RFM9x radio module.
import adafruit_rfm9x
import sys
import spidev
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

class Communication:

    def __init__(self, bus=0, device=0, baudrate=1000000):

        # Configure RFM9x LoRa Radio
        self.CS = DigitalInOut(board.CE1) # CE1 on RPi
        self.RESET = DigitalInOut(board.D25)
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # connect RPi to transciever using the SPI protocol
        self.RADIO_FREQ_MHZ = 433.0 # 433 MHz signal frequency. Approximate legal limit.

        # Initialise parameters for non-blocking read function
        self.data = ""
        self.rssi = ""

        # Attempt to set up the RFM9x Module
        try:
            self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.CS, self.RESET, self.RADIO_FREQ_MHZ, baudrate=baudrate)
            print('RFM9x: Detected')

        except RuntimeError as error:
            # Thrown on version mismatch
            print('RFM9x Error: ', error)
        
        self.executor = ThreadPoolExecutor(10)

    async def main(self):
        # For calling from another file    

        try:
            self.loop = asyncio.get_running_loop() # Better for running coroutines.
        except:
            print("no running event loop (communicate.py)")
            # loop = asyncio.get_event_loop() # get the main event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        # thread = threading.Thread(target=self.run_in_thread, args=(loop,)) # Create a thread that runs the coroutine, pass the loop 

        # thread.start() # Start the thread

        self.loop.create_task(self.process(self.loop))

    def run_in_thread(self, loop):
        future = asyncio.run_coroutine_threadsafe(self.process(loop), loop)

    async def process(self, loop):
        """
        run function for lake roomba communication module.
        For now, we're just going to continually read asynchronously
        """
        print("in process")

        while True:
            recieved = await loop.run_in_executor(self.executor, self.read_lora) # read data from module

            if recieved: # If there's data to process
                print(f'Processed: {self.data} (RSSI: {self.rssi})')
                # Do whatever must be done here. TBD depending on commands needed

                # Call respective other programs, return said data/messages, etc.

            await asyncio.sleep(0.01) # async wait to not overcrowd requests

        # return recieved # return recieved data for testing

    def read_lora(self):
        """
        Function to read data from LoRa communication module.
        """
        # print("Reading data from LoRa module.")

        packet = self.rfm9x.receive()

        if packet is not None:
            rssi = self.rfm9x.last_rssi
            data = packet.decode()
            print(f'Received: {data} (RSSI: {rssi})')
            self.data = data
            self.rssi = rssi
            return True


        else:
            # print("Nothing Recieved")
            return False # Return false to indicate that there's no output data

    async def write_lora(self, message):
        """
        Function to write data to LoRa communication module.

        Parameters:
        message -- data to be sent via LoRa
        """

        if message ==("no_message" or None):
            print("No valid message included")
        
        else:
            print(f"Writing data to LoRa module: {message}")

            byte_mes = message.encode("utf-8") # convert string to bytes
            try:
                # self.rfm9x.send(byte_mes)
                print(f'Sent: {message}')
            except Exception as e:
                print(f'Send failed: {e}')

        await asyncio.sleep(0.1) # async wait to not overcrowd requests


if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Lake Roomba Communication Module')
    parser.add_argument('--message',              default="no_message",     type=str,    help='message to send through LoRa communication module', metavar='') 

    ARGS = parser.parse_args()

    # Run code
    com = Communication()

    # com.write_lora(**vars(ARGS))

    try:
        loop = asyncio.get_running_loop() # Better for running coroutines. Will likely be used in practice
    except:
        print("no running event loop (communicate.py)")
        # loop = asyncio.get_event_loop() # get the main event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(com.process(loop))

    loop.run_forever()
