import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from flask import current_app

def rgb_to_oklab(rgb_array):
    """
    Converts an RGB numpy array to the perceptually uniform Oklab color space.
    This prevents the "hue-shifting" that causes pinks to turn yellow under bright light.
    """
    # Normalize RGB to 0.0 - 1.0
    rgb = rgb_array.astype(np.float32) / 255.0

    # Convert sRGB to Linear sRGB
    mask = rgb > 0.04045
    rgb_lin = np.empty_like(rgb)
    rgb_lin[mask] = np.power((rgb[mask] + 0.055) / 1.055, 2.4)
    rgb_lin[~mask] = rgb[~mask] / 12.92

    # Matrix 1: Linear sRGB to LMS (Cone responses)
    lms = np.empty_like(rgb_lin)
    lms[..., 0] = 0.4122214708 * rgb_lin[..., 0] + 0.5363325363 * rgb_lin[..., 1] + 0.0514459929 * rgb_lin[..., 2]
    lms[..., 1] = 0.2119034982 * rgb_lin[..., 0] + 0.6806995451 * rgb_lin[..., 1] + 0.1073969566 * rgb_lin[..., 2]
    lms[..., 2] = 0.0883024619 * rgb_lin[..., 0] + 0.2817188376 * rgb_lin[..., 1] + 0.6299787005 * rgb_lin[..., 2]

    # Non-linear perceptual transform
    lms = np.cbrt(np.maximum(lms, 0))  # Prevents NaN on tiny floating point negatives

    # Matrix 2: LMS to Oklab (L = Lightness, a = Green/Red, b = Blue/Yellow)
    oklab = np.empty_like(lms)
    oklab[..., 0] = 0.2104542553 * lms[..., 0] + 0.7936177850 * lms[..., 1] - 0.0040720468 * lms[..., 2]
    oklab[..., 1] = 1.9779984951 * lms[..., 0] - 2.4285922050 * lms[..., 1] + 0.4505937099 * lms[..., 2]
    oklab[..., 2] = 0.0259040371 * lms[..., 0] + 0.7827717662 * lms[..., 1] - 0.8086757660 * lms[..., 2]

    return oklab

def convert_image_to_mc_colors_2(pil_image, target_cols, target_rows, chunk_size=32):
    target_width = target_cols * chunk_size
    target_height = target_rows * chunk_size

    img_rgba = pil_image.convert("RGBA")

    # 1. Resize smoothly
    img_resized = img_rgba.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # 2. VIBRANCE OVERDRIVE
    # By boosting saturation by 50% before processing, we force "logical" colors
    # (like the shadowed peach yolk) across the threshold into vibrant Minecraft dyes (Orange).
    # This also guarantees Kirby's pale blush becomes a deeper, richer Pink.
    enhancer = ImageEnhance.Color(img_resized)
    img_resized = enhancer.enhance(1.5)

    alpha_channel = np.array(img_resized.split()[3])

    # 3. Composite over BLACK
    bg = Image.new("RGBA", img_resized.size, (0, 0, 0, 255))
    img_rgb = Image.alpha_composite(bg, img_resized).convert("RGB")

    img_arr_rgb = np.array(img_rgb, dtype=np.float32)
    height, width, _ = img_arr_rgb.shape

    # Pull palette from Flask context
    dye_ids = list(current_app.color_map.keys())
    dye_colors_rgb = np.array([current_app.color_map[i].rgb for i in dye_ids], dtype=np.float32)

    # Convert Image and Palette to Oklab Space
    img_arr_oklab = rgb_to_oklab(img_arr_rgb)
    dye_colors_oklab = rgb_to_oklab(dye_colors_rgb)

    preview_arr = np.zeros((height, width, 4), dtype=np.uint8)
    number_grid = []

    for y in range(height):
        row_ids = []
        for x in range(width):
            if alpha_channel[y, x] < 128:
                preview_arr[y, x] = [0, 0, 0, 0]
                row_ids.append(0)
            else:
                pixel_oklab = img_arr_oklab[y, x]
                diff = pixel_oklab - dye_colors_oklab

                # 4. Standard Oklab Distance (1:1:1 Weights)
                # Now that the saturation is boosted, we don't need harsh hue weights.
                # Standard weights will smoothly render the sunlit right arm without banding.
                distances = np.sum((diff ** 2), axis=1)
                closest_idx = np.argmin(distances)

                mc_color = dye_colors_rgb[closest_idx]
                preview_arr[y, x] = [int(mc_color[0]), int(mc_color[1]), int(mc_color[2]), 255]
                row_ids.append(dye_ids[closest_idx])

        number_grid.append(row_ids)

    return Image.fromarray(preview_arr, "RGBA"), number_grid

