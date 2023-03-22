from pynput.keyboard import Key, Controller
import time 

keyboard = Controller()

num=int(input('# entries: '))
waittime=int(input('# Seconds before start: '))
interval=float(input('Interval time: '))

time.sleep(waittime)
for i in range(num):
    keyboard.press('2')
    time.sleep(interval)
    keyboard.release('2')
    time.sleep(interval)
    keyboard.press(Key.enter)
    time.sleep(interval)
    keyboard.release(Key.enter)
    time.sleep(interval)

