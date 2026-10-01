import React, {useEffect, useMemo, useState} from 'react';

const ENCHANTMENT_CHARS = [
    'ᔑ', 'ʖ', 'ᓵ', '↸', 'ᒷ', '⎓', '⊣', '⍑', '╎', '⨅', 'ꖌ', 'ꖎ',
    'ᒲ', 'リ', '𝙹', '¡', 'ᑑ', '∷', 'ᓭ', 'ℸ', '⚍', '⍊', '∴', '||'
];

const DEFAULT_COLORS = ['#6FFEDF', '#6ECDFF', '#FF00BE', '#c929ff'];

// @ts-ignore
const FirefliesBackground = ({
        count = 40, colors = DEFAULT_COLORS,
     }) => {
    const [fireflies, setFireflies] = useState([]);

    useEffect(() => {
        // This now safely runs exactly ONE time after the browser hydrates
        const generated = Array.from({ length: count }).map((_, i) => {
            const size = Math.random() * 15 + 15;
            return {
                id: i,
                left: `${Math.random() * 100}vw`,
                top: `${Math.random() * 100}vh`,
                animationDuration: `${Math.random() * 6 + 5}s`,
                animationDelay: `${Math.random() * 10}s`,
                size: `${size}px`,
                fontSize: `${size * 0.55}px`,
                color: colors[Math.floor(Math.random() * colors.length)],
                char: ENCHANTMENT_CHARS[Math.floor(Math.random() * ENCHANTMENT_CHARS.length)],
                moveX: `${(Math.random() - 0.5) * 100}px`,
                moveY: `${(Math.random() - 0.5) * 100}px`,
                blurRadius: `${size * 1.5}px`,
                spreadRadius: `${size * 0.5}px`
            };
        });

        // @ts-ignore
        setFireflies(generated);

    }, []); // <-- Empty dependency array is the magic fix here!

    return (
        // @ts-ignore
        <div style={styles.container}>
            <style>
                {`
          @keyframes firefly-pulse {
            0% { opacity: 0; transform: scale(0.5) translate(0, 0) rotate(-10deg); }
            50% { opacity: 1; transform: scale(1.2) translate(var(--moveX), var(--moveY)) rotate(10deg); }
            100% { opacity: 0; transform: scale(0.5) translate(0, 0) rotate(-10deg); }
          }
          
          .firefly-blob {
            position: absolute;
            border-radius: 50%;
            opacity: 0; 
            animation: firefly-pulse ease-in-out infinite;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Monocraft', monospace; 
            user-select: none; 
          }
        `}
            </style>

            {fireflies.map((ff) => (
                <div
                    // @ts-ignore
                    key={ff.id}
                    className="firefly-blob"
                    style={{
                        // @ts-ignore
                        left: ff.left,
                        // @ts-ignore
                        top: ff.top,
                        // @ts-ignore
                        width: ff.size,
                        // @ts-ignore
                        height: ff.size,
                        // @ts-ignore
                        backgroundColor: ff.color,
                        // @ts-ignore
                        boxShadow: `0 0 ${ff.blurRadius} ${ff.spreadRadius} ${ff.color}`,
                        // @ts-ignore
                        animationDuration: ff.animationDuration,
                        // @ts-ignore
                        animationDelay: ff.animationDelay,
                        // @ts-ignore
                        '--moveX': ff.moveX,
                        // @ts-ignore
                        '--moveY': ff.moveY,
                        // @ts-ignore
                        fontSize: ff.fontSize,
                        color: 'rgba(0, 0, 0, 0.65)',
                    }}
                >
                    {/* @ts-ignore */}
                    {ff.char}
                </div>
            ))}
        </div>
    );
};

const styles = {
    container: {
        position: 'fixed',
        top: 0, left: 0, width: '100vw', height: '100vh',
        backgroundColor: '#0a0a0a',
        overflow: 'hidden', zIndex: -1, pointerEvents: 'none',
    }
};

export default FirefliesBackground;