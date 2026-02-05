'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { JobStatus, GeneratedJD } from '@/types';
import JobHeader from '@/features/jobs/components/JobHeader';
import JDTabs from '@/features/jobs/components/JDTabs';
import JDLoadingState from '@/features/jobs/components/JDLoadingState';
import WorkflowProgressBar from '@/features/jobs/components/WorkflowProgressBar';
import { useJobPolling } from '@/features/jobs/hooks/useJobPolling';

type TabType = 'overview' | 'requirements' | 'benefits';

interface JobDetailViewProps {
    jobId: string;
    initialStatus: JobStatus | null;
    initialJD: GeneratedJD | null;
}

export default function JobDetailView({ jobId, initialStatus, initialJD }: JobDetailViewProps) {
    const { status, jd, loading, error, refresh, setJD } = useJobPolling(jobId, {
        initialStatus,
        initialJD
    });
    const [activeTab, setActiveTab] = useState<TabType>('overview');

    if (loading && !status) {
        return <JDLoadingState />;
    }

    if (error) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center min-h-[400px] text-center"
            >
                <div className="rounded-full bg-destructive/10 p-4 mb-4">
                    <AlertCircle className="h-8 w-8 text-destructive" />
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">Failed to Load Job</h2>
                <p className="text-muted-foreground mb-4 max-w-md">{error}</p>
                <Button onClick={refresh} variant="outline">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Try Again
                </Button>
            </motion.div>
        );
    }

    // Show loading state while JD is being generated
    if (status && !status.has_generated_jd) {
        return (
            <div className="space-y-8">
                <WorkflowProgressBar currentNode={status.current_node} />
                <JDLoadingState />
            </div>
        );
    }

    if (!jd) {
        return (
            <div className="text-center py-10">
                <p className="text-muted-foreground">Job description not available yet.</p>
                <Button onClick={refresh} variant="outline" className="mt-4">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {status && <WorkflowProgressBar currentNode={status.current_node} />}
            <JobHeader
                id={jobId}
                status={status!}
                jd={jd}
                onJDUpdate={(newJD) => setJD(newJD)}
                onRefresh={refresh}
            />
            <JDTabs jd={jd} activeTab={activeTab} onTabChange={setActiveTab} />
        </div>
    );
}
