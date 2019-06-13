# -*- coding: UTF-8 -*-
#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import json
import socket
import paho.mqtt.client as mqtt

LED_GPIO = 16

broker = '118.24.169.3'
port = 80
deviceId = '902239d0495d294563e9'
groupId = '9915595732'
# username = ''
# password = ''
topic = 'device/status/' + groupId + '/' + deviceId  		# 发布主题
subTopic = 'device/desired/' + groupId + '/' + deviceId 		# 订阅主题
mqtt_client = mqtt.Client(client_id = deviceId, transport = "websockets")

'''台灯属性值'''
switch = False

'''初始化'''
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # 设置GPIO编码模式
GPIO.setup(LED_GPIO, GPIO.OUT)  # PCF8591引脚设置为输出模式（OUT）

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
	# print (data['desired'])
	Fan_desired_handle(data['desired'])

# '''初始化设置'''
# def setup():
# 	GPIO.setwarnings(False)
# 	GPIO.setmode(GPIO.BCM)#设置GPIO编码模式
# 	GPIO.setup(FAN_GPIO, GPIO.OUT)#PCF8591引脚设置为输出模式（OUT）
#
# 	pwm = GPIO.PWM(FAN_GPIO, 50)
# 	pwm.start(100)
# 	time.sleep(2)
# 	pwm.stop()

'''关闭释放资源'''
def destroy():
	GPIO.cleanup()               #释放资源

'''操作LED灯 '''
def Fan_desired_handle(data):
	global switch
	if data.__contains__('switch') == True:
		switch = data['switch']

	if switch == True:
		GPIO.output(LED_GPIO, 0)
	else:
		GPIO.output(LED_GPIO, 1)

	mqtt_pub(data)

def init():
	mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
	mqtt_client.on_connect = on_connect  # 连接后的操作
	mqtt_client.loop_start()
	on_subscribe()

# if __name__ == "__main__":
# 	# setup()
# 	try:
# 		mqtt_client.connect(broker, port, 30)  # 设置地址端口与维持心跳
# 		mqtt_client.on_connect = on_connect  # 连接后的操作
# 		mqtt_client.loop_start()
# 		on_subscribe()
# 		while True:
# 			pass
# 	except Exception:
# 		pass
# 	finally:
# 		destroy()