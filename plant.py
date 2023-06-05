#!/usr/bin/env python
import multiprocessing
import time
import numpy as np

class CV:
    MPH_TO_MS = 1.609 / 3.6
    MS_TO_MPH = 3.6 / 1.609
    KPH_TO_MS = 1. / 3.6
    MS_TO_KPH = 3.6
    MPH_TO_KPH = 1.609
    KPH_TO_MPH = 1. / 1.609
    KNOTS_TO_MS = 1 / 1.9438
    MS_TO_KNOTS = 1.9438

def scale_acceleration(speed):
    xp = [80*CV.KPH_TO_MS, 120*CV.KPH_TO_MS, 150*CV.KPH_TO_MS]
    yp = [1, 2, 3]
    acceleration_scale_factor = np.interp(speed, xp, yp)
    return acceleration_scale_factor

# function that returns the speed and acceleration of the ego vehicle
def car_plant(pos, speed=40, grade=-20, gas=1, brake=0):
    # vehicle parameters
    g = 9.81
    mass = 1700
    aero_cd = 0.3

    force_peak = mass * 3.
    force_brake_peak = -mass * 20.
    power_peak = 100000   # 100kW
    speed_base = power_peak / force_peak
    rolling_res = 0.01
    air_density = 1.225
    gas_to_peak_linear_slope = 3.33
    brake_to_peak_linear_slope = 0.2

    # *** longitudinal model ***
    # find speed where peak torque meets peak powertest_id_1.py -> import file and function... write test code and set excel data
    force_brake = brake * force_brake_peak * brake_to_peak_linear_slope #braking force
    if speed < speed_base:  # torque control
        force_gas = gas * force_peak * gas_to_peak_linear_slope #force due to throttle
    else:  # power control
        force_gas = gas * power_peak / speed * gas_to_peak_linear_slope

    force_grade = grade * mass  # positive grade means uphill

    force_resistance = -(rolling_res * mass * g + 0.5 *speed**2 * aero_cd * air_density) # negative force due to air resistance

    force = force_gas + force_brake + force_resistance + force_grade  #calculates the sum of all forces
    acceleration = (force / mass) * scale_acceleration(speed)

    return speed, acceleration
class CV:
    MPH_TO_MS = 1.609 / 3.6
    MS_TO_MPH = 3.6 / 1.609
    KPH_TO_MS = 1. / 3.6
    MS_TO_KPH = 3.6
    MPH_TO_KPH = 1.609
    KPH_TO_MPH = 1. / 1.609
    KNOTS_TO_MS = 1 / 1.9438
    MS_TO_KNOTS = 1.9438

# returns the current time
def sec_since_boot():
    return time.time()

# used to iterate the frame in visualised plot, depends on a given rate value.
class Ratekeeper(object):

    def __init__(self, rate):
        """Rate in Hz for ratekeeping. print_delay_threshold must be nonnegative."""
        self._interval = 1. / rate
        self._next_frame_time = sec_since_boot() + self._interval
        self._frame = 0

    @property
    def frame(self):
        return self._frame

    def monitor_time(self):
        self._next_frame_time += self._interval
        self._frame += 1

class Plant(object):

    def __init__(self, lead_relevancy=False, rate=100, speed=0.0, distance_lead=2.0, verbosity=0):
        self.rate = rate
        self.verbosity = verbosity
        self.distance, self.distance_prev = 0., 0.
        self.speed, self.speed_prev = speed, speed
        self.lead_relevancy = lead_relevancy

        # lead car
        self.distance_lead_prev = distance_lead

        self.rk = Ratekeeper(rate)
        self.ts = 1. / rate

    def current_time(self):
        return float(self.rk.frame) / self.rate

    def step(self, brake=0, gas=0, v_lead=0.0, grade=0.0):

        distance_lead = self.distance_lead_prev + v_lead * self.ts

        # ******** run the car ********
        speed, acceleration = car_plant(self.distance_prev, self.speed_prev, grade, gas, brake)
        distance = self.distance_prev + speed * self.ts + self.ts**2*acceleration*.5
        speed = self.speed_prev + self.ts * acceleration

        # ******** stop the car ********
        if speed <= 0:
            speed = 0
            acceleration = 0

        # *** radar model ***
        if self.lead_relevancy:
            d_rel = np.maximum(0., distance_lead - distance)
            v_rel = v_lead - speed
        else:
            d_rel = 200.
            v_rel = 0.

        # print at 5hz
        if True:
            msg_tmpl = ("%6.2f m  %6.2f m/s  %6.2f m/s2 "
                        "  gas: %.2f  brake: %.2f "
                        "  lead_rel: %6.2f m  %6.2f m/s")
            msg = msg_tmpl % (distance, speed, acceleration,
                              gas, brake, d_rel, v_rel)

            if self.verbosity > 2:
                print(msg)

        # ******** update prevs ********
        self.speed_prev = speed
        self.distance_prev = distance
        self.distance_lead_prev = distance_lead

        car_in_front = distance_lead - distance if self.lead_relevancy else 200.

        self.rk.monitor_time()
        return speed, acceleration, car_in_front
