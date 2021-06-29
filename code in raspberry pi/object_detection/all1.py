######## rasp pet feeder main code #########


# Import packages
from socket_base import Reader# socket communication
from socket_address import host, hostname, port_server, target, port_client
import os
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import tensorflow as tf
import argparse
import sys
import smbus
import RPi.GPIO as GPIO
import schedule
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

###########################
# servo motor, temperature and pressure setting
###########################
SERVO1 = 16
SERVO2 = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO1, GPIO.OUT)
GPIO.setup(SERVO2, GPIO.OUT)
# i2c setting
bus = smbus.SMBus(1)
address = 0x48

def setServoAngle(servo, angle):
    pwm = GPIO.PWM(servo, 50)
    pwm.start(8)
    dutyCycle = angle / 18. +3.
    pwm.ChangeDutyCycle(dutyCycle)
    time.sleep(0.1)
    pwm.stop()

echopin=12
trigpin=10
#cam = cv2.VideoCapture(0) # 打开摄像头
#cam.set(3, 1024) # 设置图像宽度
#cam.set(4, 768) # 设置图像高度
def iniDist():
    #GPIO.setup(vccpin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(trigpin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(echopin, GPIO.IN)

iniDist()

def getDist():
    time.sleep(0.1)
    GPIO.output(trigpin, GPIO.HIGH)
    time.sleep(0.00002)
    GPIO.output(trigpin, GPIO.LOW)
    while GPIO.input(echopin)==GPIO.LOW:
        pass
    t=time.time()
    while GPIO.input(echopin)==GPIO.HIGH:
        pass
    t=time.time()-t
    if t<0:
        print('warn')
        return -1
    return t*340/2

def meassureDist():
    dist=[]
    for i in range(5):
        tempdist = getDist()
        if tempdist!=-1:
            dist.append(tempdist)
    return np.sum(dist)/5

# temperature reading function
def read_temp():
    bus.write_byte(address,0x41)
    bus.read_byte(address)
    return bus.read_byte(address)

class Hx711():
    def setup(self):
        self.SCK = 13    # 物理引脚第11号，时钟
        self.DT = 15     #物理引脚第13号，数据
        self.flag=1      #用于首次读数校准
        self.initweight=0
        self.weight=0
        self.delay=0.09
        #self.count=[0,0,0,0]
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
        GPIO.setup(self.SCK, GPIO.OUT)      # Set pin's mode is output
        GPIO.setup(self.DT, GPIO.IN)
        GPIO.setup(self.DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
    def weigh(self):
        GPIO.output(self.SCK,0)
        if GPIO.input(self.SCK):
            time.sleep(self.delay)
            #self.count[0]+=1
        value=0
        
        while GPIO.input(self.DT):
            time.sleep(self.delay)
            #self.count[1]+=1
        for i in range(24):
            GPIO.output(self.SCK,1)
            if(0==GPIO.input(self.SCK)):
                time.sleep(self.delay)
                #self.count[2]+=1
            value=value<<1      #左移一位，相当于乘2
            GPIO.output(self.SCK,0)
            if GPIO.input(self.SCK):
                time.sleep(self.delay)
                #self.count[3]+=1
            if GPIO.input(self.DT)==1:
                value+=1
        GPIO.output(self.SCK,1)
        GPIO.output(self.SCK,0)
        #value=int(value/1905)      #1905为我传感器的特性值，不同传感器值不同。可先注释此步骤，再去测一物体A得到一个值X,而后用X除以A的真实值即可确定特性值
        if self.flag==1:
            self.flag=0
            self.initweight=value        #初始值
            return 0
        else:
            self.weight = (value-self.initweight)  #当前值减初始值得测量到的重量
            self.weight = 1.8*self.weight/1905.0+0.6
            if self.weight>1000:
                self.weight = 0 
            return self.weight
            #if(self.weight > 200):
                #setServoAngle(SERVO1,120)
                #time.sleep(0.1)
            
            ###########################
            

        
        
#######################################
# camera and objection detector setting
#######################################
# Set up camera constants
IM_WIDTH = 640
IM_HEIGHT = 480


# Select camera type (if user enters --usbcam when calling this script,
# a USB webcam will be used)
camera_type = 'picamera'
parser = argparse.ArgumentParser()
parser.add_argument('--usbcam', help='Use a USB webcam instead of picamera',
        action='store_true')
args = parser.parse_args()
if args.usbcam:
    camera_type = 'usb'

# This is needed since the working directory is the object_detection folder.
sys.path.append('..')

# Import utilites
#from utils import label_map_util
#from utils import visualization_utils as vis_util

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'data','mscoco_label_map.pbtxt')

# Number of classes the object detector can identify
NUM_CLASSES = 90

## Load the label map.
# Label maps map indices to category names, so that when the convolution
# network predicts `5`, we know that this corresponds to `airplane`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    #od_graph_def = tf.raphDef()
    od_graph_def = tf.compat.v1.GraphDef()
    #with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    #sess = tf.Session(graph=detection_graph)
    sess = tf.compat.v1.Session(graph=detection_graph)


# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX




