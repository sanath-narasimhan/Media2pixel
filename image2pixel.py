
# Created At: 2024-10-22
# Author: Sanath Narasimhan
# Reference: https://github.com/Tezumie/Image-to-Pixel?tab=readme-ov-file

from PIL import Image, ImageDraw
import numpy as np
import json
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")
    
def load_palette(palette_name=None):
    if palette_name is not None:
        palette_path = os.path.join('palette',palette_name+'.json')
        with open(palette_path,'r') as file_pointer:
            palette = json.load(file_pointer)
        if palette:
            return palette['colors']

def apply_palette(image, palette_colors):
    image_data = np.array(image)
    height, width, _ = image_data.shape

    for y in range(height):
        for x in range(width):
            old_color = image_data[y, x, :3]
            new_color = find_closest_palette_color(old_color, palette_colors)
            image_data[y, x, :3] = new_color

    return Image.fromarray(image_data)

def find_closest_palette_color(old_color, palette_colors):
    r, g, b = old_color
    distances = [(r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2 for pr, pg, pb in palette_colors]
    return palette_colors[np.argmin(distances)]

def floyd_steinberg_dithering(image, strength, palette_colors):
    image_data = np.array(image)
    height, width, _ = image_data.shape
    error_buffer = np.zeros_like(image_data, dtype=float)

    for y in range(height):
        for x in range(width):
            old_color = image_data[y, x, :3] + error_buffer[y, x, :3]
            new_color = find_closest_palette_color(old_color, palette_colors)
            image_data[y, x, :3] = new_color

            quant_error = (old_color - new_color) * strength
            if x + 1 < width:
                error_buffer[y, x + 1, :3] += quant_error * (7 / 16)
            if x - 1 >= 0 and y + 1 < height:
                error_buffer[y + 1, x - 1, :3] += quant_error * (3 / 16)
            if y + 1 < height:
                error_buffer[y + 1, x, :3] += quant_error * (5 / 16)
            if x + 1 < width and y + 1 < height:
                error_buffer[y + 1, x + 1, :3] += quant_error * (1 / 16)

    return Image.fromarray(image_data)

def hex_to_rgb(hex_value):
    hex_value = hex_value.lstrip('#')
    return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))

def pixelate(image_path, width, dither='none', strength=0, palette_name=None, resolution='original'):
    image = load_image(image_path)

    # Resize image for pixelation
    aspect_ratio = image.height / image.width
    pixels_high = int(width * aspect_ratio)
    image_resized = image.resize((width, pixels_high), Image.NEAREST)

    # Apply palette and dithering if specified
    if palette_name:
        palette = load_palette(palette_name)
        palette_colors = [hex_to_rgb(color) for color in palette] if isinstance(palette, list) else [hex_to_rgb('#000000'), hex_to_rgb('#FFFFFF')] #fetch_palette(palette)

        if dither == 'Floyd-Steinberg':
            image_resized = floyd_steinberg_dithering(image_resized, strength / 100, palette_colors)
        elif dither == 'none':
            image_resized = apply_palette(image_resized, palette_colors)

    # Resize to original resolution if required
    if resolution == 'original':
        image_resized = image_resized.resize((image.width, image.height), Image.NEAREST)

    return image_resized

# Example usage
"""
image_result = pixelate('no-bg.png', width=256, dither='Floyd-Steinberg', strength=25, palette_name='default')
image_result.show()

"""