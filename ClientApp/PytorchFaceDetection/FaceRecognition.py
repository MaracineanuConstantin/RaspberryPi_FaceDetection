import glob
import os
import PIL.Image
import torch
import numpy as np
import cv2
import socket
import time

from pathlib import Path
from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1

device = torch.device('cpu')

# Create a face detection pipeline using MTCNN
mtcnn = MTCNN(keep_all=False, device=device)

index = 0
dictionary = {}

# Create an inception resnet
resnet = InceptionResnetV1('vggface2').eval().to(device)

cap = cv2.VideoCapture(0)

# Connection
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket:
    HOST = "172.20.10.14"
    PORT = 65435
    socket.connect((HOST, PORT))
    startTime = time.time()
    while True:

        xCopy = 0
        yCopy = 0
        wCopy = 0
        hCopy = 0

        xCenter = 0
        yCenter = 0

        _, img = cap.read()
        frames_tracked = []

        # Detect faces
        boxes, _ = mtcnn.detect(img)

        # Draw faces
        frame_draw = PIL.Image.fromarray(img)
        draw = ImageDraw.Draw(frame_draw)
        boxes = [] if boxes is None else boxes
        for box in boxes:
            if len(box):
                box_list = [int(x) for x in box.tolist()]
                cv2.rectangle(img, (box_list[0], box_list[1]), (box_list[2], box_list[3]), (0, 0, 255), 2)

                x1 = box_list[0]
                y1 = box_list[1]
                x2 = box_list[2]
                y2 = box_list[3]

                w = x2 - x1
                h = y2 - y1

                # Mark the middle of the recognised face
                xCenter = int(x1 + w / 2)
                yCenter = int(y1 + h / 2)
                cv2.circle(img, (xCenter, yCenter), 3, (0, 0, 255), -1)

                # Mark the distance between center of the face and center of the image
                startPoint = (320, 240)
                endPoint = (xCenter, yCenter)
                # cv2.line(img, startPoint, endPoint, (0, 255, 0), 2)

                xCopy = x1
                yCopy = y1
                wCopy = w
                hCopy = h

        # Add to frame list
        frames_tracked.append(frame_draw.resize((640, 360), Image.BILINEAR))

        cv2.rectangle(img, (240, 160), (400, 320), (255, 0, 0), 2)

        currentTime = time.time()
        if currentTime - startTime > 1:
            startTime = currentTime

            xCenter = int(xCopy + wCopy / 2)
            yCenter = int(yCopy + hCopy / 2)

            moveUp = 0
            moveRight = 0
            moveDown = 0
            moveLeft = 0

            # Split the image into 80x80 squares to determine the distance the webcam needs to move
            if 0 < xCenter < 80:
                moveLeft = 3
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2
            if 80 <= xCenter < 160:
                moveLeft = 2
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2
            if 160 <= xCenter < 240:
                moveLeft = 1
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2
            if 240 <= xCenter < 400:
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2
            if 400 <= xCenter < 480:
                moveRight = 1
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2
            if 480 <= xCenter < 560:
                moveRight = 2
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2
            if 560 <= xCenter < 640:
                moveRight = 3
                if 0 < yCenter < 80:
                    moveUp = 2
                if 80 <= yCenter < 160:
                    moveUp = 1
                if 320 <= yCenter < 400:
                    moveDown = 1
                if 400 <= yCenter < 480:
                    moveDown = 2

            print(moveUp, moveDown, moveLeft, moveRight)

            text = "Unknown"
            dictionary = {}

            if moveUp == 0 and moveDown == 0 and moveLeft == 0 and moveRight == 0:

                # Get cropped and prewhitened image tensor
                imgCropped = mtcnn(img)

                if imgCropped is not None:

                    # Calculate embedding (unsqueeze to add batch dimension)
                    resnet.classify = True
                    imgEmbedding = resnet(imgCropped.unsqueeze(0))
                    imgEmbeddingnpy = imgEmbedding.detach().numpy()

                    fileLocation = os.path.join('People', '*.npy')
                    filenames = glob.glob(fileLocation)

                    idx = 0

                    for f in filenames:

                        currentEmb = np.load(filenames[idx])

                        distances = abs((currentEmb - imgEmbeddingnpy))
                        distances = distances.sum(axis=-1)
                        distances = np.sqrt(distances)

                        name = Path(f).stem

                        if name not in dictionary.keys():
                            dictionary[name] = abs(distances)
                        idx = idx + 1

                    dictionaryList = sorted((value, key) for (key, value) in dictionary.items())
                    sortDict = dict([(k, v) for v, k in dictionaryList])
                    text = next(iter(sortDict))

            cv2.putText(img, text, (xCopy, yCopy), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=2, lineType=cv2.FILLED, bottomLeftOrigin=False)

            # Display
            cv2.imshow('img', img)

            # Increment the index
            index = index + 1

            # Encode the data to be transferred
            coded_transfer = "{},{},{},{},{}".format(index, moveUp, moveRight, moveDown, moveLeft)
            my_transfer = coded_transfer.encode('utf-8')

            # Send the data
            socket.sendall(my_transfer)

        # Stop if escape key is pressed
        kExit = cv2.waitKey(30) & 0xff
        if kExit == 27:
            break

# Release the VideoCapture object
cap.release()
