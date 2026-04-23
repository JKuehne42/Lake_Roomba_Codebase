import argparse
import numpy as np
import serial
import time
import board
import adafruit_icm20x
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from ahrs.filters import Madgwick
from ahrs.common import Quaternion

class KalmanFilter2D:
    def __init__(self, dt=0.05, max_velocity=0.5):
        self.dt = dt
        self.max_velocity = max_velocity

        # State: [x, y, vx, vy]
        self.x = np.zeros((4, 1))
        self.P = np.eye(4) * 100.0

        self.Q = np.diag([0.01, 0.01, 2.0, 2.0])
        self.R = np.diag([11.1**2, 11.1**2])   # base GPS noise (meters²)

        # Outlier rejection threshold (meters)
        self.outlier_threshold = 1.2

    def predict(self, ax, ay, is_stationary=False):
        dt = self.dt
        F = np.array([[1, 0, dt, 0],
                      [0, 1, 0, dt],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
        B = np.array([[0.5*dt**2, 0],
                      [0, 0.5*dt**2],
                      [dt, 0],
                      [0, dt]])
        u = np.array([[ax], [ay]])
        self.x = F @ self.x + B @ u
        self.P = F @ self.P @ F.T + self.Q

        if not is_stationary:
            decay = 0.85  # tune between 0.8-0.95
            self.x[2] *= decay
            self.x[3] *= decay

        self._clamp_velocity()

    def _clamp_velocity(self):
        vx, vy = self.x[2, 0], self.x[3, 0]
        speed = np.sqrt(vx**2 + vy**2)
        if speed > self.max_velocity:
            scale = self.max_velocity / speed
            self.x[2, 0] *= scale
            self.x[3, 0] *= scale

    def update(self, z, hdop=None):
        """
        Update with GPS measurement [east, north] in meters.
        If hdop is provided, scale measurement noise accordingly.
        Returns True if update was performed, False if rejected as outlier.
        """
        H = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0]])
        z = np.array(z).reshape((2, 1))

        # Adjust measurement noise based on HDOP if available
        R = self.R.copy()
        if hdop is not None:
            # Typical HDOP 1.0 ~ 5m accuracy; scale R by (hdop)^2
            R = self.R * (hdop ** 2)

        # Innovation and its covariance
        y = z - H @ self.x
        S = H @ self.P @ H.T + R

        # Mahalanobis distance for outlier detection
        try:
            invS = np.linalg.inv(S)
            mahalanobis = np.sqrt(y.T @ invS @ y).item()
        except np.linalg.LinAlgError:
            mahalanobis = 0.0

        if mahalanobis > self.outlier_threshold:
            # Reject outlier
            print(f"GPS outlier rejected: dist={mahalanobis:.1f}m")
            return False

        # Kalman update
        K = self.P @ H.T @ invS
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P
        self._clamp_velocity()
        return True

    def get_position(self):
        return self.x[0:2].flatten()

    def get_velocity(self):
        return self.x[2:4].flatten()

