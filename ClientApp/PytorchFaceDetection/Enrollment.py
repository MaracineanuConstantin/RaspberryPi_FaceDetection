import os
import PIL.Image
import torch
import numpy
import cv2

from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1

device = torch.device('cpu')

# Create a face detection pipeline using MTCNN
mtcnn = MTCNN(keep_all=False, device=device)

img_counter = 0

# Create an inception resnet
resnet = InceptionResnetV1('vggface2').eval().to(device)

cap = cv2.VideoCapture(0)

while True:

    x1Copy = 0
    y1Copy = 0
    x2Copy = 0
    y2Copy = 0
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

            x1Copy = x1
            y1Copy = y1
            wCopy = w
            hCopy = h
            x2Copy = x2
            y2Copy = y2

    # Add to frame list
    frames_tracked.append(frame_draw.resize((640, 360), Image.BILINEAR))

    cv2.rectangle(img, (240, 160), (400, 320), (255, 0, 0), 2)

    # Display
    cv2.imshow('img', img)

    xCenter = int(x1Copy + wCopy / 2)
    yCenter = int(y1Copy + hCopy / 2)

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

    if moveUp == 0 and moveDown == 0 and moveLeft == 0 and moveRight == 0:

        # Capture image if space key is pressed
        kCapture = cv2.waitKey(30) & 0xff

        if kCapture == 32:
            name: str = input("Please enter your name: ")
            filename = "%s.npy" % name
            completePath = os.path.join("People/", filename)

            cropped_image = img[80:380, 200:460]

            imgCropped = mtcnn(cropped_image)

            if imgCropped is not None:

                # Calculate embedding (unsqueeze to add batch dimension)
                resnet.classify = True
                imgEmbedding = resnet(imgCropped.unsqueeze(0))
                imgEmbeddingnpy = imgEmbedding.detach().numpy()

                numpy.save(completePath, imgEmbeddingnpy, allow_pickle=True, fix_imports=True)

            # Exit after taking picture
            exit()

    # Stop if escape key is pressed
    kExit = cv2.waitKey(30) & 0xff
    if kExit == 27:
        break

# Release the VideoCapture object
cap.release()
