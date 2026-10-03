import numpy as np
from PIL import Image, ImageDraw
from flask import current_app

def convert_image_to_mc_colors(pil_image, target_cols, target_rows, chunk_size=32, use_dithering=False):
    target_width = target_cols * chunk_size
    target_height = target_rows * chunk_size

    img_rgba = pil_image.convert("RGBA")

    img_resized = img_rgba.resize((target_width, target_height), Image.Resampling.BILINEAR)
    alpha_channel = np.array(img_resized.split()[3])

    bg = Image.new("RGBA", img_resized.size, (0, 0, 0, 255))
    img_rgb = Image.alpha_composite(bg, img_resized).convert("RGB")

    dye_ids = list(current_app.color_map.keys())
    palette_colors = []

    for i in dye_ids:
        rgb = current_app.color_map[i].rgb
        palette_colors.extend([int(rgb[0]), int(rgb[1]), int(rgb[2])])

    padding_count = 256 - len(current_app.color_map)
    if padding_count > 0:
        last_rgb = palette_colors[-3:]
        palette_colors.extend(last_rgb * padding_count)
        dye_ids.extend([dye_ids[-1]] * padding_count)

    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette(palette_colors)

    dither_mode = Image.Dither.FLOYDSTEINBERG if use_dithering else Image.Dither.NONE
    img_quantized = img_rgb.quantize(palette=pal_img, dither=dither_mode)

    preview_arr = np.zeros((target_height, target_width, 4), dtype=np.uint8)
    number_grid = []
    idx_arr = np.array(img_quantized)

    for y in range(target_height):
        row_ids = []
        for x in range(target_width):
            if alpha_channel[y, x] < 128:
                preview_arr[y, x] = [0, 0, 0, 0]
                row_ids.append(0)
            else:
                pal_idx = idx_arr[y, x]
                dye_id = dye_ids[pal_idx]

                mc_color = current_app.color_map[dye_id].rgb
                preview_arr[y, x] = [int(mc_color[0]), int(mc_color[1]), int(mc_color[2]), 255]
                row_ids.append(dye_id)

        number_grid.append(row_ids)

    return Image.fromarray(preview_arr, "RGBA"), number_grid


def upscale_and_overlay_grid(base_preview, scale=10, grid_color=(120, 120, 120), grid=True):
    """
    Scales an image and draws a 1x1 pixel grid over it.
    Returns: A scaled PIL.Image with a grid overlay.
    """
    width, height = base_preview.size
    gridded = base_preview.resize((width * scale, height * scale), Image.NEAREST)

    if grid:
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