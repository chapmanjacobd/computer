#!/usr/bin/python3
import os

import cv2
import numpy as np
from library.utils import argparse_utils


def crop_rectangles(image_path, output_folder, max_rectangles):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    img = cv2.imread(image_path)

    # reduce noise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.medianBlur(gray, 39)

    edged = cv2.Canny(binary, 3, 81)
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, np.ones((5, 5)))

    # Connected component analysis to find separate components
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(edged, connectivity=8)

    valid_rectangles = []
    for i in range(1, nb_components):  # exclude background, start at 1
        area = stats[i, cv2.CC_STAT_AREA]
        x, y, w, h = (
            stats[i, cv2.CC_STAT_LEFT],
            stats[i, cv2.CC_STAT_TOP],
            stats[i, cv2.CC_STAT_WIDTH],
            stats[i, cv2.CC_STAT_HEIGHT],
        )

        # Filter rectangles based on area and aspect ratio
        aspect_ratio = w / float(h)
        if area > 1000 and 0.5 < aspect_ratio < 2.0:
            valid_rectangles.append((x, y, w, h))

    valid_rectangles = sorted(valid_rectangles, key=lambda x: x[2] * x[3], reverse=True)
    valid_rectangles = valid_rectangles[: min(max_rectangles, len(valid_rectangles))]

    # export
    for i, (x, y, w, h) in enumerate(valid_rectangles):
        cropped = img[y : y + h, x : x + w]
        output_path = os.path.join(output_folder, f"sub_image_{i}.jpg")
        cv2.imwrite(output_path, cropped)

        # Optionally, draw the rectangle on the original image for visualization
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Save the image with rectangles drawn (for visualization purposes)
    cv2.imwrite(os.path.join(output_folder, "detected_rectangles.jpg"), img)


def main():
    parser = argparse_utils.ArgumentParser(description='Detect and crop rectangles from an image.')
    parser.add_argument('input_image', type=str, help='Path to the input image')
    parser.add_argument(
        '-o', '--output_folder', type=str, default='output/', help='Output folder to save cropped rectangles'
    )
    args = parser.parse_args()

    input_image_path = args.input_image
    output_folder = args.output_folder

    crop_rectangles(input_image_path, output_folder, max_rectangles=8)


if __name__ == "__main__":
    main()
