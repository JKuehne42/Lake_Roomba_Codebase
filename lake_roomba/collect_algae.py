import argparse
import movement 

class Collect:

    def __init__(self):
        self.mov = movement.Movement()

    def main(example_arg=1):
        """
        Main function for lake roomba algae collection module.
        """
        print(f"Running lake roomba algae collection with example_arg: {example_arg}")


    def cover_area(shape="circle", size=10):
        """
        Function to cover area for algae collection.
        """
        if shape == "circle":
            print(f"Covering a circular area with diameter {size}.")

        if shape == "square":
            print(f"Covering a square area with side length {size}.")



if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Lake Roomba Algae Collection Module')
    parser.add_argument('--example_arg',              default=1,     type=int,    help='example argument. Of no consiquence', metavar='', choices=[0,1,2])

    ARGS = parser.parse_args()

    col = Collect()

    col.main(**vars(ARGS))