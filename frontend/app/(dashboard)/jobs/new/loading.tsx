export default function CreateJobLoading() {
    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-pulse">
            {/* Header skeleton */}
            <div className="space-y-2">
                <div className="h-8 w-48 bg-muted rounded-lg" />
                <div className="h-4 w-72 bg-muted/50 rounded" />
            </div>

            {/* Form skeleton */}
            <div className="glass-card p-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <div className="h-4 w-20 bg-muted rounded" />
                        <div className="h-11 w-full bg-muted/30 rounded-lg" />
                    </div>
                    <div className="space-y-2">
                        <div className="h-4 w-24 bg-muted rounded" />
                        <div className="h-11 w-full bg-muted/30 rounded-lg" />
                    </div>
                </div>

                <div className="space-y-2">
                    <div className="h-4 w-28 bg-muted rounded" />
                    <div className="h-11 w-full bg-muted/30 rounded-lg" />
                </div>

                <div className="space-y-2">
                    <div className="h-4 w-44 bg-muted rounded" />
                    <div className="h-36 w-full bg-muted/30 rounded-lg" />
                    <div className="h-3 w-48 bg-muted/20 rounded" />
                </div>

                <div className="pt-4 flex justify-end">
                    <div className="h-11 w-56 bg-muted rounded-lg" />
                </div>
            </div>
        </div>
    );
}
