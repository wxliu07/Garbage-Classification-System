# generated by maixhub, tested on maixpy3 v0.4.8
# copy files to TF card and plug into board and power on
import sensor, image, lcd, time, utime
import KPU as kpu
import gc, sys
from machine import Timer,PWM
from modules import ultrasonic
from Maix import GPIO
from fpioa_manager import fm

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
tim1 = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PWM)
S1 = PWM(tim, freq=50, duty=0, pin=31)
S2 = PWM(tim1, freq=50, duty=0, pin=32)

fm.register(22, fm.fpioa.GPIOHS0, force = True)
device1 = ultrasonic(fm.fpioa.GPIOHS0)

fm.register(30,fm.fpioa.GPIO0)
high=GPIO(GPIO.GPIO0,GPIO.OUT)


input_size = (224, 224)
labels = ['Other waste', 'Harmful waste', 'Recyclable waste', 'Kitchen waste']
anchors = [1.97, 1.78, 1.69, 1.41, 2.06, 0.78, 4.56, 4.16, 0.94, 2.09]
def warn():
    i = 0
    n1 = 0
    while i < 10:
        distance1 = device1.measure(unit = ultrasonic.UNIT_CM, timeout = 3000000)
        if distance1 < 19:
            n1 += 1
        if n1 == 5:
            high.value(1)
            utime.sleep_ms(500)
            high.value(0)
            utime.sleep_ms(500)
            high.value(1)
            utime.sleep_ms(500)
            high.value(0)
            utime.sleep_ms(500)
            break
        i += 1

def Servo1(servo,angle):
    S1.duty((angle+90)/180*10+2.5)

def Servo2(servo,angle):
    S2.duty((angle+90)/180*10+2.5)
    
def lcd_show_except(e):
    import uio
    err_str = uio.StringIO()
    sys.print_exception(e, err_str)
    err_str = err_str.getvalue()
    img = image.Image(size=input_size)
    img.draw_string(0, 10, err_str, scale=1, color=(0xff,0x00,0x00))
    lcd.display(img)

