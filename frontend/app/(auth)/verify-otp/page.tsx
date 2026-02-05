'use client';

import { Suspense, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { AlertCircle, CheckCircle } from 'lucide-react';

function VerifyForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const emailParam = searchParams.get('email') || '';
    const otpParam = searchParams.get('demo_otp') || '';

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData(e.currentTarget);
        const email = formData.get('email') as string;
        const otp = formData.get('otp') as string;

        try {
            await api.post('/auth/verify-otp', { email, otp });
            setSuccess('Account verified successfully! Redirecting to login...');

            setTimeout(() => {
                router.push('/login');
            }, 2000);

        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || 'Verification failed. Invalid OTP.');
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-8 space-y-6"
        >
            <div className="space-y-2 text-center">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-600">
                    Verify Account
                </h1>
                <p className="text-slate-400">Enter the OTP sent to your email</p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    <span>{error}</span>
                </div>
            )}

            {success && (
                <div className="bg-green-500/10 border border-green-500/20 text-green-400 p-3 rounded-lg text-sm flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>{success}</span>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Email</label>
                    <Input
                        name="email"
                        type="email"
                        defaultValue={emailParam}
                        placeholder="you@example.com"
                        required
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">OTP Code</label>
                    <Input
                        name="otp"
                        type="text"
                        placeholder="123456"
                        required
                        maxLength={6}
                        className="tracking-widest text-center text-lg"
                    />
                </div>

                <Button type="submit" className="w-full" isLoading={isLoading}>
                    Verify & Activate
                </Button>
            </form>

            <div className="text-center text-sm text-slate-400">
                <Link href="/login" className="text-slate-400 hover:text-white">
                    Back to Login
                </Link>
            </div>
        </motion.div>
    );
}

export default function VerifyOtpPage() {
    return (
        <Suspense fallback={<div className="text-white">Loading...</div>}>
            <VerifyForm />
        </Suspense>
    );
}
