import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { motion } from 'framer-motion';
import {
    CheckCircle,
    Pencil,
    RefreshCw,
    Users,
    MapPin,
    DollarSign
} from 'lucide-react';
import { JobStatus, GeneratedJD } from '@/types';
import dynamic from 'next/dynamic';
import { useJobActions } from '../hooks/useJobActions';

const EditJDModal = dynamic(() => import('@/features/jobs/components/EditJDModal'), {
    loading: () => null,
    ssr: false
});
const RegenerateJDModal = dynamic(() => import('@/features/jobs/components/RegenerateJDModal'), {
    loading: () => null,
    ssr: false
});

interface JobHeaderProps {
    id: string;
    status: JobStatus;
    jd: GeneratedJD;
    onJDUpdate: (jd: GeneratedJD) => void;
    onRefresh: () => void;
}

export default function JobHeader({ id, status, jd, onJDUpdate, onRefresh }: JobHeaderProps) {
    const router = useRouter();
    const [showEditModal, setShowEditModal] = useState(false);
    const [showRegenerateModal, setShowRegenerateModal] = useState(false);

    const { approveJob, addMockCandidates, isApproving } = useJobActions({
        jobId: id,
        onRefresh
    });

    const isApproved = status?.jd_approval_status === 'approved';

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col md:flex-row md:items-start md:justify-between gap-6"
        >
            <div className="space-y-3">
                <div className="flex items-center gap-3 flex-wrap">
                    <h1 className="text-3xl font-bold text-foreground">{jd.job_title}</h1>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${isApproved
                        ? 'bg-green-500/10 text-green-600 border-green-500/20'
                        : 'bg-amber-500/10 text-amber-600 border-amber-500/20 animate-pulse'
                        }`}>
                        {isApproved ? '✓ Live & Posted' : '⏳ Pending Approval'}
                    </span>
                </div>
                <div className="flex items-center gap-4 text-muted-foreground">
                    {jd.location && (
                        <span className="flex items-center gap-1.5 bg-muted/50 px-3 py-1.5 rounded-lg">
                            <MapPin className="h-4 w-4 text-primary" />
                            {jd.location}
                        </span>
                    )}
                    {jd.salary_range && (
                        <span className="flex items-center gap-1.5 bg-muted/50 px-3 py-1.5 rounded-lg">
                            <DollarSign className="h-4 w-4 text-green-600" />
                            {jd.salary_range}
                        </span>
                    )}
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2">
                {!isApproved && (
                    <>
                        <Button
                            onClick={() => setShowEditModal(true)}
                            variant="outline"
                        >
                            <Pencil className="mr-2 h-4 w-4" /> Edit
                        </Button>
                        <Button
                            onClick={() => setShowRegenerateModal(true)}
                            variant="outline"
                        >
                            <RefreshCw className="mr-2 h-4 w-4" /> Request Changes
                        </Button>
                        <Button
                            onClick={approveJob}
                            isLoading={isApproving}
                            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-lg shadow-green-500/25 text-white"
                        >
                            <CheckCircle className="mr-2 h-4 w-4" /> Approve & Post
                        </Button>
                    </>
                )}
                <Button
                    onClick={() => addMockCandidates(5)}
                    variant="outline"
                    className="border-primary/30 text-primary hover:bg-primary/10"
                >
                    <Users className="mr-2 h-4 w-4" /> + Mock Candidates
                </Button>
                <Button
                    onClick={() => router.push(`/jobs/${id}/candidates`)}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20"
                >
                    <Users className="mr-2 h-4 w-4" /> View Candidates
                </Button>
            </div>

            {/* Modals */}
            <EditJDModal
                isOpen={showEditModal}
                onClose={() => setShowEditModal(false)}
                jobId={id}
                jd={jd}
                onSave={(updatedJD) => {
                    onJDUpdate(updatedJD);
                }}
            />
            <RegenerateJDModal
                isOpen={showRegenerateModal}
                onClose={() => setShowRegenerateModal(false)}
                jobId={id}
                onRegenerate={(newJD) => {
                    onJDUpdate(newJD);
                }}
            />
        </motion.div>
    );
}
