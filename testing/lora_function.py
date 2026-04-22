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
# import keyboard

class LoRa_SPI:
    def __init__(self, bus=0, device=0, baudrate=1000000):
        # Button A
        self.btnA = DigitalInOut(board.D5)
        self.btnA.direction = Direction.INPUT
        self.btnA.pull = Pull.UP

        # Button B
        self.btnB = DigitalInOut(board.D6)
        self.btnB.direction = Direction.INPUT
        self.btnB.pull = Pull.UP

        # Button C
        self.btnC = DigitalInOut(board.D12)
        self.btnC.direction = Direction.INPUT
        self.btnC.pull = Pull.UP

        # Configure RFM9x LoRa Radio
        self.CS = DigitalInOut(board.CE1)
        self.RESET = DigitalInOut(board.D25)
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.RADIO_FREQ_MHZ = 433.0

        # keyboard.add_hotkey('alt+s', print, args=('Howdy',))
        
        self.user_input = ""

        # Attempt to set up the RFM9x Module
        try:
            self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.CS, self.RESET, self.RADIO_FREQ_MHZ, baudrate=baudrate)
            print('RFM9x: Detected')

        except RuntimeError as error:
            # Thrown on version mismatch
            print('RFM9x Error: ', error)

    break_program = False

    # def on_press(self):
    #     print("Press detected\n")
    #     self.user_input = input("Insert a message to send\n")

    # def on_key_press(self, event):
    #     if event.name == 'esc':
    #         keyboard.unhook_all()
    #     else:
    #         print(f"You pressed: {event.name}")

    def run(self):

        self.user_input = ""
        past_time = int(time.time() * 1000)
        cur_time = 0

        # print("press 'alt+s' in order to prompt a message to send\n")

        self.user_input = input("Input 's' to setup as a sender, anything else to only be a reciever\n")
        if self.user_input == "s":
            sending = True
            print(f"The user input of {self.user_input} sets the sending boolean to {sending}")
        else:
            sending = False
            print(f"The user input of {self.user_input} sets the sending boolean to {sending}")
            print(f"Time: [{cur_time}] | Waiting for transmission...")            


        self.user_input = ''
        

        while True:
            # print('loop')
            
            # print("Press a key...")
            # keyboard.on_press_key('s',self.on_key_press)
            # keyboard.wait('esc')

            # Check for received messages
            packet = self.rfm9x.receive()
            if packet is not None:
                rssi = self.rfm9x.last_rssi
                print(f'Received: {packet.decode()} (RSSI: {rssi})')
            # else:
            #     print("Nothing Recieved")

            # Check buttons
            if not self.btnA.value:
                # Button A Pressed
                print('Ada')
                self.send_message(b'Button A')
                time.sleep(0.1)
            if not self.btnB.value:
                # Button B Pressed
                print('Fruit')
                self.send_message(b'Button B')
                time.sleep(0.1)
            if not self.btnC.value:
                # Button C Pressed
                print('Radio')
                self.send_message(b'Button C')
                time.sleep(0.1)
            # time.sleep(0.1)

            cur_time = int(time.time() * 1000)
            if sending and cur_time - past_time >= 2500:
                past_time = int(time.time() * 1000)
                self.user_input = input("Insert a message to send\n")

            elif not sending and cur_time - past_time >= 100000:
                past_time = int(time.time() * 1000)
                print(f"Time: [{cur_time}] | Waiting for transmission...")            

            # if keyboard.is_pressed('s'):
            #     print("press detected")
            #     user_input = input("Insert a message to send\n")
            
            if self.user_input != "":
                # user_input = f"[KC1ZGZ] {user_input}" # Input my callsign
                print(f"Time: [{cur_time}] | Sending message: {self.user_input}")
                input_as_bytes = self.user_input.encode("utf-8")
                self.send_message(input_as_bytes)
                self.user_input = ""
                time.sleep(0.1)
                # print("press 's' in order to prompt a message to send\n")
    
    def send_message(self, message):
        """Send a LoRa message"""
        try:
            self.rfm9x.send(message)
            print(f'Sent: {message.decode()}')
        except Exception as e:
            print(f'Send failed: {e}')

if __name__ == "__main__":
    tran = LoRa_SPI()
    tran.run()

