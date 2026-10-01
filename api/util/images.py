import numpy as np
from PIL import Image, ImageDraw
from flask import current_app


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

            if numbers:
                # Smart text color contrast
                bg_color = current_app.color_map[dye_id].rgb
                luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2])
                text_color = (255, 255, 255) if luminance < 128 else (0, 0, 0)

                text_offset_x = bx + (scale // 4)
                text_offset_y = by + (scale // 6)
                draw.text((text_offset_x, text_offset_y), str(dye_id), fill=text_color)

    return blueprint