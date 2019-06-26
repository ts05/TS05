import numpy as np
import os

# 데이터 순서 --> pir , light , temp , humid

def Data_load(exist, X, Y):

    current_path = os.getcwd()

    classfication = Labeling_tag(exist)
    print(classfication)
    os.chdir("Labeled_data_out/" + exist + "/")

    typepath = os.getcwd()
    os.chdir("PIR/")

    for filename in os.listdir("."):
        print("filename ::: " + filename)
        fdate = filename.split("_")

        fpirn = filename
        ftempn = ""
        flightn = ""
        fhumidn = ""

        os.chdir(typepath)
        os.chdir("TEMP/")
        for typelist in os.listdir("."):
            filetyname = typelist.split("_")
            if filetyname[2:5] == fdate[2:5]:
                ftempn = typelist
                print(ftempn)
                break

        os.chdir(typepath)
        os.chdir("LIGHT/")
        for typelist in os.listdir("."):
            filetyname = typelist.split("_")
            if filetyname[2:5] == fdate[2:5]:
                flightn = typelist
                print(flightn)
                break

        os.chdir(typepath)
        os.chdir("HUMID/")
        for typelist in os.listdir("."):
            filetyname = typelist.split("_")
            if filetyname[2:5] == fdate[2:5]:
                fhumidn = typelist
                print(fhumidn)
                break

        os.chdir(typepath)

        data_pir = np.loadtxt("PIR/" + fpirn, delimiter=",", dtype=np.float32)
        data_temp = np.loadtxt("TEMP/" + ftempn, delimiter=",", dtype=np.float32)
        data_light = np.loadtxt("LIGHT/" + flightn, delimiter=",", dtype=np.float32)
        data_humid = np.loadtxt("HUMID/" + fhumidn, delimiter=",", dtype=np.float32)

        for i in range(0, data_pir.__len__()):
            X.append(data_pir[i])
            X.append(data_light[i])
            X.append(data_temp[i])
            X.append(data_humid[i])
            Y.append(classfication)

    os.chdir(current_path)

def Labeling_tag(exist):
    if exist == "None":
        return [1 , 0]
    #elif exist == "Animal":
    #    return [0, 1, 0]
    elif exist == "Human":
        return [0 , 1]