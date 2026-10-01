import type { Route } from "./+types/home";
import {Box, Button, CircularProgress, Typography} from "@mui/material";
import FileUploadIcon from '@mui/icons-material/FileUpload';
import postUnconvertedImage from "~/util/requests";
import {useRef, useState} from "react";
import {PrettoSlider} from "~/components/fancyslider";
import {useNavigate} from "react-router";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "ArtMap Online" },
    { name: "description", content: "Convert your image to an ArtMap ready image!" },
  ];
}

export default function Home() {
    const [uploading, setUploading] = useState(false);

    const [rows, setRows] = useState(1);
    const [columns, setColumns] = useState(1);

    const fileInputRef = useRef(null);
    const navigate = useNavigate();

    const handleButtonClick = () => {
        if (!uploading && fileInputRef.current) {
            // @ts-ignore
            fileInputRef.current.click();
        }
    };

    // @ts-ignore
    const handleFileChange = async (event) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        setUploading(true);

        try {
            const file = files[0];

            const r = await postUnconvertedImage(file, rows, columns);
            navigate(`/artwork/${r.data.data.file_hash}`)
        } catch (error) {
            console.error("Upload failed:", error);
        } finally {
            setUploading(false);

        }
    };

    return (
      <main className="flex items-center justify-center pt-16 pb-4">
          <div className="flex-1 flex flex-col items-center gap-16 min-h-0">
              <header className="flex flex-col items-center gap-9">
                  <img
                      src={"assets/img/map_texture.webp"}
                      alt={"Minecraft Map Texture"}
                      style={{ width: "400px", height: "auto" }}
                  />
              </header>
              <div className="flex flex-col items-center gap-9">
                  <h1 className="font-monocraft"
                      style={{"fontSize": 50}}>
                      ArtMap Online
                  </h1>
              </div>

              <Box sx={{ width: 320 }}>
                  <Typography gutterBottom style={{fontFamily: "Monocraft"}}>Rows</Typography>
                  <PrettoSlider
                      valueLabelDisplay="auto"
                      aria-label="Rows"
                      defaultValue={1}
                      min={1}
                      max={20}
                      // @ts-ignore
                      onChange={(event) => setRows(Number(event.target!.value))}
                  />
                  <Typography gutterBottom style={{fontFamily: "Monocraft"}}>Columns</Typography>
                  <PrettoSlider
                      valueLabelDisplay="auto"
                      aria-label="Columns"
                      defaultValue={1}
                      min={1}
                      max={20}
                      // @ts-ignore
                      onChange={(event) => setColumns(Number(event.target!.value))}
                  />
              </Box>

              <Button disabled={uploading} component="label" variant="outlined" size="large" startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <FileUploadIcon />}
                      sx={{
                          "&.Mui-disabled": {
                              color: "rgba(255, 255, 255, 0.6)",
                              borderColor: "rgba(255, 255, 255, 0.3)",
                          }
                      }} onClick={handleButtonClick}>
                  {uploading ? "Uploading..." : "Click to upload Image"}
              </Button>
              <input
                  type="file"
                  style={{ display: 'none' }}
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/*"
              />
          </div>
      </main>
  )
}