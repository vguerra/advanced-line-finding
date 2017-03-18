import cv2
import numpy as np
import matplotlib.pyplot as plt
from util import showimg

def draw_lane_area(p_transformer, warped_img, undist_img, real_warped_img, left_line, right_line):
    # Create an image to draw the lines on
    warp_zero = np.zeros_like(warped_img).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    # Recast the x and y points into usable format for cv2.fillPoly()
    # pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_left = np.array([np.transpose(np.vstack([left_line.allx, left_line.ally]))])
    # pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_line.allx, right_line.ally])))])
    pts = np.hstack((pts_left, pts_right))

    # Draw the lane onto the warped blank image
    cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))
    debug_result = cv2.addWeighted(real_warped_img, 1, color_warp, 0.3, 0)

    # Warp the blank back to original image space using inverse perspective matrix (Minv)
    newwarp = p_transformer.unwarp(color_warp)
    # newwarp = cv2.warpPerspective(color_warp, Minv, (image.shape[1], image.shape[0])) 
    
    # Combine the result with the original image
    result = cv2.addWeighted(undist_img, 1, newwarp, 0.3, 0)
    return result, debug_result

def line_finder(binary_img, color_img, left_line, right_line):
    debug_color = np.copy(color_img)

    midpoint_y = np.int(binary_img.shape[0]/2)
    histogram = np.sum(binary_img[midpoint_y:,:], axis=0)

    midpoint = np.int(np.int(histogram.shape[0]/2))
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    nwindows = 9

    # Set height of windows
    window_height = np.int(binary_img.shape[0]/nwindows)
    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = binary_img.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # Current positions to be updated for each window
    leftx_current = leftx_base
    rightx_current = rightx_base
    # Set the width of the windows +/- margin
    margin = 100
    # Set minimum number of pixels found to recenter window
    minpix = 50
    # Create empty lists to receive left and right lane pixel indices
    left_lane_inds = []
    right_lane_inds = []

    # Step through the windows one by one
    for window in range(nwindows):
        # Identify window boundaries in x and y (and right and left)
        win_y_low = binary_img.shape[0] - (window+1)*window_height
        win_y_high = binary_img.shape[0] - window*window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin
        # Draw the windows on the visualization image
        cv2.rectangle(debug_color, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), (0,255,0), 2) 
        cv2.rectangle(debug_color, (win_xright_low, win_y_low), (win_xright_high, win_y_high), (0,255,0), 2) 

        # Identify the nonzero pixels in x and y within the window
        good_left_inds = ((nonzeroy >= win_y_low)
                        & (nonzeroy < win_y_high) 
                        & (nonzerox >= win_xleft_low) 
                        & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) 
                        & (nonzeroy < win_y_high) 
                        & (nonzerox >= win_xright_low) 
                        & (nonzerox < win_xright_high)).nonzero()[0]
        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)
        # If you found > minpix pixels, recenter next window on their mean position
        if len(good_left_inds) > minpix:
            leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int(np.mean(nonzerox[good_right_inds]))
        
    # Concatenate the arrays of indices
    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds] 
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds] 

    for idx in range(len(lefty)):
        cv2.circle(debug_color, (int(leftx[idx]), int(lefty[idx])), 1, (255, 255, 255), 0)

    for idx in range(len(righty)):
        cv2.circle(debug_color, (int(rightx[idx]), int(righty[idx])), 1, (255, 255, 255), 0)

    # Fit a second order polynomial to each
    left_line.add_fit(np.polyfit(lefty, leftx, 2))
    right_line.add_fit(np.polyfit(righty, rightx, 2))

    # Generate x and y values for plotting
    left_line.ally = np.linspace(0, binary_img.shape[0]-1, binary_img.shape[0])
    right_line.ally = left_line.ally

    left_line.compute_all_points()
    right_line.compute_all_points()

    left_line.draw_on_img(debug_color, thickness=2)
    right_line.draw_on_img(debug_color, thickness=2)

    left_line.compute_stats()
    right_line.compute_stats()

    showimg(debug_color, "DEBUG COLOR")

    return debug_color