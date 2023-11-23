from condition import TTAA_codition, TTCC_codition
import re
import pandas as pd

import pandas as pd
from numpy import log as ln

# Use scheduler 25min
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.image as image
# import pandas as pd

import metpy.calc as mpcalc
from metpy.plots import Hodograph, SkewT
from metpy.units import units
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from metpy.calc import cape_cin, dewpoint_from_relative_humidity, parcel_profile
import numpy as np
import requests


class text_rawindsonde:
    def __init__(self, file_name, source=""):
        self.file_name = file_name
        self.source = source

    def find_group(self, arr_data=[], g_order=""):
        g_index = ""
        try:
            for index, data in enumerate(arr_data):
                x = re.search("^{}.*".format(g_order), data)  # don missing .
                if (x):
                    g_index = index
                    return g_index
        except:
            return g_index

    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def decoder(self):
        f_name = ""
        station = ""
        ICAO = ""
        date_lunch = ""
        time_lunch = ""

        # list for make dictionary output
        # SIGNIFICANT TEMPERATURE
        G_T = {}
        GT_GPM_AGL = []
        GT_FltTime = []
        GT_Press = []
        GT_Temp = []
        GT_RelHum = []
        GT_WSpeed = []
        GT_WDirn = []
        GT_Type = []

        # SIGNIFICANT WIND SPEED
        G_W = {}
        GW_GPM_AGL = []
        GW_FltTime = []
        GW_Press = []
        GW_Temp = []
        GW_RelHum = []
        GW_WSpeed = []
        GW_WDirn = []
        GW_Type = []

        # SIGNIFICANT OTHER SIGNIFICANT LEVELS  (Tropopause)
        G_O = {}
        GO_GPM_AGL = []
        GO_FltTime = []
        GO_Press = []
        GO_Temp = []
        GO_RelHum = []
        GO_WSpeed = []
        GO_WDirn = []
        GO_Type = []

        # SIGNIFICANT OTHER SIGNIFICANT LEVELS (Freezing Level)
        G_F = {}
        GF_GPM_AGL = []
        GF_FltTime = []
        GF_Press = []
        GF_Temp = []
        GF_RelHum = []
        GF_WSpeed = []
        GF_WDirn = []
        GF_Type = []

        start_temp_table = False
        start_wind_table = False
        start_tropopause = False
        start_freezing = False
        data_read_index = 0

        f = open(r"{}{}.txt".format(self.source, self.file_name), "r", encoding='utf-8', errors='replace')
        for index, lr in enumerate(f):
            # print(lr.strip().split())
            line_split = lr.strip().split()
            if (index <= 25):
                file_name_index = self.find_group(line_split, "\"CM")
                station_index = self.find_group(line_split, "WMO")
                ICAO_Index = self.find_group(line_split, "ICAO")
                Launched_index = self.find_group(line_split, "Launched")

                if (file_name_index != None):
                    print("file name is", line_split[file_name_index])
                    f_name = line_split[file_name_index]
                elif (station_index != None):
                    print("station name is", line_split[station_index + 3])
                    station = line_split[station_index + 3]
                elif (ICAO_Index != None):
                    print("ICAO name is", line_split[ICAO_Index + 3])
                    ICAO = line_split[ICAO_Index + 3]
                if (Launched_index != None):
                    print("Date to lunch : ", line_split[Launched_index + 3])
                    print("time to lunch : ", line_split[Launched_index + 4])
                    date_lunch = line_split[Launched_index + 3]
                    time_lunch = line_split[Launched_index + 4]

            try:
                if ((line_split[0] == "SIGNIFICANT") and (line_split[1] == "TEMPERATURE")):
                    start_temp_table = True
                    data_read_index = index + 5
                elif ((line_split[0] == "SIGNIFICANT") and (line_split[1] == "WIND")):
                    start_wind_table = True
                    data_read_index = index + 5
                elif ((line_split[0] == "OTHER") and (line_split[1] == "SIGNIFICANT")):
                    start_tropopause = True
                    start_freezing = True  # find freezing lvl after find tropopause
                    data_read_index = index + 5
            except:  # stop when can't find line_split[0] => error => except
                start_temp_table = False
                start_wind_table = False
                start_tropopause = False
                # start_freezing = False

            if (data_read_index <= index):
                if (start_temp_table == True):  # temp significant
                    if (len(line_split) == 0):  # check end of data table
                        # print("stop reading part A")
                        start_temp_table = False
                        data_read_index = 0

                    else:
                        if (self.is_float(line_split[0])):
                            GT_GPM_AGL.append(line_split[0])
                        else:
                            GT_GPM_AGL.append(None)

                        if (self.is_float(line_split[1])):
                            GT_FltTime.append(line_split[1])
                        else:
                            GT_FltTime.append(None)

                        if (self.is_float(line_split[2])):
                            GT_Press.append(line_split[2])
                        else:
                            GT_Press.append(None)

                        if (self.is_float(line_split[3])):
                            GT_Temp.append(float(line_split[3]))
                        else:
                            GT_Temp.append(None)

                        if (self.is_float(line_split[4])):
                            GT_RelHum.append(line_split[4])
                        else:
                            GT_RelHum.append(None)

                        if (self.is_float(line_split[5])):
                            GT_WSpeed.append(line_split[5])
                        else:
                            GT_WSpeed.append(None)

                        if (self.is_float(line_split[6])):
                            GT_WDirn.append(line_split[6])
                        else:
                            GT_WDirn.append(None)

                        # type is string
                        GT_Type.append(line_split[7])



                elif (start_wind_table == True):  # wind significant

                    if (len(line_split) == 0):  # check end of data table
                        # print("stop reading part B")
                        start_wind_table = False
                        data_read_index = 0
                    else:
                        if (self.is_float(line_split[0])):
                            GW_GPM_AGL.append(line_split[0])
                        else:
                            GW_GPM_AGL.append(None)

                        if (self.is_float(line_split[1])):
                            GW_FltTime.append(line_split[1])
                        else:
                            GW_FltTime.append(None)

                        if (self.is_float(line_split[2])):
                            GW_Press.append(line_split[2])
                        else:
                            GW_Press.append(None)

                        if (self.is_float(line_split[3])):
                            GW_Temp.append(float(line_split[3]))
                        else:
                            GW_Temp.append(None)

                        if (self.is_float(line_split[4])):
                            GW_RelHum.append(line_split[4])
                        else:
                            GW_RelHum.append(None)

                        if (self.is_float(line_split[5])):
                            GW_WSpeed.append(line_split[5])
                        else:
                            GW_WSpeed.append(None)

                        if (self.is_float(line_split[6])):
                            GW_WDirn.append(line_split[6])
                        else:
                            GW_WDirn.append(None)

                        # type is string
                        GW_Type.append(line_split[7])

                elif (start_tropopause == True):  # other significant level

                    if (len(line_split) == 0):
                        # print("stop reading part C")
                        start_tropopause = False
                        data_read_index = 0
                    else:
                        if (self.is_float(line_split[0])):
                            GO_GPM_AGL.append(line_split[0])
                        else:
                            GO_GPM_AGL.append(None)

                        if (self.is_float(line_split[1])):
                            GO_FltTime.append(line_split[1])
                        else:
                            GO_FltTime.append(None)

                        if (self.is_float(line_split[2])):
                            GO_Press.append(line_split[2])
                        else:
                            GO_Press.append(None)

                        if (self.is_float(line_split[3])):
                            GO_Temp.append(float(line_split[3]))
                        else:
                            GO_Temp.append(None)

                        if (self.is_float(line_split[4])):
                            GO_RelHum.append(line_split[4])
                        else:
                            GO_RelHum.append(None)

                        if (self.is_float(line_split[5])):
                            GO_WSpeed.append(line_split[5])
                        else:
                            GO_WSpeed.append(None)

                        if (self.is_float(line_split[6])):
                            GO_WDirn.append(line_split[6])
                        else:
                            GO_WDirn.append(None)

                        # type is string
                        GO_Type.append(line_split[7])

                # need add freezing level
                elif (start_freezing == True):
                    freezing_index = self.find_group(line_split, "Freezing")
                    if (freezing_index != None):
                        if (self.is_float(line_split[0])):
                            GF_GPM_AGL.append(line_split[0])
                        else:
                            GF_GPM_AGL.append(None)

                        if (self.is_float(line_split[1])):
                            GF_FltTime.append(line_split[1])
                        else:
                            GF_FltTime.append(None)

                        if (self.is_float(line_split[2])):
                            GF_Press.append(line_split[2])
                        else:
                            GF_Press.append(None)

                        if (self.is_float(line_split[3])):
                            GF_Temp.append(float(line_split[3]))
                        else:
                            GF_Temp.append(None)

                        if (self.is_float(line_split[4])):
                            GF_RelHum.append(line_split[4])
                        else:
                            GF_RelHum.append(None)

                        if (self.is_float(line_split[5])):
                            GF_WSpeed.append(line_split[5])
                        else:
                            GF_WSpeed.append(None)

                        if (self.is_float(line_split[6])):
                            GF_WDirn.append(line_split[6])
                        else:
                            GF_WDirn.append(None)

                        # type is string
                        GF_Type.append(line_split[7])

                        start_freezing = False

        G_T = {"file_name": f_name, "station_id": station, "station_name": ICAO, "date_lunch": date_lunch,
               "time_lunch": time_lunch,
               "data": {"GPM_AGL(m)": GT_GPM_AGL, "FltTime(s)": GT_FltTime, "Press(hPa)": GT_Press,
                        "Temp(celsius)": GT_Temp, "RelHum(%)": GT_RelHum, "WDirn(deg)": GT_WDirn,
                        "WSpeed(kts)": GT_WSpeed, "Type": GT_Type}}

        G_W = {"file_name": f_name, "station_id": station, "station_name": ICAO, "date_lunch": date_lunch,
               "time_lunch": time_lunch,
               "data": {"GPM_AGL(m)": GW_GPM_AGL, "FltTime(s)": GW_FltTime, "Press(hPa)": GW_Press,
                        "Temp(celsius)": GW_Temp, "RelHum(%)": GW_RelHum, "WDirn(deg)": GW_WDirn,
                        "WSpeed(kts)": GW_WSpeed, "Type": GW_Type}}

        G_O = {"file_name": f_name, "station_id": station, "station_name": ICAO, "date_lunch": date_lunch,
               "time_lunch": time_lunch,
               "data": {"GPM_AGL(m)": GO_GPM_AGL, "FltTime(s)": GO_FltTime, "Press(hPa)": GO_Press,
                        "Temp(celsius)": GO_Temp, "RelHum(%)": GO_RelHum, "WDirn(deg)": GO_WDirn,
                        "WSpeed(kts)": GO_WSpeed, "Type": GO_Type}}

        G_F = {"file_name": f_name, "station_id": station, "station_name": ICAO, "date_lunch": date_lunch,
               "time_lunch": time_lunch,
               "data": {"GPM_AGL(m)": GF_GPM_AGL, "FltTime(s)": GF_FltTime, "Press(hPa)": GF_Press,
                        "Temp(celsius)": GF_Temp, "RelHum(%)": GF_RelHum, "WDirn(deg)": GF_WDirn,
                        "WSpeed(kts)": GF_WSpeed, "Type": GF_Type}}

        # print("data",G_T["data"]["Type"])
        # print("data temp significant",G_T)
        # print("data wind significant",G_W)
        # print("data troperpause", G_O)
        # print("data freezing level", G_F)

        return G_T, G_W, G_O, G_F

