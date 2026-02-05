'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import {
    Users,
    Briefcase,
    CheckCircle,
    Clock,
    ArrowRight,
    Loader2
} from 'lucide-react';
import { useJobs } from '@/features/jobs/hooks/useJobs';

// Helper to get status info for job cards
function getStatusBadge(currentNode: string): { label: string; color: string } {
    const statusMap: Record<string, { label: string; color: string }> = {
        'generate_jd': { label: 'Generating JD', color: 'bg-blue-500/20 text-blue-400' },
        'await_jd_approval': { label: 'Awaiting Approval', color: 'bg-amber-500/20 text-amber-400' },
        'post_job': { label: 'Posting Job', color: 'bg-purple-500/20 text-purple-400' },
        'monitor_applications': { label: 'Monitoring', color: 'bg-cyan-500/20 text-cyan-400' },
        'shortlist_candidates': { label: 'Shortlisting', color: 'bg-indigo-500/20 text-indigo-400' },
    };
    return statusMap[currentNode] || { label: currentNode.replace(/_/g, ' '), color: 'bg-gray-500/20 text-gray-400' };
}

export default function DashboardPage() {
    const { jobs, total, loading } = useJobs();

    // Calculate real stats from jobs data
    const activeJobs = total;
    const recentJobs = jobs.slice(0, 5); // Show top 5 recent jobs

    const stats = [
        { name: 'Active Jobs', value: loading ? '...' : activeJobs.toString(), icon: Briefcase, color: 'text-blue-400', bg: 'bg-blue-400/10' },
        { name: 'Total Candidates', value: '—', icon: Users, color: 'text-purple-400', bg: 'bg-purple-400/10' },
        { name: 'Interviews Scheduled', value: '—', icon: Clock, color: 'text-amber-400', bg: 'bg-amber-400/10' },
        { name: 'Hires This Month', value: '—', icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-400/10' },
    ];

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-3xl font-bold tracking-tight text-foreground">Overview</h2>
                <p className="text-muted-foreground">Welcome back to your recruitment command center.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat, i) => (
                    <motion.div
                        key={stat.name}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="glass-card p-6"
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-muted-foreground">{stat.name}</p>
                                <div className="mt-2 text-3xl font-bold text-foreground">{stat.value}</div>
                            </div>
                            <div className={`rounded-xl p-3 ${stat.bg}`}>
                                <stat.icon className={`h-6 w-6 ${stat.color}`} />
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Recent Jobs Section */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <div className="glass-card p-6 col-span-4">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-foreground">Recent Jobs</h3>
                        <Link
                            href="/jobs"
                            className="text-sm text-primary hover:underline flex items-center gap-1"
                        >
                            View all <ArrowRight className="h-3 w-3" />
                        </Link>
                    </div>

                    {loading ? (
                        <div className="h-[200px] flex items-center justify-center">
                            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                    ) : recentJobs.length === 0 ? (
                        <div className="h-[200px] flex flex-col items-center justify-center text-muted-foreground border border-dashed border-border rounded-lg">
                            <Briefcase className="h-8 w-8 mb-2 opacity-50" />
                            <p>No jobs yet</p>
                            <Link href="/jobs/new" className="text-sm text-primary hover:underline mt-2">
                                Create your first job
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {recentJobs.map((job) => {
                                const status = getStatusBadge(job.current_node);
                                return (
                                    <Link
                                        key={job.job_id}
                                        href={`/jobs/${job.job_id}`}
                                        className="flex items-center justify-between p-3 rounded-lg bg-muted/50 border border-border hover:border-primary/30 transition-colors"
                                    >
                                        <div className="min-w-0 flex-1">
                                            <p className="text-sm font-medium text-foreground truncate">{job.role_title}</p>
                                            <p className="text-xs text-muted-foreground truncate">{job.company_name}</p>
                                        </div>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                                            {status.label}
                                        </span>
                                    </Link>
                                );
                            })}
                        </div>
                    )}
                </div>

                <div className="glass-card p-6 col-span-3">
                    <h3 className="text-lg font-medium text-foreground mb-4">Upcoming Interviews</h3>
                    <div className="h-[200px] flex flex-col items-center justify-center text-muted-foreground border border-dashed border-border rounded-lg">
                        <Clock className="h-8 w-8 mb-2 opacity-50" />
                        <p className="text-sm">No interviews scheduled</p>
                        <p className="text-xs mt-1">Coming soon</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