def convert_image_to_mc_colors(pil_image, canvas_columns, canvas_rows, chunk_size=32):
    """
    Resizes, dithers, and quantizes an image to exact Minecraft map colors.

    :param pil_image: Image
    :param canvas_columns: Number of Map columns (Y)
    :param canvas_rows: Number of Map rows (X)
    :param chunk_size: Size of each chunk (How many pixels per line on the map you can draw)

    :return preview_image (PIL.Image): The 1:1 pixel mapped image.
    :return number_grid (list): 2D array of color IDs.
    """
    target_width = canvas_columns * chunk_size
    target_height = canvas_rows * chunk_size

    img = pil_image.convert("RGB").resize((target_width, target_height), Image.Resampling.BILINEAR)
    img_arr = np.array(img, dtype=np.float32)
    height, width, _ = img_arr.shape

    # Bayer ordered dithering
    bayer_matrix = np.array([
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5]
    ], dtype=np.float32) / 16.0 - 0.5

    bayer_tiled = np.tile(bayer_matrix, (height // 4 + 1, width // 4 + 1))[:height, :width]
    bayer_tiled = np.expand_dims(bayer_tiled, axis=-1)

    img_arr += bayer_tiled * 25.0
    img_arr = np.clip(img_arr, 0, 255)

    # Perceptual color matching
    dye_ids = list(current_app.color_map.keys())
    dye_colors = np.array([current_app.color_map[i].rgb for i in dye_ids], dtype=np.float32)
    weights = np.array([2.0, 4.0, 3.0], dtype=np.float32)

    preview_arr = np.zeros((height, width, 3), dtype=np.uint8)
    number_grid = []

    for y in range(height):
        diff = img_arr[y][:, np.newaxis, :] - dye_colors
        distances = np.sum((diff ** 2) * weights, axis=2)
        closest_idx = np.argmin(distances, axis=1)

        preview_arr[y] = dye_colors[closest_idx].astype(np.uint8)
        number_grid.append([dye_ids[i] for i in closest_idx])

    return Image.fromarray(preview_arr), number_grid


def overlay_grid(base_preview, scale=10, grid_color=(120, 120, 120)):
    """
    Scales an image and draws a 1x1 pixel grid over it.
    Returns: A scaled PIL.Image with a grid overlay.
    """
    width, height = base_preview.size
    gridded = base_preview.resize((width * scale, height * scale), Image.NEAREST)
    draw = ImageDraw.Draw(gridded)

    for y in range(height):
        for x in range(width):
            px, py = x * scale, y * scale
            draw.rectangle([px, py, px + scale, py + scale], outline=grid_color)

    return gridded


def generate_blueprint_chunk(base_preview, number_grid, col_idx, row_idx, chunk_size=32, scale=30, grid=True, numbers=True):
    """
    Crops a specific map chunk, overlays the grid, and draws the color IDs.
    Returns: A scaled PIL.Image of just that chunk with numbers.
    """
    x0 = col_idx * chunk_size
    y0 = row_idx * chunk_size
    x1 = x0 + chunk_size
    y1 = y0 + chunk_size

    chunk_img = base_preview.crop((x0, y0, x1, y1))
    blueprint = chunk_img.resize((chunk_size * scale, chunk_size * scale), Image.NEAREST)
    draw = ImageDraw.Draw(blueprint)

    for cy in range(chunk_size):
        for cx in range(chunk_size):
            orig_x = x0 + cx
            orig_y = y0 + cy
            dye_id = number_grid[orig_y][orig_x]

            bx, by = cx * scale, cy * scale

            # Grid lines
            if grid:
                draw.rectangle([bx, by, bx + scale, by + scale], outline=(200, 200, 200, 100))

            if dye_id == 0:
                continue

            if numbers:
                # Smart text color contrast
                bg_color = current_app.color_map[dye_id].rgb
                luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2])
                text_color = (255, 255, 255) if luminance < 128 else (0, 0, 0)

                text_offset_x = bx + (scale // 4)
                text_offset_y = by + (scale // 6)
                draw.text((text_offset_x, text_offset_y), str(dye_id), fill=text_color)

    return blueprint