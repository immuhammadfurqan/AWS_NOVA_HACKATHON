'use client';

import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface DeleteJobModalProps {
    isOpen: boolean;
    jobTitle: string;
    companyName: string;
    onConfirm: () => void;
    onCancel: () => void;
    isDeleting: boolean;
}

export function DeleteJobModal({
    isOpen,
    jobTitle,
    companyName,
    onConfirm,
    onCancel,
    isDeleting
}: DeleteJobModalProps) {
    const modalRef = useRef<HTMLDivElement>(null);

    // Close on escape key
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && !isDeleting) onCancel();
        };
        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            return () => document.removeEventListener('keydown', handleEscape);
        }
    }, [isOpen, onCancel, isDeleting]);

    // Prevent body scroll when modal is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
            return () => { document.body.style.overflow = 'unset'; };
        }
    }, [isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={!isDeleting ? onCancel : undefined}
                        className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
                    />

                    {/* Modal */}
                    <motion.div
                        ref={modalRef}
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2 w-full max-w-md"
                    >
                        <div className="glass-card p-6 mx-4">
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-full bg-red-500/10">
                                        <AlertTriangle className="h-5 w-5 text-red-400" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-foreground">Delete Job</h3>
                                </div>
                                <button
                                    onClick={onCancel}
                                    disabled={isDeleting}
                                    className="p-1 rounded-lg hover:bg-muted/50 transition-colors disabled:opacity-50"
                                >
                                    <X className="h-5 w-5 text-muted-foreground" />
                                </button>
                            </div>

                            {/* Content */}
                            <div className="mb-6">
                                <p className="text-muted-foreground mb-3">
                                    Are you sure you want to delete this job? This action cannot be undone.
                                </p>
                                <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                                    <p className="font-medium text-foreground">{jobTitle}</p>
                                    <p className="text-sm text-muted-foreground">{companyName}</p>
                                </div>
                                <p className="text-xs text-muted-foreground mt-3">
                                    All job data including generated JD, candidates, and embeddings will be permanently deleted.
                                </p>
                            </div>

                            {/* Actions */}
                            <div className="flex justify-end gap-3">
                                <Button
                                    variant="outline"
                                    onClick={onCancel}
                                    disabled={isDeleting}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    onClick={onConfirm}
                                    isLoading={isDeleting}
                                    className="bg-red-500 hover:bg-red-600 text-white"
                                >
                                    Delete Job
                                </Button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
