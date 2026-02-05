'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { PlusCircle, Briefcase, RefreshCw, Inbox } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';
import { useJobs } from '@/features/jobs/hooks/useJobs';
import { JobCard } from '@/features/jobs/components/JobCard';
import { DeleteJobModal } from '@/features/jobs/components/DeleteJobModal';
import type { JobListItem } from '@/types';

export default function JobsListPage() {
    const { jobs, total, loading, error, refresh, deleteJob } = useJobs();
    const { toast } = useToast();

    // Delete modal state
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [deletingJob, setDeletingJob] = useState<JobListItem | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDeleteClick = (jobId: string) => {
        const job = jobs.find(j => j.job_id === jobId);
        if (job) {
            setDeletingJob(job);
            setDeleteModalOpen(true);
        }
    };

    const handleDeleteConfirm = async () => {
        if (!deletingJob) return;

        setIsDeleting(true);
        const success = await deleteJob(deletingJob.job_id);
        setIsDeleting(false);

        if (success) {
            toast('success', 'Job deleted successfully');
            setDeleteModalOpen(false);
            setDeletingJob(null);
        } else {
            toast('error', 'Failed to delete job');
        }
    };

    const handleDeleteCancel = () => {
        if (!isDeleting) {
            setDeleteModalOpen(false);
            setDeletingJob(null);
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
                        <Briefcase className="h-8 w-8 text-primary" />
                        Jobs
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Manage your recruitment processes
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Button
                        variant="outline"
                        onClick={refresh}
                        disabled={loading}
                        className="gap-2"
                    >
                        <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Link href="/jobs/new">
                        <Button className="gap-2">
                            <PlusCircle className="h-4 w-4" />
                            Create New Job
                        </Button>
                    </Link>
                </div>
            </div>

            {/* Error State */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400"
                >
                    {error}
                </motion.div>
            )}

            {/* Loading State */}
            {loading && jobs.length === 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="glass-card p-5 animate-pulse">
                            <div className="h-6 bg-muted/50 rounded w-3/4 mb-3" />
                            <div className="h-4 bg-muted/30 rounded w-1/2 mb-4" />
                            <div className="h-px bg-border/50 my-4" />
                            <div className="h-4 bg-muted/30 rounded w-1/3" />
                        </div>
                    ))}
                </div>
            )}

            {/* Empty State */}
            {!loading && jobs.length === 0 && !error && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-12 text-center"
                >
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                        <Inbox className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                        No jobs yet
                    </h3>
                    <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                        Get started by creating your first job. Our AI agents will help you generate compelling job descriptions.
                    </p>
                    <Link href="/jobs/new">
                        <Button className="gap-2">
                            <PlusCircle className="h-4 w-4" />
                            Create Your First Job
                        </Button>
                    </Link>
                </motion.div>
            )}

            {/* Jobs Grid */}
            {jobs.length > 0 && (
                <>
                    <p className="text-sm text-muted-foreground">
                        Showing {jobs.length} of {total} job{total !== 1 ? 's' : ''}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <AnimatePresence mode="popLayout">
                            {jobs.map((job) => (
                                <JobCard
                                    key={job.job_id}
                                    job={job}
                                    onDelete={handleDeleteClick}
                                    isDeleting={isDeleting && deletingJob?.job_id === job.job_id}
                                />
                            ))}
                        </AnimatePresence>
                    </div>
                </>
            )}

            {/* Delete Confirmation Modal */}
            <DeleteJobModal
                isOpen={deleteModalOpen}
                jobTitle={deletingJob?.role_title || ''}
                companyName={deletingJob?.company_name || ''}
                onConfirm={handleDeleteConfirm}
                onCancel={handleDeleteCancel}
                isDeleting={isDeleting}
            />
        </div>
    );
}
