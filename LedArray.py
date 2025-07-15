# LedArray.py
#  Usage : import LedArray
#
# 以下は初期プロンプトです
# 同じディレクトリにある aled.py を参考にして次の機能を実装
# led_run() を別プロセスで実行
# 変数 go および led_pattern をグローバルに宣言
# led_run() は次の機能を持つ：
#  * run_pattern0(), run_pattern1(), run_pattern2(), run_pattern3() を呼び出す
#  * 各パターンは、go が True の間、特定の LED 点灯動作をループする。go が False になるとループを抜ける
#  * 各パターンは、go が False になると終了する
#  * 各パターンの終了後、go を True に戻す
#  * led_pattern の値が変更したことを検出したら、1) go を false に変更して run_pattern*() を終了させる
#  * run_pattern*() の終了後、go を true に戻し、led_pattern の値に応じて新しい run_pattern*() を呼び出す
# メインループはスタブとして、10 秒おきに led_pattern の値を変更する。ループする。

import machine
import neopixel
from utime import sleep
import _thread
import random

class LedArray:
    def __init__(self):
        # Define number of LEDs
        self.n0 = 32  # outer
        self.n1 = 24  # inner
        self.n = self.n0 + self.n1  # inner 24 + outer 32

        # interval
        self.interval = 0.04
        self.interval2 = 0.12

        self.data_pin = machine.Pin(5, machine.Pin.OUT)  # Use GPIO 5 for data pin

        self.strip = neopixel.NeoPixel(self.data_pin, self.n)
        self.pallette = {
            "red": (63, 0, 0),
            "green": (0, 63, 0),
            "blue": (0, 0, 63),
            "white": (63, 63, 63),
            "black": (0, 0, 0),
            "yellow": (63, 63, 0),
            "cyan": (0, 63, 63),
            "magenta": (63, 0, 63)
        }

        self.colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"]
        self.col = 0  # Color index for patterns

        # create a lock to manage access to shared variables
        self.lock = _thread.allocate_lock()

        # Global variables
        self.go = True
        self.led_pattern = 0 

    def led_array_start(self):  # Initiate the LED run process
        # Initiate the LED run process
        _thread.start_new_thread(self.led_run, ())
        # print("LED run thread started. Press Ctrl+C to stop.")

    def led_run(self):
        while True:
            if self.led_pattern == 0:
                self.run_pattern0()
            elif self.led_pattern == 1:
                self.run_pattern1()
            elif self.led_pattern == 2:
                self.run_pattern2()
            elif self.led_pattern == 3:
                self.run_pattern3()
            else:
                # print("Unknown pattern")
                break   
            sleep(0.1)  

    def swap_intervals(self): 
        with self.lock:
            t = self.interval
            self.interval = self.interval2
            self.interval2 = t
            # print(f"Swapped intervals: {self.interval}, {self.interval2}")

    def run_pattern0(self):  # demo pattern
        global go
        # fix intervals
        if self.interval > self.interval2:
            self.swap_intervals()
        col = 0  # Reset color index for pattern 0
        while self.go:
            # print("Running Pattern 0")
            col = random.randint(0, len(self.colors) - 2)  # Randomly select a color
            for i in range(self.n):
                if not self.go:
                    break
                self.strip[i] = self.pallette[self.colors[col]]
                self.strip.write()
                sleep(self.interval)
                # randomly swap intervals
                if random.randint(0, 53) == 0:  # %
                    self.swap_intervals()
                if not self.go:
                    break
                self.strip[i] = (0, 0, 0)  # Turn off the LED
                self.strip.write()
            col = random.randint(0, len(self.colors) - 2)  # Randomly select a color
            for i in range(0, self.n, 4):
                if not self.go:
                    break
                self.strip[i] = self.pallette[self.colors[col]]
                self.strip.write()
                sleep(self.interval2)
                # randomly swap intervals
                if random.randint(0, 53) == 0:  # %
                    self.swap_intervals()
            for i in range(0, self.n, 4):
                if not self.go:
                    break
                self.strip[i] = (0, 0, 0)
                self.strip.write()
                sleep(self.interval2)
        # Reset the strip to off state
        self.strip.fill((0, 0, 0))
        self.strip.write()
        # print("Pattern 0 ended")
        with self.lock:
            self.go = True

    def run_pattern1(self): # Slow effect
        global go
        rotate_dir = 1  # 1 for clockwise, -1 for counter-clockwise
        # fix intervals
        if self.interval > self.interval2:
            self.swap_intervals()
        # define the outer and inner strips
        outer = [len(self.colors)-1] * self.n0  # Outer strip initialized to black
        inner = [len(self.colors)-1] * self.n1  # Inner strip initialized to black
        # fill outer strip at 90 deg interval
        col = random.randint(0, len(self.colors) - 2)
        for i in range(0, self.n0, int(self.n0/4)):
            outer[i] = col
        # fill outer strip at 90 deg interval, with 45 deg offset
        col = random.randint(0, len(self.colors) - 2)
        for i in range(int(self.n0/8), self.n0, int(self.n0/4)):
            outer[i] = col       
        # fill inner strip at 90 deg interval
        col = random.randint(0, len(self.colors) - 2)
        for i in range(0, self.n1, int(self.n1/4)):
            inner[i] = random.randint(0, len(self.colors) - 2)
        # loop, rotate outer ring clockwise, inner ring counter-clockwise
        while self.go:
            sleep(self.interval) 
            if not self.go:
                break
            # display outer and inner strips
            for i in range(self.n0):
                self.strip[i] = self.pallette[self.colors[outer[i]]]
            for i in range(self.n1):
                self.strip[self.n0 + i] = self.pallette[self.colors[inner[i]]]
            self.strip.write()
            if rotate_dir == 1:  # Rotate direction
                # rotate outer strip clockwise
                outer = [outer[-1]] + outer[:-1]  # Rotate outer strip clockwise
                # rotate inner strip counter-clockwise
                inner = inner[1:] + [inner[0]]  # Rotate inner strip counter-clockwise
            else: # rotate outer strip counter-clockwise
                outer = outer[1:] + [outer[0]]  # Rotate outer strip counter-clockwise
                # rotate inner strip clockwise
                inner = [inner[-1]] + inner[:-1]  # Rotate inner strip clockwise
            # randomly change the direction of rotation
            if random.randint(0, 53) == 0:  # 1/53 = 1.89%
                rotate_dir = - rotate_dir  # Change rotation direction
            # randomly swap intervals
            if random.randint(0, 53) == 0:  # %
                self.swap_intervals()
        # Restrict the strip to off state
        self.strip.fill((0, 0, 0))
        self.strip.write()
        with self.lock:
            self.go = True

    def run_pattern2(self): # medium effect
        global go
        # fix intervals
        if self.interval > self.interval2:
            self.swap_intervals()
        col = 0  # Reset color index for pattern 0
        while self.go:
            col1 = random.randint(0, len(self.colors) - 2)  # Randomly select a color
            col2 = random.randint(0, len(self.colors) - 2)  # Randomly select a second color
            for i in range(0, self.n0, int(self.n0/8)):
                if not self.go:
                    break
                self.strip[i] = self.pallette[self.colors[col1]]
            for i in range(int(self.n1/16), self.n1, int(self.n1/8)):
                if not self.go:
                    break
                self.strip[self.n0 + i] = self.pallette[self.colors[col2]]  
                self.strip.write()
            sleep(self.interval)
            # Turn off all the leds
            self.strip.fill((0, 0, 0))
            self.strip.write()
            # switch the outer and inner colors
            for i in range(0, self.n0, int(self.n0/8)):
                if not self.go:
                    break
                self.strip[i] = self.pallette[self.colors[col2]]
            for i in range(int(self.n1/16), self.n1, int(self.n1/8)):
                if not self.go:
                    break
                self.strip[self.n0 + i] = self.pallette[self.colors[col1]]
                self.strip.write()
            sleep(self.interval)
            # Turn off all the leds
            self.strip.fill((0, 0, 0))
            # print("Running Pattern 1")
            if not self.go:
                break
        # turn off all LEDs when the thread exits
        self.strip.fill((0, 0, 0))
        self.strip.write()
        # print("Pattern 1 ended")
        with self.lock:
            self.go = True

    def run_pattern3(self): # Slow effect
        global go
        rotate_dir = 1  # 1 for clockwise, -1 for counter-clockwise
        # fix intervals
        if self.interval > self.interval2:
            self.swap_intervals()
        l_interval = self.interval * 0.6 # speed up
        l_interval2 = self.interval2 * 0.6 # speed up
        # define the outer and inner strips
        outer = [len(self.colors)-1] * self.n0  # Outer strip initialized to black
        inner = [len(self.colors)-1] * self.n1  # Inner strip initialized to black
        # fill outer strip at 90 deg interval
        col = random.randint(0, len(self.colors) - 2)
        for i in range(0, self.n0, int(self.n0/4)):
            outer[i] = col
        # fill outer strip at 90 deg interval, with 45 deg offset
        col = random.randint(0, len(self.colors) - 2)
        for i in range(int(self.n0/8), self.n0, int(self.n0/4)):
            outer[i] = col       
        # fill inner strip at 90 deg interval
        col = random.randint(0, len(self.colors) - 2)
        for i in range(0, self.n1, int(self.n1/4)):
            inner[i] = random.randint(0, len(self.colors) - 2)
        # loop, rotate outer ring clockwise, inner ring counter-clockwise
        while self.go:
            sleep(l_interval) 
            if not self.go:
                break
            # display outer and inner strips
            for i in range(self.n0):
                self.strip[i] = self.pallette[self.colors[outer[i]]]
            for i in range(self.n1):
                self.strip[self.n0 + i] = self.pallette[self.colors[inner[i]]]
            # add random sparcles
            for i in range(self.n):
                if random.randint(0, 100) < 20: 
                    # sparkle light at 200% brightness (val = 128)
                    self.strip[i] = self.pallette[self.colors[random.randint(0, len(self.colors) - 2)]] * 2 
            self.strip.write()
            if rotate_dir == 1:  # Rotate direction
                # rotate outer strip clockwise
                outer = [outer[-1]] + outer[:-1]  # Rotate outer strip clockwise
                # rotate inner strip counter-clockwise
                inner = inner[1:] + [inner[0]]  # Rotate inner strip counter-clockwise
            else: # rotate outer strip counter-clockwise
                outer = outer[1:] + [outer[0]]  # Rotate outer strip counter-clockwise
                # rotate inner strip clockwise
                inner = [inner[-1]] + inner[:-1]  # Rotate inner strip clockwise
            # randomly change the direction of rotation
            if random.randint(0, 53) == 0:  # 1/53 = 1.89%
                rotate_dir = - rotate_dir  # Change rotation direction
            # randomly swap intervals
            if random.randint(0, 24) == 0:  # %
                t = l_interval
                l_interval = l_interval2
                l_interval2 = t
        # Restrict the strip to off state
        self.strip.fill((0, 0, 0))
        self.strip.write()
        with self.lock:
            self.go = True

    def stop(self): # erase the LED strip
        with self.lock:
            self.go = False
        self.strip.fill((0, 0, 0))  # Turn off all LEDs
        self.strip.write()  # Write the changes to the strip
        # print("LED strip stopped and cleared.")