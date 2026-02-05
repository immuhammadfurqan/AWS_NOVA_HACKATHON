"use client";

import * as React from "react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
    const { setTheme, theme, systemTheme } = useTheme();
    const [mounted, setMounted] = React.useState(false);

    React.useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return (
            <button
                className="size-9 rounded-full flex items-center justify-center bg-white/10 border border-white/10 text-white/50 backdrop-blur-sm transition-all"
                aria-label="Toggle Theme"
            >
                <span className="material-symbols-outlined text-[20px]">light_mode</span>
            </button>
        );
    }

    const currentTheme = theme === "system" ? systemTheme : theme;
    const isDark = currentTheme === "dark";

    return (
        <button
            onClick={() => setTheme(isDark ? "light" : "dark")}
            className="size-9 rounded-full flex items-center justify-center transition-all bg-[var(--landing-glass-bg)] border border-[var(--landing-glass-border)] text-[var(--landing-text)] hover:bg-[var(--landing-text)] hover:text-[var(--landing-bg)] shadow-sm"
            aria-label="Toggle Theme"
        >
            <span className="material-symbols-outlined text-[20px]">
                {isDark ? "light_mode" : "dark_mode"}
            </span>
        </button>
    );
}
