# GameMessages.py
#  Usage : import GameMessages
# Micropython implementation for handling game messages and button inputs

from machine import Pin
import time
import json
import select
import sys

debounce_delay = 0.01 # debounce delay in seconds

class Button:
    # define button status 
    pressed = False
    just_pressed = False
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)


    def is_pressed(self): 
        # Check if the button is pressed (active low)
        # Returns True if it has just been pressed (previous status was "not pressed" and the current status is "pressed")
        # check debounce before determining the state
        if not self.pin.value() != self.pressed:
            time.sleep(debounce_delay)
            # check again 
            if not self.pin.value() != self.pressed:
                self.pressed = not self.pressed
        # update the status 'just_pressed'
        if self.pressed and not self.just_pressed:
            self.just_pressed = True
            return True
        if not self.pressed:
            self.just_pressed = False
        return False

class GameMessages:

    def __init__(self, start_button_pin=7, main_button_pin=6, debounce_delay=0.01):
        # Init serial read polling
        self.debounce_delay = debounce_delay
        self.start_button_pin = start_button_pin  # start button
        self.main_button_pin = main_button_pin     # main button
        self.start_button = Button(self.start_button_pin)
        self.main_button = Button(self.main_button_pin) 

        self.poll_obj = select.poll()
        self.poll_obj.register(sys.stdin, select.POLLIN)
        self.serial_input_buf = []

    @staticmethod
    def send_message(event, state):
        message = {
            "time": time.ticks_ms() / 1000,
            "event": event,
            "state": state
        }
        print(json.dumps(message))

    def receive_message(self):
        events = self.poll_obj.poll(1)  # Poll for events with a timeout of 0ms (non-blocking)
        for obj, event in events:
            if obj == sys.stdin and event & select.POLLIN:
                char = sys.stdin.read(1)
                self.serial_input_buf.append(char)
                if "\n" in self.serial_input_buf:
                    line = "".join(self.serial_input_buf)
                    self.serial_input_buf.clear()
                    if line:
                        try:
                            message = json.loads(line)
                            return message
                        except json.JSONDecodeError:
                            print("Invalid JSON received:", line)
                            self.serial_input_buf.clear()
        # If no complete message is found, return None
        return None


