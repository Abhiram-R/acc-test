#!/usr/bin/env python
import pandas as pd

from maneuver import Maneuver
from cruise import control

class CV:
    MPH_TO_MS = 1.609 / 3.6
    MS_TO_MPH = 3.6 / 1.609
    KPH_TO_MS = 1. / 3.6
    MS_TO_KPH = 3.6
    MPH_TO_KPH = 1.609
    KPH_TO_MPH = 1. / 1.609
    KNOTS_TO_MS = 1 / 1.9438
    MS_TO_KNOTS = 1.9438

maneuvers = [
    Maneuver(
        'while cruising at 50 mph, change cruise speed to 60mph',
        duration=30.,
        initial_speed=50. * CV.KPH_TO_MS,
        cruise_speeds=[(60 * CV.KPH_TO_MS, 0)]
    ),
    Maneuver(
        'while cruising at 60 mph, change cruise speed to 50mph',
        duration=30.,
        initial_speed=60. * CV.KPH_TO_MS,
        cruise_speeds=[(50 * CV.KPH_TO_MS, 0)]
    ),
    Maneuver(
        'approaching a 40kph car while cruising at 50kph from 50m away',
        duration=30.,
        initial_speed=150. * CV.KPH_TO_MS,
        lead_relevancy=True,
        initial_distance_lead=140.,
        speed_lead_values=[0. * CV.KPH_TO_MS, 0. * CV.KPH_TO_MS], # defines speed of car in front
        speed_lead_breakpoints=[0., 100.],
        cruise_speeds=[(60. * CV.KPH_TO_MS, 0)]
    ),
    Maneuver(
        "following a car at 50kph, must adjust accordingly to speed change of lead vehicle.",
        duration=25.,
        initial_speed=80. * CV.KPH_TO_MS,
        lead_relevancy=True,
        initial_distance_lead=50.,
        speed_lead_values=[40. * CV.KPH_TO_MS, 40. * CV.KPH_TO_MS, 38. * CV.KPH_TO_MS, 40. * CV.KPH_TO_MS, 42. * CV.KPH_TO_MS, 40. * CV.KPH_TO_MS, 38. * CV.KPH_TO_MS],
        speed_lead_breakpoints=[0., 20., 22., 24., 26., 28., 30.],
        cruise_speeds=[(80. * CV.KPH_TO_MS, 0)]
    )
]
maneuvers[3].evaluate(control=control, verbosity=5, animate=True, plot=True, test_id=1)
'''dataframe = pd.read_excel('./xlsx/test_cases.xlsx')
row_length = len(dataframe.axes[0])

excelData = dataframe.values.tolist()

for i in range(row_length):
    currentData = excelData[i]

    maneuverDict = {}
    maneuverDict.update({"title": currentData[0]})
    maneuverDict.update({"duration": float(currentData[1])})
    maneuverDict.update({"initial_speed": round(float(currentData[2]) * CV.KPH_TO_MS, 3)})
    if currentData[3] == 1: maneuverDict.update({"lead_relevancy": bool(currentData[3])})
    else: maneuverDict.update({"lead_relevancy": int(0)})
    if currentData[3]: maneuverDict.update({"initial_distance_lead": float(currentData[4])})

    if not str(currentData[5]) == 'nan':
        speed_lead_valuesList = list(currentData[5].split(", "))
        maneuverDict.update({"speed_lead_values": [round(float(a) * CV.KPH_TO_MS,4) for a in speed_lead_valuesList]})

    if not str(currentData[6]) == 'nan':
        speed_lead_breakpointsList = list(currentData[6].split(", "))
        speed_lead_breakpoints = [float(a) for a in speed_lead_breakpointsList]
        maneuverDict.update({"speed_lead_breakpoints": speed_lead_breakpoints})

    maneuverDict.update({"cruise_speeds": [(round(float(currentData[7])*CV.KPH_TO_MS, 3), 0)]})
    #print(maneuverDict)
    Maneuver(**maneuverDict).evaluate(control=control, verbosity=5, animate=True, plot=True, test_id=int(i))
'''
#test_case = 3 # SET TEST CASE ID HERE!
#maneuvers[test_case-1].evaluate(control=control, verbosity=5, animate=True, plot=True)
