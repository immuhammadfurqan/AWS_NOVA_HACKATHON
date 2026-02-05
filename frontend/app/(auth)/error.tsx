'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

interface ErrorProps {
    error: Error & { digest?: string };
    reset: () => void;
}

export default function AuthError({ error, reset }: ErrorProps) {
    useEffect(() => {
        console.error('Auth Error:', error);
    }, [error]);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-8 max-w-md w-full text-center space-y-6"
        >
            <div className="mx-auto w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="h-8 w-8 text-red-400" />
            </div>

            <div className="space-y-2">
                <h2 className="text-2xl font-bold text-white">
                    Authentication Error
                </h2>
                <p className="text-slate-400">
                    Something went wrong during authentication. Please try again.
                </p>
            </div>

            {error.message && process.env.NODE_ENV === 'development' && (
                <div className="p-3 rounded-lg bg-slate-800/50 text-left">
                    <p className="text-xs font-mono text-slate-400 break-all">
                        {error.message}
                    </p>
                </div>
            )}

            <div className="flex flex-col gap-3">
                <Button onClick={reset} variant="outline">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Try Again
                </Button>
                <Link href="/" className="text-sm text-blue-400 hover:text-blue-300">
                    <ArrowLeft className="inline mr-1 h-3 w-3" />
                    Back to Home
                </Link>
            </div>
        </motion.div>
    );
}
