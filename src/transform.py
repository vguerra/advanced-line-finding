import cv2
import numpy as np

class PerspectiveTransformer():
    src = np.float32(
        [[700, 458],
        [1040, 686],
        [250, 686],
        [580, 458]])

    dst = np.float32(
        [[1040, 0],
        [1040, 686],
        [250, 686],
        [250, 0]])

    def __init__(self):
        self.warp_matrix = cv2.getPerspectiveTransform(self.src, self.dst)
        self.unwarp_matrix = cv2.getPerspectiveTransform(self.dst, self.src)

    def warp(self, img):
        img_size = img.shape[1], img.shape[0]
        return cv2.warpPerspective(img, self.warp_matrix, img_size, flags=cv2.INTER_LINEAR)

    def unwarp(self, img):
        img_size = img.shape[1], img.shape[0]
        return cv2.warpPerspective(img, self.unwarp_matrix, img_size, flags=cv2.INTER_LINEAR)

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    transformer = PerspectiveTransformer()

    img = cv2.imread('./test_images/straight_lines1.jpg')
    plt.imshow(img)
    plt.show()
    plt.clf()

    warped = transformer.warp(img)
    plt.imshow(warped)
    plt.show()
    plt.clf()

    unwarped = transformer.unwarp(warped)
    plt.imshow(unwarped)
    plt.show()
    plt.clf()


    