"use client";

import { useEffect, useState, useMemo } from "react";
import { api } from "@/lib/api";
import { motion } from "framer-motion";
import { Users, ArrowUpDown, Filter, ChevronDown, Briefcase, Clock, Mail } from "lucide-react";
import { Button } from "@/components/ui/Button";
import Link from "next/link";

interface Candidate {
    id: string;
    name: string;
    email: string;
    phone: string | null;
    resume_path: string | null;
    similarity_score: number;
    shortlisted: boolean;
    applied_at: string;
    job_id: string;
    job_title: string;
}

type SortOption = "score_desc" | "score_asc" | "date_desc" | "date_asc" | "name_asc";
type FilterOption = "all" | "shortlisted" | "high_match" | "medium_match" | "low_match";

const sortLabels: Record<SortOption, string> = {
    score_desc: "Highest Match",
    score_asc: "Lowest Match",
    date_desc: "Newest First",
    date_asc: "Oldest First",
    name_asc: "Name (A-Z)",
};

const filterLabels: Record<FilterOption, string> = {
    all: "All Candidates",
    shortlisted: "Shortlisted",
    high_match: "High Match (80%+)",
    medium_match: "Medium (50-79%)",
    low_match: "Low Match (<50%)",
};

function getScoreColor(score: number): string {
    if (score >= 80) return "text-green-500";
    if (score >= 50) return "text-amber-500";
    return "text-red-500";
}

function getScoreBgColor(score: number): string {
    if (score >= 80) return "bg-green-500";
    if (score >= 50) return "bg-amber-500";
    return "bg-red-500";
}

