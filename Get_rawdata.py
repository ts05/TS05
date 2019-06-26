import csv
import threading
import picamera
import spidev, time
import Adafruit_DHT as Adafruit_DHT # for dht11 sensor
import datetime as dt
import time
from multiprocessing import Process, Value
from mcp3208 import MCP3208
import numpy as np

def initDHT():

    isSuccess = False
    DHT_HUMID_DATA.value,DHT_TEMP_DATA.value = Adafruit_DHT.read_retry(sensor,DHT_PIN)
    
    if DHT_HUMID_DATA.value is not None and DHT_TEMP_DATA.value is not None:
        isSuccess = True
        
    else:
        print("Failed to get reading from DHT sensor.")
        
    return isSuccess

def readDHT():

    while True:
	
        humidity,temperature = Adafruit_DHT.read_retry(sensor,DHT_PIN)
        
        if humidity is not None and temperature is not None:

            DHT_HUMID_DATA.value = humidity
            DHT_TEMP_DATA.value = temperature
            print("--------------------------Read !------------------------")
            #time.delay(5)
 
def printDHT():

    i = 1

    while True:

        print('Humidity : ', DHT_HUMID_DATA.value)

        print('TEMP : ', DHT_TEMP_DATA.value)

        print(i)

        i = i+1
 

DHT_TEMP_DATA = Value('d', -1.0)
DHT_HUMID_DATA = Value('d', -1.0)
sensor = Adafruit_DHT.DHT11
DHT_PIN = 21
 
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

slice_time = 0.01
serial_num = 1

pir_channel = 0
light_channel = 5
test_channel = 2

print_text = ""
serial_text = ""

pir_data = list()
light_data = list()

one_sec = False

adc = MCP3208()

with picamera.PiCamera() as camera:

	start_day = str(dt.datetime.now()).split(".")
	start = start_day[0].replace(" ","_")
	start = start.replace(":","-")
	
	camera.resolution = (320,240)
	camera.framerate = 10
	camera.annotate_text_size = 10
	
	camera.start_preview()
	camera.start_recording("Video/Video_" + str(start) + ".h264")

	camera.annotate_background = picamera.Color('black')


	PIR_fn = "Data_PIR_" + str(start) + ".txt"
	Light_fn = "Data_Light_" + str(start) + ".txt"
	Temp_fn = "Data_Temp_" + str(start) + ".txt"
	Humid_fn = "Data_Humid_" + str(start) + ".txt"
	
	f1 = open("PIR/" + PIR_fn,"w")
	f2 = open("LIGHT/" + Light_fn,"w")
	f3 = open("TEMP/" + Temp_fn,"w")
	f4 = open("HUMID/" + Humid_fn,"w")
 
	if not initDHT():

		print('init Failed')

		exit()

	th1 = Process(target=readDHT)
	th1.start()

	start_time = time.time()

	while(True):

		try:

			cur_time = time.time()

			if cur_time - start_time >= slice_time:

				start_time = cur_time
 
				pir = adc.read(pir_channel)
				light = adc.read(light_channel)
				DHT_TEMP_DATA.value = round(DHT_TEMP_DATA.value,2)
				DHT_HUMID_DATA.value = round(DHT_HUMID_DATA.value,2)
				
				f1.write(str(pir) + " ")
				f2.write(str(light) + " ")
				f3.write(str(DHT_TEMP_DATA.value) + " ")
				f4.write(str(DHT_HUMID_DATA.value) + " ")

				serial_num += 1

				pir_data.append(pir)
				light_data.append(light)
				
				serial_text = "Serial_num :: " + str(serial_num)
				
				one_sec = True

			if serial_num % 10 == 0 and one_sec:
				
				print_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S\n')
				
				print_text += ("PIR :: %d %d %d %d %d %d %d \n" % (pir_data[0],pir_data[1],pir_data[2],pir_data[3],pir_data[4],pir_data[5],pir_data[6]))
				print_text += ("LIGHT :: %d %d %d %d %d %d %d \n" % (light_data[0],light_data[1],light_data[2],light_data[3],light_data[4],light_data[5],light_data[6]))
				print_text += ("DHT :: TEMP = %.2f , Humidity %.2f \n" %(DHT_TEMP_DATA.value,DHT_HUMID_DATA.value))
				
				pir_data = []
				light_data = []
				testpir_data = []
			
			if serial_num % 10 == 0:
				
				camera.annotate_text = print_text + serial_text
				
				print("DHT :: TEMP = %f , Humidity %f" %(DHT_TEMP_DATA.value,DHT_HUMID_DATA.value))
				print("PIR :: ADC = %s(%d) " %(hex(pir), pir))
				print("LIGHT :: ADC = %s(%d) " %(hex(light), light))
				print("Serial Number :: %d" % (serial_num))
				print("")

				one_sec = False

		except KeyboardInterrupt:

			break;


	f1.close()
	f2.close()
	f3.close()
	f4.close()
	
	th1.terminate()

	camera.stop_preview()

	camera.close()
