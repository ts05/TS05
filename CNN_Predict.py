import csv
import threading
import picamera
import spidev, time
import Adafruit_DHT as Adafruit_DHT  # for dht11 sensor

import datetime as dt
import time
from multiprocessing import Process, Value
from mcp3208 import MCP3208

import numpy as np
import queue
from collections import deque

DIR = '/home/pi/Get_data/'

from keras.utils import *
import tensorflow as tf
import numpy as np
from keras.models import model_from_json
from firebase import firebase

firebase = firebase.FirebaseApplication('https://retest-9f308.firebaseio.com/', None)

#modelname = input("Insert_modelname :: ")
modelname = "Model_cnn_merge_predict"
modelname_json = "Models/" + modelname + ".json"
modelname_weight = "Models/" + modelname + ".h5"
json_file = open(modelname_json,"r")

loaded_model_json = json_file.read()
json_file.close()

model = tf.keras.models.model_from_json(loaded_model_json)
model.load_weights(modelname_weight)
print("Model Loaded...!")


exist_recent = ["None"] * 3
i = 0


def decision(predict):
    global i
    global exist_recent
    print(predict)
    i += 1
    i = i % 3 
    
    if predict[0][0] > predict[0][1]:
        exist_recent[i] = "None"
    else:
        exist_recent[i] = "Exist"
    
    count_exist = exist_recent.count("Exist")
    
    if count_exist > 0:
        return "Exist"
    else:
        return "None"
   
def initDHT():
    isSuccess = False
    DHT_HUMID_DATA.value, DHT_TEMP_DATA.value = Adafruit_DHT.read_retry(sensor, DHT_PIN)

    if DHT_HUMID_DATA.value is not None and DHT_TEMP_DATA.value is not None:
        isSuccess = True

    else:
        print("Failed to get reading from DHT sensor.")

    return isSuccess


def readDHT():
    while True:

        humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_PIN)

        if humidity is not None and temperature is not None:
            DHT_HUMID_DATA.value = humidity
            DHT_TEMP_DATA.value = temperature
            print("--------------------------Read !------------------------")

def printDHT():
    i = 1

    while True:
        print('Humidity : ', DHT_HUMID_DATA.value)

        print('TEMP : ', DHT_TEMP_DATA.value)

        print(i)

        i = i + 1

def sendDB():
    global light
    
    firebase.put('/sensor/dht/', 'temperature', DHT_TEMP_DATA.value)
    firebase.put('/sensor/dht/', 'humidity', DHT_HUMID_DATA.value)
    firebase.put('/sensor/dht/', 'light', light)
       
def sendExistDB():
    global exist_out
    
    firebase.put('/sensor/dht/', 'Exist', exist_out)

def sendNoneDB():
    global exist_out
    firebase.put('/sensor/dht/', 'Exist', exist_out)
    
DHT_TEMP_DATA = Value('d', -1.0)
DHT_HUMID_DATA = Value('d', -1.0)
sensor = Adafruit_DHT.DHT11
DHT_PIN = 21

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

slice_time = 0.01
serial_num = 0

pir_channel = 0
light_channel = 5
test_channel = 2

print_text = ""
serial_text = ""

pir_data = list()
light_data = list()
temp_data = list()
humid_data = list()

one_sec = False

adc = MCP3208()

light = 0
after_one_sec = False
exist_out = "None"
before_exist_out = "None"

'''
속도 개선으로 predict 코드에서는 카메라와 카메라 텍스트를 주석 처리해둠. terminal 상으로만 출력.
'''

