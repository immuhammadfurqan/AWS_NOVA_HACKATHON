'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';
import type { GeneratedJD } from '@/types';

interface RegenerateJDModalProps {
    isOpen: boolean;
    onClose: () => void;
    jobId: string;
    onRegenerate: (newJD: GeneratedJD) => void;
}

export default function RegenerateJDModal({ isOpen, onClose, jobId, onRegenerate }: RegenerateJDModalProps) {
    const [feedback, setFeedback] = useState('');
    const [isRegenerating, setIsRegenerating] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!feedback.trim()) {
            alert('Please provide feedback for the AI');
            return;
        }

        setIsRegenerating(true);

        try {
            const res = await api.post(`/jobs/${jobId}/regenerate-jd`, { feedback });
            onRegenerate(res.data);
            setFeedback('');
            onClose();
        } catch (error) {
            console.error('Failed to regenerate JD:', error);
            alert('Failed to regenerate JD');
        } finally {
            setIsRegenerating(false);
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="glass-card w-full max-w-lg p-6"
                >
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
                            <Sparkles className="h-5 w-5 text-primary" />
                            Request AI Changes
                        </h2>
                        <button onClick={onClose} className="text-muted-foreground hover:text-foreground" aria-label="Close">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">
                                What changes would you like?
                            </label>
                            <textarea
                                value={feedback}
                                onChange={(e) => setFeedback(e.target.value)}
                                rows={4}
                                placeholder="e.g. Make it more concise, emphasize Python skills, add remote work option..."
                                className="w-full rounded-lg border border-border bg-muted/50 px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary focus:outline-none"
                            />
                            <p className="text-xs text-muted-foreground">
                                The AI will regenerate the entire JD incorporating your feedback.
                            </p>
                        </div>

                        {isRegenerating && (
                            <div className="flex items-center justify-center gap-3 py-4">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse" />
                                    <RefreshCw className="h-8 w-8 text-primary animate-spin relative z-10" />
                                </div>
                                <span className="text-muted-foreground">AI is regenerating...</span>
                            </div>
                        )}

                        <div className="flex justify-end gap-3 pt-4 border-t border-border">
                            <Button type="button" variant="outline" onClick={onClose} disabled={isRegenerating}>
                                Cancel
                            </Button>
                            <Button type="submit" isLoading={isRegenerating} disabled={!feedback.trim()}>
                                <Sparkles className="mr-2 h-4 w-4" /> Regenerate JD
                            </Button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
