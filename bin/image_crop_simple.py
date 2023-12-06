#!/usr/bin/python3
import cv2
import numpy as np
import os
import argparse

def crop_rectangles(image_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    upper_threshold, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lower_threshold = 0.5 * upper_threshold

    canny = cv2.Canny(gray, lower_threshold, upper_threshold)
    pts = np.argwhere(canny > 0)

    y1, x1 = pts.min(axis=0)
    y2, x2 = pts.max(axis=0)
    output_image = img[y1:y2, x1:x2]

    output_path = os.path.join(output_folder, "cropped_image.jpg")
    cv2.imwrite(output_path, output_image)

def main():
    parser = argparse.ArgumentParser(description='Crop based on edge detection.')
    parser.add_argument('input_image', type=str, help='Path to the input image')
    parser.add_argument('-o', '--output_folder', type=str, default='output/', help='Output folder to save cropped image')
    args = parser.parse_args()

    input_image_path = args.input_image
    output_folder = args.output_folder

    crop_rectangles(input_image_path, output_folder)

if __name__ == "__main__":
    main()
