'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useToast } from '@/components/ui/Toast';
import { api } from '@/lib/api';
import type { GeneratedJD } from '@/types';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

// Define Zod Schema
const jdSchema = z.object({
    job_title: z.string().min(1, 'Job title is required'),
    summary: z.string().min(10, 'Summary is required'),
    responsibilities: z.array(z.string().min(1, 'Cannot be empty')),
    requirements: z.array(z.string().min(1, 'Cannot be empty')),
    benefits: z.array(z.string().min(1, 'Cannot be empty')),
    location: z.string().optional(),
    salary_range: z.string().optional(),
});

type JDFormValues = z.infer<typeof jdSchema>;

interface EditJDModalProps {
    isOpen: boolean;
    onClose: () => void;
    jobId: string;
    jd: GeneratedJD;
    onSave: (updatedJD: GeneratedJD) => void;
}

export default function EditJDModal({ isOpen, onClose, jobId, jd, onSave }: EditJDModalProps) {
    const { toast } = useToast();

    const {
        control,
        register,
        handleSubmit,
        reset,
        formState: { isSubmitting, errors },
    } = useForm<JDFormValues>({
        resolver: zodResolver(jdSchema),
        defaultValues: jd, // Initialize with passed JD data
    });

    // Reset form when modal opens or JD data changes
    useEffect(() => {
        if (isOpen) {
            reset(jd);
        }
    }, [isOpen, jd, reset]);

    // Field Arrays for lists
    const responsibilities = useFieldArray({
        control,
        name: "responsibilities" as never, // Cast to avoid complex recursive type error with primitive arrays
    });
    const requirements = useFieldArray({
        control,
        name: "requirements" as never,
    });
    const benefits = useFieldArray({
        control,
        name: "benefits" as never,
    });

    const onSubmit = async (data: JDFormValues) => {
        try {
            // Merge base JD data with form data to keep other fields like approval status
            const payload: GeneratedJD = { ...jd, ...data };
            const res = await api.put(`/jobs/${jobId}/jd`, payload);
            onSave(res.data);
            onClose();
            toast('success', 'Job description updated successfully');
        } catch (error) {
            console.error('Failed to update JD:', error);
            toast('error', 'Failed to update job description');
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
                    className="glass-card w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6"
                >
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-foreground">Edit Job Description</h2>
                        <button onClick={onClose} className="text-muted-foreground hover:text-foreground" aria-label="Close">
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        {/* Job Title */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Job Title</label>
                            <Input
                                {...register('job_title')}
                                placeholder="Job Title"
                                className={errors.job_title ? 'border-red-500' : ''}
                            />
                            {errors.job_title && <p className="text-red-500 text-xs">{errors.job_title.message}</p>}
                        </div>

                        {/* Summary */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Summary</label>
                            <textarea
                                {...register('summary')}
                                rows={4}
                                className="w-full rounded-lg border border-border bg-muted/50 px-3 py-2 text-sm text-foreground focus:ring-2 focus:ring-primary focus:outline-none"
                            />
                            {errors.summary && <p className="text-red-500 text-xs">{errors.summary.message}</p>}
                        </div>

                        {/* Responsibilities */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Responsibilities</label>
                            <div className="space-y-2">
                                {responsibilities.fields.map((field, index) => (
                                    <div key={field.id} className="flex gap-2">
                                        <Input
                                            {...register(`responsibilities.${index}` as const)}
                                            className={errors.responsibilities?.[index] ? 'border-red-500 flex-1' : 'flex-1'}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => responsibilities.remove(index)}
                                            className="text-red-400 hover:text-red-300 px-2"
                                            aria-label="Remove"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <button
                                type="button"
                                onClick={() => responsibilities.append('')}
                                className="flex items-center gap-1 text-sm text-primary hover:text-primary/80 mt-2"
                            >
                                <Plus className="h-3 w-3" /> Add Responsibility
                            </button>
                        </div>

                        {/* Requirements */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Requirements</label>
                            <div className="space-y-2">
                                {requirements.fields.map((field, index) => (
                                    <div key={field.id} className="flex gap-2">
                                        <Input
                                            {...register(`requirements.${index}` as const)}
                                            className={errors.requirements?.[index] ? 'border-red-500 flex-1' : 'flex-1'}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => requirements.remove(index)}
                                            className="text-red-400 hover:text-red-300 px-2"
                                            aria-label="Remove"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <button
                                type="button"
                                onClick={() => requirements.append('')}
                                className="flex items-center gap-1 text-sm text-primary hover:text-primary/80 mt-2"
                            >
                                <Plus className="h-3 w-3" /> Add Requirement
                            </button>
                        </div>

                        {/* Benefits */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-muted-foreground">Benefits</label>
                            <div className="space-y-2">
                                {benefits.fields.map((field, index) => (
                                    <div key={field.id} className="flex gap-2">
                                        <Input
                                            {...register(`benefits.${index}` as const)}
                                            className={errors.benefits?.[index] ? 'border-red-500 flex-1' : 'flex-1'}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => benefits.remove(index)}
                                            className="text-red-400 hover:text-red-300 px-2"
                                            aria-label="Remove"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <button
                                type="button"
                                onClick={() => benefits.append('')}
                                className="flex items-center gap-1 text-sm text-primary hover:text-primary/80 mt-2"
                            >
                                <Plus className="h-3 w-3" /> Add Benefit
                            </button>
                        </div>

                        {/* Location & Salary */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-muted-foreground">Location</label>
                                <Input {...register('location')} placeholder="e.g. Remote, NYC" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-muted-foreground">Salary Range</label>
                                <Input {...register('salary_range')} placeholder="e.g. $120k - $150k" />
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end gap-3 pt-4 border-t border-border">
                            <Button type="button" variant="outline" onClick={onClose}>
                                Cancel
                            </Button>
                            <Button type="submit" isLoading={isSubmitting}>
                                <Save className="mr-2 h-4 w-4" /> Save Changes
                            </Button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
