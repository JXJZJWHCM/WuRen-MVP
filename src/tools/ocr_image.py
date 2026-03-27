import argparse
import os

from src.utils.ocr import ocr_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="Image file path (png/jpg/webp)")
    args = parser.parse_args()

    image_path = args.image_path
    if not os.path.exists(image_path):
        raise SystemExit(f"Image not found: {image_path}")

    text, provider = ocr_image(image_path=image_path)
    print(f"[provider] {provider}")
    print(text)


if __name__ == "__main__":
    main()
