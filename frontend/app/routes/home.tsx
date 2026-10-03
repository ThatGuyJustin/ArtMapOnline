import type { Route } from "./+types/home";
import {Box, Button, CircularProgress, Switch, Typography} from "@mui/material";
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
    const [isDragging, setIsDragging] = useState(false);

    const dragCounter = useRef(0);

    const [useDither, setDithering] = useState(false);
    const [rows, setRows] = useState(1);
    const [columns, setColumns] = useState(1);

    const fileInputRef = useRef(null);
    const navigate = useNavigate();

    const handleFiles = async (files: FileList | null) => {
        if (!files || files.length === 0) return;

        setUploading(true);

        try {
            const file = files[0];
            const r = await postUnconvertedImage(file, rows, columns, useDither);
            navigate(`/artwork/${r.data.data.file_hash}`);
        } catch (error) {
            console.error("Upload failed:", error);
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                // @ts-ignore
                fileInputRef.current.value = null;
            }
        }
    };

    const handleButtonClick = () => {
        if (!uploading && fileInputRef.current) {
            // @ts-ignore
            fileInputRef.current.click();
        }
    };

    // @ts-ignore
    const handleFileChange = (event) => {
        handleFiles(event.target.files);
    };

    const onDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current += 1;
        if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            setIsDragging(true);
        }
    };

    const onDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounter.current -= 1;
        if (dragCounter.current === 0) {
            setIsDragging(false);
        }
    };

    const onDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const onDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        dragCounter.current = 0;

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFiles(e.dataTransfer.files);
        }
    };

    return (
        <main
            className="flex items-center justify-center min-h-screen p-4 overflow-hidden"
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            onDrop={onDrop}
        >
            <div className={`
              flex flex-col items-center justify-center w-full max-w-4xl p-8 rounded-2xl transition-colors duration-200
              ${isDragging ? 'bg-white/10 border-2 border-dashed border-white/50' : 'border-2 border-transparent'}
          `}>
                <div className={`flex flex-col items-center justify-center gap-8 w-full ${isDragging ? 'pointer-events-none' : ''}`}>
                    <header className="flex flex-col items-center gap-4 w-full">
                        <img
                            src={"assets/img/map_texture.webp"}
                            alt={"Minecraft Map Texture"}
                            style={{ width: "400px", height: "auto" }}
                        />
                    </header>

                    <div className="flex flex-col items-center gap-2">
                        <h1 className="font-monocraft text-white" style={{ fontSize: 50 }}>
                            ArtMap Online
                        </h1>
                        <p className={`font-monocraft transition-opacity ${isDragging ? 'opacity-100 text-green-400' : 'opacity-0'}`}>
                            Drop image to upload!
                        </p>
                    </div>

                    <Box sx={{ width: 320, color: 'white' }}>
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
                        <Typography gutterBottom style={{fontFamily: "Monocraft", marginTop: 16}}>Columns</Typography>
                        <PrettoSlider
                            valueLabelDisplay="auto"
                            aria-label="Columns"
                            defaultValue={1}
                            min={1}
                            max={20}
                            // @ts-ignore
                            onChange={(event) => setColumns(Number(event.target!.value))}
                        />

                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 3 }}>
                            <Typography style={{fontFamily: "Monocraft"}}>Use Dithering</Typography>
                            <Switch checked={useDither} onChange={(e) => setDithering(e.target.checked)} />
                        </Box>
                    </Box>

                    <Button
                        disabled={uploading}
                        component="button"
                        variant="outlined"
                        size="large"
                        onClick={handleButtonClick}
                        startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <FileUploadIcon />}
                        sx={{
                            "&.Mui-disabled": {
                                color: "rgba(255, 255, 255, 0.6)",
                                borderColor: "rgba(255, 255, 255, 0.3)",
                            }
                        }}
                    >
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
            </div>
        </main>
    );
}