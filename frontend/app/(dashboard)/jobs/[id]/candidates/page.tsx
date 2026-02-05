"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { CandidatesTable } from "@/components/candidates/CandidatesTable";
import { motion } from "framer-motion";
import { Users, Filter } from "lucide-react";
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

export default function CandidatesPage() {
    const params = useParams();
    const [candidates, setCandidates] = useState<Applicant[]>([]);
    const [isLoading, setIsLoading] = useState(true);

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
                    <Button variant="outline" size="sm">
                        <Filter className="mr-2 h-4 w-4" />
                        Filter
                    </Button>
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-6"
            >
                {isLoading ? (
                    <div className="text-center py-10 text-muted-foreground">Loading candidates...</div>
                ) : (
                    <CandidatesTable candidates={candidates} />
                )}
            </motion.div>
        </div>
    );
}
