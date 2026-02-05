"use client";

import { motion } from "framer-motion";
import { CheckCircle, XCircle, MoreHorizontal, FileText } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface Applicant {
    id: string;
    name: string;
    email: string;
    similarity_score: number;
    shortlisted: boolean;
    applied_at: string;
}

interface CandidatesTableProps {
    candidates: Applicant[];
}

export function CandidatesTable({ candidates }: CandidatesTableProps) {
    if (candidates.length === 0) {
        return (
            <div className="text-center py-10 text-muted-foreground">
                No candidates found for this job yet.
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
                <thead className="border-b border-border text-muted-foreground">
                    <tr>
                        <th className="px-4 py-3 font-medium">Name</th>
                        <th className="px-4 py-3 font-medium">Match Score</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                        <th className="px-4 py-3 font-medium">Applied Date</th>
                        <th className="px-4 py-3 font-medium text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-border">
                    {candidates.map((candidate, i) => (
                        <motion.tr
                            key={candidate.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: i * 0.05 }}
                            className="hover:bg-muted/50 transition-colors"
                        >
                            <td className="px-4 py-3">
                                <div className="font-medium text-foreground">{candidate.name}</div>
                                <div className="text-xs text-muted-foreground">{candidate.email}</div>
                            </td>
                            <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <div className="h-2 w-24 rounded-full bg-secondary overflow-hidden">
                                        <div
                                            className={`h-full rounded-full ${candidate.similarity_score >= 80
                                                ? "bg-green-500"
                                                : candidate.similarity_score >= 50
                                                    ? "bg-amber-500"
                                                    : "bg-red-500"
                                                }`}
                                            style={{ width: `${candidate.similarity_score}%` }}
                                        />
                                    </div>
                                    <span className="text-xs font-medium text-foreground">
                                        {candidate.similarity_score}%
                                    </span>
                                </div>
                            </td>
                            <td className="px-4 py-3">
                                {candidate.shortlisted ? (
                                    <span className="inline-flex items-center gap-1 rounded-full bg-green-500/10 px-2 py-0.5 text-xs font-medium text-green-500">
                                        <CheckCircle className="h-3 w-3" /> Shortlisted
                                    </span>
                                ) : (
                                    <span className="inline-flex items-center gap-1 rounded-full bg-slate-500/10 px-2 py-0.5 text-xs font-medium text-muted-foreground">
                                        Applied
                                    </span>
                                )}
                            </td>
                            <td className="px-4 py-3 text-muted-foreground">
                                {new Date(candidate.applied_at).toLocaleDateString()}
                            </td>
                            <td className="px-4 py-3 text-right">
                                <Button variant="ghost" size="icon" aria-label="More actions">
                                    <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
                                </Button>
                            </td>
                        </motion.tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
