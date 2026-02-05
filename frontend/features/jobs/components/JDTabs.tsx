'use client';

import { motion, AnimatePresence } from 'framer-motion';
import {
    FileText,
    Target,
    Award,
    Briefcase,
    CheckCircle,
    Sparkles,
} from 'lucide-react';
import type { GeneratedJD } from '@/types';

type TabType = 'overview' | 'requirements' | 'benefits';

interface JDTabsProps {
    jd: GeneratedJD;
    activeTab: TabType;
    onTabChange: (tab: TabType) => void;
}

const TABS = [
    { id: 'overview' as const, label: 'Overview', icon: FileText },
    { id: 'requirements' as const, label: 'Requirements', icon: Target },
    { id: 'benefits' as const, label: 'Benefits', icon: Award },
];

export default function JDTabs({ jd, activeTab, onTabChange }: JDTabsProps) {
    return (
        <>
            {/* Tab Navigation */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="flex gap-1 p-1 bg-muted/50 rounded-xl w-fit"
            >
                {TABS.map((tab) => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25'
                                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                                }`}
                        >
                            <Icon className="h-4 w-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </motion.div>

            {/* Tab Content */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="glass-card p-8"
                >
                    {activeTab === 'overview' && <OverviewTab jd={jd} />}
                    {activeTab === 'requirements' && <RequirementsTab jd={jd} />}
                    {activeTab === 'benefits' && <BenefitsTab jd={jd} />}
                </motion.div>
            </AnimatePresence>
        </>
    );
}

function OverviewTab({ jd }: { jd: GeneratedJD }) {
    return (
        <div className="space-y-8">
            <section>
                <SectionHeader icon={FileText} title="Professional Summary" color="blue" />
                <p className="text-muted-foreground leading-relaxed text-lg">{jd.summary}</p>
            </section>

            <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent" />

            <section>
                <SectionHeader icon={Briefcase} title="Key Responsibilities" color="purple" />
                <AnimatedList items={jd.responsibilities} />
            </section>
        </div>
    );
}

function RequirementsTab({ jd }: { jd: GeneratedJD }) {
    return (
        <div className="space-y-8">
            <section>
                <SectionHeader icon={Target} title="Must-Have Requirements" color="red" />
                <ul className="grid gap-3">
                    {jd.requirements.map((item, i) => (
                        <motion.li
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.05 }}
                            className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border/50 text-foreground"
                        >
                            <CheckCircle className="mt-0.5 h-5 w-5 text-red-500 flex-shrink-0" />
                            <span>{item}</span>
                        </motion.li>
                    ))}
                </ul>
            </section>

            {jd.nice_to_have.length > 0 && (
                <>
                    <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent" />
                    <section>
                        <SectionHeader icon={Sparkles} title="Nice to Have" color="amber" />
                        <AnimatedList items={jd.nice_to_have} dotColor="bg-amber-500" />
                    </section>
                </>
            )}
        </div>
    );
}

function BenefitsTab({ jd }: { jd: GeneratedJD }) {
    return (
        <div className="space-y-6">
            <SectionHeader icon={Award} title="What We Offer" color="green" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {jd.benefits.map((item, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.05 }}
                        className="flex items-center gap-3 p-4 rounded-xl bg-gradient-to-br from-muted/50 to-muted/30 border border-border/50 hover:border-green-500/30 transition-colors"
                    >
                        <div className="p-2 rounded-lg bg-green-500/10">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                        </div>
                        <span className="text-foreground">{item}</span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

// Helper Components
function SectionHeader({
    icon: Icon,
    title,
    color
}: {
    icon: typeof FileText;
    title: string;
    color: 'blue' | 'purple' | 'red' | 'amber' | 'green';
}) {
    const colors = {
        blue: 'bg-blue-500/10 text-blue-400',
        purple: 'bg-purple-500/10 text-purple-400',
        red: 'bg-red-500/10 text-red-400',
        amber: 'bg-amber-500/10 text-amber-400',
        green: 'bg-green-500/10 text-green-400',
    };

    return (
        <div className="flex items-center gap-2 mb-4">
            <div className={`p-2 rounded-lg ${colors[color].split(' ')[0]}`}>
                <Icon className={`h-5 w-5 ${colors[color].split(' ')[1]}`} />
            </div>
            <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        </div>
    );
}

function AnimatedList({
    items,
    dotColor = 'bg-gradient-to-r from-blue-500 to-purple-500'
}: {
    items: string[];
    dotColor?: string;
}) {
    return (
        <ul className="grid gap-3">
            {items.map((item, i) => (
                <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-start gap-3 p-3 rounded-lg bg-muted/30 border border-border/50 text-foreground"
                >
                    <span className={`mt-1.5 h-2 w-2 rounded-full ${dotColor} flex-shrink-0`} />
                    <span>{item}</span>
                </motion.li>
            ))}
        </ul>
    );
}
