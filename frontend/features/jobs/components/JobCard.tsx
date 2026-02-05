'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
    Building2,
    Calendar,
    MoreVertical,
    Trash2,
    Eye,
    Clock,
    CheckCircle2,
    AlertCircle,
    Loader2
} from 'lucide-react';
import type { JobListItem } from '@/types';

interface JobCardProps {
    job: JobListItem;
    onDelete: (jobId: string) => void;
    isDeleting?: boolean;
}

// Map current_node to user-friendly status
function getStatusInfo(currentNode: string): { label: string; color: string; icon: React.ReactNode } {
    const statusMap: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
        'generate_jd': { label: 'Generating JD', color: 'bg-blue-500/20 text-blue-400', icon: <Loader2 className="h-3 w-3 animate-spin" /> },
        'await_jd_approval': { label: 'Awaiting Approval', color: 'bg-amber-500/20 text-amber-400', icon: <Clock className="h-3 w-3" /> },
        'post_job': { label: 'Posting Job', color: 'bg-purple-500/20 text-purple-400', icon: <Loader2 className="h-3 w-3 animate-spin" /> },
        'monitor_applications': { label: 'Monitoring', color: 'bg-cyan-500/20 text-cyan-400', icon: <Eye className="h-3 w-3" /> },
        'shortlist_candidates': { label: 'Shortlisting', color: 'bg-indigo-500/20 text-indigo-400', icon: <CheckCircle2 className="h-3 w-3" /> },
        'await_shortlist_approval': { label: 'Review Shortlist', color: 'bg-amber-500/20 text-amber-400', icon: <Clock className="h-3 w-3" /> },
        'voice_prescreening': { label: 'Prescreening', color: 'bg-green-500/20 text-green-400', icon: <Loader2 className="h-3 w-3 animate-spin" /> },
        'schedule_interview': { label: 'Scheduling', color: 'bg-teal-500/20 text-teal-400', icon: <Calendar className="h-3 w-3" /> },
        'error': { label: 'Error', color: 'bg-red-500/20 text-red-400', icon: <AlertCircle className="h-3 w-3" /> },
        'completed': { label: 'Completed', color: 'bg-green-500/20 text-green-400', icon: <CheckCircle2 className="h-3 w-3" /> },
    };

    return statusMap[currentNode] || { label: currentNode.replace(/_/g, ' '), color: 'bg-gray-500/20 text-gray-400', icon: <Clock className="h-3 w-3" /> };
}

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

export function JobCard({ job, onDelete, isDeleting = false }: JobCardProps) {
    const [showMenu, setShowMenu] = useState(false);
    const statusInfo = getStatusInfo(job.current_node);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass-card p-5 hover:border-primary/30 transition-all duration-200 group"
        >
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                    <Link
                        href={`/jobs/${job.job_id}`}
                        className="block"
                    >
                        <h3 className="font-semibold text-lg text-foreground truncate group-hover:text-primary transition-colors">
                            {job.role_title}
                        </h3>
                    </Link>
                    <div className="flex items-center gap-2 mt-1.5 text-muted-foreground text-sm">
                        <Building2 className="h-4 w-4 flex-shrink-0" />
                        <span className="truncate">{job.company_name}</span>
                    </div>
                </div>

                {/* Status Badge */}
                <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusInfo.color}`}>
                    {statusInfo.icon}
                    <span>{statusInfo.label}</span>
                </div>
            </div>

            <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/50">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>Created {formatDate(job.created_at)}</span>
                </div>

                {/* Actions */}
                <div className="relative">
                    <button
                        onClick={() => setShowMenu(!showMenu)}
                        className="p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
                        disabled={isDeleting}
                    >
                        {isDeleting ? (
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                        ) : (
                            <MoreVertical className="h-4 w-4 text-muted-foreground" />
                        )}
                    </button>

                    {showMenu && !isDeleting && (
                        <>
                            <div
                                className="fixed inset-0 z-10"
                                onClick={() => setShowMenu(false)}
                            />
                            <div className="absolute right-0 top-full mt-1 z-20 min-w-[140px] rounded-lg border border-border bg-background/95 backdrop-blur-sm shadow-lg py-1">
                                <Link
                                    href={`/jobs/${job.job_id}`}
                                    className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted/50 transition-colors"
                                    onClick={() => setShowMenu(false)}
                                >
                                    <Eye className="h-4 w-4" />
                                    View Details
                                </Link>
                                <button
                                    onClick={() => {
                                        setShowMenu(false);
                                        onDelete(job.job_id);
                                    }}
                                    className="flex items-center gap-2 px-3 py-2 text-sm w-full text-left text-red-400 hover:bg-red-500/10 transition-colors"
                                >
                                    <Trash2 className="h-4 w-4" />
                                    Delete
                                </button>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
