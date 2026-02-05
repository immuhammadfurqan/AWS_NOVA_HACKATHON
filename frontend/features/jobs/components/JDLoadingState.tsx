'use client';

import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

/**
 * Loading state shown while AI generates the Job Description.
 * Displays animated sparkles and pulsing dots.
 */
export default function JDLoadingState() {
    return (
        <div className="flex flex-col items-center justify-center h-96 space-y-6">
            <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 to-purple-500/30 blur-3xl rounded-full animate-pulse" />
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    className="relative z-10"
                >
                    <Sparkles className="h-20 w-20 text-blue-400" />
                </motion.div>
            </div>
            <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold text-white">AI Agent is Crafting Your JD</h2>
                <p className="text-slate-400 max-w-md">
                    Analyzing industry standards, SEO keywords, and best practices...
                </p>
            </div>
            <div className="flex gap-2">
                {[0, 1, 2].map((i) => (
                    <motion.div
                        key={i}
                        className="w-3 h-3 rounded-full bg-blue-500"
                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                    />
                ))}
            </div>
        </div>
    );
}
