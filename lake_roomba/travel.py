import argparse
import movement
import mapping

import asyncio

class Travel:

    def __init__(self, mov_obj, map_obj):
        # take in initialised classes from main
        self.mov_obj = mov_obj
        self.map_obj = map_obj


    async def main(self, example_arg=1):
        """
        Main function for lake roomba algae collection module.
        """
        try:
            self.loop = asyncio.get_running_loop() # Better for running coroutines.
        except:
            print("no running event loop (travel.py)")
            # loop = asyncio.get_event_loop() # get the main event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        print(f"Running lake roomba algae collection with example_arg: {example_arg}")
        

    def make_path(self, des_pos):
        """
        Make a path from the current position to a desired position
        
        Arguments:
        des_pos -- array of [x, y]
        """
        # find current position using mapping.py
        # consider the desired position and path there
        # for simplicity purposes at this point, no path planning just a straight line

        cur_pos = [0, 0] # filler

        
        self.mov_obj.stop()

    def follow_path(self, path):
        """
        Follow the path given by makee_path() using PID control
        and potentially quintic trajectory creation. Nope.
        """


if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Lake Roomba Algae Collection Module')
    parser.add_argument('--example_arg',              default=1,     type=int,    help='example argument. Of no consiquence', metavar='', choices=[0,1,2])

    ARGS = parser.parse_args()
    mov_obj = movement.Movement()
    map_obj = mapping.Map()

    trav = Travel(mov_obj, map_obj)

    trav.main(**vars(ARGS))