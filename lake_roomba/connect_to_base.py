import argparse
import movement

class Connect:

    def __init__(self):

        self.mov = movement.Movement()

    def main(self, example_arg=1):
        """
        Main function for lake roomba base connection module.
        """
        print(f"Running lake roomba base connection with example_arg: {example_arg}")


    def calc_align(self):
        """
        Calculate the alignment error with respect to the base station.

        Returns:
        alignment_error -- the calculated alignment error
        distance_to_base -- estimated distance to the base station (meters)
        """
        april_tag_positions = []
        # TODO read april tag positions
        # Once all 4 are read
        while len(april_tag_positions) < 4:
            # turn until all 4 tags are visible
            self.mov.drive(0, 0.2)  # turn in place at angular velocity 0.2 rad/s
            # TODO update april_tag_positions

        # TODO calculate alignment error based on tag positions
        # calculate average position of tags along the horizontal axis
        alignment_error = 0 

        # TODO calculate distance to base using known tag size and camera parameters
        distance_to_base = 0

        return alignment_error, distance_to_base

        # Should I return error here and use it in the drive function combined with approach?

    def approach(self):
        """
        Approach the base station.
        """

        [alignment_error, distance] = self.calc_align()

        while abs(alignment_error) > 0.05 and distance > 0.05:  # threshold for alignment error
            # TODO implement PID controller for alignment
            kp = 1.0  # proportional gain
            kd = 0.1  # derivative gain
            ki = 0.0  # integral gain


            lin_vel = 0.5 # example
            ang_vel = 0.1 # example
            self.mov.drive(lin_vel, ang_vel)


    def connect(self):
        """
        Connect to the base station.
        """
        print("Connecting to base station.")
        # TODO implement connection mechanism


    def transfer(self):
        """
        Transfer algae to the base station.
        """
        print("Transferring algae to base station.")
        # TODO implement transfer mechanism


    def disconnect(self):
        """
        Disconnect from the base station.
        """
        print("Disconnecting from base station.")
        # TODO implement disconnection mechanism

    def leave(self):
        """
        Leave the base station area.
        """
        # Drive backward a small distance
        # Get the april tags in view
        self.mov.dead_reckon(-0.05, 0, 5)  
        alignment_error, distance = self.calc_align()

        while distance < 1.0:  # threshold distance to consider "left" the base area
            # Adjust heading to move away from base
            kp = 1.0  # proportional gain
            kd = 0.1  # derivative gain
            ki = 0.0  # integral gain

            lin_vel = -0.5 # example
            ang_vel = 0.0 # example
            self.mov.drive(lin_vel, ang_vel)

            alignment_error, distance = self.calc_align()



        print("Leaving base station area.")
        self.mov.stop()


if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Lake Roomba Base Connection Module')
    parser.add_argument('--example_arg',              default=1,     type=int,    help='example argument. Of no consiquence', metavar='', choices=[0,1,2])

    ARGS = parser.parse_args()

    con = Connect()

    con.main(**vars(ARGS))