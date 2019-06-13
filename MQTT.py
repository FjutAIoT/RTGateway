import RPi.GPIO as GPIO
import LED_1
import LED_2
import LED_3
import Alarm
import Fan
import Fan_2
import DHT11
import Flame
import Light
import schedule

'''关闭释放资源'''
def destroy():
    GPIO.cleanup()  # 释放资源

if __name__ == "__main__":
    try:
        LED_1.init()
        LED_2.init()
        LED_3.init()
        Alarm.init()
        Fan.init()
        Fan_2.init()
        DHT11.init()
        Flame.init()
        Light.init()
        schedule.every(120).seconds.do(DHT11.get_data)
        schedule.every(2).seconds.do(Flame.get_data)
        schedule.every(20).seconds.do(Light.get_data)
        while True:
            schedule.run_pending()
    except Exception:
        print (Exception)
    finally:
        destroy()
