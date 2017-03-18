import argparse
import cv2
import numpy as np

from config import IMG_SHAPE, DEBUG

FONT = cv2.FONT_HERSHEY_PLAIN
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 0.9
MIDDLE_PIX = 640

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('img_calibration_path', help="Path to directory containing camera calibration images ")
    parser.add_argument('--video', help="Input video")
    parser.add_argument('--image', help="Input image")
    parser.add_argument('--output', help="output video file name")
    return parser.parse_args()

def readimg(path):
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def showimg(img, title="image"):
    if DEBUG:
        cv2.imshow('{} - dtype: {}'.format(title, img.dtype), img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def saveimg(img, title="image"):
    if DEBUG:
        cv2.imwrite('./output_images/' + title + '.jpg', img)

def add_overlay(img, alpha=0.7):
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (1280, 240), (135, 206, 250), -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    return img

def add_stats(img, left_line, right_line):
    avg_curvature = (left_line.radius_of_curvature + right_line.radius_of_curvature)/2
    
    txt = 'Radious of curvature: {:08.2f} mts.'.format(avg_curvature)
    cv2.putText(img, txt, (900, 100), FONT, FONT_SIZE, FONT_COLOR, 1)
    
    car_middle_pixel = int((right_line.line_base_pos + left_line.line_base_pos)/2)
    pixels_off_center = MIDDLE_PIX - car_middle_pixel
    off_center = left_line.xm_per_pix * pixels_off_center

    txt = 'Distance from center: {:04.2f} mts ({})'.format(abs(off_center), 'L' if off_center <= 0 else 'R')
    cv2.putText(img, txt, (900, 150), FONT, FONT_SIZE, FONT_COLOR)
    
    return img

def add_debug_img(img, debug_left_img, debug_right_img, left_top=(10, 50)):
    debug_left_img = cv2.resize(debug_left_img, (128*3, 72*3), interpolation=cv2.INTER_LINEAR)
    debug_right_img = cv2.resize(debug_right_img, (128*3, 72*3), interpolation=cv2.INTER_LINEAR)

    img[10:10 + 216, 50:50 + 384] = debug_left_img
    img[10:10 + 216, 484:484 + 384, :3] = debug_right_img

    return img