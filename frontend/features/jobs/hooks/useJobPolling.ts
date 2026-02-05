import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { JobStatus, GeneratedJD } from '@/types';

interface JobData {
    status: JobStatus | null;
    jd: GeneratedJD | null;
}

interface UseJobPollingOptions {
    initialStatus?: JobStatus | null;
    initialJD?: GeneratedJD | null;
    pollingInterval?: number;
}

export function useJobPolling(jobId: string, options: UseJobPollingOptions = {}) {
    const [status, setStatus] = useState<JobStatus | null>(options.initialStatus || null);
    const [jd, setJD] = useState<GeneratedJD | null>(options.initialJD || null);
    const [loading, setLoading] = useState(!options.initialStatus);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        try {
            // Fetch status
            const statusRes = await api.get<JobStatus>(`/jobs/status/${jobId}`);
            const newStatus = statusRes.data;
            setStatus(newStatus);

            // Fetch JD if generated and not present or if re-generated
            if (newStatus.has_generated_jd) {
                // Determine if we need to fetch JD (if missing or if potentially updated)
                // For now, simple check: if we don't have it, or if status implies change
                if (!jd) {
                    const jdRes = await api.get<GeneratedJD>(`/jobs/${jobId}/jd`);
                    setJD(jdRes.data);
                }
            }
        } catch (err: any) {
            console.error('Failed to poll job data:', err);
            // Don't set global error on poll failure to avoid UI flickering, just log it
            if (!status) {
                setError(err.response?.data?.detail || 'Failed to load job details');
            }
        } finally {
            setLoading(false);
        }
    }, [jobId, jd, status]);

    useEffect(() => {
        // Initial fetch if no data
        if (!options.initialStatus) {
            fetchData();
        }

        let intervalId: NodeJS.Timeout;

        // Smart Polling Strategy
        const isTerminal = status?.jd_approval_status === 'approved'; // Broad simplification
        const isGenerating = status && !status.has_generated_jd;

        // Interval: Fast (3s) if generating, Slow (10s) if active, Off if terminal (or very slow?)
        // User requested to STOP if completed.
        // Let's keep it live but slow for candidate updates (e.g. 15s)
        const intervalTime = isGenerating ? 3000 : (isTerminal ? 15000 : 5000);

        intervalId = setInterval(fetchData, intervalTime);

        return () => clearInterval(intervalId);
    }, [jobId, fetchData, options.initialStatus, status?.jd_approval_status, status?.has_generated_jd]);

    // Manual refresh action
    const refresh = useCallback(() => {
        setLoading(true);
        fetchData();
    }, [fetchData]);

    return { status, jd, loading, error, refresh, setJD }; // expose setJD for optimistic updates
}
