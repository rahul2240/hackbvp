import os
import ffmpeg
import sys
import imutils
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from collections import deque
import dlib
from app import upload_s3
import logging
from PIL import Image
from fpdf import FPDF

detector = dlib.get_frontal_face_detector()

x1, y1, x2, y2 = 0, 0, 0, 0


def face_cordinates(frame):

    faces = detector(frame, 1)
    if faces:
        for face in faces:
            x = face.left()
            y = face.top()
            w = face.right() - x
            h = face.bottom() - y
            return x, y, x+w, y+h

    return 0, 0, 0, 0
    


def edit_image(frame_path, i, face_cord):

    frame = cv2.imread(os.path.join(frame_path, str(i)), cv2.IMREAD_COLOR)

    frame = imutils.resize(frame, width = 700)

    frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    x1, y1, x2, y2 = face_cord

    if x1 == 0 or y1 == 0 or x2 == 0 or y2 == 0:
        x1, y1, x2, y2 = face_cordinates(frame1)
        
    if x1 != 0 or y1 != 0 or x2 != 0 or y2!=0:
        if x1 < 150:  
            cv2.rectangle(frame1, (0, y1 - 50), (x2+60, frame1.shape[0]), (255, 0, 0), -1)
        else:
            #cv2.rectangle(frame, (x1 - 80, y1 - 20), (750, frame1.shape[0]), (255, 255, 255), -1)
            cv2.rectangle(frame1, (x1 - 80, y1 - 25), (700, frame1.shape[0]), (255, 0, 0), -1)

    return frame1, (x1, y1, x2, y2)

def frame_diff(frame_path, max_th, min_th):

    prev_score = -1
    prev_image = []

    dir = sorted(os.listdir(frame_path))

    i = ''
    prev_path = ''

    found_before = 0
    q = deque()

    face_cord = (0,0,0,0)

    final_images = []

    for i in dir:
        
        frame, face_cord = edit_image(frame_path, i, face_cord)
        
        if len(prev_image) == 0:
            prev_image = frame
            prev_path = os.path.join(frame_path, str(i))
            continue


        (score, diff) = ssim(frame, prev_image, full=True)

        if prev_score > max_th and score < min_th:
            
            for k in range(len(q)):
                (score1, diff1) = ssim(q[k], prev_image, full=True)
                
                if score1 >= 0.93:
                    found_before = 1
                    print("=======found repeated======", score1)
                    break
               
            if found_before == 0:
                final_images.append(prev_path)
                print("saving frame and sending to pdf")
                if len(q)==8:
                    q.popleft()
                q.append(prev_image)
                
            
            found_before = 0

            #cv2.imwrite(result_path + "/result%d.jpg" % count, prev_image)
                 
        prev_image = frame
        prev_score = score
        prev_path = os.path.join(frame_path, str(i))

    final_images.append(os.path.join(frame_path, str(i)))
    

    return final_images

def start_from_here(video_id, frame_path, result_path, thresh):
    max_th = thresh
    min_th = thresh
    final_images_paths = frame_diff(frame_path, max_th, min_th)

    pdf = FPDF('P', 'mm', (200, 112))

    for j in final_images_paths:
        pdf.add_page()
        pdf.image(j, 0, 0, 200)

    pdf_path = os.path.join(result_path, video_id) + ".pdf"
    pdf.output(pdf_path, "F") 

    try:
        uploaded_img, uploaded_pdf = upload_s3.upload_file(video_id, final_images_paths, pdf_path)
        print(uploaded_pdf)
    except Exception as e:
        print('Cant Upload to S3 or postgres', e)
    
    try:
        os.remove(pdf_path)
    except:
        print('pdf path not removed')