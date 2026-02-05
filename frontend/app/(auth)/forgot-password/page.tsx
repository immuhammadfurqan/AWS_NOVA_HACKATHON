'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { AtSign, ArrowLeft, Shield, Radar, KeyRound, Send } from 'lucide-react';
import {
    AuthLayout,
    AarlpLogo,
    AuthInput,
    AuthButton,
} from '@/features/auth/components/AuthLayout';

// Left Panel Content for Forgot Password Page
function ForgotPasswordLeftPanel() {
    return (
        <div className="flex flex-col justify-center h-full p-12 lg:p-16 xl:p-24 relative">
            {/* Decorative Line */}
            <div className="w-16 h-1 bg-[#25aff4] mb-8 rounded-full"></div>

            <h1 className="text-4xl lg:text-5xl xl:text-6xl font-bold leading-[1.1] mb-6 tracking-tight">
                Securing the <br /><span className="text-[#25aff4]">Next Frontier.</span>
            </h1>

            <p className="text-slate-400 text-lg max-w-md leading-relaxed">
                Recruitment gateway for verified AARLP personnel. Our proprietary multi-factor protocols ensure zero-trust integrity across all terminal access points.
            </p>

            {/* Security Icons */}
            <div className="mt-12 flex items-center gap-6">
                <div className="flex -space-x-3">
                    <div className="w-10 h-10 rounded-full border-2 border-[#101c22] bg-[#182b34] flex items-center justify-center overflow-hidden">
                        <Shield className="size-4 text-[#25aff4]" />
                    </div>
                    <div className="w-10 h-10 rounded-full border-2 border-[#101c22] bg-[#182b34] flex items-center justify-center overflow-hidden">
                        <Radar className="size-4 text-[#25aff4]" />
                    </div>
                    <div className="w-10 h-10 rounded-full border-2 border-[#101c22] bg-[#182b34] flex items-center justify-center overflow-hidden">
                        <KeyRound className="size-4 text-[#25aff4]" />
                    </div>
                </div>
                <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest leading-none">
                    Security Level: Class-A Recruitment
                </p>
            </div>
        </div>
    );
}

// Header Right Content
function HeaderRightContent() {
    return (
        <button className="text-sm font-medium text-slate-400 hover:text-white transition-colors">
            System Status
        </button>
    );
}

export default function ForgotPasswordPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        const formData = new FormData(e.currentTarget);
        const email = formData.get('email') as string;

        try {
            const response = await api.post('/auth/forgot-password', { email });
            const demoOtp = response.data.otp;
            router.push(`/reset-password?email=${encodeURIComponent(email)}${demoOtp ? `&demo_otp=${demoOtp}` : ''}`);

        } catch (err: unknown) {
            console.error(err);
            const errorObj = err as { response?: { data?: { detail?: string } } };
            setError(errorObj.response?.data?.detail || 'Failed to request password reset.');
        } finally {
            setIsLoading(false);
        }
    };

    const formContent = (
        <>
            <div className="auth-glass-card rounded-xl p-8 lg:p-12 shadow-2xl">
                <div className="space-y-8">
                    <div className="space-y-2">
                        <h2 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">Reset Password</h2>
                        <p className="text-slate-400 text-sm">
                            Enter your recruiter email to receive a temporary 6-digit OTP code.
                        </p>
                    </div>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm"
                        >
                            {error}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="flex flex-col gap-2">
                            <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 ml-1">
                                Corporate Email
                            </label>
                            <AuthInput
                                name="email"
                                type="email"
                                placeholder="recruiter@aarlp.ai"
                                required
                                icon={<AtSign className="size-5" />}
                            />
                        </div>

                        <AuthButton type="submit" isLoading={isLoading}>
                            <span>Send OTP Code</span>
                            <Send className="size-5" />
                        </AuthButton>
                    </form>

                    <div className="pt-6 border-t border-[#315668]/30">
                        <Link
                            href="/login"
                            className="text-sm font-medium text-slate-400 hover:text-white flex items-center justify-center lg:justify-start gap-2 transition-colors"
                        >
                            <ArrowLeft className="size-4" />
                            Return to Login Portal
                        </Link>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-8 text-center">
                <p className="text-slate-600 text-[10px] tracking-[0.2em] uppercase font-bold">
                    © 2024 AARLP SYSTEMS • SECURE RECRUITMENT NODES
                </p>
            </div>
        </>
    );

    return (
        <AuthLayout
            leftPanel={<ForgotPasswordLeftPanel />}
            showHeader={true}
            headerRightContent={<HeaderRightContent />}
        >
            {formContent}
        </AuthLayout>
    );
}
