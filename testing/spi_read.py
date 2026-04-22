import spidev
import time
import struct

class ICM20948_Full:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 7000000  # 7MHz max for ICM-20948
        self.spi.mode = 0b11
        
        # Magnetometer (AK09916) I2C address
        self.AK09916_ADDR = 0x0C
        self.AK09916_WHO_AM_I = 0x48
        
    def i2c_master_write(self, addr, reg, data):
        """Write to I2C slave via SPI"""
        # I2C master single write
        self.write_register(0x30, 0x02, bank=3)  # I2C_MST_EN = 1
        self.write_register(0x24, 0x0C, bank=0)  # I2C_MST_CTRL
        
        # Set slave address and register
        self.write_register(0x25, addr << 1, bank=3)  # I2C_SLV0_ADDR (write)
        self.write_register(0x26, reg, bank=3)        # I2C_SLV0_REG
        self.write_register(0x27, 0x81, bank=3)       # I2C_SLV0_CTRL (enable + length=1)
        self.write_register(0x63, data, bank=3)       # I2C_SLV0_DO
        
        time.sleep(0.01)
        
    def i2c_master_read(self, addr, reg, length):
        """Read from I2C slave via SPI"""
        # I2C master single read
        self.write_register(0x30, 0x02, bank=3)  # I2C_MST_EN = 1
        self.write_register(0x24, 0x0C, bank=0)  # I2C_MST_CTRL
        
        # Set slave address and register
        self.write_register(0x25, (addr << 1) | 0x01, bank=3)  # I2C_SLV0_ADDR (read)
        self.write_register(0x26, reg, bank=3)                 # I2C_SLV0_REG
        self.write_register(0x27, 0x80 | length, bank=3)       # I2C_SLV0_CTRL (enable + length)
        
        time.sleep(0.01)
        
        # Read data from EXT_SENS_DATA_00
        return self.read_register(0x3B, length, bank=0)
    
    def initialize_magnetometer(self):
        """Initialize the AK09916 magnetometer"""
        try:
            # Check WHO_AM_I
            whoami = self.i2c_master_read(self.AK09916_ADDR, 0x01, 1)[0]
            print(f"AK09916 WHO_AM_I: 0x{whoami:02X}")
            
            if whoami != self.AK09916_WHO_AM_I:
                print("AK09916 magnetometer not found!")
                return False
            
            # Reset magnetometer
            self.i2c_master_write(self.AK09916_ADDR, 0x32, 0x01)
            time.sleep(0.1)
            
            # Set continuous mode 4 (100Hz)
            self.i2c_master_write(self.AK09916_ADDR, 0x31, 0x08)
            
            print("Magnetometer initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Magnetometer initialization failed: {e}")
            return False
    
    def read_magnetometer(self):
        """Read magnetometer data"""
        try:
            # Check data ready
            status = self.i2c_master_read(self.AK09916_ADDR, 0x18, 1)[0]
            
            if status & 0x01:  # Data ready
                data = self.i2c_master_read(self.AK09916_ADDR, 0x11, 6)
                
                # Convert to signed 16-bit values
                mag_x = struct.unpack('<h', bytes(data[0:2]))[0]
                mag_y = struct.unpack('<h', bytes(data[2:4]))[0]
                mag_z = struct.unpack('<h', bytes(data[4:6]))[0]
                
                # Convert to microtesla (0.15 μT/LSB)
                return [mag_x * 0.15, mag_y * 0.15, mag_z * 0.15]
            else:
                return [0, 0, 0]
                
        except Exception as e:
            print(f"Error reading magnetometer: {e}")
            return [0, 0, 0]

# Add these methods to the previous ICM20948_SPI class