def main(anchors, labels = None, model_addr="/sd/m.kmodel", sensor_window=input_size, lcd_rotation=0, sensor_hmirror=False, sensor_vflip=False):
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing(sensor_window)
    sensor.set_hmirror(sensor_hmirror)
    sensor.set_vflip(sensor_vflip)
    sensor.run(1)

    lcd.init(type=1)
    lcd.rotation(lcd_rotation)
    lcd.clear(lcd.WHITE)

    if not labels:
        with open('labels.txt','r') as f:
            exec(f.read())
    if not labels:
        print("no labels.txt")
        img = image.Image(size=(320, 240))
        img.draw_string(90, 110, "no labels.txt", color=(255, 0, 0), scale=2)
        lcd.display(img)
        return 1
    try:
        img = image.Image("startup.jpg")
        lcd.display(img)
    except Exception:
        img = image.Image(size=(320, 240))
        img.draw_string(90, 110, "loading model...", color=(255, 255, 255), scale=2)
        lcd.display(img)

    try:
        task = None
        task = kpu.load(model_addr)
        kpu.init_yolo2(task, 0.5, 0.3, 5, anchors) # threshold:[0,1], nms_value: [0, 1]

        n = [0, 0, 0, 0]
        num = 0
        allNum = 0
        num1 = 0
        num2 = 0
        num3 = 0
        num4 = 0
        str = "Delivery sequence:\n"
        str1 = ""
        str2 = "Task completion."
        thisStr = ""
        Servo1(S1,0)
        Servo2(S2,-5)
        while(True):
            img = sensor.snapshot()
            t = time.ticks_ms()
            objects = kpu.run_yolo2(task, img)
            t = time.ticks_ms() - t
            if objects:
                for obj in objects:
                    if labels[obj.classid()] == 'Harmful waste':
                        n[0] += 1
                    if labels[obj.classid()] == 'Kitchen waste':
                        n[1] += 1
                    if labels[obj.classid()] == 'Other waste':
                        n[2] += 1
                    if labels[obj.classid()] == 'Recyclable waste':
                        n[3] += 1
                    i = 0
                    while i < 4:
                        if n[0] == 3:
                            num += 1
                            allNum += 1
                            num1 += 1
                            thisStr = labels[obj.classid()]
                            Servo2(S2,-70)
                            time.sleep(1)
                            Servo2(S2,-5)
                            time.sleep(1)
                            img.draw_string(0, 50, "%s" %(str2), scale=2, color=(255, 0, 0))
                            n = [0, 0, 0, 0]
                            if num > 8:
                                str1 += "->Harmful waste\n"
                            else:
                                str += "->Harmful waste\n"
                            break
                        if n[1] == 3:
                            num += 1
                            allNum += 1
                            num2 += 1
                            thisStr = labels[obj.classid()]
                            Servo1(S1,-70)
                            time.sleep(1)
                            Servo1(S1,0)
                            time.sleep(1)
                            img.draw_string(0, 50, "%s" %(str2), scale=2, color=(255, 0, 0))
                            n = [0, 0, 0, 0]
                            if num > 8:
                                str1 + "->Kitchen waste\n"
                            else:
                                str += "->Kitchen waste\n"
                            break
                        if n[2] == 3:
                            num += 1
                            allNum += 1
                            num3 += 1
                            thisStr = labels[obj.classid()]
                            Servo2(S2,70)
                            time.sleep(1)
                            Servo2(S2,-5)
                            time.sleep(1)
                            img.draw_string(0, 50, "%s" %(str2), scale=2, color=(255, 0, 0))
                            n = [0, 0, 0, 0]
                            if num > 8:
                                str1 += "->Other waste\n"
                            else:
                                str += "->Other waste\n"
                            break
                        if n[3] == 3:
                            num += 1
                            allNum += 1
                            num4 += 1
                            thisStr = labels[obj.classid()]
                            Servo1(S1,70)
                            time.sleep(1)
                            Servo1(S1,0)
                            time.sleep(1)
                            img.draw_string(0, 50, "%s" %(str2), scale=2, color=(255, 0, 0))
                            n = [0, 0, 0, 0]
                            if num > 8:
                                str1 += "->Recyclable waste\n"
                            else:
                                str += "->Recyclable waste\n"
                            break
                        i += 1
            img.draw_string(0, 0, "Total garbage:%d" %(allNum), scale=1, color=(255, 0, 0))
            img.draw_string(0, 10, "Harmful waste:%d" %(num1), scale=1, color=(255, 0, 0))
            img.draw_string(120, 10, "Kitchen waste:%d" %(num2), scale=1, color=(255, 0, 0))
            img.draw_string(0, 20, "Other waste:%d" %(num3), scale=1, color=(255, 0, 0))
            img.draw_string(120, 20, "Recyclable waste:%d" %(num4), scale=1, color=(255, 0, 0))
            img.draw_string(0, 100, "%s" %(str), scale=1, color=(255, 0, 0))
            if num > 8:
                img.draw_string(120, 115, "%s" %(str1), scale=1, color=(255, 0, 0))
            img.draw_string(0, 40, "Types of garbage:%s" %(thisStr), scale=1, color=(255, 0, 0))
            warn()
            lcd.display(img)
            if (num % 16) == 0:
                num = 0
                str = "Delivery sequence:\n"
                str1 = ""
    except Exception as e:
        raise e
    finally:
        if not task is None:
            kpu.deinit(task)


if __name__ == "__main__":
    try:
        # main(anchors = anchors, labels=labels, model_addr=0x300000, lcd_rotation=0)
        main(anchors = anchors, labels=labels, model_addr="/sd/model-32374.kmodel")
    except Exception as e:
        sys.print_exception(e)
        lcd_show_except(e)
    finally:
        gc.collect()
