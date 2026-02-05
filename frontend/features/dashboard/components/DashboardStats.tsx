'use client';

import { motion } from 'framer-motion';
import {
    Users,
    Briefcase,
    CheckCircle,
    Clock
} from 'lucide-react';

const stats = [
    { name: 'Active Jobs', value: '12', icon: Briefcase, color: 'text-blue-400', bg: 'bg-blue-400/10' },
    { name: 'Total Candidates', value: '1,234', icon: Users, color: 'text-purple-400', bg: 'bg-purple-400/10' },
    { name: 'Interviews Scheduled', value: '45', icon: Clock, color: 'text-amber-400', bg: 'bg-amber-400/10' },
    { name: 'Hires This Month', value: '8', icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-400/10' },
];

export default function DashboardStats() {
    return (
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
                    <div className="mt-4 flex items-center gap-1 text-xs text-muted-foreground">
                        <span className="text-green-500 font-medium">+12%</span>
                        <span>from last month</span>
                    </div>
                </motion.div>
            ))}
        </div>
    );
}
