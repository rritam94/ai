import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO

def animal(img):
    model = YOLO("animal.pt")
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    results = model(img_cv)

    for result in results:
        result.save("animal.png")

def damage(img) -> str:
    model = YOLO("damage.pt")
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    results = model(img_cv)

    for result in results:
        result.save("damage.png")

img = Image.open("test.jpg")
animal(img)
damage(img)