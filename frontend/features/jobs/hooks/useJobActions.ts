import { useState } from 'react';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui/Toast';

interface UseJobActionsProps {
    jobId: string;
    onRefresh: () => void;
}

export function useJobActions({ jobId, onRefresh }: UseJobActionsProps) {
    const [isApproving, setIsApproving] = useState(false);
    const [isAddingMock, setIsAddingMock] = useState(false);
    const { toast } = useToast();

    const approveJob = async () => {
        setIsApproving(true);
        try {
            await api.post(`/jobs/${jobId}/approve-jd`);
            onRefresh();
            toast('success', 'Job description approved and posted!');
        } catch (error) {
            console.error('Failed to approve:', error);
            toast('error', 'Failed to approve JD');
        } finally {
            setIsApproving(false);
        }
    };

    const addMockCandidates = async (count: number = 5) => {
        setIsAddingMock(true);
        try {
            await api.post(`/jobs/${jobId}/mock/add-applicants?count=${count}`);
            toast('success', `Added ${count} mock candidates!`);
            onRefresh();
        } catch (error) {
            console.error(error);
            toast('error', 'Failed to add mock candidates');
        } finally {
            setIsAddingMock(false);
        }
    };

    return {
        approveJob,
        addMockCandidates,
        isApproving,
        isAddingMock
    };
}
