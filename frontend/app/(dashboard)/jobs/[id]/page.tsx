import JobDetailView from '@/features/jobs/components/views/JobDetailView';

interface PageProps {
    params: Promise<{ id: string }>;
}

/**
 * Job detail page - uses client-side fetching only to avoid server timeout.
 * The Next.js server cannot reliably reach the API (different process/port),
 * so we skip server-side fetch and let JobDetailView poll from the client.
 */
export default async function JobPage({ params }: PageProps) {
    const { id } = await params;

    return (
        <JobDetailView
            jobId={id}
            initialStatus={null}
            initialJD={null}
        />
    );
}
