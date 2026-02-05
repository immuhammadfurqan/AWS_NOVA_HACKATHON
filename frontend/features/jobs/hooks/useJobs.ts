'use client';

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { JobListItem, JobListResponse } from '@/types';

interface UseJobsResult {
    jobs: JobListItem[];
    total: number;
    loading: boolean;
    error: string | null;
    refresh: () => void;
    deleteJob: (jobId: string) => Promise<boolean>;
}

export function useJobs(): UseJobsResult {
    const [jobs, setJobs] = useState<JobListItem[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchJobs = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.get<JobListResponse>('/jobs/');
            setJobs(response.data.jobs);
            setTotal(response.data.total);
        } catch (err: any) {
            console.error('Failed to fetch jobs:', err);
            setError(err.response?.data?.detail || 'Failed to load jobs');
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteJob = useCallback(async (jobId: string): Promise<boolean> => {
        try {
            await api.delete(`/jobs/${jobId}`);
            // Optimistic update
            setJobs(prev => prev.filter(job => job.job_id !== jobId));
            setTotal(prev => prev - 1);
            return true;
        } catch (err: any) {
            console.error('Failed to delete job:', err);
            return false;
        }
    }, []);

    useEffect(() => {
        fetchJobs();
    }, [fetchJobs]);

    return { jobs, total, loading, error, refresh: fetchJobs, deleteJob };
}
