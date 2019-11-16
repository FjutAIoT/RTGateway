import RPi.GPIO as GPIO
import time
import json
import socket
import paho.mqtt.client as mqtt

T_SensorRight = 26
T_SensorLeft  = 13
PWMA = 18
AIN1   =  22
AIN2   =  27

PWMB = 23
BIN1   = 25
BIN2  =  24

BtnPin  = 19
Gpin    = 5
Rpin    = 6
direction = 0
switch = False
broker = '192.168.43.56'
port = 8000
deviceId = '49df7fe3bf745432f6b4'
groupId = '7088591900'
# username = ''
# password = ''
topic = 'device/status/' + groupId + '/' + deviceId         # 发布主题
subTopic = 'device/desired/' + groupId + '/' + deviceId         # 订阅主题
mqtt_client = mqtt.Client(client_id = deviceId, transport = "websockets")

def t_up(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)#AIN2
        GPIO.output(AIN1,True) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)#BIN2
        GPIO.output(BIN1,True) #BIN1
        time.sleep(t_time)
        
def t_stop(t_time):
        L_Motor.ChangeDutyCycle(0)
        GPIO.output(AIN2,False)#AIN2
        GPIO.output(AIN1,False) #AIN1

        R_Motor.ChangeDutyCycle(0)
        GPIO.output(BIN2,False)#BIN2
        GPIO.output(BIN1,False) #BIN1
        time.sleep(t_time)
        
def t_down(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)#AIN2
        GPIO.output(AIN1,False) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)#BIN2
        GPIO.output(BIN1,False) #BIN1
        time.sleep(t_time)

def t_left(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)#AIN2
        GPIO.output(AIN1,False) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)#BIN2
        GPIO.output(BIN1,True) #BIN1
        time.sleep(t_time)

def t_right(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)#AIN2
        GPIO.output(AIN1,True) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)#BIN2
        GPIO.output(BIN1,False) #BIN1
        time.sleep(t_time)    
#init GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V) 
GPIO.setup(T_SensorRight,GPIO.IN)
GPIO.setup(T_SensorLeft,GPIO.IN)
    
GPIO.setup(AIN2,GPIO.OUT)
GPIO.setup(AIN1,GPIO.OUT)
GPIO.setup(PWMA,GPIO.OUT)

GPIO.setup(BIN1,GPIO.OUT)
GPIO.setup(BIN2,GPIO.OUT)
GPIO.setup(PWMB,GPIO.OUT)

L_Motor= GPIO.PWM(PWMA,100)
L_Motor.start(0)

R_Motor = GPIO.PWM(PWMB,100)
R_Motor.start(0)

'''连接成功'''
def on_connect(client, userdata, flags, rc):   # 连接后的操作 0为成功
    print("MQTT_pub 连接反馈：" + str(rc))
    mqtt_pub({'switch': switch})

'''MQTT发布消息'''
def mqtt_pub(content):
    rc = 0
    data = {"reported": content}
    data = json.dumps(data).encode('utf-8')
    rc , mid = mqtt_client.publish(topic, data, qos=1)  # 发布消息

'''MQTT订阅消息'''
def on_subscribe():
    mqtt_client.subscribe(subTopic, 1)
    mqtt_client.on_message = on_message # 消息到来处理函数

'''消息处理函数'''
def on_message(lient, userdata, msg):
    data = msg.payload.decode('utf-8')
    data = json.loads(data)
    #print (data['desired'])
    Fan_desired_handle(data['desired'])
def destroy():
    GPIO.cleanup()
def Fan_desired_handle(data):
    global switch
    global direction
    if data.__contains__('switch') == True:
        switch = data['switch']
        print("kaiguan == ",switch)
    if data.__contains__('direction') == True:
        direction = data['direction']
        print("fangxiang",direction)
    if(switch == True and direction == 1):
        t_left(50,0.5)
    if(switch == False):
        t_stop(0.5)
    if(switch == True and direction == 2):
        t_right(50,0.5)
    if(switch == True and direction == 3):
        t_up(50,1)
    if(switch == True and direction == 4):
        t_down(50,1)
    if(switch == True and direction == 5):
        direction = 5
    else:
        t_stop(0.1)
        direction = 0
    mqtt_pub(data)
def init():
    mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
    mqtt_client.on_connect = on_connect  # 连接后的操作
    mqtt_client.loop_start()
    on_subscribe()
if __name__ == "__main__":
   try:
       mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
       mqtt_client.on_connect = on_connect  # 连接后的操作
       mqtt_client.loop_start()
       on_subscribe()
       while True:
           while(switch == True and direction == 5):
               SR = GPIO.input(T_SensorRight)
               SL = GPIO.input(T_SensorLeft)
               if SL == False and SR == False:
                    t_up(50,0)
               elif SL == True and SR ==False:
                    t_left(50,0)
               elif SL==False and SR ==True:
                    t_right(50,0)
               else:
                    t_stop(0)
   except Exception:
       pass
   finally:
       destroy()
