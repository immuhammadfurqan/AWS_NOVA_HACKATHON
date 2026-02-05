import { motion } from 'framer-motion';

export default function DashboardLoading() {
    return (
        <div className="space-y-8 animate-pulse">
            {/* Header skeleton */}
            <div className="space-y-2">
                <div className="h-8 w-48 bg-muted rounded-lg" />
                <div className="h-4 w-72 bg-muted/50 rounded" />
            </div>

            {/* Stats grid skeleton */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="glass-card p-6 space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="space-y-2">
                                <div className="h-4 w-24 bg-muted rounded" />
                                <div className="h-8 w-16 bg-muted/70 rounded" />
                            </div>
                            <div className="h-12 w-12 bg-muted rounded-xl" />
                        </div>
                        <div className="h-3 w-32 bg-muted/30 rounded" />
                    </div>
                ))}
            </div>

            {/* Content grid skeleton */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <div className="glass-card p-6 col-span-4">
                    <div className="h-5 w-32 bg-muted rounded mb-4" />
                    <div className="h-[200px] bg-muted/30 rounded-lg" />
                </div>
                <div className="glass-card p-6 col-span-3">
                    <div className="h-5 w-40 bg-muted rounded mb-4" />
                    <div className="space-y-3">
                        {[1, 2, 3].map((j) => (
                            <div key={j} className="flex items-center gap-4 p-3 rounded-lg bg-muted/30">
                                <div className="h-10 w-10 rounded-full bg-muted" />
                                <div className="space-y-2 flex-1">
                                    <div className="h-4 w-28 bg-muted rounded" />
                                    <div className="h-3 w-36 bg-muted/50 rounded" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
