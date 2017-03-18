# Advanced Line Finding

* [The goal](#the-goal)
* [Rubric](#rubric)
* [Writeup](#writeup)
* [The Code](#the-code)
* [Camera Calibration](#camera-calibration)
* [Pipeline](#pipeline)
* [Output video](#output-video)
* [Discussion](#discussion)

---

## The Goal
What we want to achieve with this project is to be able to visually highlight
the lane boundaries on the road that our car has to respect.

The following steps are going to help us to get to our goal: 

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

---

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points
Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---

## Writeup
This document that you are reading! :).

---

## The Code
The project is organized as follows:
* `camera_cal` folder containing all chess board images used for camera calibration.
* `output_images` folder containing all debug images and videos displayed throughout this write up.
* `src` folder containing all source code of the project. Containing:
    - `ALF.py`: Containing a Class that implements the whole pipeline of finding lanes.
    - `calibration.py`: Implementation of calibration of car's camera.
    - `colorthreshold.py`: Threshold of color and gradient for images.
    - `line.py`: Class that encapsulates all information about found Lanes.
    - `linefinder.py` : Implements the algorithm to find lanes.
    - `transform.py` : Perspective transformation implementation.
    - `config.py`: Configuration parameters for the entire pipeline.
    - `util.py`: Utilities for parsing command line arguments and debugging.

---

## Camera Calibration
This is the first step performed in the entire [pipeline](https://github.com/vguerra/advanced-line-finding/blob/master/src/ALF.py#L15). The [CameraCalibrator class](https://github.com/vguerra/advanced-line-finding/blob/master/src/calibration.py#L11) is in charge of:
* Computing the camera matrix and distrotion coefficients.
* Uses all this information to undistort the stream of images coming from the car's camera.

The Camera Calibration process goes as follows:

* Using a set of [calibration images](https://github.com/vguerra/advanced-line-finding/tree/master/camera_cal) that contain a chess board with dimensions 9 x 6 taken from different perspectives, we find the corners of each board square. First, each image is converted to gray scale and then OpenCV function `findChessboardCorners` is used to find all corners. To help understand what `findChessboardCorners` looks for, we can have a look at one of the images with all corners found marked:

<p align="center">
<img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/calibration11.jpg" width="400">
</p>

This entire process is performed by the [`_compute_points` method](https://github.com/vguerra/advanced-line-finding/blob/master/src/calibration.py#L69-L103) of the CameraCalibrator class.
* Once all points describing the corners are gathered, we proceed to [compute the camera matrix and distortion coefficients](https://github.com/vguerra/advanced-line-finding/blob/master/src/calibration.py#L58) using the OpenCV function `calibrateCamera`.
* Now that we know the camera matrix and distortion coefficients we can undistort any image taken with the car's camera. For that purpose, we use the OpenCV funtion `undistort`. This is done by the [`undistort` method](https://github.com/vguerra/advanced-line-finding/blob/master/src/calibration.py#L42)

Here we can see how an image used for calibration is undistorted:

* Original Image
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/calibration1.jpg" width="500">
</p>

* Undistorted Image
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/calibration1_undistorted.jpg" width="500">
</p>

In order to avoid re-computation of needed calibration information a [cache](https://github.com/vguerra/advanced-line-finding/blob/master/src/calibration.py#L25-L40) is put in place so that everytime the pipeline is started we save some time.

---

## Pipeline

The entire pipeline is implemented within the class [ALF](https://github.com/vguerra/advanced-line-finding/blob/master/src/ALF.py#L13) (short for Advanced Lane Finding). For each frame in the video, the method [`process`](https://github.com/vguerra/advanced-line-finding/blob/master/src/ALF.py#L20-L66) returns a modified image that has marked a corresponding lane where the car should drive, as well as some debug information about what's happening through the calculation of that area.

As mentioned above, the first phase in the pipeline is to do the camera calibration. Once calibration is out of the way, the pipeline continues with: 

### Undistortion
Using the camera calibration information the function in OpenCV `undistort` is used to [correct distortion](https://github.com/vguerra/advanced-line-finding/blob/master/src/calibration.py#L42-L43) on images. For example, if we take this shot from the car's camera:

* Original Image
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/original.jpg" width="500">
</p>

* Undistorted Image
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/undist.jpg" width="500">
</p>


### Color and Gradient Threshold
Next step in the pipeline is the [thresholding of gradients and color](https://github.com/vguerra/advanced-line-finding/blob/master/src/ALF.py#L26). This is implemented by the [`threshold_color`](https://github.com/vguerra/advanced-line-finding/blob/master/src/colorthreshold.py#L4-L31) defined in `src\colorthreshold.py`. We try to combine color and gradient thresholding so that we can identify the lanes on the road.

We first convert the image to a HLS color space, specially because we want to use the L and S channels.  The S channel does a good job picking up the lines under different color and contrast conditions. The L channel will help us to detect edges. We compute the gradient for the luminosity channel (L) and we do that with the help of the OpenCV function `Sobel`. Once the gradient is computed, we threshold it. We threshold as well the saturation channel (S) and at the end, the result of both thresholds are combined.

One example of the resulting binary image would be:

* Undistorted Image
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/undist.jpg" width="500">
</p>

* Color and Gradient Threshold
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/color_binary.jpg" width="500">
</p>

All green pixels in the image are the contribution of the gradient threshold, the red ones are coming from the saturation channel threshold. If we combine them:

* Color and Gradient Threshold - Binary
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/binary.jpg" width="500">
</p>

The ranges used for thresholding are as follow (values chosen from observing what worked best): 
* S channel (190, 255)
* L channel gradient (100, 150)

---

### Perspective transformation
The idea of doing a perspective transformation on the images is to have a birds eye view of the road, having this view should facilitate finding the lines that define our lanes. Ideally they should look like straight lines.

The class [PerspectiveTransformer](https://github.com/vguerra/advanced-line-finding/blob/master/src/transform.py#L4) implements all the logic for the image transformation.

We need to compute a perspective matrix using the OpenCV function `getPerspectiveTransform`. The parameters for this function are two sets of points that map a rectangle from one perspective to the other. The sets of points were hand-picked with the help of an image viewer. We know that our lanes would form a Trapezoid which would look like a rectangle from a birds eye view perspective. Hence, we define the following geometric figures for computing the perspective matrix:

The points used to define a Trapeziod (starting from the upper-right corner and finishing at the upper-left corner):
```  
    src = np.float32(
        [[700, 458],
        [1040, 686],
        [250, 686],
        [580, 458]])
```

The points used to define a rectangle in the transformed space (starting from the upper-right corner and finishing at the upper-left corner):
```
    dst = np.float32(
        [[1040, 0],
        [1040, 686],
        [250, 686],
        [250, 0]])
```

Given this two sets of points we can compute matrices to transform [from one space to the other](https://github.com/vguerra/advanced-line-finding/blob/master/src/transform.py#L18-L19).

To help us perform the space transformation for an image we use the OpenCV function `warpPerspective`. The PerspectiveTransformer class has two methods to [warp](https://github.com/vguerra/advanced-line-finding/blob/master/src/transform.py#L21-L23) and [unwarp](https://github.com/vguerra/advanced-line-finding/blob/master/src/transform.py#L25-L27) an image.

An examples of a warped image would be:

* Color and Gradient Threshold
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/color_binary.jpg" width="500">
</p>

* Warped - Color and Gradient Threshold
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/warped_color_binary.jpg" width="500">
</p>

---

### Identifying lanes
Now that we have a birds eye view image with pixels that could give us information about where to find the lines, we proceed with the [detection process](https://github.com/vguerra/advanced-line-finding/blob/master/src/ALF.py#L43). The [`line_finder`](https://github.com/vguerra/advanced-line-finding/blob/master/src/linefinder.py#L30-L125) method defined in `src\linefinder.py` encapsulates the logic for this process.

The first step is to find where are the bases for the left and right lines. For this, we [build a histogram](https://github.com/vguerra/advanced-line-finding/blob/master/src/linefinder.py#L33-L38) over the x axis for each of the halfs of the image. The histogram will present a peak where the higher concentration of pixels is located, there is a big change that our lines are located at this peaks.

Once the bases for each line are identified we proceed with the [search of the lines](https://github.com/vguerra/advanced-line-finding/blob/master/src/linefinder.py#L60-L88). We define 9 search regions for each line. Each search region is simple a rectangle in which we look all the none 0 pixels defined in the image. All this pixels are gathered and will be used later to define a [second order polynomial](https://github.com/vguerra/advanced-line-finding/blob/master/src/linefinder.py#L107-L108) that describes a line. The OpenCV function `polyfit` helps us here.

The following image shows the search regions defined for each line and the second order polynomials that best describe each of the lines:

* Search regions and 2nd order Polynomials.
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/debug_birds_eye.jpg" width="500">
</p>

All the information found about pixels and polynomial coefficients is stored into a [Line object](https://github.com/vguerra/advanced-line-finding/blob/master/src/line.py#L7). During the whole pipeline 2 of this objects are used to represent information gathered for the [Left and Right line](https://github.com/vguerra/advanced-line-finding/blob/master/src/ALF.py#L17-L18).

At this point we can [project the lines](https://github.com/vguerra/advanced-line-finding/blob/master/src/linefinder.py#L6-L28) we found into our birds eye view image.

* Lines on birds eye view Image.
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/debug_warped_lines.jpg" width="500">
</p>

---

### Radius of curvature and car position
The final step is to compute radius of curvature and car position which is done by a utility method that computes all this [stats](https://github.com/vguerra/advanced-line-finding/blob/master/src/util.py#L40-L53).

* The radius of curvature is [computed for each Line](https://github.com/vguerra/advanced-line-finding/blob/master/src/line.py#L64-L74) and then averaged among the two lines. For this process the polynomial representing the line has to be converted to the real world space first and then the following formula is used to compute the curvature:

<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/r-curvature.png" width="300">
</p>
where A and B are the 2nd and 1rst order coefficients of the polynomial of the line in the real world.

* For the [car position](https://github.com/vguerra/advanced-line-finding/blob/master/src/util.py#L46-L48), we simply take the mid point of the two lines bases that will be the point the middle of the car should be at and substracted from the middle of the image ( which is the real car position at a given frame).

---

### Puting all together
Finally we put all information together with some debug images to understand what is going on during the pipeline. The final result is an image that looks as follows:

* Final result.
<p align="center">
 <img src="https://github.com/vguerra/advanced-line-finding/blob/master/output_images/result.jpg" width="500">
</p>

* The debug image at the top left shows the resulting driving area in green on the birds eye view perspective.
* The debug image at the top center shows all regions used to search for lines, as well as the pixels that contributed to the lane definition. The second order polynomial is as well shown.
* At the top right all information regarding radious of curvature and car position w.r.t. to the center.

---

## Output video

Now it is time to see all put together in action. Checkout this repository and at the root directory execute the following:
```
$> python src/ALF.py ./camera_cal --video project_video.mp4 --output output_project_video.mp4
```
The `output_project_video.mp4` should look something like this:

[![Project Video](https://img.youtube.com/vi/u6KVd3F_oEg/0.jpg)](https://youtu.be/u6KVd3F_oEg)

---
## Discussion

1. The hardest part during implementation of this project was the handling of outliers. To tackel this problem I implemented [2 simple strategies](https://github.com/vguerra/advanced-line-finding/blob/master/src/line.py#L37-L55):

* To describe a line, use an average of the last best 15 polynomial fits.
* Ignoring all those polynomials for which at least one of the coefficients is greather than 210.0 ( value chosen by trial and error ) w.r.t to the best fit mentioned in the previous point. 

2. To search for all pixels that contribute to the definition of a line I tried the convolutional approach recommended in the lectures, unfortunately it was performing really bad. Much so, on the parts of the video on which there are tree shadows on the road. The resulting polynomials, specially for the left line, were having parabolic shapes. Messing up the resulting drawings even with the outlier detection mechanism I mentioned on point 1.

3. One point I thought would be worth trying is the recomendation on the Rubric about re-using search areas and not blindly repeat the whole process of search for each frame. Currently the generation of the video takes a lot of resources, slowing down its process. This solution would clearly  not work in a real time environment. As well, the recomendation mentions that this would help with outlier detection.