'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useToast } from '@/components/ui/Toast';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, Upload } from 'lucide-react';

export default function CreateJobPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setIsLoading(true);

        const formData = new FormData(e.currentTarget);
        const role_title = formData.get('role_title') as string;
        const department = formData.get('department') as string;
        const company_name = formData.get('company_name') as string;
        const descriptionRaw = formData.get('description') as string;

        // Convert description lines to list
        const key_requirements = descriptionRaw
            ? descriptionRaw.split('\n').map(line => line.trim()).filter(line => line.length > 0)
            : [];

        try {
            const res = await api.post('/jobs/create', {
                role_title,
                department,
                company_name,
                key_requirements: key_requirements,
                experience_years: 3 // Default
            });

            // Redirect to job details/status page
            router.push(`/jobs/${res.data.job_id}`);

        } catch (error) {
            console.error(error);
            console.error(error);
            toast('error', 'Failed to create job');
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <div>
                <h2 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
                    <Sparkles className="text-primary" />
                    Create New Job
                </h2>
                <p className="text-muted-foreground">
                    Let our AI agents take over. Just provide the role details.
                </p>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-8"
            >
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-foreground">Role Title</label>
                            <Input
                                name="role_title"
                                placeholder="e.g. Senior Frontend Engineer"
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-foreground">Department</label>
                            <Input
                                name="department"
                                placeholder="e.g. Engineering"
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-foreground">Company Name</label>
                        <Input
                            name="company_name"
                            placeholder="e.g. Acme Inc"
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-foreground">
                            Key Requirements / Notes (Optional)
                        </label>
                        <textarea
                            name="description"
                            rows={6}
                            className="w-full rounded-lg glass-input px-3 py-2 text-sm shadow-sm focus:ring-2 focus:ring-primary focus:outline-none"
                            placeholder="Paste raw requirements or notes... (One per line if possible)"
                        />
                        <p className="text-xs text-muted-foreground">
                            The AI will use this to fine-tune the JD.
                        </p>
                    </div>

                    <div className="pt-4 flex justify-end">
                        <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto">
                            Start AI Recruitment Agent <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                </form>
            </motion.div>
        </div>
    );
}