with picamera.PiCamera() as camera:
    start_day = str(dt.datetime.now()).split(".")
    start = start_day[0].replace(" ", "_")
    start = start.replace(":", "-")
    '''
    camera.resolution = (320, 240)
    camera.framerate = 10
    camera.annotate_text_size = 10

    camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    '''
    PIR_fn = "Data_PIR_" + str(start) + ".txt"
    Light_fn = "Data_Light_" + str(start) + ".txt"
    Temp_fn = "Data_Temp_" + str(start) + ".txt"
    Humid_fn = "Data_Humid_" + str(start) + ".txt"

    if not initDHT():
        print('init Failed')

        exit()

    th1 = Process(target=readDHT)
    th1.start()
    
    start_time = time.time()
    
    while (True):

        try:

            cur_time = time.time()

            if cur_time - start_time >= slice_time:
                start_time = cur_time

                pir = adc.read(pir_channel)

                light = adc.read(light_channel)

                DHT_TEMP_DATA.value = round(DHT_TEMP_DATA.value, 2)
                DHT_HUMID_DATA.value = round(DHT_HUMID_DATA.value, 2)

                serial_num += 1

                if after_one_sec:
                    pir_data.append(pir)
                    light_data.append(light)
                    temp_data.append(DHT_TEMP_DATA.value)
                    humid_data.append(DHT_HUMID_DATA.value)
                    
                    del pir_data[0]
                    del light_data[0]
                    del temp_data[0]
                    del humid_data[0]
                   
                else:
                    pir_data.append(pir)
                    light_data.append(light)
                    temp_data.append(DHT_TEMP_DATA.value)
                    humid_data.append(DHT_HUMID_DATA.value)

                one_sec = True


            if serial_num % 100 == 0 and one_sec:
                '''
                print_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S\n')

                print_text += ("PIR :: %d %d %d %d %d %d %d \n" % (
                    pir_data[0], pir_data[1], pir_data[2], pir_data[3], pir_data[4], pir_data[5], pir_data[6]))

                print_text += ("LIGHT :: %d %d %d %d %d %d %d \n" % (
                    light_data[0], light_data[1], light_data[2], light_data[3], light_data[4], light_data[5],
                    light_data[6]))

                print_text += ("DHT :: TEMP = %.2f , Humidity %.2f \n" % (DHT_TEMP_DATA.value, DHT_HUMID_DATA.value))
                '''
                after_one_sec = True

            if serial_num % 10 == 0:
                '''
                serial_text = "Serial_num :: " + str(serial_num)
                
                camera.annotate_text = print_text + serial_text + "\n" + exist_out
    
                
                print("DHT :: TEMP = %f , Humidity %f" % (DHT_TEMP_DATA.value, DHT_HUMID_DATA.value))

                print("PIR :: ADC = %s(%d) " % (hex(pir), pir))

                print("LIGHT :: ADC = %s(%d) " % (hex(light), light))

                print("Serial Number :: %d" % (serial_num))

                print("")
                '''
                one_sec = False
               
			# Predict 주기 :: 0.3초
            if serial_num % 30 == 0 and after_one_sec:
                
                data_pir = np.asarray(pir_data)
                data_light = np.asarray(light_data)
                data_temp = np.asarray(temp_data)
                data_humid = np.asarray(humid_data)
                
                x_data = np.reshape(data_pir, (1, 10, 10, 1))
                
                others = list()
                others.append(light_data[serial_num % 50])
                others.append(temp_data[serial_num % 50])
                others.append(humid_data[serial_num % 50])
                
                others = np.asarray(others)
                others = np.reshape(others, (1, 3))
                
                exist_out = decision(model.predict([x_data, others]))
                
				# Firebase로는 기존 값과 변화가 있을 때에만 보냄
                if exist_out == "Exist" and before_exist_out == "None":
                    th3 = Process(target=sendExistDB)
                    th3.start()
                    before_exist_out = "Exist"
                elif exist_out == "None" and before_exist_out == "Exist":
                    th4 = Process(target=sendNoneDB)
                    th4.start()
                    before_exist_out = "None"
                    
                print(exist_out)
                
            if serial_num % 500 == 0:
                
                th2 = Process(target=sendDB)
                th2.start()
                
        except KeyboardInterrupt:

            break

    th1.terminate()
    th2.terminate()
    th3.terminate()
    th4.terminate()
    '''
    camera.stop_preview()

    camera.close()
    '''
