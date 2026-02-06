import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, MapPin, DollarSign, Clock, Building2, CheckCircle } from 'lucide-react';
import Script from 'next/script';
import ApplyButton from './ApplyButton';

interface PublicJobResponse {
    job_id: string;
    job_title: string;
    company_name: string;
    company_description: string | null;
    location: string | null;
    salary_range: string | null;
    summary: string;
    description: string;
    responsibilities: string[];
    requirements: string[];
    nice_to_have: string[];
    benefits: string[];
    posted_at: string;
    jsonld: Record<string, unknown>;
}

interface PageProps {
    params: Promise<{ id: string }>;
}

async function getPublicJob(id: string): Promise<PublicJobResponse | null> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    try {
        const res = await fetch(`${apiUrl}/careers/${id}`, {
            next: { revalidate: 60 },
        });

        if (!res.ok) {
            return null;
        }

        return res.json();
    } catch (error) {
        console.error('Failed to fetch job:', error);
        return null;
    }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
    const resolvedParams = await params;
    const job = await getPublicJob(resolvedParams.id);

    if (!job) {
        return { title: 'Job Not Found' };
    }

    return {
        title: `${job.job_title} at ${job.company_name} | Careers`,
        description: job.summary,
        openGraph: {
            title: `${job.job_title} at ${job.company_name}`,
            description: job.summary,
            type: 'website',
        },
    };
}

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
    });
}

export default async function JobDetailPage({ params }: PageProps) {
    const resolvedParams = await params;
    const job = await getPublicJob(resolvedParams.id);

    if (!job) {
        notFound();
    }

    return (
        <>
            {/* JSON-LD for Google for Jobs */}
            <Script
                id="job-posting-jsonld"
                type="application/ld+json"
                dangerouslySetInnerHTML={{
                    __html: JSON.stringify(job.jsonld),
                }}
            />

            <div className="max-w-4xl mx-auto px-4">
                {/* Back Link */}
                <Link
                    href="/careers"
                    className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Back to all jobs
                </Link>

                {/* Header */}
                <div className="glass-card p-8 mb-8">
                    <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
                        {job.job_title}
                    </h1>

                    <div className="flex items-center gap-2 text-lg text-muted-foreground mb-6">
                        <Building2 className="h-5 w-5" />
                        <span>{job.company_name}</span>
                    </div>

                    <div className="flex flex-wrap gap-4 mb-6">
                        {job.location && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 text-sm">
                                <MapPin className="h-4 w-4 text-primary" />
                                <span>{job.location}</span>
                            </div>
                        )}
                        {job.salary_range && (
                            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 text-sm">
                                <DollarSign className="h-4 w-4 text-green-500" />
                                <span>{job.salary_range}</span>
                            </div>
                        )}
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 text-sm">
                            <Clock className="h-4 w-4 text-blue-500" />
                            <span>Posted {formatDate(job.posted_at)}</span>
                        </div>
                    </div>

                    <p className="text-lg text-foreground/90 leading-relaxed">
                        {job.summary}
                    </p>

                    {/* Apply Button */}
                    <div className="mt-8">
                        <ApplyButton jobId={job.job_id} jobTitle={job.job_title} />
                    </div>
                </div>

                {/* Description */}
                {job.description && (
                    <section className="glass-card p-8 mb-6">
                        <h2 className="text-xl font-semibold text-foreground mb-4">About the Role</h2>
                        <div className="prose prose-invert max-w-none">
                            <p className="text-foreground/80 whitespace-pre-wrap">{job.description}</p>
                        </div>
                    </section>
                )}

                {/* Responsibilities */}
                {job.responsibilities.length > 0 && (
                    <section className="glass-card p-8 mb-6">
                        <h2 className="text-xl font-semibold text-foreground mb-4">Responsibilities</h2>
                        <ul className="space-y-3">
                            {job.responsibilities.map((item, i) => (
                                <li key={i} className="flex items-start gap-3">
                                    <CheckCircle className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                                    <span className="text-foreground/80">{item}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* Requirements */}
                {job.requirements.length > 0 && (
                    <section className="glass-card p-8 mb-6">
                        <h2 className="text-xl font-semibold text-foreground mb-4">Requirements</h2>
                        <ul className="space-y-3">
                            {job.requirements.map((item, i) => (
                                <li key={i} className="flex items-start gap-3">
                                    <CheckCircle className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                                    <span className="text-foreground/80">{item}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* Nice to Have */}
                {job.nice_to_have.length > 0 && (
                    <section className="glass-card p-8 mb-6">
                        <h2 className="text-xl font-semibold text-foreground mb-4">Nice to Have</h2>
                        <ul className="space-y-3">
                            {job.nice_to_have.map((item, i) => (
                                <li key={i} className="flex items-start gap-3">
                                    <CheckCircle className="h-5 w-5 text-purple-400 flex-shrink-0 mt-0.5" />
                                    <span className="text-foreground/80">{item}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* Benefits */}
                {job.benefits.length > 0 && (
                    <section className="glass-card p-8 mb-6">
                        <h2 className="text-xl font-semibold text-foreground mb-4">Benefits</h2>
                        <ul className="space-y-3">
                            {job.benefits.map((item, i) => (
                                <li key={i} className="flex items-start gap-3">
                                    <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                                    <span className="text-foreground/80">{item}</span>
                                </li>
                            ))}
                        </ul>
                    </section>
                )}

                {/* Company Info */}
                {job.company_description && (
                    <section className="glass-card p-8 mb-6">
                        <h2 className="text-xl font-semibold text-foreground mb-4">About {job.company_name}</h2>
                        <p className="text-foreground/80">{job.company_description}</p>
                    </section>
                )}

                {/* Bottom CTA */}
                <div className="glass-card p-8 text-center">
                    <h3 className="text-xl font-semibold text-foreground mb-2">Interested in this role?</h3>
                    <p className="text-muted-foreground mb-6">We&apos;d love to hear from you!</p>
                    <ApplyButton jobId={job.job_id} jobTitle={job.job_title} />
                </div>
            </div>
        </>
    );
}
