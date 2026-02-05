import { fetchServer } from '@/lib/fetch-server';
import JobDetailView from '@/features/jobs/components/views/JobDetailView';
import type { JobStatus, GeneratedJD } from '@/types';

interface PageProps {
    params: Promise<{ id: string }>;
}

export default async function JobPage({ params }: PageProps) {
    const { id } = await params;

    // Fetch initial data on the server
    // We try/catch to gracefully handle partial failures or let error.tsx handle critical ones
    // For now, let critical status fetch bubble up to error boundary if it fails
    const status: JobStatus = await fetchServer(`/jobs/status/${id}`, {
        cache: 'no-store' // Ensure we get fresh status
    });

    let jd: GeneratedJD | null = null;
    if (status.has_generated_jd) {
        try {
            jd = await fetchServer(`/jobs/${id}/jd`, {
                cache: 'no-store'
            });
        } catch (e) {
            console.error('Failed to fetch JD server-side', e);
            // Non-fatal, client can retry
        }
    }

    return (
        <JobDetailView
            jobId={id}
            initialStatus={status}
            initialJD={jd}
        />
    );
}
