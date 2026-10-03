import json
import mimetypes
from io import BytesIO

from flask import Blueprint, send_file, current_app, request

from util.images import generate_blueprint_chunk, upscale_and_overlay_grid

media = Blueprint("media", __name__)

@media.get("/converted/<media_hash>")
def get_converted_image(media_hash):

    if media_hash not in current_app.CACHE:
        return "Media hash not found", 400

    cached_media = current_app.CACHE[media_hash]

    converted_image = BytesIO()

    if "grid" in request.args:
        cached_media["overlay_image"].save(converted_image, format="PNG")
    else:
        upscale_and_overlay_grid(cached_media["image_preview"], 10, grid=False).save(converted_image, format="PNG")

    converted_image.seek(0)

    return send_file(converted_image, download_name=media_hash + ".png", as_attachment=False, mimetype=mimetypes.guess_type(media_hash + ".png")[0])

@media.get("/chunk/<media_hash>/<row>/<col>")
def get_chunk(media_hash, row, col):
    if media_hash not in current_app.CACHE:
        return "Media hash not found", 400

    cached_media = current_app.CACHE[media_hash]

    chunk_image = BytesIO()

    grid = request.args.get("grid", type=json.loads)
    numbers = request.args.get("numbers", type=json.loads)

    grid_image = generate_blueprint_chunk(cached_media["image_preview"], cached_media["num_grid"], int(col), int(row), grid=grid, numbers=numbers)
    grid_image.save(chunk_image, format="PNG")

    chunk_image.seek(0)

    return send_file(chunk_image, download_name=media_hash + f"_{row}_{col}.png", as_attachment=False,
                     mimetype=mimetypes.guess_type(media_hash + f"_{row}_{col}.png")[0])
