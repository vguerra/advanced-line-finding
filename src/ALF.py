from moviepy.editor import VideoFileClip

# Utilities and config
from util import *
from calibration import CameraCalibrator
from transform import PerspectiveTransformer
from colorthreshold import threshold_color
from linefinder import draw_lane_area, line_finder
from line import Line

from config import BOARD_SHAPE

class ALF():
    def __init__(self, img_calibration_path):
        self._cam_calibrator = CameraCalibrator(img_calibration_path, BOARD_SHAPE)
        self._p_transformer = PerspectiveTransformer()
        self._left_line = Line()
        self._right_line = Line()
        
    def process(self, img):
        # Undistortion image
        undist_img = self._cam_calibrator.undistort(img)
        saveimg(undist_img, 'undist')

        # Color thresholding
        color_binary_img, binary_img = threshold_color(undist_img)
        showimg(color_binary_img, "Threshold image - Color")
        saveimg(color_binary_img, 'color_binary')
        showimg(binary_img, "Threshold image - Binary")
        saveimg(binary_img, 'binary')

        # Transform images
        warped_binary_img = self._p_transformer.warp(binary_img)
        saveimg(warped_binary_img, 'warped_binary')
        warped_color_binary_img = self._p_transformer.warp(color_binary_img)
        saveimg(warped_color_binary_img, 'warped_color_binary')
        warped_undist_img = self._p_transformer.warp(undist_img)
        saveimg(warped_undist_img, 'warped_undist')
        showimg(warped_undist_img, "Warped Image")

        # Finding lines info in this image and populate
        # _left_line and _right_line objects
        debug_birds_eye = line_finder(warped_binary_img,
                            warped_color_binary_img,
                            self._left_line,
                            self._right_line)
        showimg(debug_birds_eye, "BIRD EYE")
        saveimg(debug_birds_eye, 'debug_birds_eye')

        # Draw the lines we have so far
        result, debug_warped_lines = draw_lane_area(self._p_transformer,
                                        warped_binary_img,
                                        undist_img,
                                        warped_undist_img,
                                        self._left_line,
                                        self._right_line)
        saveimg(debug_warped_lines, 'debug_warped_lines')

        # # Populate resulting frame with debug images + stats
        result = add_overlay(result)
        result = add_stats(result, self._left_line, self._right_line)
        result = add_debug_img(result, debug_warped_lines, debug_birds_eye)

        showimg(result, "Final Image")
        saveimg(result, 'result')
        return result

if __name__ == '__main__':
    args = parse_args()
    afl = ALF(args.img_calibration_path)
    
    if args.image:
        img = readimg(args.image)
        showimg(img, "ORIGINAL IMAGE")
        result = afl.process(img)
    elif args.video:
        out = "output.mp4" if args.output == None else args.output
        video = VideoFileClip(args.video)
        output_video = video.fl_image(afl.process)
        output_video.write_videofile(out, audio=False)