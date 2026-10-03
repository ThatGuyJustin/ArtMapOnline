import axios from "axios";

export default async function postUnconvertedImage(file: File, rows: number, columns: number, dither: boolean) {
    const fd = new FormData();
    fd.append("file", file);
    // @ts-ignore
    fd.append("target_rows", rows)
    // @ts-ignore
    fd.append("target_columns", columns)
    // @ts-ignore
    fd.append("use_dither", dither)
    return await axios.post(
        "/api/artwork/convert",
        fd
    );
}

export async function getArtworkData(artId: string) {
    const response = await axios.get(
        `/api/artwork/${artId}`,
    )

    return response.data
}