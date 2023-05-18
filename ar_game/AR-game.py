# Quelle: Exercise 01: pyglet_click.py
import pyglet
from pyglet import shapes, clock
import random
import time
import numpy as np
import sys
import cv2
from PIL import Image

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])
    
# converts OpenCV image to PIL image and then to pyglet texture
# https://gist.github.com/nkymut/1cb40ea6ae4de0cf9ded7332f1ca0d55
def cv2glet(img,fmt):
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if fmt == 'GRAY':
      rows, cols = img.shape
      channels = 1
    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols, 
                                   height=rows, 
                                   fmt=fmt, 
                                   data=raw_img, 
                                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg

# Create a video capture object for the webcam
cap = cv2.VideoCapture(video_id)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 648

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

def measure_distance(x1, y1, x2, y2):
    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance

class Target:
    targets = []

    def update_targets(delta_time):
        for target in Target.targets:
            target.update(delta_time)

    def draw_targets():
        for target in Target.targets:
            target.draw()

    def create_target(delta_time):
        if random.randint(0, 10) == 0:
            radius = random.randint(10, 80)
            x = random.randint(0, window.width - radius)
            y = random.randint(0, window.height - radius)
            Target.targets.append(Target(x, y, radius))

    def propagate_click(x, y):
        for target in Target.targets:
            distance = measure_distance(x, y, target.x, target.y)
            if distance < target.radius:
                Target.targets.remove(target)
                break

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (55, 55, 255)
        self.shape = shapes.Circle(x=self.x,
                                   y=self.y,
                                   radius=self.radius,
                                   color=self.color)
        self.lifetime = random.randint(3, 8)
        self.age = 0

    def update(self, time_delta):
        self.age += time_delta
        if self.age > self.lifetime:
            Target.targets.remove(self)

    def draw(self):
        self.shape.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    Target.propagate_click(x, y)

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        sys.exit(0)

@window.event
def on_draw():
    window.clear()
    ret, frame = cap.read()
    img = cv2glet(frame, 'BGR')
    img.blit(0, 0, 0)
    Target.draw_targets()

clock.schedule_interval(Target.update_targets, 0.1)
clock.schedule_interval(Target.create_target, 0.1)

pyglet.app.run()
