import json
import mimetypes
from io import BytesIO

from PIL import Image
from flask import Blueprint, send_file, current_app, request
from redis_om import NotFoundError

from models.Artmap import ArtMap
from util.images import generate_blueprint_chunk, upscale_and_overlay_grid

media = Blueprint("media", __name__)

@media.get("/converted/<artmap>")
def get_converted_image(artmap):
    try:
        db_art = ArtMap.get(artmap)
    except NotFoundError:
        return "Art not found", 404

    if current_app.redis_client.exists(f"preview_image_scaled:{db_art.original_image}"):
        return send_file(BytesIO(current_app.redis_client.get(f"preview_image_scaled:{db_art.original_image}")), download_name=f"{db_art.original_image}_converted.png", as_attachment=False, mimetype=mimetypes.guess_type(f"{db_art.original_image}_converted.png")[0]), 200

    og_preview_image = Image.open(BytesIO(current_app.redis_client.get(f"preview_image:{db_art.original_image}")))
    upscale_preview = BytesIO()
    upscale_and_overlay_grid(og_preview_image, 10, grid=False).save(upscale_preview, format="PNG")

    upscale_preview.seek(0)

    current_app.redis_client.setex(f"preview_image_scaled:{db_art.original_image}", current_app.cache_time, upscale_preview.getvalue())
    upscale_preview.seek(0)

    return send_file(upscale_preview, download_name=f"{db_art.original_image}_converted.png", as_attachment=False, mimetype=mimetypes.guess_type(f"{db_art.original_image}_converted.png")[0]), 200

@media.get("/chunk/<artmap>/<row>/<col>")
def get_chunk(artmap, row, col):
    try:
        db_art = ArtMap.get(artmap)
    except NotFoundError:
        return "Art not found", 404

    grid = request.args.get("grid", type=json.loads)
    numbers = request.args.get("numbers", type=json.loads)

    check_key = f"chunk_image{'_grid' if grid else ''}{'_numbers' if numbers else ''}:{db_art.pk}:{row}_{col}"

    if current_app.redis_client.exists(check_key):
        return send_file(BytesIO(current_app.redis_client.get(check_key)),
                         download_name=f"{db_art.pk}_{row}_{col}.png", as_attachment=False,
                         mimetype=mimetypes.guess_type(f"{db_art.pk}_{row}_{col}.png")[0]), 200

    chunk_image = BytesIO()

    retrieved_bytes = current_app.redis_client.get(f"preview_image:{db_art.original_image}")
    og_preview_image = Image.open(BytesIO(retrieved_bytes))

    grid_image = generate_blueprint_chunk(og_preview_image, db_art.num_grid, int(col), int(row), grid=grid, numbers=numbers)
    grid_image.save(chunk_image, format="PNG")

    chunk_image.seek(0)

    current_app.redis_client.setex(check_key, current_app.cache_time,
                                   chunk_image.getvalue())
    chunk_image.seek(0)

    return send_file(chunk_image, download_name=f"{db_art.pk}_{row}_{col}.png", as_attachment=False,
                     mimetype=mimetypes.guess_type(f"{db_art.pk}_{row}_{col}.png")[0])
