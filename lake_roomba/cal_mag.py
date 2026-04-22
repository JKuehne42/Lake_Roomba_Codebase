# data_collector.py
import time
import csv
import board
import adafruit_icm20x
import os
directory_of_python_script = os.path.dirname(os.path.abspath(__file__))
# Initialize I2C and sensor
i2c = board.I2C() 
try:
    icm = adafruit_icm20x.ICM20948(i2c)
except:
    print("ERROR: IMU not recognized")
    exit()

print("Starting data collection. Rotate the sensor slowly in all directions...")
print("Press Ctrl+C to stop.")

# Create/open a CSV file to store the data
with open(os.path.join(directory_of_python_script, "mag_data.csv"), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write a header
    writer.writerow(['x', 'y', 'z']) 

    try:
        while True:
            # Get raw magnetometer data (in microteslas, uT)
            mag_x, mag_y, mag_z = icm.magnetic
            # Write to CSV
            writer.writerow([mag_x, mag_y, mag_z])
            
            # Small delay to control data rate
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nData collection stopped.")