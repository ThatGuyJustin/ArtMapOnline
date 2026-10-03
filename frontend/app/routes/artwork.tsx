import { useState, useEffect } from "react";
import type { Route } from "./+types/artwork";
import { Avatar, Box, Paper, Stack, Typography, Tooltip, Switch, FormControlLabel, Button } from "@mui/material";
import { getArtworkData } from "~/util/requests";
import axios from "axios";

export function meta({}: Route.MetaArgs) {
    return [
        { title: "Viewing Artwork" },
        { name: "description", content: "Viewing converted artwork!" },
    ];
}

export async function clientLoader({ params }: Route.LoaderArgs){
    let colors = await axios.get("/api/colors");
    let artInfo = await getArtworkData(params.artId);
    return {colors: colors.data, artInfo: artInfo.data};
}

export default function Artwork({ loaderData }: Route.ComponentProps) {
    const [selectedChunk, setSelectedChunk] = useState(null);
    const [toggleGrid, setToggleGrid] = useState(true);
    const [toggleNumbers, setToggleNumbers] = useState(false);
    const [hideUnusedColors, setHideUnusedColors] = useState(false);

    const [viewingChunk, setViewingChunk] = useState(null);
    const [colorCounts, setColorCounts] = useState({});

    useEffect(() => {
        const fetchCounts = async () => {
            try {
                if (viewingChunk !== null) {
                    const res = await axios.get(`/api/artwork/${loaderData.artInfo.artwork_id}/counts/${viewingChunk.row}/${viewingChunk.col}`);
                    setColorCounts(res.data.data.color_counts);
                } else {
                    setColorCounts(loaderData.artInfo.color_counts);
                }
            } catch (error) {
                console.error("Failed to fetch color counts:", error);
                setColorCounts({});
            }
        };

        fetchCounts();
    }, [viewingChunk, loaderData.artInfo.artwork_id]);

    return (
        <Box
            component="main"
            sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
                py: 2
            }}
        >
            <Paper
                variant="outlined"
                sx={{
                    display: 'flex',
                    width: '95vw',
                    height: '95vh',
                    p: 3,
                    gap: 3,
                    backgroundColor: 'rgba(10, 10, 10, 0.8)',
                    backdropFilter: 'blur(4px)',
                    borderColor: 'rgba(255, 255, 255, 0.12)', // Replaced MUI 'divider'
                }}
            >
                {/* Left Section: Stacked Color List */}
                <Stack
                    spacing={2}
                    sx={{
                        width: 320,
                        p: 2,
                        border: '1px solid rgba(255, 255, 255, 0.12)',
                        borderRadius: 1,
                        height: '100%',
                    }}
                >
                    <Typography
                        variant="h6"
                        sx={{
                            fontFamily: 'Monocraft, monospace',
                            color: 'white',
                            borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
                            pb: 1
                        }}
                    >
                        {viewingChunk !== null ? `Chunk (${viewingChunk.col}, ${viewingChunk.row}) Colors` : 'Total Colors'}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <FormControlLabel
                            control={<Switch checked={hideUnusedColors} onChange={(e) => setHideUnusedColors(e.target.checked)} size="small" />}
                            label={<Typography sx={{ fontFamily: 'Monocraft, monospace', fontSize: '0.75rem', color: 'white' }}>Hide Unused Colors</Typography>}
                            sx={{ m: 0 }}
                        />
                    </Box>

                    <Stack
                        spacing={1.5}
                        sx={{
                            overflowY: 'auto',
                            flex: 1,
                            pr: 1,
                        }}
                    >
                        {Object.entries(loaderData.colors).map(([id, color]) => {
                            const qty = colorCounts[id] || 0;
                            if(hideUnusedColors && qty == 0) return;
                            const isActive = qty > 0;

                            return (
                                <Paper
                                    key={color.id || id}
                                    variant="outlined"
                                    sx={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        p: 1.5,
                                        border: isActive ? `1px solid ${color.hex}` : '1px solid transparent',
                                        backgroundColor: isActive ? `${color.hex}15` : 'transparent',
                                        transition: 'all 0.2s',
                                        '&:hover': { borderColor: isActive ? color.hex : 'rgba(255, 255, 255, 0.3)' }
                                    }}
                                >
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                        <Box
                                            sx={{
                                                width: 32,
                                                height: 32,
                                                borderRadius: 1,
                                                backgroundColor: color.hex,
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                border: '1px solid rgba(255,255,255,0.2)',
                                                boxShadow: 'inset 0 0 4px rgba(0,0,0,0.3)',
                                                flexShrink: 0,
                                                opacity: isActive ? 1 : 0.5
                                            }}
                                        >
                                            <Typography
                                                sx={{
                                                    fontFamily: 'Monocraft, monospace',
                                                    fontSize: '0.75rem',
                                                    color: 'white',
                                                    textShadow: '1px 1px 1px black, -1px -1px 1px black, 1px -1px 1px black, -1px 1px 1px black'
                                                }}
                                            >
                                                {id}
                                            </Typography>
                                        </Box>

                                        <Box sx={{ opacity: isActive ? 1 : 0.5 }}>
                                            <Typography sx={{ fontFamily: 'Monocraft, monospace', fontSize: '0.875rem' , color:'white'}}>
                                                {color.name}
                                            </Typography>

                                            {/* Fixed the dark text bug by setting an explicit light gray fallback */}
                                            <Typography variant="caption" sx={{ color: isActive ? 'white' : 'rgba(255, 255, 255, 0.5)', fontFamily: 'Monocraft, monospace'}}>
                                                Qty: {qty}
                                            </Typography>
                                        </Box>
                                    </Box>

                                    <Tooltip title={color.material || "Material"} placement="top" arrow>
                                        <Avatar
                                            src={color.asset_url}
                                            alt={color.material}
                                            variant="rounded"
                                            sx={{
                                                width: 32,
                                                height: 32,
                                                bgcolor: 'rgba(0,0,0,0.4)',
                                                border: '1px solid',
                                                borderColor: isActive ? color.hex : 'rgba(255, 255, 255, 0.12)',
                                                cursor: 'help',
                                                opacity: isActive ? 1 : 0.5
                                            }}
                                        />
                                    </Tooltip>
                                </Paper>
                            );
                        })}
                    </Stack>
                </Stack>

                {/* Right Section: Giant Preview Box */}
                <Stack
                    sx={{
                        flex: 1,
                        p: 2,
                        border: '1px solid rgba(255, 255, 255, 0.12)',
                        borderRadius: 1,
                        position: 'relative',
                        height: '100%',
                        minWidth: 0,
                    }}
                >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                            <Typography variant="h6" sx={{ fontFamily: 'Monocraft, monospace', color: 'white'}}>
                                Map Preview
                            </Typography>

                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <FormControlLabel
                                    control={<Switch checked={toggleGrid} onChange={(e) => setToggleGrid(e.target.checked)} size="small" />}
                                    label={<Typography sx={{ fontFamily: 'Monocraft, monospace', fontSize: '0.75rem', color: 'white' }}>Grid</Typography>}
                                    sx={{ m: 0 }}
                                />
                                <FormControlLabel
                                    control={<Switch checked={toggleNumbers} onChange={(e) => setToggleNumbers(e.target.checked)} size="small" />}
                                    label={<Typography sx={{ fontFamily: 'Monocraft, monospace', fontSize: '0.75rem', color: 'white' }}>Numbers</Typography>}
                                    sx={{ m: 0 }}
                                />
                            </Box>
                        </Box>

                        <Typography variant="body2" color='white' sx={{ fontFamily: 'Monocraft, monospace'}}>
                            Map Size: {loaderData.artInfo.target_rows}x{loaderData.artInfo.target_columns}
                        </Typography>
                    </Box>

                    {/* Image & Grid Container */}
                    <Box
                        sx={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            bgcolor: 'rgba(0,0,0,0.4)',
                            borderRadius: 1,
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            p: 2,
                            position: 'relative',
                            overflow: 'hidden',
                            minHeight: 0,
                        }}
                    >
                        <Box
                            sx={{
                                position: 'relative',
                                // Forces the wrapper to scale up while maintaining ratio
                                height: '100%',
                                maxWidth: '100%',
                                aspectRatio: `${loaderData.artInfo.target_columns} / ${loaderData.artInfo.target_rows}`,
                                margin: 'auto'
                            }}
                        >
                            <Box
                                component="img"
                                src={`/api/media/converted/${loaderData.artInfo.artwork_id}`}
                                alt="Converted Map Preview"
                                sx={{
                                    width: '100%',
                                    height: '100%',
                                    // Use fill because the wrapper mathematically guarantees the correct aspect ratio
                                    objectFit: 'fill',
                                    userSelect: 'none',
                                    boxShadow: 3
                                }}
                            />

                            <Box
                                sx={{
                                    position: 'absolute',
                                    top: 0, left: 0, right: 0, bottom: 0,
                                    display: 'grid',
                                    gridTemplateColumns: `repeat(${loaderData.artInfo.target_columns}, 1fr)`,
                                    gridTemplateRows: `repeat(${loaderData.artInfo.target_rows}, 1fr)`
                                }}
                            >
                                {Array.from({ length: loaderData.artInfo.target_rows * loaderData.artInfo.target_columns }).map((_, index) => {
                                    const isSelected = selectedChunk === index;
                                    const showNumber = toggleNumbers || isSelected;

                                    return (
                                        <Box
                                            key={index}
                                            onMouseEnter={() => setSelectedChunk(index)}
                                            onMouseLeave={() => setSelectedChunk(null)}
                                            onClick={() => {
                                                const cols = loaderData.artInfo.target_columns;
                                                const row = Math.floor(index / cols);
                                                const col = index % cols;

                                                setViewingChunk({ index, row, col });
                                            }}
                                            sx={{
                                                position: 'relative',
                                                border: toggleGrid ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid transparent',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                transition: 'all 0.15s ease',
                                                '&:hover': {
                                                    borderColor: 'rgba(255, 255, 255, 0.8)',
                                                    backgroundColor: 'rgba(255, 255, 255, 0.1)'
                                                },
                                                ...(isSelected && {
                                                    backgroundColor: 'rgba(33, 150, 243, 0.2)',
                                                    border: '2px solid',
                                                    borderColor: 'primary.main',
                                                    zIndex: 10
                                                })
                                            }}
                                        >
                                            {showNumber && (
                                                <Box
                                                    sx={{
                                                        position: 'absolute',
                                                        top: '50%',
                                                        left: '50%',
                                                        transform: 'translate(-50%, -50%)',
                                                        bgcolor: isSelected ? 'rgba(33, 150, 243, 0.9)' : 'rgba(0,0,0,0.6)',
                                                        color: 'white',
                                                        px: 1,
                                                        py: 0.5,
                                                        borderRadius: 1,
                                                        fontFamily: 'Monocraft, monospace',
                                                        fontSize: '0.75rem',
                                                        pointerEvents: 'none',
                                                    }}
                                                >
                                                    {index + 1}
                                                </Box>
                                            )}
                                        </Box>
                                    );
                                })}
                            </Box>
                        </Box>

                        {viewingChunk !== null && (
                            <Box
                                sx={{
                                    position: 'absolute',
                                    top: 0, left: 0, right: 0, bottom: 0,
                                    bgcolor: 'rgba(0,0,0,0.85)',
                                    backdropFilter: 'blur(8px)',
                                    zIndex: 50,
                                    display: 'flex',
                                    flexDirection: 'column',
                                    p: 3
                                }}
                            >
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="h6" sx={{ fontFamily: 'Monocraft, monospace', color: 'white' }}>
                                        Canvas {viewingChunk.index + 1} ({viewingChunk.col}, {viewingChunk.row})
                                    </Typography>
                                    <Button
                                        variant="outlined"
                                        color="error"
                                        onClick={() => setViewingChunk(null)}
                                        sx={{ fontFamily: 'Monocraft, monospace' }}
                                    >
                                        Close
                                    </Button>
                                </Box>

                                <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 0 }}>
                                    <Box
                                        component="img"
                                        src={`/api/media/chunk/${loaderData.artInfo.artwork_id}/${viewingChunk.row}/${viewingChunk.col}?numbers=${toggleNumbers}&grid=${toggleGrid}`}
                                        alt={`Map ${viewingChunk.index + 1}`}
                                        sx={{
                                            maxWidth: '100%',
                                            maxHeight: '100%',
                                            objectFit: 'contain',
                                            boxShadow: 5,
                                            border: '1px solid rgba(255, 255, 255, 0.12)',
                                            bgcolor: 'rgba(0,0,0,0.5)'
                                        }}
                                    />
                                </Box>
                            </Box>
                        )}
                    </Box>
                </Stack>
            </Paper>
        </Box>
    )
}