export default function CandidatesPage() {
    const [candidates, setCandidates] = useState<Candidate[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [sortBy, setSortBy] = useState<SortOption>("date_desc");
    const [filterBy, setFilterBy] = useState<FilterOption>("all");
    const [jobFilter, setJobFilter] = useState<string>("all");
    const [showSortMenu, setShowSortMenu] = useState(false);
    const [showFilterMenu, setShowFilterMenu] = useState(false);
    const [showJobMenu, setShowJobMenu] = useState(false);

    useEffect(() => {
        loadCandidates();
    }, []);

    async function loadCandidates() {
        try {
            const res = await api.get("/candidates");
            setCandidates(res.data.candidates || []);
        } catch (error) {
            console.error("Failed to load candidates", error);
        } finally {
            setIsLoading(false);
        }
    }

    // Get unique jobs for job filter
    const uniqueJobs = useMemo(() => {
        const jobs = new Map<string, string>();
        candidates.forEach(c => {
            if (!jobs.has(c.job_id)) {
                jobs.set(c.job_id, c.job_title);
            }
        });
        return Array.from(jobs.entries());
    }, [candidates]);

    // Apply filtering and sorting
    const processedCandidates = useMemo(() => {
        let result = [...candidates];

        // Apply job filter
        if (jobFilter !== "all") {
            result = result.filter(c => c.job_id === jobFilter);
        }

        // Apply match filter
        switch (filterBy) {
            case "shortlisted":
                result = result.filter(c => c.shortlisted);
                break;
            case "high_match":
                result = result.filter(c => c.similarity_score >= 80);
                break;
            case "medium_match":
                result = result.filter(c => c.similarity_score >= 50 && c.similarity_score < 80);
                break;
            case "low_match":
                result = result.filter(c => c.similarity_score < 50);
                break;
        }

        // Apply sort
        switch (sortBy) {
            case "score_desc":
                result.sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0));
                break;
            case "score_asc":
                result.sort((a, b) => (a.similarity_score || 0) - (b.similarity_score || 0));
                break;
            case "date_desc":
                result.sort((a, b) => new Date(b.applied_at).getTime() - new Date(a.applied_at).getTime());
                break;
            case "date_asc":
                result.sort((a, b) => new Date(a.applied_at).getTime() - new Date(b.applied_at).getTime());
                break;
            case "name_asc":
                result.sort((a, b) => a.name.localeCompare(b.name));
                break;
        }

        return result;
    }, [candidates, sortBy, filterBy, jobFilter]);

    const stats = useMemo(() => ({
        total: candidates.length,
        shortlisted: candidates.filter(c => c.shortlisted).length,
        highMatch: candidates.filter(c => c.similarity_score >= 80).length,
        avgScore: candidates.length > 0
            ? Math.round(candidates.reduce((sum, c) => sum + (c.similarity_score || 0), 0) / candidates.length)
            : 0,
    }), [candidates]);

    const closeAllMenus = () => {
        setShowSortMenu(false);
        setShowFilterMenu(false);
        setShowJobMenu(false);
    };

    return (
        <div className="space-y-6" onClick={() => closeAllMenus()}>
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
                        <Users className="text-primary" />
                        All Candidates
                    </h2>
                    <p className="text-muted-foreground">
                        View and manage all candidates across all job postings.
                    </p>
                </div>
                <div className="flex flex-wrap items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    {/* Job Filter */}
                    <div className="relative">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => { setShowJobMenu(!showJobMenu); setShowSortMenu(false); setShowFilterMenu(false); }}
                        >
                            <Briefcase className="mr-2 h-4 w-4" />
                            {jobFilter === "all" ? "All Jobs" : uniqueJobs.find(j => j[0] === jobFilter)?.[1]?.substring(0, 15) + "..."}
                            <ChevronDown className="ml-2 h-3 w-3" />
                        </Button>
                        {showJobMenu && (
                            <div className="absolute right-0 mt-1 w-56 py-1 glass-card rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
                                <button
                                    onClick={() => { setJobFilter("all"); setShowJobMenu(false); }}
                                    className={`w-full px-4 py-2 text-left text-sm hover:bg-muted/50 transition-colors ${jobFilter === "all" ? "text-primary font-medium" : "text-foreground"
                                        }`}
                                >
                                    All Jobs
                                </button>
                                {uniqueJobs.map(([id, title]) => (
                                    <button
                                        key={id}
                                        onClick={() => { setJobFilter(id); setShowJobMenu(false); }}
                                        className={`w-full px-4 py-2 text-left text-sm hover:bg-muted/50 transition-colors truncate ${jobFilter === id ? "text-primary font-medium" : "text-foreground"
                                            }`}
                                    >
                                        {title}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Sort Dropdown */}
                    <div className="relative">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => { setShowSortMenu(!showSortMenu); setShowFilterMenu(false); setShowJobMenu(false); }}
                        >
                            <ArrowUpDown className="mr-2 h-4 w-4" />
                            {sortLabels[sortBy]}
                            <ChevronDown className="ml-2 h-3 w-3" />
                        </Button>
                        {showSortMenu && (
                            <div className="absolute right-0 mt-1 w-44 py-1 glass-card rounded-lg shadow-lg z-10">
                                {(Object.keys(sortLabels) as SortOption[]).map(option => (
                                    <button
                                        key={option}
                                        onClick={() => { setSortBy(option); setShowSortMenu(false); }}
                                        className={`w-full px-4 py-2 text-left text-sm hover:bg-muted/50 transition-colors ${sortBy === option ? "text-primary font-medium" : "text-foreground"
                                            }`}
                                    >
                                        {sortLabels[option]}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Filter Dropdown */}
                    <div className="relative">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => { setShowFilterMenu(!showFilterMenu); setShowSortMenu(false); setShowJobMenu(false); }}
                        >
                            <Filter className="mr-2 h-4 w-4" />
                            {filterLabels[filterBy]}
                            <ChevronDown className="ml-2 h-3 w-3" />
                        </Button>
                        {showFilterMenu && (
                            <div className="absolute right-0 mt-1 w-48 py-1 glass-card rounded-lg shadow-lg z-10">
                                {(Object.keys(filterLabels) as FilterOption[]).map(option => (
                                    <button
                                        key={option}
                                        onClick={() => { setFilterBy(option); setShowFilterMenu(false); }}
                                        className={`w-full px-4 py-2 text-left text-sm hover:bg-muted/50 transition-colors ${filterBy === option ? "text-primary font-medium" : "text-foreground"
                                            }`}
                                    >
                                        {filterLabels[option]}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Stats Cards */}
            {!isLoading && candidates.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="glass-card p-4 text-center">
                        <div className="text-2xl font-bold text-foreground">{stats.total}</div>
                        <div className="text-xs text-muted-foreground">Total Candidates</div>
                    </div>
                    <div className="glass-card p-4 text-center">
                        <div className="text-2xl font-bold text-green-500">{stats.highMatch}</div>
                        <div className="text-xs text-muted-foreground">High Match (80%+)</div>
                    </div>
                    <div className="glass-card p-4 text-center">
                        <div className="text-2xl font-bold text-primary">{stats.shortlisted}</div>
                        <div className="text-xs text-muted-foreground">Shortlisted</div>
                    </div>
                    <div className="glass-card p-4 text-center">
                        <div className="text-2xl font-bold text-foreground">{stats.avgScore}%</div>
                        <div className="text-xs text-muted-foreground">Avg Match Score</div>
                    </div>
                </div>
            )}

            {/* Candidates List */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-6"
            >
                {isLoading ? (
                    <div className="text-center py-10 text-muted-foreground">Loading candidates...</div>
                ) : processedCandidates.length === 0 ? (
                    <div className="text-center py-10 text-muted-foreground">
                        {candidates.length === 0
                            ? "No candidates have applied yet."
                            : "No candidates match the current filters."}
                    </div>
                ) : (
                    <>
                        {(filterBy !== "all" || jobFilter !== "all") && (
                            <div className="mb-4 text-sm text-muted-foreground">
                                Showing {processedCandidates.length} of {candidates.length} candidates
                            </div>
                        )}
                        <div className="space-y-3">
                            {processedCandidates.map((candidate, i) => (
                                <motion.div
                                    key={candidate.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.03 }}
                                    className="flex flex-col md:flex-row md:items-center justify-between p-4 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors gap-4"
                                >
                                    {/* Candidate Info */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-3">
                                            <div className="flex-1 min-w-0">
                                                <div className="font-medium text-foreground truncate">
                                                    {candidate.name}
                                                </div>
                                                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                                    <span className="flex items-center gap-1 truncate">
                                                        <Briefcase className="h-3 w-3 flex-shrink-0" />
                                                        {candidate.job_title}
                                                    </span>
                                                    <span className="flex items-center gap-1 truncate">
                                                        <Mail className="h-3 w-3 flex-shrink-0" />
                                                        {candidate.email}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Match Score */}
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-2 w-32">
                                            <div className="h-2 flex-1 rounded-full bg-secondary overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full ${getScoreBgColor(candidate.similarity_score)}`}
                                                    style={{ width: `${candidate.similarity_score}%` }}
                                                />
                                            </div>
                                            <span className={`text-sm font-medium min-w-[40px] text-right ${getScoreColor(candidate.similarity_score)}`}>
                                                {Math.round(candidate.similarity_score)}%
                                            </span>
                                        </div>

                                        {/* Status Badge */}
                                        {candidate.shortlisted ? (
                                            <span className="inline-flex items-center rounded-full bg-green-500/10 px-2 py-0.5 text-xs font-medium text-green-500">
                                                Shortlisted
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center rounded-full bg-slate-500/10 px-2 py-0.5 text-xs font-medium text-muted-foreground">
                                                Applied
                                            </span>
                                        )}

                                        {/* Date */}
                                        <div className="hidden md:flex items-center gap-1 text-xs text-muted-foreground min-w-[80px]">
                                            <Clock className="h-3 w-3" />
                                            {new Date(candidate.applied_at).toLocaleDateString()}
                                        </div>

                                        {/* View Link */}
                                        <Link
                                            href={`/jobs/${candidate.job_id}/candidates`}
                                            className="text-sm text-primary hover:underline"
                                        >
                                            View
                                        </Link>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </>
                )}
            </motion.div>
        </div>
    );
}