class top_decode:
    def __init__(self, txt_name, source=""):
        self.txt_name = txt_name
        self.source = source
        self.date_time_file = ""

    def get_data(self, header=""):
        f = open(r'{}{}.txt'.format(self.source, self.txt_name), "r")
        result = "NODATA"
        for index, lr in enumerate(f):
            # print("index is {} , line text is {}".format(index,lr))
            if index == 0:
                self.date_time_file = lr.strip()
            try:
                if (lr.strip().split()[0] == header):
                    # print("have group in list :",lr)
                    first_line = index + 1
                    result = lr.strip()
                if (index == first_line) and (lr.strip()):
                    first_line += 1
                    result += " " + lr.strip()
                if (not (lr.strip())):
                    first_line = 0
            except:
                pass
        return result

    def find_group(arr_data=[], g_order=""):
        g_index = ""
        try:
            for index, data in enumerate(arr_data):
                # x = re.search('^99.*', data)
                x = re.search("^{}.*".format(g_order), data)  # don missing .
                if (x):
                    g_index = index
                    return g_index
        except:
            return g_index

    def TTAA_exc(TTAA_data="", condition={}):

        press = []
        temp = []
        dew_point = []
        wind_dir = []
        wind_vel = []
        height = []

        TTAA = TTAA_data.strip().split()

        # print(TTAA_codition)
        # get information
        group = TTAA[0]
        g_date = int(TTAA[1][:2]) - 50
        g_time = TTAA[1][2:4] + "00UTC"
        g_station = TTAA[2]

        TTAA_con = condition

        def TTAA_decode(data_check=""):
            for key, value in TTAA_con.items():
                # print("key : ", key," value : ", value['g_idx'])
                if data_check == value['g_idx']:
                    del TTAA_con[key]
                    # print("dict remain : " ,TTAA_con)
                    return value

        for index, value in enumerate(TTAA):
            # print("index : ", index, " value : " , value)
            if ((index > 2) and (index % 3 == 0)):
                if (value[2:5] == "999"):  # 999 is not report so no data form this group
                    if (value == "88999"):  # stop to topropause report
                        break
                    # print("don't report")
                    press.append(None)
                    height.append(None)
                    temp.append(None)
                    dew_point.append(None)
                    wind_dir.append(None)
                    wind_vel.append(None)
                elif (value[0:2] != "88"):
                    decode_condtion = TTAA_decode(value[0:2])
                    # press
                    try:
                        if (decode_condtion["press"]):
                            p_get = int(decode_condtion["press"])
                            press.append(decode_condtion["press"])
                        elif (int(decode_condtion["press_add"][0] + TTAA[index][decode_condtion["press_pos"][0]:
                        decode_condtion["press_pos"][1]] + decode_condtion["press_add"][1]) > 1030):
                            p_get = int(TTAA[index][decode_condtion["press_pos"][0]:decode_condtion["press_pos"][1]])
                            press.append(TTAA[index][decode_condtion["press_pos"][0]:decode_condtion["press_pos"][
                                1]])  # cotain ligit
                        else:  # add ligit
                            press.append(decode_condtion["press_add"][0] + TTAA[index][decode_condtion["press_pos"][0]:
                                                                                       decode_condtion["press_pos"][
                                                                                           1]] +
                                         decode_condtion["press_add"][1])
                            p_get = int(decode_condtion["press_add"][0] + TTAA[index][decode_condtion["press_pos"][0]:
                                                                                      decode_condtion["press_pos"][1]] +
                                        decode_condtion["press_add"][1])
                    except:  # if can't convert to number (//)
                        press.append(None)
                    # Height
                    try:
                        if (decode_condtion["height"]):
                            height.append(decode_condtion["height"])
                        elif (TTAA[index][decode_condtion["h_pos"][0]:decode_condtion["h_pos"][1]] == "//"):
                            height.append(None)
                        else:
                            height.append(decode_condtion["h_add"][0] + TTAA[index][decode_condtion["h_pos"][0]:
                                                                                    decode_condtion["h_pos"][1]] +
                                          decode_condtion["h_add"][1])
                    except:
                        height.append(None)

                    # temp and dewpoint
                    try:
                        if (
                                p_get >= 700):  # check press level to set - or + temperature (< 700mb temp is minus from refer.)
                            temp_cal = int(TTAA[index + 1][0:3]) / 10
                        else:
                            temp_cal = int(TTAA[index + 1][0:3]) / -10

                        if (int(TTAA[index + 1][3:5]) >= 50):
                            delta = int(TTAA[index + 1][3:5]) - 50
                        else:
                            delta = int(TTAA[index + 1][3:5]) / 10

                        dew_cal = temp_cal - delta

                        temp.append(str(round(temp_cal, 1)))
                        dew_point.append(str(round(dew_cal, 1)))

                    except:
                        temp.append(None)
                        dew_point.append(None)

                    # wind direction and wind speed
                    try:
                        if (TTAA[index + 2]):  # check wind data in code
                            Wd = TTAA[index + 2][0:3]
                            Ws = TTAA[index + 2][3:5]
                            wind_dir.append(str(int(Wd)))
                            wind_vel.append(str(int(Ws)))
                    except:
                        wind_dir.append(None)
                        wind_vel.append(None)

                elif (value[0:2] == "88"):
                    decode_condtion = TTAA_decode(value[0:2])
                    # press
                    try:
                        if (decode_condtion["press"]):
                            press.append(decode_condtion["press"])
                        elif (int(decode_condtion["press_add"][0] + TTAA[index][decode_condtion["press_pos"][0]:
                        decode_condtion["press_pos"][1]] + decode_condtion["press_add"][1]) > 1030):
                            press.append(TTAA[index][decode_condtion["press_pos"][0]:decode_condtion["press_pos"][
                                1]])  # cotain ligit
                        else:  # add ligit
                            press.append(decode_condtion["press_add"][0] + TTAA[index][decode_condtion["press_pos"][0]:
                                                                                       decode_condtion["press_pos"][
                                                                                           1]] +
                                         decode_condtion["press_add"][1])
                    except:  # if can't convert to number (//)
                        press.append(None)

                    # height
                    try:
                        if (decode_condtion["height"]):
                            height.append(decode_condtion["height"])
                        elif (TTAA[index][decode_condtion["h_pos"][0]:decode_condtion["h_pos"][1]] == "//"):
                            height.append(None)
                        else:
                            height.append(decode_condtion["h_add"][0] + TTAA[index][decode_condtion["h_pos"][0]:
                                                                                    decode_condtion["h_pos"][1]] +
                                          decode_condtion["h_add"][1])
                    except:
                        height.append(None)

                    # temp and dewpoint
                    try:
                        if (
                                p_get >= 700):  # check press level to set - or + temperature (< 700mb temp is minus from refer.)
                            temp_cal = int(TTAA[index + 1][0:3]) / 10
                        else:
                            temp_cal = int(TTAA[index + 1][0:3]) / -10

                        if (int(TTAA[index + 1][3:5]) >= 50):
                            delta = int(TTAA[index + 1][3:5]) - 50
                        else:
                            delta = int(TTAA[index + 1][3:5]) / 10

                        dew_cal = temp_cal - delta

                        temp.append(str(round(temp_cal, 1)))
                        dew_point.append(str(round(dew_cal, 1)))

                    except:
                        temp.append(None)
                        dew_point.append(None)

                    # wind direction and wind speed
                    try:
                        if (TTAA[index + 2]):  # check wind data in code
                            Wd = TTAA[index + 2][0:3]
                            Ws = TTAA[index + 2][3:5]
                            wind_dir.append(str(int(Wd)))
                            wind_vel.append(str(int(Ws)))
                    except:
                        wind_dir.append(None)
                        wind_vel.append(None)

                    break

                else:
                    press.append(None)
                    height.append(None)
                    temp.append(None)
                    dew_point.append(None)
                    wind_dir.append(None)
                    wind_vel.append(None)

        TTAA_output = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                       "TTAA": {"press(mb)": press, "height(m)": height, "temp(celsius)": temp,
                                "dewpoint(celsius)": dew_point, "wind_dir(degree)": wind_dir, "wind_vel(kt)": wind_vel}}

        return TTAA_output

    def TTBB_exc(TTBB_data=""):
        press_T_Td = []
        press_wd_ws = []
        temp = []
        dew_point = []
        wind_dir = []
        wind_vel = []

        TTBB = TTBB_data.strip().split()

        # get information
        group = TTBB[0]
        g_date = int(TTBB[1][:2]) - 50
        g_time = TTBB[1][2:4] + "00UTC"
        g_station = TTBB[2]

        wind_flag = False

        for index, value in enumerate(TTBB):
            if (wind_flag == False):
                if ((index > 2) and (index % 2 != 0)):
                    if (value == "21212"):  # 212122 is wind speed and wind direction of TTBB group
                        if ((value[-1:] == "=") or (value == '41414') or (
                                value == '31313')):  # stop to report this is end of message# 41414 is cloud group
                            break
                        wind_flag = True
                    elif ((value[0:2] != "21") or (value == '41414')):
                        # press
                        try:
                            P = TTBB[index][2:5]
                            if (int(P) < 10):
                                P = "1" + P
                            else:
                                P = str(int(P))
                            press_T_Td.append(P)
                            # print(press_T_Td)

                        except:  # if can't convert to number (//)
                            press_T_Td.append(None)

                        # temp and dewpoint
                        try:
                            if (
                                    int(P) >= 700):  # check press level to set - or + temperature (< 700mb temp is minus from refer.)
                                temp_cal = int(TTBB[index + 1][0:3]) / 10
                            else:
                                temp_cal = int(TTBB[index + 1][0:3]) / -10

                            if (int(TTBB[index + 1][3:5]) >= 50):
                                delta = int(TTBB[index + 1][3:5]) - 50
                            else:
                                delta = int(TTBB[index + 1][3:5]) / 10

                            dew_cal = temp_cal - delta

                            temp.append(str(round(temp_cal, 1)))
                            dew_point.append(str(round(dew_cal, 1)))

                        except:
                            temp.append(None)
                            dew_point.append(None)

            if (wind_flag == True):
                # print("start find wind parameter")
                if ((value[-1:] == "=") or (value == '41414') or (
                        value == '31313')):  # stop to report this is end of message# 41414 is cloud group
                    break
                elif (index % 2 == 0):
                    # print(TTBB[index])
                    # press
                    try:
                        P = TTBB[index][2:5]
                        if (int(P) < 10):
                            P = "1" + P
                        else:
                            P = str(int(P))
                        press_wd_ws.append(P)
                        # print(press_wd_ws)

                    except:  # if can't convert to number (//)
                        press_wd_ws.append(None)

                    # wind direction and wind speed
                    try:
                        if (TTBB[index + 2]):  # check wind data in code
                            Wd = TTBB[index + 1][0:3]
                            Ws = TTBB[index + 1][3:5]
                            wind_dir.append(str(int(Wd)))
                            wind_vel.append(str(int(Ws)))
                    except:
                        wind_dir.append(None)
                        wind_vel.append(None)

        # TTBB part A get press , temp , dewponit
        TTBB_output_partA = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                             "TTBB_partA": {"press(mb)": press_T_Td, "temp(celsius)": temp,
                                            "dewpoint(celsius)": dew_point}}
        # TTBB part B get press , wind direction, wind speed
        TTBB_output_partB = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                             "TTBB_partB": {"press(mb)": press_wd_ws, "wind_dir(degree)": wind_dir,
                                            "wind_vel(kt)": wind_vel}}

        return TTBB_output_partA, TTBB_output_partB

    def TTCC_exc(TTCC_data="", condition={}):
        press = []
        temp = []
        dew_point = []
        wind_dir = []
        wind_vel = []
        height = []

        TTCC = TTCC_data.strip().split()

        # get information
        group = TTCC[0]
        g_date = int(TTCC[1][:2]) - 50
        g_time = TTCC[1][2:4] + "00UTC"
        g_station = TTCC[2]

        TTCC_con = condition

        # print(TTCC_con)

        def TTCC_decode(data_check=""):
            for key, value in TTCC_con.items():
                # print("key : ", key," value : ", value['g_idx'])
                if data_check == value['g_idx']:
                    del TTCC_con[key]
                    # print("dict remain : " ,TTCC_con)
                    return value

        for index, value in enumerate(TTCC):
            # print("index : ", index, " value : " , value)
            if ((index > 2) and (index % 3 == 0)):
                if (value[2:5] == "999"):  # 999 is not report so no data form this group
                    if (value == "88999"):  # stop to topropause report
                        break
                    # print("don't report")
                    press.append(None)
                    height.append(None)
                    temp.append(None)
                    dew_point.append(None)
                    wind_dir.append(None)
                    wind_vel.append(None)
                elif (value[0:2] != "88"):
                    decode_condtion = TTCC_decode(value[0:2])
                    # print(value)
                    # print("value group 1 : ",TTCC[index] , " group 2 :",TTCC[index+1] , "group 3 :",TTCC[index+2])
                    # press
                    try:
                        if (decode_condtion["press"]):
                            p_get = int(decode_condtion["press"])
                            press.append(decode_condtion["press"])
                        elif (int(decode_condtion["press_add"][0] + TTCC[index][decode_condtion["press_pos"][0]:
                        decode_condtion["press_pos"][1]] + decode_condtion["press_add"][1]) > 1030):
                            p_get = int(TTCC[index][decode_condtion["press_pos"][0]:decode_condtion["press_pos"][1]])
                            press.append(TTCC[index][decode_condtion["press_pos"][0]:decode_condtion["press_pos"][
                                1]])  # cotain ligit
                        else:  # add ligit
                            press.append(decode_condtion["press_add"][0] + TTCC[index][decode_condtion["press_pos"][0]:
                                                                                       decode_condtion["press_pos"][
                                                                                           1]] +
                                         decode_condtion["press_add"][1])
                            p_get = int(decode_condtion["press_add"][0] + TTCC[index][decode_condtion["press_pos"][0]:
                                                                                      decode_condtion["press_pos"][1]] +
                                        decode_condtion["press_add"][1])
                    except:  # if can't convert to number (//)
                        press.append(None)
                    # Height
                    try:
                        if (decode_condtion["height"]):
                            height.append(decode_condtion["height"])
                        elif (TTCC[index][decode_condtion["h_pos"][0]:decode_condtion["h_pos"][1]] == "//"):
                            height.append(None)
                        else:
                            height.append(decode_condtion["h_add"][0] + TTCC[index][decode_condtion["h_pos"][0]:
                                                                                    decode_condtion["h_pos"][1]] +
                                          decode_condtion["h_add"][1])
                    except:
                        height.append(None)

                    # temp and dewpoint
                    try:
                        if (TTCC[index + 1]):  # check press level to set - or + temperature (< 700mb temp is minus from refer.)
                            temp_cal = int(TTCC[index + 1][0:3]) / -10

                        if (int(TTCC[index + 1][3:5]) >= 50):
                            delta = int(TTCC[index + 1][3:5]) - 50
                        else:
                            delta = int(TTCC[index + 1][3:5]) / 10

                        dew_cal = temp_cal - delta

                        temp.append(str(round(temp_cal, 1)))
                        dew_point.append(str(round(dew_cal, 1)))

                    except:
                        temp.append(None)
                        dew_point.append(None)

                    # wind direction and wind speed
                    try:
                        if (TTCC[index + 2]):  # check wind data in code
                            Wd = TTCC[index + 2][0:3]
                            Ws = TTCC[index + 2][3:5]
                            wind_dir.append(str(int(Wd)))
                            wind_vel.append(str(int(Ws)))
                    except:
                        wind_dir.append(None)
                        wind_vel.append(None)

                elif (value[0:2] == "88"):
                    decode_condtion = TTCC_decode(value[0:2])
                    # press
                    try:
                        if (decode_condtion["press"]):
                            press.append(decode_condtion["press"])
                        elif (int(decode_condtion["press_add"][0] + TTCC[index][decode_condtion["press_pos"][0]:
                        decode_condtion["press_pos"][1]] + decode_condtion["press_add"][1]) > 1030):
                            press.append(TTCC[index][decode_condtion["press_pos"][0]:decode_condtion["press_pos"][
                                1]])  # cotain ligit
                        else:  # add ligit
                            press.append(decode_condtion["press_add"][0] + TTCC[index][decode_condtion["press_pos"][0]:
                                                                                       decode_condtion["press_pos"][
                                                                                           1]] +
                                         decode_condtion["press_add"][1])
                    except:  # if can't convert to number (//)
                        press.append(None)

                    # height
                    try:
                        if (decode_condtion["height"]):
                            height.append(decode_condtion["height"])
                        elif (TTCC[index][decode_condtion["h_pos"][0]:decode_condtion["h_pos"][1]] == "//"):
                            height.append(None)
                        else:
                            height.append(decode_condtion["h_add"][0] + TTCC[index][decode_condtion["h_pos"][0]:
                                                                                    decode_condtion["h_pos"][1]] +
                                          decode_condtion["h_add"][1])
                    except:
                        height.append(None)

                    # temp and dewpoint
                    try:
                        if (
                                p_get >= 700):  # check press level to set - or + temperature (< 700mb temp is minus from refer.)
                            temp_cal = int(TTCC[index + 1][0:3]) / 10
                        else:
                            temp_cal = int(TTCC[index + 1][0:3]) / -10

                        if (int(TTCC[index + 1][3:5]) >= 50):
                            delta = int(TTCC[index + 1][3:5]) - 50
                        else:
                            delta = int(TTCC[index + 1][3:5]) / 10

                        dew_cal = temp_cal - delta

                        temp.append(str(round(temp_cal, 1)))
                        dew_point.append(str(round(dew_cal, 1)))

                    except:
                        temp.append(None)
                        dew_point.append(None)

                    # wind direction and wind speed
                    try:
                        if (TTCC[index + 2]):  # check wind data in code
                            Wd = TTCC[index + 2][0:3]
                            Ws = TTCC[index + 2][3:5]
                            wind_dir.append(str(int(Wd)))
                            wind_vel.append(str(int(Ws)))
                    except:
                        wind_dir.append(None)
                        wind_vel.append(None)

                    break

                else:
                    press.append(None)
                    height.append(None)
                    temp.append(None)
                    dew_point.append(None)
                    wind_dir.append(None)
                    wind_vel.append(None)

        TTCC_output = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                       "TTCC": {"press(mb)": press, "height(m)": height, "temp(celsius)": temp,
                                "dewpoint(celsius)": dew_point, "wind_dir(degree)": wind_dir, "wind_vel(kt)": wind_vel}}

        return TTCC_output

    def TTDD_exc(TTDD_data=""):
        press_T_Td = []
        press_wd_ws = []
        temp = []
        dew_point = []
        wind_dir = []
        wind_vel = []
        height = []

        TTDD = TTDD_data.strip().split()

        # get information
        group = TTDD[0]
        g_date = int(TTDD[1][:2]) - 50
        g_time = TTDD[1][2:4] + "00UTC"
        g_station = TTDD[2]

        wind_flag = False

        for index, value in enumerate(TTDD):
            if (wind_flag == False):
                if ((index > 2) and (index % 2 != 0)):
                    if (value == "21212"):  # 212122 is wind speed and wind direction of TTDD group
                        if ((value[-1:] == "=") or (value == '41414') or (
                                value == '31313')):  # stop to report this is end of message# 41414 is cloud group
                            break
                        # print("this is wind group for report")
                        wind_flag = True
                    elif ((value[0:2] != "21") or (value == '41414')):
                        # press
                        try:
                            P = TTDD[index][2:5]
                            if (P):
                                P = str(int(P) / 10)
                            press_T_Td.append(P)
                            # print(press_T_Td)

                        except:  # if can't convert to number (//)
                            press_T_Td.append(None)

                        # temp and dewpoint
                        try:
                            temp_cal = int(TTDD[index + 1][0:3]) / -10

                            if (int(TTDD[index + 1][3:5]) >= 50):
                                delta = int(TTDD[index + 1][3:5]) - 50
                            else:
                                delta = int(TTDD[index + 1][3:5]) / 10

                            dew_cal = temp_cal - delta

                            temp.append(str(round(temp_cal, 1)))
                            dew_point.append(str(round(dew_cal, 1)))

                        except:
                            temp.append(None)
                            dew_point.append(None)

            if (wind_flag == True):
                # print("start find wind parameter")
                if ((value[-1:] == "=") or (value == '41414') or (
                        value == '31313')):  # stop to report this is end of message# 41414 is cloud group
                    break
                elif (index % 2 == 0):
                    # print(TTDD[index])
                    # press
                    try:
                        P = TTDD[index][2:5]
                        if (P):
                            P = str(int(P) / 10)
                        press_wd_ws.append(P)
                        # print(press_wd_ws)

                    except:  # if can't convert to number (//)
                        press_wd_ws.append(None)

                    # wind direction and wind speed
                    try:
                        if (TTDD[index + 2]):  # check wind data in code
                            Wd = TTDD[index + 1][0:3]
                            Ws = TTDD[index + 1][3:5]
                            wind_dir.append(str(int(Wd)))
                            wind_vel.append(str(int(Ws)))
                    except:
                        wind_dir.append(None)
                        wind_vel.append(None)

        # TTDD part A get press , temp , dewponit
        TTDD_output_partA = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                             "TTDD_partA": {"press(mb)": press_T_Td, "temp(celsius)": temp,
                                            "dewpoint(celsius)": dew_point}}
        # TTDD part B get press , wind direction, wind speed
        TTDD_output_partB = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                             "TTDD_partB": {"press(mb)": press_wd_ws, "wind_dir(degree)": wind_dir,
                                            "wind_vel(kt)": wind_vel}}

        return TTDD_output_partA, TTDD_output_partB

    def PPAA_exc(PPAA_data=""):
        press = []
        wind_dir = []
        wind_vel = []

        PPAA = PPAA_data.strip().split()

        # get information
        group = PPAA[0]
        g_date = int(PPAA[1][:2]) - 50
        g_time = PPAA[1][2:4] + "00UTC"
        g_station = PPAA[2]

        # 850 700 500 400 300 250 200 150    pressure divide by 3 pressure for each group

        for index, value in enumerate(PPAA):
            if ((index > 2) and (PPAA[index][0:3] == "553")):
                # print(PPAA[index][0:3])
                # print(PPAA[index][3:5])
                if (PPAA[index][0:5] == "77799"):  # stop condition
                    break
                elif (PPAA[index][3:5] == "85"):
                    if (PPAA[index + 1][0:3] != "553"):
                        press.append("850")
                        wd = PPAA[index + 1][0:3]
                        ws = PPAA[index + 1][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                    if (PPAA[index + 2][0:3] != "553"):
                        press.append("700")
                        wd = PPAA[index + 2][0:3]
                        ws = PPAA[index + 2][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                    if (PPAA[index + 3][0:3] != "553"):
                        press.append("500")
                        wd = PPAA[index + 3][0:3]
                        ws = PPAA[index + 3][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                elif (PPAA[index][3:5] == "40"):
                    if (PPAA[index + 1][0:3] != "553"):
                        press.append("400")
                        wd = PPAA[index + 1][0:3]
                        ws = PPAA[index + 1][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                    if (PPAA[index + 2][0:3] != "553"):
                        press.append("300")
                        wd = PPAA[index + 2][0:3]
                        ws = PPAA[index + 2][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                    if (PPAA[index + 3][0:3] != "553"):
                        press.append("250")
                        wd = PPAA[index + 3][0:3]
                        ws = PPAA[index + 3][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                elif (PPAA[index][3:5] == "20"):
                    if (PPAA[index + 1][0:3] != "553"):
                        press.append("200")
                        wd = PPAA[index + 1][0:3]
                        ws = PPAA[index + 1][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                    if (PPAA[index + 2][0:3] != "553"):
                        press.append("150")
                        wd = PPAA[index + 2][0:3]
                        ws = PPAA[index + 2][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

                    if (PPAA[index + 3][0:3] != "553"):
                        press.append("100")
                        wd = PPAA[index + 3][0:3]
                        ws = PPAA[index + 3][3:5]
                        wind_dir.append(str(int(wd)))
                        wind_vel.append(str(int(ws)))
                    else:
                        press.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)

        PPAA_output = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                       "PPAA": {"press(mb)": press, "wind_dir(degree)": wind_dir, "wind_vel(kt)": wind_vel}}

        return PPAA_output

    def PPBB_or_PPDD_exc(PPBD_data=""):
        wind_dir = []
        wind_vel = []
        height = []

        PPBD = PPBD_data.strip().split()

        # get information
        group = PPBD[0]
        g_date = int(PPBD[1][:2]) - 50
        g_time = PPBD[1][2:4] + "00UTC"
        g_station = PPBD[2]

        # height for PPAA , PPBD , PPBD is  feet not meter => covert feet to meter by multiply by 0.3048

        for index, value in enumerate(PPBD):
            try:
                if ((index > 2) and (PPBD[index][0:1] == "9")):
                    # print(PPBD[index][1:2])
                    # print(PPBD[index][2:5])

                    if (PPBD[index][1:2] == "0"):
                        height_add_sting = ""
                    else:
                        height_add_sting = str(PPBD[index][1:2])

                    # fist height index (first digit)
                    if (PPBD[index][2:3] == "/"):
                        height_feet = "0"
                        get_wind_dir = int(PPBD[index + 1][0:5][0:3])
                        get_wind_spd = int(PPBD[index + 1][0:5][3:5])

                        height.append(str(round(int(height_feet) * 0.3048, 1)))
                        wind_dir.append(str(get_wind_dir))
                        wind_vel.append(str(get_wind_spd))


                    else:
                        # print("height : " , PPBD[index+1])
                        height_feet = height_add_sting + PPBD[index][2:3] + "000"
                        get_wind_dir = PPBD[index + 1][0:5][0:3]
                        get_wind_spd = PPBD[index + 1][0:5][3:5]

                        height.append(str(round(int(height_feet) * 0.3048, 1)))
                        wind_dir.append(str(get_wind_dir))
                        wind_vel.append(str(get_wind_spd))

                    # second digit
                    if (PPBD[index][3:4] == "/"):
                        height.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)
                    else:
                        height_feet = height_add_sting + PPBD[index][3:4] + "000"
                        get_wind_dir = PPBD[index + 2][0:5][0:3]
                        get_wind_spd = PPBD[index + 2][0:5][3:5]

                        height.append(str(round(int(height_feet) * 0.3048, 1)))
                        wind_dir.append(str(get_wind_dir))
                        wind_vel.append(str(get_wind_spd))

                    # third digit
                    if (PPBD[index][4:5] == "/"):
                        height.append(None)
                        wind_dir.append(None)
                        wind_vel.append(None)
                    else:
                        height_feet = height_add_sting + PPBD[index][4:5] + "000"
                        get_wind_dir = PPBD[index + 3][0:5][0:3]
                        get_wind_spd = PPBD[index + 3][0:5][3:5]

                        height.append(str(round(int(height_feet) * 0.3048, 1)))
                        wind_dir.append(str(get_wind_dir))
                        wind_vel.append(str(get_wind_spd))

            except:
                pass

        PPBD_output = {"group": group, "date": g_date, "time": g_time, "station": g_station,
                       "PPBD": {"height(m)": height, "wind_dir(degree)": wind_dir, "wind_vel(kt)": wind_vel}}

        return PPBD_output

class rawindsonde_decode(top_decode):
    def __init__(self, txt_name, source=""):
        super().__init__(txt_name, source)
        # self.txt_name = txt_name
        # self.source = source

    def data_merge(self, type=None, file_name="out_put", dest="",press_limit=None):
        VTCC_rws = top_decode(self.txt_name,self.source)
        TTAA_raw = VTCC_rws.get_data("TTAA")
        TTBB_raw = VTCC_rws.get_data("TTBB")
        TTCC_raw = VTCC_rws.get_data("TTCC")
        TTDD_raw = VTCC_rws.get_data("TTDD")
        PPBB_raw = VTCC_rws.get_data("PPBB")
        PPDD_raw = VTCC_rws.get_data("PPDD")

        TTAA_output = top_decode.TTAA_exc(TTAA_raw, TTAA_codition.copy())               #use .copy for duplicate dictionary only because we use del operant in dict , del or pop will delete data in dict permanently
        TTAA_df = pd.DataFrame(TTAA_output['TTAA'])

        TTBB_part1_output, TTBB_part2_output = top_decode.TTBB_exc(TTBB_raw)
        TTBB_p1_df = pd.DataFrame(TTBB_part1_output['TTBB_partA'])
        TTBB_p2_df = pd.DataFrame(TTBB_part2_output['TTBB_partB'])

        TTCC_output = top_decode.TTCC_exc(TTCC_raw, TTCC_codition)
        TTCC_df = pd.DataFrame(TTCC_output['TTCC'])

        TTDD_part1_output, TTDD_part2_outout = top_decode.TTDD_exc(TTDD_raw)

        TTDD_p1_df = pd.DataFrame(TTDD_part1_output['TTDD_partA'])
        TTDD_p2_df = pd.DataFrame(TTDD_part2_outout['TTDD_partB'])

        PPBB_output = top_decode.PPBB_or_PPDD_exc(PPBB_raw)
        PPBB_df = pd.DataFrame(PPBB_output['PPBD'])

        PPDD_output = top_decode.PPBB_or_PPDD_exc(PPDD_raw)
        PPDD_df = pd.DataFrame(PPDD_output['PPBD'])

        ############# no use TTBB part A
        P_T_Td_df = pd.merge(TTAA_df[['press(mb)', 'temp(celsius)', 'dewpoint(celsius)']],
                             TTCC_df[['press(mb)', 'temp(celsius)', 'dewpoint(celsius)']], how='outer')
        P_T_Td_df = pd.merge(P_T_Td_df[['press(mb)', 'temp(celsius)', 'dewpoint(celsius)']],
                             TTDD_p1_df[['press(mb)', 'temp(celsius)', 'dewpoint(celsius)']],
                             how='outer').dropna().astype(
            float)
        P_T_Td_df = P_T_Td_df.sort_values('press(mb)', ascending=False).drop_duplicates(subset='press(mb)')

        # print(P_T_Td_df)

        # prss wind_direction wind_speed => TTBB_partB + TTCC + TTDD_partB + PPBB + PPDD
        P_Wd_Ws_df = pd.merge(TTBB_p2_df[['press(mb)', 'wind_dir(degree)', 'wind_vel(kt)']],
                              TTCC_df[['press(mb)', 'wind_dir(degree)', 'wind_vel(kt)']], how='outer')
        P_Wd_Ws_df = pd.merge(P_Wd_Ws_df[['press(mb)', 'wind_dir(degree)', 'wind_vel(kt)']],
                              TTDD_p2_df[['press(mb)', 'wind_dir(degree)', 'wind_vel(kt)']],
                              how='outer').dropna().astype(float)
        # P_Wd_Ws_df = pd.merge(P_Wd_Ws_df[['press(mb)','wind_dir(degree)','wind_vel(kt)']],PPBB_df[['press(mb)','wind_dir(degree)','wind_vel(kt)']],how='outer')
        # P_Wd_Ws_df = pd.merge(P_Wd_Ws_df[['press(mb)','wind_dir(degree)','wind_vel(kt)']],PPDD_df[['press(mb)','wind_dir(degree)','wind_vel(kt)']],how='outer').dropna().astype(float)
        P_Wd_Ws_df = P_Wd_Ws_df.sort_values('press(mb)', ascending=False).drop_duplicates(subset='press(mb)')

        # limit data by pressure level
        if (press_limit):
            P_T_Td_df = P_T_Td_df[P_T_Td_df['press(mb)'] >= press_limit]
            print("part a limit pressure at {} mb.".format(press_limit))

        if (press_limit):
            P_Wd_Ws_df = P_Wd_Ws_df[P_Wd_Ws_df['press(mb)'] >= press_limit]
            print("part b limit pressure at {} mb.".format(press_limit))
        # print(P_Wd_Ws_df)

        P_input = P_T_Td_df['press(mb)'].tolist()
        T_input = P_T_Td_df['temp(celsius)'].tolist()
        Td_input = P_T_Td_df['dewpoint(celsius)'].tolist()
        P_b_input = P_Wd_Ws_df['press(mb)'].tolist()
        Wd_input = P_Wd_Ws_df['wind_dir(degree)'].tolist()
        Ws_input = P_Wd_Ws_df['wind_vel(kt)'].tolist()

        try:
            if (type != None):
                print("merge data and create file ....")
                merge_s1 = pd.merge(TTAA_df, TTBB_p1_df, how='outer')
                merge_s2 = pd.merge(merge_s1, TTBB_p2_df, how='outer')
                merge_s3 = pd.merge(merge_s2, TTCC_df, how='outer')
                merge_s4 = pd.merge(merge_s3, TTDD_p1_df, how='outer')
                merge_s5 = pd.merge(merge_s4, TTDD_p2_df, how='outer')
                merge_s6 = pd.merge(merge_s5, PPBB_df, how='outer')
                merge_s7 = pd.merge(merge_s6, PPDD_df, how='outer').astype(float)

                df_result = merge_s7.sort_values('press(mb)', ascending=False).dropna().drop_duplicates(
                    subset='press(mb)')

                if (type == "csv"):
                    df_result.to_csv(r"{}{}.csv".format(dest, file_name), index=False)
                if (type == "excel"):
                    df_result.to_excel(r"{}{}.xlsx".format(dest, file_name), index=False)
        except:
            print("Can't save file.")

        return P_input, T_input, Td_input, P_b_input, Wd_input, Ws_input

class rawindsonde_txt(text_rawindsonde):
    def __init__(self,file_name, source=""):
        super().__init__(file_name, source)

    def data_merge(self,type=None, file_name="out_put", dest="",press_limit=None):
        print("merge text data to new file")
        T, W, TP, FL = text_rawindsonde(self.file_name,self.source).decoder()

        # Temp_sig_df = pd.DataFrame(T['data']['Press(hPa)'])
        Temp_sig_df = pd.DataFrame(T['data'], columns=['Press(hPa)', 'Temp(celsius)', 'RelHum(%)', 'WDirn(deg)',
                                                       'WSpeed(kts)']).astype(float)
        Wind_sig_df = pd.DataFrame(W['data'], columns=['Press(hPa)', 'Temp(celsius)', 'RelHum(%)', 'WDirn(deg)',
                                                       'WSpeed(kts)']).astype(float)
        Tropopause_sig_df = pd.DataFrame(TP['data'], columns=['Press(hPa)', 'Temp(celsius)', 'RelHum(%)', 'WDirn(deg)',
                                                              'WSpeed(kts)']).astype(float)
        Freezing_sig_df = pd.DataFrame(FL['data'], columns=['Press(hPa)', 'Temp(celsius)', 'RelHum(%)', 'WDirn(deg)',
                                                            'WSpeed(kts)']).astype(float)

        # merge data step by step
        rawindsonde_df = []
        # try:
        #     rawindsonde_df = pd.merge(rawindsonde_df, Temp_sig_df, how='outer')
        # except:
        #     rawindsonde_df = Temp_sig_df

        try:
            rawindsonde_df = pd.merge(rawindsonde_df, Wind_sig_df, how='outer')
        except:
            rawindsonde_df = Wind_sig_df

        try:
            rawindsonde_df = pd.merge(rawindsonde_df, Tropopause_sig_df, how='outer')
        except:
            rawindsonde_df = Tropopause_sig_df

        try:
            rawindsonde_df = pd.merge(rawindsonde_df, Freezing_sig_df, how='outer').dropna().astype(float)
        except:
            rawindsonde_df = Freezing_sig_df.dropna().astype(float)

        rawindsonde_df = rawindsonde_df.sort_values('Press(hPa)', ascending=False).drop_duplicates(subset='Press(hPa)')

        # calculate dewpoint
        # Tdp  =(243.04 × [ln(RH/100) + ( (17.625×T) / (243.04+T) )]) / (17.625 - [ln(RH/100) +( (17.625×T) / (243.04+T) )])
        # Tdp  =(243.04 * (ln(rawindsonde_df['RelHum(%)']/100) + ( (17.625*rawindsonde_df['Temp(celsius)']) / (243.04+rawindsonde_df['Temp(celsius)']) ))) / (17.625 - (ln(rawindsonde_df['RelHum(%)']/100) +( (17.625×rawindsonde_df['Temp(celsius)']) / (243.04+rawindsonde_df['Temp(celsius)']))))
        rawindsonde_df['Dewpoint(celsius)'] = round((243.04 * (ln(rawindsonde_df['RelHum(%)'] / 100) + (
                    (17.625 * rawindsonde_df['Temp(celsius)']) / (243.04 + rawindsonde_df['Temp(celsius)'])))) / (
                                                                17.625 - (ln(rawindsonde_df['RelHum(%)'] / 100) + (
                                                                    (17.625 * rawindsonde_df['Temp(celsius)']) / (
                                                                        243.04 + rawindsonde_df['Temp(celsius)'])))), 2)

        #limit data with pressure level
        if (press_limit):
            rawindsonde_df = rawindsonde_df[rawindsonde_df['Press(hPa)'] >= press_limit]
            print("limit pressure at {} mb.".format(press_limit))

        # seperate data to input of skew-t
        P_input = rawindsonde_df['Press(hPa)'].tolist()
        T_input = rawindsonde_df['Temp(celsius)'].tolist()
        Td_input = rawindsonde_df['Dewpoint(celsius)'].tolist()
        # P_b_input = rawindsonde_df['press(mb)'].tolist()
        Wd_input = rawindsonde_df['WDirn(deg)'].tolist()
        Ws_input = rawindsonde_df['WSpeed(kts)'].tolist()

        try:
            if (type != None):
                print("merge data and create file ....")
                if (type == "csv"):
                    rawindsonde_df.to_csv(r"{}{}.csv".format(dest, file_name), index=False)
                if (type == "excel"):
                    rawindsonde_df.to_excel(r"{}{}.xlsx".format(dest, file_name), index=False)
        except:
            print("Can't save file.")

        return P_input,T_input,Td_input,Wd_input,Ws_input

class windprofiler_csv:
    def __init__(self,file_name,source=""):
        self.file_name = file_name
        self.source = source
    def data_merge(self, type=None, file_name="out_put", dest="" , press_limit = None):
        raob_df = pd.read_csv(r"{}{}.csv".format(self.source, self.file_name), header=14)
        # change value -999.0 to None
        p_t_td_df = pd.DataFrame(raob_df, columns=['PRES', ' TEMP', ' TD'])
        # replace missing value (-999.0) to None
        p_t_td_df = p_t_td_df.replace(-999.0, None).dropna().astype(float).sort_values('PRES',ascending=False).drop_duplicates(subset='PRES')

        p_wd_ws_df = pd.DataFrame(raob_df, columns=['PRES', ' WIND', ' SPEED'])
        # replace missing value (-999.0) to None
        p_wd_ws_df = p_wd_ws_df.replace(-999.0, None).dropna().astype(float).sort_values('PRES',ascending=False).drop_duplicates(subset='PRES')
        # p_wd_ws_df.to_csv("replace_output.csv",index=False)

        # if (press_limit):
        #     p_t_td_df = p_t_td_df.query('PRES > {}'.format(press_limit))
        #     print("limit pressure at {} mb.".format(press_limit))

        #limit data by pressure level
        if (press_limit):
            p_t_td_df = p_t_td_df[p_t_td_df['PRES'] >= press_limit]
            print("limit pressure at {} mb.".format(press_limit))


        P_input = p_t_td_df['PRES'].tolist()
        T_input = p_t_td_df[' TEMP'].tolist()
        Td_input = p_t_td_df[' TD'].tolist()
        P_b_input = p_wd_ws_df['PRES'].tolist()
        Wd_input = p_wd_ws_df[' WIND'].tolist()
        Ws_input = p_wd_ws_df[' SPEED'].tolist()

        try:
            if (type != None):
                print("filter data and create file ....")
                filter_na_df = raob_df.replace(-999.0, None).dropna().sort_values('PRES',ascending=False).drop_duplicates(subset='PRES')
                if (type == "csv"):
                    filter_na_df.to_csv(r"{}{}.csv".format(dest, file_name), index=False)
                if (type == "excel"):
                    filter_na_df.to_excel(r"{}{}.xlsx".format(dest, file_name), index=False)
        except:
            print("Can't save file.")

        return P_input, T_input, Td_input, P_b_input, Wd_input, Ws_input
class skew_t_create:
    def __init__(self, P_input, T_input, Td_input, Wd_input, Ws_input):
        self.P_input = P_input
        self.T_input = T_input
        self.Td_input = Td_input
        self.Wd_input = Wd_input
        self.Ws_input = Ws_input

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    def format_zero_time(self, some_string):
        try:
            if int(some_string) < 10:
                output_str = "0" + str(some_string)
            else:
                output_str = str(some_string)
        except:
            pass
        return output_str

    def send_data_to_ln(self, text, img_path, l_token):
        LINE_ACCESS_TOKEN = l_token
        url = "https://notify-api.line.me/api/notify"
        file = {'imageFile': open(img_path, 'rb')}
        data = ({
            'message': text
        })
        LINE_HEADERS = {"Authorization": "Bearer " + LINE_ACCESS_TOKEN}
        session = requests.Session()
        r = session.post(url, headers=LINE_HEADERS, files=file, data=data)
        return r

    def plot_skew_t(self, file_output_name, file_output_path, date_stamp, time_stamp, press_barb=[], wd_barb=[],
                    ws_barb=[], name_location="",
                    send_line=False, show_skt=False, Token="add_you_token", y_limit=10,
                    logo_stamp=[False, 0.15, 0.22, 0.93],
                    size=[10, 6], x_limit=[-40, 80], brab_itv=[None, None, None], hodo_itv=[None, None, None],
                    hodo_max=5 , hodo_color = False ,cape_cin_plot = False, pacel_prof_plot = False):
        # name_location = "Chiang Mai International Airport"

        p = self.P_input * units.hPa
        T = self.T_input * units.degC
        Td = self.Td_input * units.degC

        wind_speed = self.Ws_input * units.knots
        wind_dir = self.Wd_input * units.degrees
        # u, v = mpcalc.wind_components(wind_speed, wind_dir)

        if press_barb != []:
            press_barb = press_barb * units.hPa
            # print('use main added wind data')
        else:
            press_barb = p

        if wd_barb != []:
            wd_barb = wd_barb * units.degrees
            # print('use wind direction added')
        else:
            wd_barb = wind_dir

        if ws_barb != []:
            ws_barb = ws_barb * units.knots
            # print('use wind speed added')
        else:
            ws_barb = wind_speed

        # u, v = mpcalc.wind_components(ws_barb, wd_barb)
        # u, v = mpcalc.wind_components(wind_speed, wind_dir)
        u, v = mpcalc.wind_components(ws_barb, wd_barb)
        prof = parcel_profile(p, T[0], Td[0]).to('degC')

        try:
            lift_index = mpcalc.lifted_index(p, T, prof)
            lift_show = str(lift_index).replace("delta_degree_Celsius", "")
            try:
                lift_show = lift_show.replace("[", "")
                lift_show = float(lift_show.replace("]", ""))
                lift_show = round(lift_show, 2)
            except:
                lift_show = float(lift_show)
                lift_show = round(lift_show, 2)
        except:
            lift_show = "  -  "

        try:
            kindex = mpcalc.k_index(p, T, Td)
            k_index_show = float(str(kindex).replace("degree_Celsius", ""))
            k_index_show = round(k_index_show, 2)

        except:
            k_index_show = "  -  "

        try:
            lclp, lclt = mpcalc.lcl(p[0], T[0], Td[0])
            lcl_show = float(str(lclp).replace("hectopascal", ""))
            lcl_show = round(lcl_show, 2)
        except:
            lcl_show = "  -  "

        try:
            lfcp, _ = mpcalc.lfc(p, T, Td)
            lfc_show = str(lfcp).replace("hectopascal", "")
            if (lfc_show.strip() == 'nan'):
                lfc_show = '  -  '
            else:
                lfc_show = round(float(lfc_show), 2)
        except:
            lfc_show = "  -  "

        try:
            el_pressure, _ = mpcalc.el(p, T, Td, prof)
            el_show = str(el_pressure).replace("hectopascal", "")
            if (el_show.strip() == 'nan'):
                el_show = '  -  '
            else:
                el_show = round(float(el_show), 2)
        except:
            el_show = "  -  "

        try:
            # use normal solution
            cape, cin = cape_cin(p, T, Td, prof)
            cape_show = float(str(cape).replace("joule / kilogram", ""))
            cape_show = round(cape_show, 2)
            cin_show = float(str(cin).replace("joule / kilogram", ""))
            cin_show = round(cin_show, 2)
        except:
            try:
                press_nearest, neareast_index = self.find_nearest(p, value=lfc_show)
                # use skip data process
                prof2 = parcel_profile(p[int(neareast_index):], T[int(neareast_index)], Td[int(neareast_index)]).to(
                    'degC')
                cape, cin = cape_cin(p[int(neareast_index):], T[int(neareast_index):], Td[int(neareast_index):], prof2)

                cape_show = float(str(cape).replace("joule / kilogram", ""))
                cape_show = round(cape_show, 2)
                cin_show = float(str(cin).replace("joule / kilogram", ""))
                cin_show = round(cin_show, 2)
            except:
                # cannot find solution anymore and just report bug is happen.
                cape_show = "  -  "
                cin_show = "  -  "

        fig = plt.figure(figsize=(size[0], size[1]))

        logo = image.imread('logo/tmd.png')

        gs = gridspec.GridSpec(3, 3)

        skew = SkewT(fig, rotation=45, subplot=gs[:, :2])

        skew.plot(p, T, 'r',label='Temperature')
        skew.plot(p, Td, 'g',label='Dewpoint')

        if(pacel_prof_plot == True):
            skew.plot(p, prof, 'k', linewidth=1.5 ,label='Air parcel')
        if(cape_cin_plot == True):
            # Shade areas of CAPE and CIN
            skew.shade_cin(p, T, prof, Td)
            skew.shade_cape(p, T, prof)

        # skew.plot_barbs(press_barb[::5], u[::5], v[::5])
        skew.plot_barbs(press_barb[::brab_itv[0]], u[::brab_itv[1]], v[::brab_itv[2]])
        # skew.plot_barbs(p, u, v)
        skew.ax.set_ylim(1000, y_limit)
        skew.ax.set_xlabel('Temperature (°C)', fontdict=dict(size=11))
        skew.ax.set_ylabel('Pressure (hPa)', fontdict=dict(size=11))
        skew.ax.set_title('Upper Air Sounding Analysis {} \n{} {}UTC'.format(name_location, date_stamp, time_stamp),
                          loc='center', fontsize=11, fontname='Tahoma')

        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()
        skew.ax.set_xlim(x_limit[0], x_limit[1])
        skew.ax.legend()                            #make label line show on top of table

        ax = fig.add_subplot(gs[0, -1])
        ax.set_title('Hodograph', loc='center', fontname='Tahoma', fontsize=11)

        # hodograph config scaling
        try:
            v_scale_max = int(max(wind_speed)) - (int(max(wind_dir)) % 10)
            # v_scale_min = int(min(Ws_clean) - min(Ws_clean)%10)
        except:
            # default setting when wind speed is error.
            v_scale_max = 20
            # v_scale_min = 0

        h = Hodograph(ax, component_range=v_scale_max + hodo_max)
        # grid response
        if v_scale_max > 50:
            grid_hdg = 20
        elif v_scale_max > 20:
            grid_hdg = 10
        elif v_scale_max > 10:
            grid_hdg = 5
        elif v_scale_max > 5:
            grid_hdg = 2.5
        else:
            grid_hdg = 2

        h.add_grid(increment=grid_hdg)
        # h.add_grid(increment=3,color='tab:orange',linestyle= "-")
        # h.add_grid(increment=5)
        # h.plot(u, v, linewidth=1.5)
        # h.plot_colormapped(u[::hodo_itv[0]], v[::hodo_itv[1]], wind_speed[::hodo_itv[2]], linewidth=1.8)
        #h.plot_colormapped(u[::hodo_itv[0]], v[::hodo_itv[1]], wind_speed[::hodo_itv[2]], linewidth=1.8)
        if hodo_color == True:
            h.plot_colormapped(u[::hodo_itv[0]], v[::hodo_itv[1]], wind_speed[::hodo_itv[2]], linewidth=1.8)
        else:
            h.plot(u[::hodo_itv[0]], v[::hodo_itv[1]], linewidth=1.5)

        h.ax.set_xlabel('knot', fontdict=dict(size=10))
        # h.ax.set_ylabel('knot', fontdict=dict(size=10))
        h.ax.set_ylabel('', fontdict=dict(size=10))

        ax_text = fig.add_subplot(gs[1, -1])
        ax_text.axis('off')
        show_index = "\n\n\n\n\n\n\n\n\n\n\n\n" + "         " + "Atmospheric Stability\n\nCAPE:        {}  J/KG\n\nCIN:          {}  J/KG\n\nLI:           {}  °C\n\nK-index:    {}  °C\n\nLFC:          {}  hPa\n\nLCL:          {}  hPa\n\nEL:           {}  hPa".format(
            cape_show, cin_show, lift_show, k_index_show, lfc_show, lcl_show, el_show)
        ax_text.text(0.1, 0.5, show_index, verticalalignment='center', fontname='Tahoma', fontsize=11)
        if logo_stamp[0] == True:
            ax_skt = fig.add_subplot(gs[:, :2])
            ax_skt.axis('off')
            imagebox = OffsetImage(logo, zoom=logo_stamp[1])
            ab = AnnotationBbox(imagebox, (logo_stamp[2], logo_stamp[3]), frameon=False)
            ax_skt.add_artist(ab)

        img_output_path = r'{}{}.png'.format(file_output_path, file_output_name)
        line_text = "ข้อมูล Sounding สกบ.เชียงใหม่ date : {}".format(time_stamp)
        plt.savefig(img_output_path)

        if (send_line) == True:
            self.send_data_to_ln(line_text, img_output_path, Token)

        if (show_skt == True):
            plt.show()


if __name__ == "__main__":
    #Use rawindsonde or pilot data (.txt) to create skew-t ,wind brab and hodograph.
    CM_SIGLVLS_name = "CM2023111523_SIGLVLS"
    souce_file_input = "example_data\\"
    dest_file_output = "example_output\\"
    #Read data from text file, It will return to filtered output data as temperature, dew potnt , wind speed , wind direction in list.
    P2, T2, Td2, Wd2, Ws2 = rawindsonde_txt(CM_SIGLVLS_name, souce_file_input).data_merge()
    #Input pressure, temperature, dew point, wind speed ,wind direction to template (use metpy and matplotlib library to make template.)
    pilot_txt_vtcc = skew_t_create(P2, T2, Td2, Wd2, Ws2)
    pilot_txt_vtcc.plot_skew_t("Output_name_1", dest_file_output, "15-11-2023", "15:23",name_location="Chiang maistaion", size=[14, 8])


    #you can limit pressure level and make out put data to csv or excel by use parameter just like this code.
    P3, T3, Td3, Wd3, Ws3 = rawindsonde_txt(CM_SIGLVLS_name, souce_file_input).data_merge(press_limit=250,type="excel",file_name="excel_output",dest="example_output\\")
    pilot_txt_vtcc = skew_t_create(P3, T3, Td3, Wd3, Ws3)
    #but you should adjust parameter to make ratio template and decorate skew-t chart like this command.
    pilot_txt_vtcc.plot_skew_t("Output_name_2", dest_file_output, "15-11-2023", "15:23", name_location="Chiang maistaion", size=[14, 8],y_limit=200,x_limit=[-20, 40], hodo_color=True,pacel_prof_plot = True,cape_cin_plot = True)



    #Use rawindsonde or pilot code to create skew-t , hodograph
    Code_file_name = "16112566"
    Code_file_input = "example_data\\"

    pilot_code = rawindsonde_decode(Code_file_name, Code_file_input)
    P4, T4, Td4, Pb4, Wd4, Ws4 = pilot_code.data_merge(press_limit=25)
    # make skew-t from rawindsonde code

    pilot_code_plt = skew_t_create(P4, T4, Td4, Wd4, Ws4)
    #you should add more Pressure brab, wind direction and wind speed to template maker because of data from decoder is separate group.
    pilot_code_plt.plot_skew_t("decode_data", "example_output\\", "16-11-2023", "00:00", name_location="title name",hodo_itv=[2, 2, 2],press_barb=Pb4, wd_barb=Wd4, ws_barb=Ws4, hodo_color=True, size=[14, 8])



    #Use csv from wind profiler to filter and make data template.
    CSV_file_name = "20231117_0450"
    source_csv_input = "example_data\\"
    P5, T5, Td5, Pb5, Wd5, Ws5 = windprofiler_csv(CSV_file_name,source_csv_input).data_merge()       #press_limit=250

    wpfl_csv_vtcc = skew_t_create(P5, T5, Td5, Wd5, Ws5)
    wpfl_csv_vtcc.plot_skew_t("wind_profiler_output", "example_output\\", "17-11-2023", "00:00",name_location="Chiang mai", y_limit=200,press_barb=Pb5, wd_barb=Wd5, ws_barb=Ws5,brab_itv=[5, 5, 5], x_limit=[-20, 40], size=[8, 6],hodo_color=True)

    #you can use your data from different format file by copy and paste data instead example input file and enjoy with this library.

