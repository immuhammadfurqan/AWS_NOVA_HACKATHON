export default function JobDetailLoading() {
    return (
        <div className="space-y-8 animate-pulse">
            {/* Progress bar skeleton */}
            <div className="glass-card p-4">
                <div className="flex justify-between items-center">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-full bg-muted" />
                            <div className="h-4 w-20 bg-muted/50 rounded hidden sm:block" />
                        </div>
                    ))}
                </div>
            </div>

            {/* Header skeleton */}
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                <div className="space-y-3">
                    <div className="flex items-center gap-3">
                        <div className="h-8 w-64 bg-muted rounded-lg" />
                        <div className="h-6 w-24 bg-muted/50 rounded-full" />
                    </div>
                    <div className="flex gap-4">
                        <div className="h-8 w-28 bg-muted/30 rounded-lg" />
                        <div className="h-8 w-32 bg-muted/30 rounded-lg" />
                    </div>
                </div>
                <div className="flex gap-2">
                    <div className="h-10 w-24 bg-muted rounded-lg" />
                    <div className="h-10 w-32 bg-muted rounded-lg" />
                    <div className="h-10 w-36 bg-muted rounded-lg" />
                </div>
            </div>

            {/* Tabs skeleton */}
            <div className="h-12 w-80 bg-muted/50 rounded-xl" />

            {/* Content skeleton */}
            <div className="glass-card p-8 space-y-6">
                <div className="space-y-3">
                    <div className="h-6 w-48 bg-muted rounded" />
                    <div className="h-4 w-full bg-muted/30 rounded" />
                    <div className="h-4 w-3/4 bg-muted/30 rounded" />
                </div>
                <div className="h-px bg-muted/20" />
                <div className="space-y-3">
                    <div className="h-6 w-40 bg-muted rounded" />
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="h-12 w-full bg-muted/20 rounded-lg" />
                    ))}
                </div>
            </div>
        </div>
    );
}
