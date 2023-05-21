# Quelle: Exercise 01: pyglet_click.py, opencv_pyglet.py, aruco_sample.py
import pyglet
from pyglet import shapes, clock
import random
import time
import numpy as np
import sys
import cv2
from PIL import Image
import cv2.aruco as aruco
import math

MIN_TARGET_RADIUS = 8
MAX_TARGET_RADIUS = 25
SLOW_SPEED = 5
FAST_SPEED = 15
LABEL_SCORE = "Current Score: "
EASY_SCORE = 1
MIDDLE_SCORE = 2
HARD_SCORE = 3
NEGATIV_SCROE = 2
score = 0

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()

    
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

cap = cv2.VideoCapture(video_id)

# https://chat.openai.com/  Answer to question: How to get the width and height of the webcam frame
webcam_frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
webcam_frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

window = pyglet.window.Window(webcam_frame_width, webcam_frame_height)
label = pyglet.text.Label(LABEL_SCORE+str(score), font_name='Times New Roman', font_size=14, x=10, y=window.height-20)

min_marker_x = 0
max_marker_x = window.width
min_marker_y = 0
max_marker_y = window.height
marker_pos = []

def measure_distance(x1, y1, x2, y2):
    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance

def update_game_field(corners, ids):
    global min_marker_x, max_marker_x, min_marker_y, max_marker_y, marker_pos
    marker_pos = []
    marker_x = []
    marker_y = []
    for i in range(len(ids)):
        # https://chat.openai.com/  Answer to question: How to get position of aruco marker
        marker_corners = corners[i][0]
        cx = int((marker_corners[0][0] + marker_corners[2][0]) / 2)
        cy = int((marker_corners[0][1] + marker_corners[2][1]) / 2)
        
        marker_pos.append((cx,cy))
        marker_x.append(cx)
        marker_y.append(cy)
        
    min_marker_x = min(marker_x)
    max_marker_x = max(marker_x)
    min_marker_y = min(marker_y)
    max_marker_y = max(marker_y)    
    
def sort_four_points(points): # https://chat.openai.com/ I asked ChatGPT how to sort coordinates with array sort
    sorted_points = sorted(points, key=lambda p: p[0])
    top_left, top_right = sorted(sorted_points[:2], key=lambda p: p[1])
    bottom_left, bottom_right = sorted(sorted_points[2:], key=lambda p: p[1])
    return [top_left, bottom_left, bottom_right, top_right]
    
def transformation(frame, marker_pos):
    markers = np.float32(sort_four_points(marker_pos))
    destination = np.float32(np.array([[0, 0], [window.width, 0], [window.width, window.height], [0, window.height]]))
    mat = cv2.getPerspectiveTransform(markers, destination)
    warped_frame = cv2.warpPerspective(frame, mat, (window.width, window.height)) #https://docs.opencv.org/3.4/da/d6e/tutorial_py_geometric_transformations.html
    return warped_frame

def detected_finger(frame): # finger detection with HSV color space https://chat.openai.com/
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100 and len(cnt) > 10]
    
    for contour in filtered_contours:
        topmost = tuple(contour[contour[:,:,1].argmin()][0])
        cv2.circle(frame, topmost, 10, (0, 255, 0), 2)

    return frame, filtered_contours

class Target:
    targets = []

    def update_targets(delta_time):
        for target in Target.targets:
            target.update(delta_time)

    def draw_targets():
        for target in Target.targets:
            target.draw()

    def create_target(delta_time):
        global min_marker_x, max_marker_x, min_marker_y, max_marker_y
        if random.randint(0, 10) == 0:
            radius = random.randint(MIN_TARGET_RADIUS, MAX_TARGET_RADIUS)
            x = random.randint(radius, window.width - radius)
            y = window.height
            Target.targets.append(Target(x, y, radius))

    def finger_click(finger_contours): # The highest point of the hand can interact with targets
        global score
        for contour in finger_contours:
            for target in Target.targets:
                (x,y) = tuple(contour[contour[:,:,1].argmin()][0])
                distance = measure_distance(window.width-x, window.height-y, target.x, target.y)
                if distance <= target.radius + 10:
                    Target.targets.remove(target)
                    if target.radius < MIN_TARGET_RADIUS + (MAX_TARGET_RADIUS-MIN_TARGET_RADIUS)/3:
                        score += HARD_SCORE
                    elif target.radius > MAX_TARGET_RADIUS - (MAX_TARGET_RADIUS-MIN_TARGET_RADIUS)/3:
                        score += EASY_SCORE
                    else:
                        score += MIDDLE_SCORE
                    label.text = LABEL_SCORE+str(score)
                    break
    
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.shape = shapes.Circle(x=self.x,
                                   y=self.y,
                                   radius=self.radius,
                                   color=self.color)

    def update(self, time_delta):
        global score
        if score < 30:
            self.y -= SLOW_SPEED
        else:
            self.y -= FAST_SPEED
        self.shape.y = self.y
        if self.shape.y < 0:
            Target.targets.remove(self)
            score -= NEGATIV_SCROE
            label.text = LABEL_SCORE+str(score)
            
    def draw(self):
        self.shape.draw()
        
while True:
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.Q:
            sys.exit(0)

    @window.event
    def on_draw():
        global marker_pos
        window.clear()
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
            img = cv2glet(frame, 'BGR')
            img.blit(0, 0, 0)
            if ids is not None:
                if len(ids) == 4:
                    update_game_field(corners, ids)     
                    warped_frame = transformation(frame, marker_pos)
                    detect_frame, finger_contours = detected_finger(warped_frame)
                    flip_warped_frame = cv2.flip(detect_frame, 1)
                    img = cv2glet(flip_warped_frame, 'BGR')
                    img.blit(0, 0, 0)           
                    Target.draw_targets()
                    Target.update_targets(0.1)
                    Target.finger_click(finger_contours)
                else:
                    img = cv2glet(frame, 'BGR')
                    img.blit(0, 0, 0)
                    marker_pos = []
        label.draw()
            
    clock.schedule_interval(Target.update_targets, 0.1)
    clock.schedule_interval(Target.create_target, 0.2)

    pyglet.app.run()
