'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

interface ErrorProps {
    error: Error & { digest?: string };
    reset: () => void;
}

export default function DashboardError({ error, reset }: ErrorProps) {
    useEffect(() => {
        // Log to error reporting service
        console.error('Dashboard Error:', error);
    }, [error]);

    return (
        <div className="min-h-[60vh] flex items-center justify-center p-6">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card p-8 max-w-md w-full text-center space-y-6"
            >
                <div className="mx-auto w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center">
                    <AlertTriangle className="h-8 w-8 text-destructive" />
                </div>

                <div className="space-y-2">
                    <h2 className="text-2xl font-bold text-foreground">
                        Something went wrong
                    </h2>
                    <p className="text-muted-foreground">
                        We encountered an unexpected error. Please try again or return to the dashboard.
                    </p>
                </div>

                {error.message && process.env.NODE_ENV === 'development' && (
                    <div className="p-3 rounded-lg bg-muted/50 text-left">
                        <p className="text-xs font-mono text-muted-foreground break-all">
                            {error.message}
                        </p>
                    </div>
                )}

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <Button onClick={reset} variant="outline">
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Try Again
                    </Button>
                    <Link href="/dashboard">
                        <Button>
                            <Home className="mr-2 h-4 w-4" />
                            Go to Dashboard
                        </Button>
                    </Link>
                </div>
            </motion.div>
        </div>
    );
}
