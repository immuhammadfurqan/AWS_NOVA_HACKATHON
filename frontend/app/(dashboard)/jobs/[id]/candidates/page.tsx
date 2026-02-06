"use client";

import { useEffect, useState, useMemo } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { CandidatesTable } from "@/components/candidates/CandidatesTable";
import { motion } from "framer-motion";
import { Users, ArrowUpDown, Filter, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface Applicant {
    id: string;
    name: string;
    email: string;
    phone: string;
    resume_path: string;
    similarity_score: number;
    shortlisted: boolean;
    applied_at: string;
}

type SortOption = "score_desc" | "score_asc" | "date_desc" | "date_asc";
type FilterOption = "all" | "shortlisted" | "high_match" | "medium_match" | "low_match";

const sortLabels: Record<SortOption, string> = {
    score_desc: "Highest Match First",
    score_asc: "Lowest Match First",
    date_desc: "Newest First",
    date_asc: "Oldest First",
};

const filterLabels: Record<FilterOption, string> = {
    all: "All Candidates",
    shortlisted: "Shortlisted Only",
    high_match: "High Match (80%+)",
    medium_match: "Medium Match (50-79%)",
    low_match: "Low Match (<50%)",
};

export default function CandidatesPage() {
    const params = useParams();
    const [candidates, setCandidates] = useState<Applicant[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [sortBy, setSortBy] = useState<SortOption>("score_desc");
    const [filterBy, setFilterBy] = useState<FilterOption>("all");
    const [showSortMenu, setShowSortMenu] = useState(false);
    const [showFilterMenu, setShowFilterMenu] = useState(false);

    useEffect(() => {
        if (params.id) {
            loadCandidates(params.id as string);
        }
    }, [params.id]);

    async function loadCandidates(jobId: string) {
        try {
            const res = await api.get(`/jobs/${jobId}/applicants`);
            setCandidates(res.data.applicants || []);
        } catch (error) {
            console.error("Failed to load candidates", error);
        } finally {
            setIsLoading(false);
        }
    }

    // Apply filtering and sorting
    const processedCandidates = useMemo(() => {
        let result = [...candidates];

        // Apply filter
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
        }

        return result;
    }, [candidates, sortBy, filterBy]);

    const stats = useMemo(() => ({
        total: candidates.length,
        shortlisted: candidates.filter(c => c.shortlisted).length,
        highMatch: candidates.filter(c => c.similarity_score >= 80).length,
        avgScore: candidates.length > 0
            ? Math.round(candidates.reduce((sum, c) => sum + (c.similarity_score || 0), 0) / candidates.length)
            : 0,
    }), [candidates]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
                        <Users className="text-primary" />
                        Candidates
                    </h2>
                    <p className="text-muted-foreground">
                        Review and shortlist applicants based on AI matching.
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    {/* Sort Dropdown */}
                    <div className="relative">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => { setShowSortMenu(!showSortMenu); setShowFilterMenu(false); }}
                        >
                            <ArrowUpDown className="mr-2 h-4 w-4" />
                            {sortLabels[sortBy]}
                            <ChevronDown className="ml-2 h-3 w-3" />
                        </Button>
                        {showSortMenu && (
                            <div className="absolute right-0 mt-1 w-48 py-1 glass-card rounded-lg shadow-lg z-10">
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
                            onClick={() => { setShowFilterMenu(!showFilterMenu); setShowSortMenu(false); }}
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
                        <div className="text-xs text-muted-foreground">Total Applicants</div>
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

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-6"
            >
                {isLoading ? (
                    <div className="text-center py-10 text-muted-foreground">Loading candidates...</div>
                ) : (
                    <>
                        {filterBy !== "all" && (
                            <div className="mb-4 text-sm text-muted-foreground">
                                Showing {processedCandidates.length} of {candidates.length} candidates
                            </div>
                        )}
                        <CandidatesTable candidates={processedCandidates} />
                    </>
                )}
            </motion.div>
        </div>
    );
}

