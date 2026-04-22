import spidev
import time
import struct

class ICM20948_SPI:
    def __init__(self, bus=0, device=0, speed=1000000):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = speed
        self.spi.mode = 0b11  # SPI mode 3
        self.spi.lsbfirst = False
        
        # ICM-20948 Register addresses
        self.REG_BANK_SEL = 0x7F
        self.REG_WHO_AM_I = 0x00
        self.REG_PWR_MGMT_1 = 0x06
        self.REG_ACCEL_XOUT_H = 0x2D
        self.REG_GYRO_XOUT_H = 0x33
        
    def write_register(self, reg, data, bank=0):
        """Write to a register with bank selection"""
        # Set bank if needed
        if bank != 0:
            self.spi.xfer2([self.REG_BANK_SEL & 0x7F, bank << 4])
        
        # Write to register (clear MSB for write)
        self.spi.xfer2([reg & 0x7F, data])
        
        # Return to bank 0
        if bank != 0:
            self.spi.xfer2([self.REG_BANK_SEL & 0x7F, 0x00])
    
    def read_register(self, reg, length=1, bank=0):
        """Read from register with bank selection"""
        # Set bank if needed
        if bank != 0:
            self.spi.xfer2([self.REG_BANK_SEL & 0x7F, bank << 4])
        
        # Read from register (set MSB for read)
        tx_data = [reg | 0x80] + [0x00] * length
        rx_data = self.spi.xfer2(tx_data)
        
        # Return to bank 0
        if bank != 0:
            self.spi.xfer2([self.REG_BANK_SEL & 0x7F, 0x00])
            
        return rx_data[1:]  # Skip first byte (dummy)
    
    def initialize(self):
        """Initialize the ICM-20948"""
        try:
            # Check WHO_AM_I
            whoami = self.read_register(self.REG_WHO_AM_I)[0]
            print(f"WHO_AM_I: 0x{whoami:02X}")
            if whoami != 0xEA:
                print("ICM-20948 not found!")
                return False
            
            # Wake up device
            self.write_register(self.REG_PWR_MGMT_1, 0x01)
            
            # Configure accelerometer and gyroscope
            # Accel: ±8g, Gyro: ±1000dps
            self.write_register(0x00, 0x08, bank=2)  # GYRO_CONFIG_1
            self.write_register(0x14, 0x08, bank=2)  # ACCEL_CONFIG_1
            
            print("ICM-20948 initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    def read_accelerometer(self):
        """Read accelerometer data"""
        data = self.read_register(self.REG_ACCEL_XOUT_H, 6)
        
        # Convert to signed 16-bit values
        accel_x = struct.unpack('>h', bytes(data[0:2]))[0]
        accel_y = struct.unpack('>h', bytes(data[2:4]))[0]
        accel_z = struct.unpack('>h', bytes(data[4:6]))[0]
        
        # Convert to g (assuming ±8g range)
        scale = 4096.0  # 8g range = 4096 LSB/g
        return [accel_x / scale, accel_y / scale, accel_z / scale]
    
    def read_gyroscope(self):
        """Read gyroscope data"""
        data = self.read_register(self.REG_GYRO_XOUT_H, 6)
        
        # Convert to signed 16-bit values
        gyro_x = struct.unpack('>h', bytes(data[0:2]))[0]
        gyro_y = struct.unpack('>h', bytes(data[2:4]))[0]
        gyro_z = struct.unpack('>h', bytes(data[4:6]))[0]
        
        # Convert to dps (assuming ±1000dps range)
        scale = 32.8  # 1000dps range = 32.8 LSB/dps
        return [gyro_x / scale, gyro_y / scale, gyro_z / scale]
    
    def read_magnetometer(self):
        """Read magnetometer data (AK09916)"""
        # Enable I2C master and configure magnetometer
        self.write_register(0x03, 0x08, bank=0)  # Enable I2C master
        self.write_register(0x07, 0x01, bank=3)  # Configure I2C master
        
        # Read magnetometer via I2C master
        # This is more complex - see full implementation below
        
        return [0, 0, 0]  # Placeholder

# Main program
if __name__ == "__main__":
    imu = ICM20948_SPI()
    
    if imu.initialize():
        try:
            while True:
                accel = imu.read_accelerometer()
                gyro = imu.read_gyroscope()
                
                print(f"Accel: X:{accel[0]:.2f} Y:{accel[1]:.2f} Z:{accel[2]:.2f} g")
                print(f"Gyro:  X:{gyro[0]:.2f} Y:{gyro[1]:.2f} Z:{gyro[2]:.2f} dps")
                print("-" * 40)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        print("Failed to initialize ICM-20948")
