import datetime
import json
from io import BytesIO

from PIL import Image
from flask import Blueprint, request, current_app
from redis_om import NotFoundError

from models.Artmap import ArtMap
from util.colors import get_global_color_tally, get_chunk_color_tally
from util.files import allowed_file, generate_filename
from util.images import convert_image_to_mc_colors, upscale_and_overlay_grid

artwork = Blueprint('artwork', __name__)

@artwork.get("/<artwork_id>")
def get_artwork(artwork_id):
    if not artwork_id:
        return { "code": 400, "message": "Missing artwork id." }, 400

    try:
        db_art = ArtMap.get(artwork_id)
    except NotFoundError:
        return { "code": 400, "message": "Artwork not found." }, 400

    return {
        "code": 200,
        "message": "Artwork found",
        "data": db_art.model_dump(mode="json", exclude={'uploaded_by', 'num_grid'})
    }, 200

@artwork.get("/<artwork_id>/counts/<row>/<col>")
def get_artwork_counts(artwork_id, row, col):
    if not artwork_id:
        return { "code": 400, "message": "Missing artwork id." }, 400

    try:
        db_art = ArtMap.get(artwork_id)
    except NotFoundError:
        return {"code": 400, "message": "Artwork not found."}, 400

    chunk_count = get_chunk_color_tally(db_art.num_grid, int(row), int(col))

    return {
        "code": 200,
        "message": f"Color info for chunk {row}x{col}",
        "data": {
            "color_counts": chunk_count
        }
    }, 200

@artwork.post("convert")
def convert():

    if not request.files:
        return { "code": 400, "message": "Missing file to convert." }, 400

    file = request.files.get("file")

    if not file or file.filename == "":
        return { "code": 400, "message": "Missing file to convert." }, 400

    if not allowed_file(file.filename):
        return { "code": 400, "message": "Invalid file to convert."}, 400

    file_hash, file_ext = generate_filename(file)

    cols = int(request.form.get('target_columns', 1))
    rows = int(request.form.get('target_rows', 1))

    use_dither = request.form.get('use_dither', None) and request.form.get('use_dither') == 'true'

    # TODO: Replace with grabbing from redis, and updating to match the size and settings
    # if file_hash in current_app.CACHE:
    #     if current_app.CACHE[file_hash]['rows'] == rows and current_app.CACHE[file_hash]['cols'] == cols and current_app.CACHE[file_hash]['dither'] == use_dither:
    #         return {"code": 200, "message": "File already converted", "data": {"file_hash": file_hash}}, 200

    img = Image.open(file)
    original_image_bytes = BytesIO()
    img.save(original_image_bytes, format='PNG')
    raw_original_image = original_image_bytes.getvalue()
    current_app.redis_client.setex(f"original_image:{file_hash}", current_app.expire_time, raw_original_image)

    converted_image, num_grid = convert_image_to_mc_colors(img, cols, rows, use_dithering=use_dither)
    color_counts = get_global_color_tally(num_grid)

    preview_image_bytes = BytesIO()
    converted_image.save(preview_image_bytes, format='PNG')
    raw_preview_image = preview_image_bytes.getvalue()
    current_app.redis_client.setex(f"preview_image:{file_hash}", current_app.expire_time, raw_preview_image)

    artmap = ArtMap(original_image=file_hash,
                    rows=rows,
                    cols=cols,
                    use_dither=use_dither,
                    created_at=datetime.datetime.now(),
                    uploaded_by=request.remote_addr,
                    num_grid=num_grid,
                    color_counts=color_counts)

    artmap.save()
    artmap.expire(current_app.expire_time)

    return {"code": 200, "message": "File is now converting", "data": {"art_id": artmap.pk}}, 200