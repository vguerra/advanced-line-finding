import glob
import pickle
import os.path

import cv2
import numpy as np
import matplotlib.pyplot as plt

from config import BOARD_SHAPE

class CameraCalibrator:

    _debug = True

    def __init__(self, images_path, board_shape):
        # board shape
        self._nx = board_shape[0]
        self._ny = board_shape[1]

        # directory path where the calibrations images reside
        self._cal_imgs_path = images_path

        # camera matrix and distortion coefficients
        # check for cached mtx and dist first
        cache_file = images_path + '/calibration.p'
        if os.path.exists(cache_file):
            print("reading calibration info from cache")
            f = open(cache_file, "rb")
            calibration_info = pickle.load(f)
            f.close()
        else:
            # if not found in cache then compute
            calibration_info = self._calibrate_camera()
            f = open(cache_file, "wb")
            print("dumping calibration to cache")
            pickle.dump(calibration_info, f)
            f.close()

        self._mtx = calibration_info["mtx"]
        self._dist = calibration_info["dist"]
    
    def undistort(self, img):
        return cv2.undistort(img, self._mtx, self._dist, None, self._mtx)


    def _calibrate_camera(self):
        """
        Calibrates a camera given a folder of images for calibration.
        """
        
        # computing points of interest for calibrating calibrate_camera
        # 3d and 2d points in calibration images.
        objpoints, imgpoints, img_shape = self._compute_points()

        img_size = (img_shape[1], img_shape[0])

        # we compute the camera matrix and distrotion coeff.
        ret, mtx, dist, _, _ = cv2.calibrateCamera(objpoints,
            imgpoints,
            img_size,
            None,
            None)

        calibration_info = {}
        calibration_info["mtx"] = mtx
        calibration_info["dist"] = dist
        return calibration_info

    def _compute_points(self):
        """
        Goes over all calibration images in given path
        and returns a tuple of lists so that:
        - firs tuple element represents 3d points in real space.
        - second tuple element represents 2d points in image space.
        - third the shape of images used for calibration.
        """
        points = np.zeros((self._nx*self._ny, 3), np.float32)
        points[:, :2] = np.mgrid[0:self._nx, 0:self._ny].T.reshape(-1,2)

        objpoints = []
        imgpoints = []
        img_shape = ()
        imgs = glob.glob(self._cal_imgs_path + '/calibration*.jpg')

        if (len(imgs) > 0):
            img_shape = cv2.imread(imgs[0]).shape

        for index, img_file in enumerate(imgs):
            img = cv2.imread(img_file)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            found, corners = cv2.findChessboardCorners(gray, (self._nx, self._ny), None)
            if found:
                objpoints.append(points)
                imgpoints.append(corners)
                cv2.drawChessboardCorners(img, (self._nx, self._ny), corners, True)

                if self._debug:
                    output_img_file = './output_images/calibration' + str(index) + '.jpg' 
                    print(output_img_file)
                    cv2.imwrite(output_img_file, img)
        
        return objpoints, imgpoints, img_shape

if __name__ == '__main__':
    cam_calibration = CameraCalibrator('./camera_cal', BOARD_SHAPE)