######################################
# socket communication for uploading information to the server
######################################
print('finish configuring picamera')
pic_client = Reader(hostname, port_client)
print('finish socket connecting')

######################################
# feeding function with pressure controll
######################################
# pressure detector
Pressure=Hx711()
Pressure.setup()
Pressure.weigh()
feed_sign = 0
feed_start = 0
print('finish configuring pressure detector')
# feeding program
feed_amount = 0 
def feeding(food_amount):
    global feed_amount
    global feed_sign
    feed_amount = food_amount
    
    feed_start = time.time()
    while True:
        weight = Pressure.weigh()
        print('current weight',weight,'target',food_amount)
        if (float(weight) < float(food_amount)):
            setServoAngle(SERVO1,180)
            time.sleep(1)
        else:
            feed_sign = time.time()
            break


def feed_check(pressure):
    global feed_amount
    print('feed checking!!!!!!!!',feed_amount,pressure)
    return float(feed_amount)-pressure

open_flag=0
def food_open():
    print('open!!!!')
    setServoAngle(SERVO2,90)
    global open_flag
    open_flag = 0
    
    
# in case people come, cover the food bowl
def close():
    global open_flag
    open_flag = 1
    print('close!!!!')
    setServoAngle(SERVO2,0)
    time.sleep(1)
    
    
######################################
# watchdog for feedtime changing
######################################
feed_time = {}
f = open('feedtime.txt','r')
feedtime=f.read().split('\n')
for setting in feedtime:
    if setting=='':
        continue
    _time = setting.split(' ')[0]
    amount = setting.split(' ')[1]
    feed_time[_time] = int(amount)
f.close()

for set_time in feed_time:
    schedule.every().day.at(set_time).do(feeding, feed_time[set_time])
print('finish configuring schedule')


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global feed_time
        if event.src_path =='./feedtime.txt':
            f = open(event.src_path,'r')
            data = f.read().split('\n')
            f.close()
            print(data)
            for setting in data:
                if setting=='':
                    continue
                time = setting.split(' ')[0]
                amount = setting.split(' ')[1]
                feed_time[time] = amount
            for set_time in feed_time:
                schedule.every().day.at(set_time).do(feeding, feed_time[set_time])


path =  "./"
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()
print('finish configuring watchdog')


########################################
### main program picamera
########################################

if camera_type == 'picamera':
    # Initialize Picamera and grab reference to the raw capture
    camera = PiCamera()
    camera.resolution = (IM_WIDTH,IM_HEIGHT)
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
    rawCapture.truncate(0)
    tempnum = 0

    for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        
        schedule.run_pending() # feed time control
        print('weighing!!!!',Pressure.weigh())
        if open_flag!=0:
            open_flag += 1
            
        if open_flag==10:
            food_open()
        
        # temperature reading
        if (tempnum == 0):
            temperature = 28+0.2*(read_temp()-188-28)-0.5
            pic_client.subscribePublisher(target, port_server)
            pic_client.send_temperature(temperature)
        tempnum = (tempnum + 1) % 10
        
        # feed check
        if feed_sign!=0:
            if (time.time()-feed_sign)<=180 and (int(time.time()-feed_sign))%5==0:
                print('eat status check!')
            #feed_sign = 0
                weight = Pressure.weigh() # messure the current weight
                eating = feed_check(weight)
                if eating<0:
                    eating=0
                pic_client.subscribePublisher(target, port_server)
                pic_client.send_eat_status(eating)
            elif (time.time()-feed_sign)>180:
                feed_sign = 0
        # if no creature is around, skip the object detection process
        result = meassureDist()
        # print(result*100,'cm')
        if (result > 0.5):
            rawCapture.truncate(0)
            cv2.destroyAllWindows()
            continue
        print(result*100,'cm')
        t1 = cv2.getTickCount()

        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        frame = np.copy(frame1.array)
        frame.setflags(write=1)
        frame_expanded = np.expand_dims(frame, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: frame_expanded})


        
        
        # cat
        if (classes[0][0]==17 or classes[0][1] == 17):
            cv2.imwrite('temp_cat.jpg',frame)
            pic_client.subscribePublisher(target, port_server)
            pic_client.send_pic('temp_cat.jpg','b')
            time.sleep(1)
        
        # dog
        elif(classes[0][0]==18):
            print("Here is a dog!")
            close() # cover the bowl
            cv2.imwrite('temp_dog.jpg',frame)
            pic_client.subscribePublisher(target, port_server)
            pic_client.send_pic('temp_dog.jpg','a')
            time.sleep(1)
        
        # people, send a waring
        elif(classes[0][0]==1 and scores[0][0]*100 >= 70):
            print("Here is a person!")
            close() # cover the bowl
            pic_client.subscribePublisher(target, port_server)
            pic_client.send_warning('people')
            time.sleep(1)
            
        
            
            
        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
                frame,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=0.40)

        cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)

        # All the results have been drawn on the frame, so it's time to display it.
        # cv2.imshow('Object detector', frame)

        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc = 1/time1
        

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

        rawCapture.truncate(0)

    camera.close()

cv2.destroyAllWindows()



