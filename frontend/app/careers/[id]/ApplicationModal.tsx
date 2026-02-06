'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Upload, Send, FileText, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useToast } from '@/components/ui/Toast';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

// Zod validation schema
const applicationSchema = z.object({
    name: z.string().min(2, 'Name must be at least 2 characters').max(100),
    email: z.string().email('Please enter a valid email address'),
    phone: z.string().max(20).optional().or(z.literal('')),
});

type ApplicationFormValues = z.infer<typeof applicationSchema>;

interface ApplicationModalProps {
    isOpen: boolean;
    onClose: () => void;
    jobId: string;
    jobTitle: string;
}

export default function ApplicationModal({ isOpen, onClose, jobId, jobTitle }: ApplicationModalProps) {
    const { toast } = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [resumeFile, setResumeFile] = useState<File | null>(null);
    const [fileError, setFileError] = useState<string | null>(null);
    const [isSuccess, setIsSuccess] = useState(false);

    const {
        register,
        handleSubmit,
        reset,
        formState: { isSubmitting, errors },
    } = useForm<ApplicationFormValues>({
        resolver: zodResolver(applicationSchema),
        defaultValues: {
            name: '',
            email: '',
            phone: '',
        },
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        setFileError(null);

        if (!file) {
            setResumeFile(null);
            return;
        }

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            setFileError('Please upload a PDF file');
            setResumeFile(null);
            return;
        }

        // Validate file size (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            setFileError('File size must be less than 10MB');
            setResumeFile(null);
            return;
        }

        setResumeFile(file);
    };

    const onSubmit = async (data: ApplicationFormValues) => {
        if (!resumeFile) {
            setFileError('Please upload your resume');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('name', data.name);
            formData.append('email', data.email);
            if (data.phone) formData.append('phone', data.phone);
            formData.append('resume', resumeFile);

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/careers/${jobId}/apply`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to submit application');
            }

            setIsSuccess(true);
            toast('success', 'Application submitted successfully!');
            
            // Reset after delay
            setTimeout(() => {
                reset();
                setResumeFile(null);
                setIsSuccess(false);
                onClose();
            }, 2000);

        } catch (error) {
            console.error('Application error:', error);
            toast('error', error instanceof Error ? error.message : 'Failed to submit application');
        }
    };

    const handleClose = () => {
        if (!isSubmitting) {
            reset();
            setResumeFile(null);
            setFileError(null);
            setIsSuccess(false);
            onClose();
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
                    className="glass-card w-full max-w-md p-6"
                >
                    {/* Header */}
                    <div className="flex justify-between items-center mb-6">
                        <div>
                            <h2 className="text-xl font-semibold text-foreground">Apply Now</h2>
                            <p className="text-sm text-muted-foreground mt-1">{jobTitle}</p>
                        </div>
                        <button 
                            onClick={handleClose} 
                            className="text-muted-foreground hover:text-foreground" 
                            aria-label="Close"
                            disabled={isSubmitting}
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>

                    {isSuccess ? (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-center py-8"
                        >
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 mb-4">
                                <CheckCircle className="h-8 w-8 text-green-500" />
                            </div>
                            <h3 className="text-lg font-semibold text-foreground mb-2">Application Submitted!</h3>
                            <p className="text-muted-foreground">We&apos;ll review your application and get back to you soon.</p>
                        </motion.div>
                    ) : (
                        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                            {/* Name */}
                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-muted-foreground">Full Name *</label>
                                <Input
                                    {...register('name')}
                                    placeholder="John Doe"
                                    className={errors.name ? 'border-red-500' : ''}
                                    disabled={isSubmitting}
                                />
                                {errors.name && <p className="text-red-500 text-xs">{errors.name.message}</p>}
                            </div>

                            {/* Email */}
                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-muted-foreground">Email Address *</label>
                                <Input
                                    {...register('email')}
                                    type="email"
                                    placeholder="you@example.com"
                                    className={errors.email ? 'border-red-500' : ''}
                                    disabled={isSubmitting}
                                />
                                {errors.email && <p className="text-red-500 text-xs">{errors.email.message}</p>}
                            </div>

                            {/* Phone */}
                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-muted-foreground">Phone Number</label>
                                <Input
                                    {...register('phone')}
                                    type="tel"
                                    placeholder="+1 (555) 123-4567"
                                    disabled={isSubmitting}
                                />
                            </div>

                            {/* Resume Upload */}
                            <div className="space-y-1.5">
                                <label className="text-sm font-medium text-muted-foreground">Resume (PDF) *</label>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    disabled={isSubmitting}
                                />
                                <div
                                    onClick={() => !isSubmitting && fileInputRef.current?.click()}
                                    className={`
                                        border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors
                                        ${resumeFile ? 'border-green-500 bg-green-500/10' : 'border-border hover:border-primary/50'}
                                        ${fileError ? 'border-red-500' : ''}
                                        ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}
                                    `}
                                >
                                    {resumeFile ? (
                                        <div className="flex items-center justify-center gap-2 text-green-500">
                                            <FileText className="h-5 w-5" />
                                            <span className="text-sm font-medium">{resumeFile.name}</span>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center gap-2 text-muted-foreground">
                                            <Upload className="h-6 w-6" />
                                            <span className="text-sm">Click to upload your resume</span>
                                            <span className="text-xs">PDF only, max 10MB</span>
                                        </div>
                                    )}
                                </div>
                                {fileError && <p className="text-red-500 text-xs">{fileError}</p>}
                            </div>

                            {/* Submit Button */}
                            <div className="pt-4">
                                <Button type="submit" className="w-full" isLoading={isSubmitting}>
                                    <Send className="mr-2 h-4 w-4" /> Submit Application
                                </Button>
                            </div>
                        </form>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
