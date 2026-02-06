'use client';

import { useState } from 'react';
import ApplicationModal from './ApplicationModal';

interface ApplyButtonProps {
    jobId: string;
    jobTitle: string;
    className?: string;
}

export default function ApplyButton({ jobId, jobTitle, className }: ApplyButtonProps) {
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <>
            <button
                onClick={() => setIsModalOpen(true)}
                className={className || "px-8 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"}
            >
                Apply Now
            </button>
            <ApplicationModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                jobId={jobId}
                jobTitle={jobTitle}
            />
        </>
    );
}
