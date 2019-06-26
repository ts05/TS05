import os
import numpy as np
import pandas as pd

#filelist = ["PIR", "Light", "Temp", "Humid"]

def file_exist(sensor_num, file_name):

    for filename in os.listdir("."):
        if filename.startswith("pir" + str(sensor_num) + file_name):
            print(filename)
            return True

    return False

def set_filenum(fname):

    k = 0
    while (True):
        if (os.path.exists(fname + str(k) + ".csv")):
            k = k + 1
        else:
            return k

while (True):
    date = input("Write the date (Month-day) (if insert 0, exit) :: ")
    if (date == "0"):
        break
    time = input("Write the time (HH-MM-SS) :: ")
    time.replace("-","_")
    pre_file_name = "_data_" + date + "_" + time

    current_path = os.getcwd()
    # sr 초 단위로 pir 파일 쌓아서 라벨링
    sr = 15  #0.15초

    year = "2019-"
    fname = year + date + "_" + time

    fpir = "Data_PIR_" + fname + ".txt"
    ftemp = "Data_TEMP_" + fname + ".txt"
    flight = "Data_LIGHT_" + fname + ".txt"
    fhumid = "Data_HUMID_" + fname + ".txt"

    if os.path.exists("Data/PIR/" + fpir) is False:
        print("File PIR is Not exist!!")
        break

    if os.path.exists("Data/TEMP/" + ftemp) is False:
        print("File TEMP is Not exist!!")
        break

    if os.path.exists("Data/LIGHT/" + flight) is False:
        print("File Light is Not exist!!")
        break

    if os.path.exists("Data/HUMID/" + fhumid) is False:
        print("File Humid is Not exist!!")
        break

    while (True):

        tag = input("1. Exist   /   2. None  :: ")

        if tag == "1":
            tag_exist = "Exist"
        elif tag == "2":
            tag_exist = "None"
        elif tag == "0":
            break
        else:
            print("Error..!")
            break

        outmenu = False
        while True:

            sn_start = input("Start Sn :: ")
            sn_end = input("End Sn :: ")

            sn_start = int(sn_start)
            sn_end = int(sn_end)

            if sn_start >= sn_end :
                print("End value is bigger then start value..!")
            elif sn_start == 0 or sn_end == 0:
                outmenu = True
            else:
                break

        if outmenu:
            break

        flabeled = "Labeled_"

        data_pir = np.loadtxt("Data/PIR/" + fpir)
        data_temp = np.loadtxt("Data/TEMP/" + ftemp)
        data_light = np.loadtxt("Data/LIGHT/" + flight)
        data_humid = np.loadtxt("Data/HUMID/" + fhumid)

        os.chdir("Labeled_data_4/" + tag_exist + "/")

        topmenu = os.getcwd()

        #pir 기준 파일 있는지 검사
        os.chdir("PIR/")
        count = set_filenum(flabeled + "PIR_" + fname + "_" + tag_exist)

        X = list()
        for j in range(sn_start, sn_end, sr):
            if j >= sn_end:
                break
            slice_data = data_pir[j - 1: j - 1 + 100]

            np.asarray(slice_data)
            X.append(slice_data)

        dataframe = pd.DataFrame(X)
        dataframe.to_csv("Labeled_PIR_" + fname + "_" + tag_exist + str(count) + ".csv", header=False, index=False)
        print(fpir)
        print(ftemp)
        print(flight)
        print(fhumid)

        os.chdir(topmenu)

        os.chdir("Light/")
        X = list()
        for j in range(sn_start, sn_end, sr):
            if j >= sn_end:
                break

            slice_data = data_light[j - 1: j - 1 + 100]

            np.asarray(slice_data)
            X.append(slice_data)

        dataframe = pd.DataFrame(X)
        dataframe.to_csv("Labeled_Light_" + fname +  "_" + tag_exist + str(count) + ".csv", header=False, index=False)

        os.chdir(topmenu)
        os.chdir("Temp/")

        X = list()
        for j in range(sn_start, sn_end, sr):
            if j >= sn_end:
                break

            slice_data = data_temp[j - 1: j - 1 + 100]

            np.asarray(slice_data)
            X.append(slice_data)

        dataframe = pd.DataFrame(X)
        dataframe.to_csv("Labeled_TEMP_" + fname + "_" + tag_exist + str(count) + ".csv", header=False, index=False)

        os.chdir(topmenu)

        os.chdir("Humid/")

        X = list()
        for j in range(sn_start, sn_end, sr):
            if j >= sn_end:
                break

            slice_data = data_humid[j - 1: j - 1 + 100]

            np.asarray(slice_data)
            X.append(slice_data)

        dataframe = pd.DataFrame(X)
        dataframe.to_csv("Labeled_HUMID_" + fname +  "_" + tag_exist + str(count) + ".csv", header=False, index=False)

        print("Make " + tag_exist + str(count))

        os.chdir(current_path)