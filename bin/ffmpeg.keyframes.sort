#!/usr/bin/python3
import argparse
import io
import os
import tempfile

import ffmpeg
import numpy as np
from annoy import AnnoyIndex
from PIL import Image


def frame_to_vector(frame_data, size=(64, 64)):
    img = Image.open(io.BytesIO(frame_data))
    img = img.resize(size).convert('L')
    return np.array(img).flatten().astype('float32') / 255.0


def extract_keyframes_ffmpeg_filter(input_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_pattern = os.path.join(temp_dir, 'frame_%05d.png')

        (
            ffmpeg.input(input_path)
            .output(output_pattern, vf="select='eq(pict_type,PICT_TYPE_I)'", vsync='vfr')
            .run(quiet=True, overwrite_output=True)
        )
        keyframes = []
        frame_files = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])

        for i, frame_file in enumerate(frame_files):
            with open(os.path.join(temp_dir, frame_file), 'rb') as f:
                frame_data = f.read()
            vector = frame_to_vector(frame_data)
            keyframes.append((f'frame_{i}', vector, frame_data))

        return keyframes


def sort_frames_by_similarity(input_path, output_path, n_neighbors=50, tree_count=10):
    keyframes = []
    keyframes = extract_keyframes_ffmpeg_filter(input_path)
    if not keyframes:
        print("Could not extract any frames. Aborting.")
        return

    frame_dims = keyframes[0][1].shape[0]
    print(f"Extracted {len(keyframes)} keyframes with vector size {frame_dims}.")

    ann = AnnoyIndex(frame_dims, 'angular')
    frame_data_map = {}
    for i, (uid, vector, frame_data) in enumerate(keyframes):
        ann.add_item(i, vector)
        frame_data_map[i] = (uid, frame_data)

    ann.build(tree_count)

    current_index = 0
    sorted_indices = [current_index]
    visited_indices = {current_index}
    while len(sorted_indices) < len(keyframes):
        neighbors = ann.get_nns_by_item(current_index, n_neighbors, include_distances=True)
        found_next = False

        for next_index in neighbors[0]:
            if next_index not in visited_indices:
                current_index = next_index
                sorted_indices.append(current_index)
                visited_indices.add(current_index)
                found_next = True
                break

        if not found_next and len(sorted_indices) < len(keyframes):
            # Fallback: add first unvisited frame
            unvisited = [i for i in range(len(keyframes)) if i not in visited_indices]
            if unvisited:
                current_index = unvisited[0]
                sorted_indices.append(current_index)
                visited_indices.add(current_index)

    with tempfile.TemporaryDirectory() as temp_img_dir:
        for i, frame_index in enumerate(sorted_indices):
            _, frame_data = frame_data_map[frame_index]
            with open(os.path.join(temp_img_dir, f'sorted_frame_{i:05d}.png'), 'wb') as f:
                f.write(frame_data)

        output_fps = 3
        (
            ffmpeg.input(f'{temp_img_dir}/sorted_frame_%05d.png', framerate=output_fps)
            .output(output_path, vcodec='libx264', pix_fmt='yuv420p', crf=20)
            .run(quiet=True, overwrite_output=True)
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort video keyframes by visual similarity using Annoy.")
    parser.add_argument("input_path", type=str, help="Path to the input video file.")
    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        default="sorted_output.mp4",
        help="Path for the output sorted video file (default: sorted_output.mp4).",
    )
    parser.add_argument(
        "-n",
        "--n-neighbors",
        type=int,
        default=200,
        help="Number of nearest neighbors to check for the next best frame (default: 200).",
    )
    parser.add_argument(
        "-t",
        "--tree-count",
        type=int,
        default=30,
        help="Number of trees for Annoy (higher is more accurate, slower build, default: 30).",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print(f"Error: Input file '{args.input_path}' not found.")
        exit(1)

    sort_frames_by_similarity(args.input_path, args.output_path, args.n_neighbors, args.tree_count)
