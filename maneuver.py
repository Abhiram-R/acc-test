from plant import Plant
from visualize import Visualizer
import numpy as np
import pandas as pd

class CV:
    MPH_TO_MS = 1.609 / 3.6
    MS_TO_MPH = 3.6 / 1.609
    KPH_TO_MS = 1. / 3.6
    MS_TO_KPH = 3.6
    MPH_TO_KPH = 1.609
    KPH_TO_MPH = 1. / 1.609
    KNOTS_TO_MS = 1 / 1.9438
    MS_TO_KNOTS = 1.9438

SAFE_DISTANCE = (
    (20, 3),
    (30, 5),
    (40, 9),
    (50, 15),
    (60, 21),
    (70, 29),
    (80, 38),
    (90, 47),
    (100, 60),
    (110, 73),
    (120, 86),
    (130, 98),
    (140, 123),
    (160, 136),
    (170, 151),
    (180, 166),
)

def safe_gap(speed):
    x = np.array([x * CV.KPH_TO_MS for x, y in SAFE_DISTANCE])
    y = np.array([y for x, y in SAFE_DISTANCE])
    z = np.polyfit(x, y, 3)
    p = np.poly1d(z)

    return p(speed)

class Maneuver(object):

    def __init__(self, title, duration, **kwargs):
        #self.dataframe = pd.read_excel('./xlsx/test_cases.xlsx')
        # Was tempted to make a builder class
        self.distance_lead = kwargs.get("initial_distance_lead", 200.0)
        self.speed = kwargs.get("initial_speed", 0.0)
        self.lead_relevancy = kwargs.get("lead_relevancy", 0)

        self.grade_values = kwargs.get("grade_values", [0.0, 0.0])
        self.grade_breakpoints = kwargs.get("grade_breakpoints", [0.0, duration])
        self.speed_lead_values = kwargs.get("speed_lead_values", [0.0, 0.0])
        self.speed_lead_breakpoints = kwargs.get("speed_lead_values", [0.0, duration])
        self.cruise_speeds = kwargs.get("cruise_speeds", [])

        self.duration = duration
        self.title = title

    def evaluate(self, control=None, verbosity=0, plot=False, animate=False, test_id=0):
        plant = Plant(lead_relevancy=self.lead_relevancy, speed=self.speed, distance_lead=self.distance_lead, verbosity=verbosity)

        speeds_sorted = sorted(self.cruise_speeds, key=lambda a: a[1])
        cruise_speed = 0
        brake = 0
        gas = 0

        if verbosity >= 4:
            vis = Visualizer(title=self.title, animate=animate, show=plot, max_speed=80, max_accel=10)

        safe_distance_flag = 0

        while plant.current_time() < self.duration:
            while speeds_sorted and plant.current_time() >= speeds_sorted[0][1]:
                # getting the current cruise speed
                cruise_speed = speeds_sorted[0][0]
                speeds_sorted = speeds_sorted[1:]
                if verbosity > 1:
                    print("current cruise speed changed to", cruise_speed)

            grade = np.interp(plant.current_time(),
                              self.grade_breakpoints, self.grade_values)
            speed_lead = np.interp(
                plant.current_time(), self.speed_lead_breakpoints, self.speed_lead_values)

            speed, acceleration, car_in_front = plant.step(brake=brake, gas=gas, v_lead=speed_lead, grade=grade)

            # limiting the value of acceleration betwen a range
            # i feel this should be an assertion
            acceleration = np.clip(acceleration, -0.9 * 9.81, 0.4 * 9.81)

            # Assert the gap parameter is respected during all the maneuver.
            gap = safe_gap(speed)
            if not car_in_front >= gap:
                safe_distance_flag = 1
                break

            brake, gas = control(speed=speed, acceleration=acceleration, car_in_front=car_in_front, gap=gap, cruise_speed=cruise_speed)

            if verbosity >= 4:
                vis.update_data(cur_time=plant.current_time(), speed=speed, acceleration=acceleration, gas_control=gas, brake_control=brake, car_in_front=car_in_front, safe_distance=gap)


        '''if safe_distance_flag == 1: self.dataframe.at[test_id,'outcome'] = 'FAIL'
        else: self.dataframe.at[test_id,'outcome'] = 'PASS'
        self.dataframe.to_excel('./xlsx/test_cases.xlsx',index=False)'''
        return