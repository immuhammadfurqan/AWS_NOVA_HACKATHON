import Link from 'next/link';
import { Briefcase, MapPin, DollarSign, Clock } from 'lucide-react';

interface PublicJobListItem {
    job_id: string;
    job_title: string;
    company_name: string;
    location: string | null;
    salary_range: string | null;
    summary: string;
    posted_at: string;
}

interface PublicJobListResponse {
    jobs: PublicJobListItem[];
    total: number;
}

async function getPublicJobs(): Promise<PublicJobListResponse> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    try {
        const res = await fetch(`${apiUrl}/careers/`, {
            next: { revalidate: 60 }, // Revalidate every 60 seconds
        });

        if (!res.ok) {
            return { jobs: [], total: 0 };
        }

        return res.json();
    } catch (error) {
        console.error('Failed to fetch public jobs:', error);
        return { jobs: [], total: 0 };
    }
}

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default async function CareersPage() {
    const { jobs, total } = await getPublicJobs();

    return (
        <div className="max-w-6xl mx-auto px-4">
            {/* Hero Section */}
            <div className="text-center mb-12">
                <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                    Join Our Team
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                    Discover exciting opportunities and take the next step in your career.
                    We&apos;re looking for talented individuals to help us build the future.
                </p>
            </div>

            {/* Job Count */}
            {total > 0 && (
                <p className="text-muted-foreground mb-6">
                    Showing {total} open position{total !== 1 ? 's' : ''}
                </p>
            )}

            {/* Empty State */}
            {jobs.length === 0 && (
                <div className="glass-card p-12 text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                        <Briefcase className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                        No Open Positions
                    </h3>
                    <p className="text-muted-foreground max-w-md mx-auto">
                        We don&apos;t have any open positions right now, but check back soon!
                        New opportunities are added regularly.
                    </p>
                </div>
            )}

            {/* Job Cards */}
            <div className="space-y-4">
                {jobs.map((job) => (
                    <Link
                        key={job.job_id}
                        href={`/careers/${job.job_id}`}
                        className="block glass-card p-6 hover:border-primary/30 transition-all duration-200 group"
                    >
                        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                            <div className="flex-1">
                                <h2 className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors">
                                    {job.job_title}
                                </h2>
                                <p className="text-muted-foreground mt-1">{job.company_name}</p>
                                <p className="text-sm text-muted-foreground mt-3 line-clamp-2">
                                    {job.summary}
                                </p>
                            </div>

                            <div className="flex flex-wrap gap-3 md:flex-col md:items-end md:gap-2">
                                {job.location && (
                                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                        <MapPin className="h-4 w-4" />
                                        <span>{job.location}</span>
                                    </div>
                                )}
                                {job.salary_range && (
                                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                        <DollarSign className="h-4 w-4" />
                                        <span>{job.salary_range}</span>
                                    </div>
                                )}
                                <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                                    <Clock className="h-4 w-4" />
                                    <span>{formatDate(job.posted_at)}</span>
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}