class Map:
    def __init__(self):
        # IMU / GPS data
        self.initial_imu_data = np.zeros((3,3))
        self.initial_gps_data = np.array([0,0])
        self.imu_data = np.zeros((3,3))
        self.gps_data = np.array([0.0, 0.0])
        self.old_imu_data = np.zeros((3,3))
        self.gps_initialized = False

        self.resolution = 1000
        self.map_array = self.create_simple_map(10, 10, self.resolution)

        # Madgwick filter
        self.madgwick = Madgwick(frequency=20.0, gain=0.05)
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.last_imu_time = time.time()

        self.velocity = np.zeros(3)          # raw IMU velocity (deprecated)
        self.position = np.zeros(3)          # raw IMU position (deprecated)
        self.total_distance = 0.0

        self.accel_bias = np.zeros(3)
        self.accel_buffer = []
        self.gyro_buffer = []

        # Magnetometer calibration
        self.MAG_OFFSET = np.array([25, 11, 45])
        self.MAG_SCALE = np.array([1.060011, 1.028042, 0.922602])

        # Kalman filter for fused position
        self.kf = KalmanFilter2D(dt=0.05)
        self.kf_lock = asyncio.Lock()
        self.gps_ref_lat = None
        self.gps_ref_lon = None
        self.gps_initialized_flag = False
        self.accel_bias_dynamic = np.zeros(3)   # learned offset when stationary
        self.is_stationary = False

        # IMU hardware
        i2c = board.I2C()
        try:
            self.icm = adafruit_icm20x.ICM20948(i2c)
        except:
            self.icm = None
            print("WARNING: IMU not recognized")

        # GPS hardware
        self.port = "/dev/serial0"
        self.ser = serial.Serial(self.port)
        self.gpgga_info = "$GPGGA,"
        self.executor = ThreadPoolExecutor(10)

    
    async def main(self):
        print("Hi from mapping.py!")
        self.calc_accel_bias()
        print("Warming up Madgwick filter (3s)...")
        t_end = time.time() + 3.0
        while time.time() < t_end:
            accel = np.array(self.icm.acceleration) - self.accel_bias
            gyro = np.array(self.icm.gyro)
            dt = 0.05
            self.q = self.madgwick.updateIMU(q=self.q, gyr=gyro, acc=accel, dt=dt)
            time.sleep(dt)

        euler = self.quaternion_to_euler(self.q) * 180/np.pi
        print(f"Madgwick converged to Roll:{euler[0]:.1f} Pitch:{euler[1]:.1f} Yaw:{euler[2]:.1f}")
        self.last_imu_time = time.time()
        try:
            self.loop = asyncio.get_running_loop()
        except:
            print("no running event loop (mapping.py)")
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        thread = threading.Thread(target=self.run_in_thread, args=(self.loop,))
        thread.start()

    def run_in_thread(self, loop):
        asyncio.run_coroutine_threadsafe(self.imu_update(), loop)
        asyncio.run_coroutine_threadsafe(self.gps_update(loop), loop)

    def gps_to_local_enu(self, lat, lon):
        """Convert lat/lon to East, North (meters) relative to reference."""
        if self.gps_ref_lat is None or self.gps_ref_lon is None:
            return None, None
        R = 6371000  # Earth radius in meters
        dlat = np.radians(lat - self.gps_ref_lat)
        dlon = np.radians(lon - self.gps_ref_lon)
        lat_avg = np.radians((lat + self.gps_ref_lat) / 2)
        east = R * dlon * np.cos(lat_avg)
        north = R * dlat
        return east, north

    def convert_to_degrees(self, raw_value):
        decimal_value = raw_value / 100.0
        degrees = int(decimal_value)
        mm_mmmm = (decimal_value - int(decimal_value)) / 0.6
        position = degrees + mm_mmmm
        return float(position)   # Return float, not string

    async def gps_update(self, loop):
        while True:
            if await self.read_gps(loop):
                if not self.gps_initialized:
                    self.initial_gps_data = self.gps_data
                    self.gps_initialized = True

    async def read_gps(self, loop):
        try:
            received_data = await loop.run_in_executor(self.executor, self.ser.readline)
            received_data = str(received_data)
            GPGGA_data_available = received_data.find(self.gpgga_info)
        except Exception as error:
            print(f"Problem reading GPS port {self.port}, error: {error}")
            self.ser = serial.Serial(self.port)
            return False

        if GPGGA_data_available > 0:
            try:
                GPGGA_buffer = received_data.split("$GPGGA,", 1)[1]
                NMEA_buff = GPGGA_buffer.split(',')
                nmea_latitude = NMEA_buff[1]
                lat_direction = NMEA_buff[2]
                nmea_longitude = NMEA_buff[3]
                longi_direction = NMEA_buff[4]

                lat = float(nmea_latitude)
                if lat_direction == 'S':
                    lat = -lat
                lat = self.convert_to_degrees(lat)

                longi = float(nmea_longitude)
                if longi_direction == 'W':
                    longi = -longi
                longi = self.convert_to_degrees(longi)

                self.gps_data = np.array([lat, longi])

                # Set reference on first valid fix
                if not self.gps_initialized_flag:
                    self.gps_ref_lat = lat
                    self.gps_ref_lon = longi
                    self.gps_initialized_flag = True
                    self.initial_gps_data = np.array([lat, longi])
                    return True

                # Convert to local ENU and update Kalman filter
                east, north = self.gps_to_local_enu(lat, longi)
                if east is not None:
                    async with self.kf_lock:
                        self.kf.update([east, north])
                    # print(f"GPS Update: East={east:.2f}, North={north:.2f}")
                return True
            except Exception as e:
                print(f"Error with GPS data processing: {e}")
                return False
        return False

    async def imu_update(self):
        while True:
            await self.read_imu()

    def calc_accel_bias(self):
        N = 200
        avg = np.zeros(3)
        for _ in range(N):
            avg += np.array(self.icm.acceleration)
            time.sleep(0.01)
        avg /= N
        g_mag = np.linalg.norm(avg)
        # g_dir = avg / g_mag
        self.accel_bias = avg - (avg / g_mag) *  9.81
        print(f"Accel bias computed: {self.accel_bias.round(4)}")   

    def world_acceleration(self, accel_sensor, q):
        R = Quaternion(q).to_DCM()
        accel_world = R @ accel_sensor
        gravity_world = np.array([0, 0, 9.81])
        return accel_world - gravity_world

    def quaternion_to_euler(self, q):
        w, x, y, z = q
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = np.copysign(np.pi / 2, sinp)
        else:
            pitch = np.arcsin(sinp)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        return np.array([roll, pitch, yaw])

    async def read_imu(self):
        cur_time = time.time()
        dt = cur_time - self.last_imu_time
        dt = min(dt, 0.1) # max 100ms step
        self.last_imu_time = cur_time

        accel = np.array(self.icm.acceleration) - self.accel_bias
        gyro = np.array(self.icm.gyro)
        raw_mag = np.array(self.icm.magnetic)
        mag = (raw_mag - self.MAG_OFFSET) / self.MAG_SCALE

        # Update quaternion orientation
        self.q = self.madgwick.updateMARG(q=self.q, gyr=gyro, acc=accel, mag=mag dt=dt)

        # World linear acceleration (still contains tilt bias)
        accel_linear_raw = self.world_acceleration(accel, self.q)
        # accel_linear_raw[np.abs(accel_linear_raw) < 0.05] = 0.0
        accel_linear_raw = self.soft_deadzone(accel_linear_raw)

        # Maintain buffers
        self.accel_buffer.append(accel_linear_raw)
        self.gyro_buffer.append(gyro)
        if len(self.accel_buffer) > 20:   # longer buffer for better variance estimate
            self.accel_buffer.pop(0)
            self.gyro_buffer.pop(0)

        # Stationary detection using variance (tune thresholds for your sensor)
        if len(self.accel_buffer) >= 10:
            accel_var = np.var(self.accel_buffer, axis=0).max()
            gyro_var = np.var(self.gyro_buffer, axis=0).max()
            self.is_stationary = (accel_var < 0.05 and gyro_var < 0.005)
        else:
            self.is_stationary = False
            await asyncio.sleep(0.05)
            return

        # Dynamic bias update when stationary
        if self.is_stationary:
            # Low-pass filter the raw linear acceleration to learn the offset
            alpha = 0.05
            self.accel_bias_dynamic = (1 - alpha) * self.accel_bias_dynamic + alpha * accel_linear_raw
            # Zero the Kalman velocity
            async with self.kf_lock:
                self.kf.x[2:4] = 0.0   # zero velocity
                self.kf.x[0:2] = self.kf.x[0:2]  # hold position
                self.kf.P[2:4, 2:4] = np.eye(2) * 1e-6  # collapse velocity covariance
            # Use a very small acceleration for prediction (effectively no motion)
            accel_corrected = np.zeros(3)
        else:
            # Subtract the learned bias
            accel_corrected = accel_linear_raw - self.accel_bias_dynamic

        # Apply dead-zone on corrected acceleration
        # accel_corrected[np.abs(accel_corrected) < 0.05] = 0.0
        accel_corrected = self.soft_deadzone(accel_corrected)

        # Kalman filter prediction
        async with self.kf_lock:
            self.kf.dt = dt
            self.kf.predict(accel_corrected[0], accel_corrected[1], is_stationary=self.is_stationary)

        # Get fused position and map coordinates (unchanged)
        fused_pos = self.kf.get_position()
        map_center_x = self.map_array.shape[0] // 2
        map_center_y = self.map_array.shape[1] // 2
        map_x = int(map_center_x + fused_pos[0] * self.resolution)
        map_y = int(map_center_y + fused_pos[1] * self.resolution)
        map_x = max(0, min(self.map_array.shape[0]-1, map_x))
        map_y = max(0, min(self.map_array.shape[1]-1, map_y))

        # Diagnostics (include bias info)
        euler = self.quaternion_to_euler(self.q) * 180/np.pi
        print(f"Roll: {euler[0]:.1f}°, Pitch: {euler[1]:.1f}°, Yaw: {euler[2]:.1f}°")
        print(f"LinAcc raw: {accel_linear_raw.round(3)}")
        print(f"LinAcc corr: {accel_corrected.round(3)}")
        print(f"Bias dynamic: {self.accel_bias_dynamic.round(3)}")
        print(f"Stationary: {self.is_stationary}")
        print(f"KF Position: East={fused_pos[0]:.2f}m, North={fused_pos[1]:.2f}m")

        await asyncio.sleep(0.05)
    
    def soft_deadzone(self, vec, threshold=0.08):
        """Smoothly reduces small values to zero rather than hard clipping."""
        result = np.zeros_like(vec)
        for i, v in enumerate(vec):
            if abs(v) > threshold:
                result[i] = v - np.sign(v) * threshold
        return result

    def create_simple_map(self, length=10, width=10, resolution=10):
        print(f"Creating a map of size {length}m x {width}m with resolution {resolution}cell/m^2.")
        map_array = np.zeros((int(length*resolution), int(width*resolution)))
        middle_pos = np.array([int(length*resolution//2), int(width*resolution//2)])
        self.position = middle_pos  # for compatibility, but prefer KF position
        return map_array

    def run(self, map_bool=True):
        starting_position = [0,0]
        while map_bool:
            # In real use, you'd use the Kalman filter position for navigation
            # predicted_position = self.kf.get_position()
            # self.localize(predicted_position, self.map_array, starting_position)
            time.sleep(0.1)

    def locate(self, previous_position=np.array([0.0, 0.0])):
        return np.array([0,0])

    def localize(self, cur_position, map_array, ini_position):
        return np.array([0,0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lake Roomba Mapping Module')
    parser.add_argument('--map_bool', default=True, type=bool,
                        help='Choose whether or not to run the mapping loop')
    ARGS = parser.parse_args()
    map_instance = Map()
    map_instance.run(**vars(ARGS))