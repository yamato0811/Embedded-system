#17T2130G

import picamera
import time
import RPi.GPIO as GPIO
import pygame.mixer

import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from os.path import basename

PICTURE_WIDTH = 800
PICTURE_HEIGHT = 600
SAVEDIR = "/home/pi/Desktop/pictures/"

INTAVAL = 10  # interval to take a photo

#GPIO設定
SENSOR_PIN = 12
LED_green = 26
LED_red = 20
SW = 16

GPIO.setmode( GPIO.BCM )
GPIO.setup( SENSOR_PIN, GPIO.IN )
GPIO.setup(LED_green,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED_red,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(SW,GPIO.IN,pull_up_down=GPIO.PUD_UP)

cam = picamera.PiCamera()
cam.resolution = ( PICTURE_WIDTH, PICTURE_HEIGHT )

st = time.time() - INTAVAL

s = 0
def checkSW(pin):
 global s
 s = 1

GPIO.add_event_detect(SW,GPIO.FALLING,callback=checkSW,bouncetime=200)

def green_light():
    GPIO.output(LED_green, GPIO.LOW)
    time.sleep(1)
    GPIO.output(LED_green, GPIO.HIGH)
    
#シャッター音
sound = "/home/pi/Desktop/Python/sound.mp3"
play_volume = 100 
pygame.mixer.init()
pygame.mixer.music.load(sound)
pygame.mixer.music.set_volume(play_volume/100)

################# mail #####################
msg = 'Detected a person'   #本文
subject = 'Monitoring System'    #件名

to_addr = 'super.black.g17@gmail.com'    #送り先

from_addr = '17t2130g@shinshu-u.ac.jp'   #送り元
mail_id = from_addr
############################################

mail_pass = ''

sender = smtplib.SMTP_SSL('smtp.gmail.com')
sender.login(mail_id, mail_pass)


try:
    while True:
        if (s == 1):
            GPIO.output(LED_red, GPIO.LOW)
            s = 0
            while True:
                if (s == 1):
                    GPIO.output(LED_red, GPIO.HIGH)
                    s = 0
                    break
                if ( GPIO.input(SENSOR_PIN) == GPIO.HIGH ) and (st + INTAVAL < time.time() ):
                    st = time.time()
                    filename = time.strftime( "%Y%m%d%H%M%S" ) + ".jpg"
                    save_file = SAVEDIR + filename
                    cam.capture( save_file )
                    print(time.strftime("photo was taken in : " + "%Y/%m/%d/%H/%M/%S"))
                    pygame.mixer.music.play()
                    green_light()
                    
                    ###################################################################
                    message = MIMEMultipart()
                    body = MIMEText(msg)
                    message.attach(body)
                    message['Subject'] = subject  
                    message['From'] = from_addr   
                    message['To'] = to_addr      
    
                    path = "/home/pi/Desktop/pictures/{}".format(filename) 
                    with open(path, "rb") as f:
                        part = MIMEApplication(
                            f.read(),
                            Name=basename(path)
                        )
                    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(path)
                    message.attach(part)
                    
                    sender.sendmail(from_addr, to_addr, message.as_string())        
                    print('send a mail to :', from_addr)
                    ####################################################################

                    
except KeyboardInterrupt:
        pass
        
GPIO.cleanup()

