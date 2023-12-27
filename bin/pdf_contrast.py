#!/usr/bin/python3

import argparse
import io
import os
from pathlib import Path
from typing import List

import img2pdf
import ocrmypdf
import pdf2image
from PIL import ImageEnhance, Image
from tqdm import tqdm


def pdf_contrast(args):
    if args.input_path.is_dir():
        files = sorted(p for p in args.input_path.glob('*') if p.suffix != '.pdf')
        input_images = [Image.open(p) for p in files]
    else:
        input_images = pdf2image.convert_from_path(args.input_path)
    print(f'Loaded {len(input_images)} pages')

    output_images: list[bytes] = []
    for img in tqdm(input_images, unit="pages"):
        for method in ['Brightness', 'Contrast', 'Color', 'Sharpness']:
            val = getattr(args, method.lower())
            if val != 100:
                enhancer = getattr(ImageEnhance, method)(img)
                img = enhancer.enhance(val / 100)

        out_img_bytes = io.BytesIO()
        img.save(out_img_bytes, format="JPEG")
        output_images.append(out_img_bytes.getvalue())

    print(f'Saving {args.output_path}')
    if args.output_path.endswith(os.sep) or args.output_path.is_dir():
        output_path = Path(args.output_path)
        output_path.mkdir(exist_ok=True, parents=True)
        for i, page_bytes in enumerate(output_images):
            page_name = f"{args.input_path.stem}_page_{i + 1}.jpg"
            page_path = output_path / page_name
            with open(page_path, "wb") as page_out:
                page_out.write(page_bytes)
    else:
        with open(args.output_path, "wb") as outf:
            img2pdf.convert(*output_images, outputstream=outf)

        if args.ocr:
            ocrmypdf.ocr(args.output_path, args.output_path, deskew=True, optimize=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--brightness", "-b", type=int, default=100)
    parser.add_argument("--contrast", "-c", type=int, default=100)
    parser.add_argument("--color", "-C", type=int, default=100)
    parser.add_argument("--sharpness", "-s", type=int, default=100)
    parser.add_argument("--no-ocr", "--skip-ocr", dest='ocr', action='store_false')

    parser.add_argument("input_path", help="Input PDF file")
    parser.add_argument("output_path", nargs='?', help="Output PDF file")
    args = parser.parse_intermixed_args()

    args.input_path = Path(args.input_path).resolve()

    if args.output_path is None:
        params: List[str] = []
        if args.contrast != 100:
            params.append(f"c{args.contrast}")
        if args.brightness != 100:
            params.append(f"b{args.brightness}")
        if args.color != 100:
            params.append(f"C{args.color}")
        if args.sharpness != 100:
            params.append(f"s{args.sharpness}")

        suffix = '.' + '.'.join(params) + '.pdf'
        if Path(args.input_path).is_dir():
            args.output_path = (args.input_path / args.input_path.name).with_suffix(suffix)
        else:
            args.output_path = os.path.splitext(args.input_path)[0] + suffix

    pdf_contrast(args)
