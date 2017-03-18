import cv2
import numpy as np

from collections import deque

# Define a class to receive the characteristics of each line detection
class Line():

    ym_per_pix = 30/720 # meters per pixel in y dimension
    xm_per_pix = 3.7/700 # meters per pixel in x dimension
    MAX_FITS = 15

    def __init__(self):
        # was the line detected in the last iteration?
        self.detected = False  
        # x values of the last n fits of the line
        self.recent_xfitted = []
        #average x values of the fitted line over the last n iterations
        self.bestx = None     
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = None
        #polynomial coefficients for the most recent fit
        self.current_fit = []
        # polynomial coefficients for the last coefficients
        self.all_fits = deque()
        #radius of curvature of the line in some units
        self.radius_of_curvature = None 
        #distance in meters of vehicle center from the line
        self.line_base_pos = None 
        #difference in fit coefficients between last and new fits
        self.diffs = np.array([0,0,0], dtype='float') 
        #x values for detected line pixels
        self.allx = None  
        #y values for detected line pixels
        self.ally = None

    def add_fit(self, coeffs):
        if self.best_fit != None:
            current_diffs = np.abs(self.best_fit - coeffs)
            if (np.max(current_diffs) > 210.0):
                 return

        self.current_fit = coeffs
        self.all_fits.append(coeffs)
        num_coeffs = len(self.all_fits)

        if (len(self.all_fits) > self.MAX_FITS):
            self.all_fits.popleft()
            num_coeffs = self.MAX_FITS
        
        self.best_fit = np.array([0.0, 0.0, 0.0])
        for coef in self.all_fits:
            self.best_fit += coef
        
        self.best_fit = self.best_fit / num_coeffs
        
    def compute_all_points(self):
        self.allx = self.best_fit[0]*self.ally**2 + self.best_fit[1]*self.ally + self.best_fit[2]
    
    def draw_on_img(self, img, color=(255, 255, 0), thickness=2):
        for idx in range(len(self.ally)):
            cv2.circle(img, (int(self.allx[idx]), int(self.ally[idx])), 1, color, thickness)

    def compute_stats(self):
        y_eval = np.max(self.ally)

        # Fit new polynomials to x,y in world space
        fit_cr = np.polyfit(self.ally*self.ym_per_pix, self.allx*self.xm_per_pix, 2)

        # Calculate the new radii of curvature
        self.radius_of_curvature = ((1 + (2*fit_cr[0]*y_eval*self.ym_per_pix + fit_cr[1])**2)**1.5) / np.absolute(2*fit_cr[0])

        # Line positions
        self.line_base_pos = int(fit_cr[0]*y_eval**2 + fit_cr[1]*y_eval + fit_cr[2])
