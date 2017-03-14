#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A fork of pyglet's timer.py by Luke Macken
#
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

'''A full-screen minute:second timer/countdown timer, with wallclock.

Can be controlled either via keyboard or via GPIO buttons in a Raspberry Pi

If a numerical parameter is provided, it will be used as the amount of 
minutes to count down. Else the counter will start from zero.

Bellow the time elapsed/remaining there always be a wall clock with the 
current time.

In the countdown mode, once there is 1 minute left, the timer goes red.  
This limit is easily adjustable by editing the running_out_minutes variable.

There are 2 keys/GPIO buttons used to control the clock
Enter key / GPIO #3 :  Starts the timer / Stops / Restarts sequentially
Space key / GPIO #4 :  Sets a red background until the timer is restarted

Press ESC key to exit
'''

import sys
import pyglet
import time
import Adafruit_CharLCD as LCD


# Raspberry Pi pin configuration:
lcd_rs        = 5  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 23
lcd_d4        = 6
lcd_d5        = 13
lcd_d6        = 19
lcd_d7        = 26
lcd_backlight = 24


# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2


# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)


fullscreen = True
font_size = 200
minute = 60
start_running = False
running_out_minutes = 1
timeout_text = ''
time_step = 1.0
colors = {
  'default_text' :      (255, 255, 255, 255),
  'default_clock' :     (200, 200, 200, 255),
  'timeout_text' :      (0,   0,   0,   255),
  'default_bg' :        (0,   0,   0,   255),
  'timeout_bg' :        (255, 0,   0,   255),
  'running_out_color' : (180, 0,   0,   255)
  }
key_stop_reset = pyglet.window.key.RETURN
gpio_stop_reset = 14
key_timeout = pyglet.window.key.SPACE
gpio_timeout = 15
key_exit = pyglet.window.key.ESCAPE
gpio_button3 = 18
red="   "

try:
  import RPi.GPIO as GPIO
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(gpio_stop_reset, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(gpio_timeout, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  print "Running on Raspberry PI"
except:
  print "Running on PC"

try:
    COUNTDOWN = int(sys.argv[1])
    updown = -1.0
except:
    COUNTDOWN = 0
    updown =1.0

window = pyglet.window.Window(fullscreen=fullscreen)

class Timer(object):
    def __init__(self):
        self.start = '%02d:00' % COUNTDOWN
        self.label = pyglet.text.Label(self.start, font_size=font_size,
                                       x=window.width//2, y=window.height*3//4,
                                       anchor_x='center', anchor_y='center')
        self.curtime = pyglet.text.Label(time.strftime('%X'), font_size=font_size//2,
                                       x=window.width//2, y=window.height//4,
                                       anchor_x='center', anchor_y='center')
        self.bg_color = pyglet.text.Label("-", font_size=font_size*20,
                                       x=window.width//2, y=window.height+500,
                                       anchor_x='center', anchor_y='center')
        self.reset()

    def reset(self):
        self.time = COUNTDOWN * minute + 0.1
        self.running = start_running
        self.label.text = self.start
        self.label.color = colors['default_text']
        self.bg_color.color = colors['default_bg']

    def update(self, dt):
        self.curtime.text = time.strftime('%X')
        if self.running:
            self.time += dt*updown
            m, s = divmod(self.time, minute)
            self.label.text = '%02d:%02d' % (m, s)
            if m < running_out_minutes:
                if (COUNTDOWN > 0):
                    self.label.color = colors['running_out_color']
            if m < 0:
                self.running = False
                self.label.text = timeout_text
                window.close()

    def stop_reset(self):
        if timer.running:
            timer.running = False
        else:
            timer.reset()
            timer.running = True

    def timeout(self):
        global red
        if timer.running:
            if red=="   ":
              self.label.color = colors['timeout_text']
              self.bg_color.color = colors['timeout_bg']
              red = "###"
            else:
              self.label.color = colors['default_text']
              self.bg_color.color = colors['default_bg']
              red = "   "


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key_timeout:
        timer.timeout()
    elif symbol == key_exit:
        window.close()
    elif symbol == key_stop_reset:
        timer.stop_reset()

@window.event
def on_draw():
    window.clear()
    timer.bg_color.draw()
    timer.label.draw()
    timer.curtime.draw()
    lcd.clear()
    lcd.message(red + "   " + timer.label.text + "  " + red + "\n" + red + " " + timer.curtime.text + " " + red)


def on_button(channel):
    if GPIO.input(gpio_stop_reset) == False and GPIO.input(gpio_timeout) == False: 
        sys.exit()
    if channel==gpio_stop_reset:
        timer.stop_reset()
    elif channel== gpio_timeout:
        timer.timeout()

timer = Timer()
try:
    GPIO.add_event_detect(gpio_stop_reset, GPIO.FALLING, callback=on_button, bouncetime=1000)
    GPIO.add_event_detect(gpio_timeout, GPIO.FALLING, callback=on_button, bouncetime=1000)
except:
    pass

pyglet.clock.schedule_interval(timer.update, time_step)
pyglet.app.run()
