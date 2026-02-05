'use client';

import { motion } from 'framer-motion';
import {
    Sparkles,
    CheckCircle,
    FileText,
    Users,
    Target,
    Calendar,
    Briefcase,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface WorkflowStep {
    id: string;
    label: string;
    icon: LucideIcon;
}

const WORKFLOW_STEPS: WorkflowStep[] = [
    { id: 'generate_jd', label: 'Generate JD', icon: Sparkles },
    { id: 'jd_review', label: 'Review & Approve', icon: FileText },
    { id: 'post_job', label: 'Post Job', icon: Briefcase },
    { id: 'monitor_applications', label: 'Collect Applications', icon: Users },
    { id: 'shortlist_candidates', label: 'Shortlist', icon: Target },
    { id: 'voice_prescreening', label: 'Prescreening', icon: Calendar },
];

interface WorkflowProgressBarProps {
    currentNode: string;
}

export function getStepIndex(currentNode: string): number {
    const index = WORKFLOW_STEPS.findIndex(s => s.id === currentNode);
    return index === -1 ? 0 : index;
}

export default function WorkflowProgressBar({ currentNode }: WorkflowProgressBarProps) {
    const currentStepIndex = getStepIndex(currentNode);

    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Recruitment Pipeline
                </h3>
                <span className="text-xs text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">
                    Step {currentStepIndex + 1} of {WORKFLOW_STEPS.length}
                </span>
            </div>
            <div className="flex items-center justify-between">
                {WORKFLOW_STEPS.map((step, index) => {
                    const Icon = step.icon;
                    const isCompleted = index < currentStepIndex;
                    const isCurrent = index === currentStepIndex;

                    return (
                        <div key={step.id} className="flex items-center flex-1">
                            <div className="flex flex-col items-center">
                                <motion.div
                                    initial={false}
                                    animate={{
                                        scale: isCurrent ? 1.1 : 1,
                                        backgroundColor: isCompleted
                                            ? 'rgb(34 197 94)' // Green is fine/semantic-ish
                                            : isCurrent
                                                ? 'oklch(var(--primary))' // Use primary CSS variable
                                                : 'oklch(var(--muted))', // Use muted for incomplete
                                    }}
                                    className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${isCurrent ? 'ring-4 ring-blue-500/30' : ''
                                        }`}
                                >

                                    {isCompleted ? (
                                        <CheckCircle className="h-5 w-5 text-white" />
                                    ) : (
                                        <Icon className={`h-5 w-5 ${isCurrent ? 'text-primary-foreground' : 'text-muted-foreground'}`} />
                                    )}
                                </motion.div>
                                <span
                                    className={`text-xs mt-2 text-center max-w-[80px] ${isCurrent ? 'text-primary font-medium' : 'text-muted-foreground'
                                        }`}
                                >
                                    {step.label}
                                </span>
                            </div>
                            {index < WORKFLOW_STEPS.length - 1 && (
                                <div
                                    className={`flex-1 h-0.5 mx-2 ${index < currentStepIndex ? 'bg-green-500' : 'bg-muted'
                                        }`}
                                />
                            )}
                        </div>
                    );
                })}
            </div>
        </motion.div>
    );
}
