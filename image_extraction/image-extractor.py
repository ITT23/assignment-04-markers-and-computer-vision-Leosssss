import cv2
import numpy as np
import os

PREVIEW_WINDOW_NAME = 'Preview Window'
RESULT_WINDOW_NAME = 'Result'
RESULT_WINDOW_WIDTH = int(input("Please enter the result window width(int): "))
RESULT_WINDOW_HEIGHT = int(input("Please enter the result window height(int): "))
RADIUS = 3
COLOR = (0, 0, 255)
THICKNESS = -1

points = []
img = cv2.imread(input("Please enter the input image path: ")) # e.g. './image_extraction/sample_image.jpg'
img_copy = img.copy()
cv2.namedWindow(PREVIEW_WINDOW_NAME)

def mouse_callback(event, x, y, flags, param):
    global img, points
    cv2.imshow(PREVIEW_WINDOW_NAME, img)
    if event == cv2.EVENT_LBUTTONDOWN:
        img = cv2.circle(img, (x, y), RADIUS, COLOR, THICKNESS)
        points.append((x,y))
        if len(points) == 4:
            cv2.destroyAllWindows()
        
cv2.setMouseCallback(PREVIEW_WINDOW_NAME, mouse_callback)

def transformation(img, points):
    # TODO: sort points
    selected_points = np.float32(points)
    destination = np.float32(np.array([[0, 0], [RESULT_WINDOW_WIDTH - RADIUS, 0], [RESULT_WINDOW_WIDTH - RADIUS, RESULT_WINDOW_HEIGHT - RADIUS], [0, RESULT_WINDOW_HEIGHT - RADIUS]]))
    mat = cv2.getPerspectiveTransform(selected_points, destination)
    warped_img = cv2.warpPerspective(img, mat, (RESULT_WINDOW_WIDTH, RESULT_WINDOW_HEIGHT)) #https://docs.opencv.org/3.4/da/d6e/tutorial_py_geometric_transformations.html
    return warped_img

def clearPoints():
    global points
    for p in points:
        (x,y) = p
        img[y-RADIUS:y+RADIUS, x-RADIUS:x+RADIUS] = img_copy[y-RADIUS:y+RADIUS, x-RADIUS:x+RADIUS]
    points = []

while True:
    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyAllWindows()
        clearPoints()
        cv2.namedWindow(PREVIEW_WINDOW_NAME)
        cv2.setMouseCallback(PREVIEW_WINDOW_NAME, mouse_callback)
    elif len(points) == 4:
        wrapped_area = transformation(img, points)
        cv2.imshow(RESULT_WINDOW_NAME, wrapped_area)
        if key == ord("s"):
            destination = input("Enter the output destination: ")
            cv2.imwrite(os.path.join(destination ,"result.jpg"), wrapped_area)
            print("Image saved successfully!")
            cv2.waitKey(0)
