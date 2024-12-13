#!/usr/bin/python3
import os

import cv2
import numpy as np
import skimage.color
import skimage.measure
import skimage.morphology
from library.utils import argparse_utils


def crop_rectangles(image_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    image_hsv = skimage.color.rgb2hsv(image_rgb)
    seg = image_hsv[:, :, 1] < 0.10

    seg_cleaned = skimage.morphology.isotropic_opening(seg, 1)
    seg_cleaned = skimage.morphology.isotropic_closing(seg_cleaned, 25)

    def get_main_component(segments):
        labels = skimage.measure.label(segments)
        if labels.max() == 0:
            return segments
        return labels == np.argmax(np.bincount(labels.flat)[1:]) + 1

    background = get_main_component(~seg_cleaned)
    filled = ~background

    mask = skimage.morphology.isotropic_opening(filled, 100)

    masked_result = image_rgb.copy()
    masked_result[~mask, :] = 0

    mask_x = mask.max(axis=0)
    mask_y = mask.max(axis=1)
    indices_x = mask_x.nonzero()[0]
    indices_y = mask_y.nonzero()[0]
    minx, maxx = int(indices_x[0]), int(indices_x[-1])
    miny, maxy = int(indices_y[0]), int(indices_y[-1])

    cropped = img[miny:maxy, minx:maxx]
    output_path = os.path.join(output_folder, "cropped_image.jpg")
    cv2.imwrite(output_path, cropped)


def main():
    parser = argparse_utils.ArgumentParser(description='Crop main component from an image.')
    parser.add_argument('input_image', type=str, help='Path to the input image')
    parser.add_argument(
        '-o', '--output_folder', type=str, default='output/', help='Output folder to save cropped image'
    )
    args = parser.parse_args()

    input_image_path = args.input_image
    output_folder = args.output_folder

    crop_rectangles(input_image_path, output_folder)


if __name__ == "__main__":
    main()
