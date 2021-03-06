# ImageUtils.
# Brandon Joffe
# 2016
#
# Copyright 2016, Brandon Joffe, All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Code used in this project included opensource software (openface)
# developed by Brandon Amos
# Copyright 2015-2016 Carnegie Mellon University

# This is a utilities script used for testing, resizing images etc

import os
import threading
import time

import cv2
import dlib

start = time.time()
import numpy as np

np.set_printoptions(precision=2)

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, '..', 'facemodels')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

cascade_lock = threading.Lock()
facecascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")
uppercascade = cv2.CascadeClassifier("cascades/haarcascade_upperbody.xml")
eyecascade = cv2.CascadeClassifier("cascades/haarcascade_eye.xml")
detector = dlib.get_frontal_face_detector()


def resize(frame):
    r = 640.0 / frame.shape[1]
    dim = (640, int(frame.shape[0] * r))
    # Resize frame to be processed
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    return frame


def resize_mjpeg(frame):
    r = 320.0 / frame.shape[1]
    dim = (320, 200)  # int(frame.shape[0] * r))
    # perform the actual resizing of the image and show it
    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    return frame


def crop(image, box, dlibRect=False):
    if dlibRect == False:
        x, y, w, h = box
        return image[y: y + h, x: x + w]

    return image[box.top():box.bottom(), box.left():box.right()]


def is_inside(o, i):
    ox, oy, ow, oh = o
    ix, iy, iw, ih = i
    return ox > ix and oy > iy and ox + ow < ix + iw and oy + oh < iy + ih


def draw_boxes(image, rects, dlibrects):
    if dlibrects:
        image = draw_rects_dlib(image, rects)
    else:
        image = draw_rects_cv(image, rects)
    return image


def draw_rects_cv(img, rects, color=(0, 40, 255)):
    overlay = img.copy()
    output = img.copy()
    count = 1
    for x, y, w, h in rects:
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
        cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    return output


def draw_rects_dlib(img, rects, color=(0, 255, 255)):
    overlay = img.copy()
    output = img.copy()

    for bb in rects:
        bl = (bb.left(), bb.bottom())  # (x, y)
        tr = (bb.right(), bb.top())  # (x+w,y+h)
        cv2.rectangle(overlay, bl, tr, color, thickness=2)
        cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    return output


def draw_rect(img, x, y, w, h, color=(0, 40, 255)):
    overlay = img.copy()
    output = img.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
    cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    return output


def draw_rects_dlib(img, rects):
    overlay = img.copy()
    output = img.copy()
    for bb in rects:
        bl = (bb.left(), bb.bottom())  # (x, y)
        tr = (bb.right(), bb.top())  # (x+w,y+h)
        cv2.rectangle(overlay, bl, tr, color=(0, 255, 255), thickness=2)
        cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
    return output


def detect_upper_cascade(img):
    rects = uppercascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
    return rects


def pre_processing(image):
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl1 = clahe.apply(grey)
    cv2.imwrite('clahe_2.jpg', cl1)
    return cl1


def detectdlibgrey_face(grey):
    bbs = detector(grey, 1)
    return bbs


def convertImageToNumpyArray(img, height, width):  # Numpy array used by dlib for image operations
    buf = np.asarray(img)
    rgbFrame = np.zeros((height, width, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 2]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 0]
    annotatedFrame = np.copy(buf)
    return annotatedFrame


def writeToFile(filename, lineString):  # Used for writing testing data to file
    f = open(filename, "a")
    f.write(lineString + "\n")
    f.close()
