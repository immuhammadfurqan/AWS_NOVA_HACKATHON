'use client';

import { Suspense, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { ArrowLeft, CheckCircle, Shield, Radar, KeyRound, ShieldCheck } from 'lucide-react';
import {
    AuthLayout,
    AuthInput,
    AuthButton,
} from '@/features/auth/components/AuthLayout';

// OTP Input Component
function OtpInput({
    value,
    onChange
}: {
    value: string[];
    onChange: (value: string[]) => void;
}) {
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    const handleChange = (index: number, val: string) => {
        if (val.length > 1) val = val[0];
        if (!/^\d*$/.test(val)) return;

        const newOtp = [...value];
        newOtp[index] = val;
        onChange(newOtp);

        // Auto-focus next input
        if (val && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
        if (e.key === 'Backspace' && !value[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handlePaste = (e: React.ClipboardEvent) => {
        e.preventDefault();
        const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        const newOtp = pasted.split('').concat(Array(6 - pasted.length).fill(''));
        onChange(newOtp);
        inputRefs.current[Math.min(pasted.length, 5)]?.focus();
    };

    return (
        <div className="flex justify-between gap-2 sm:gap-3">
            {[0, 1, 2, 3, 4, 5].map((index) => (
                <input
                    key={index}
                    ref={(el) => { inputRefs.current[index] = el; }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={value[index]}
                    onChange={(e) => handleChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    onPaste={handlePaste}
                    className="w-full h-14 text-center text-xl font-bold bg-[#182b34] border border-[#315668] rounded-lg text-white focus:border-[#25aff4] focus:ring-1 focus:ring-[#25aff4]/30 focus:shadow-[0_0_15px_rgba(37,175,244,0.4)] outline-none transition-all"
                />
            ))}
        </div>
    );
}

// Left Panel Content
function ResetPasswordLeftPanel() {
    return (
        <div className="flex flex-col justify-center h-full p-12 lg:p-16 xl:p-24 relative">
            {/* Decorative Line */}
            <div className="w-16 h-1 bg-[#25aff4] mb-8 rounded-full"></div>

            <h1 className="text-4xl lg:text-5xl xl:text-6xl font-bold leading-[1.1] mb-6 tracking-tight">
                Securing the <br /><span className="text-[#25aff4]">Next Frontier.</span>
            </h1>

            <p className="text-slate-400 text-lg max-w-md leading-relaxed">
                Enter the verification code sent to your email and set a new secure password for your recruiter account.
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

function ResetForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [otp, setOtp] = useState(['', '', '', '', '', '']);

    const emailParam = searchParams.get('email') || '';
    const demoOtp = searchParams.get('demo_otp') || '';

    async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData(e.currentTarget);
        const email = formData.get('email') as string;
        const new_password = formData.get('new_password') as string;
        const otpValue = otp.join('');

        if (otpValue.length !== 6) {
            setError('Please enter a complete 6-digit OTP code.');
            setIsLoading(false);
            return;
        }

        try {
            await api.post('/auth/reset-password', {
                email,
                otp: otpValue,
                new_password
            });

            setSuccess('Password reset successfully! Redirecting to login...');
            setTimeout(() => {
                router.push('/login');
            }, 2000);

        } catch (err: unknown) {
            console.error(err);
            const errorObj = err as { response?: { data?: { detail?: string } } };
            setError(errorObj.response?.data?.detail || 'Failed to reset password.');
        } finally {
            setIsLoading(false);
        }
    }

    const formContent = (
        <>
            <div className="auth-glass-card rounded-xl p-8 lg:p-12 shadow-2xl">
                <div className="space-y-8">
                    <div className="space-y-2">
                        {!success && (
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#25aff4]/10 border border-[#25aff4]/20 text-[#25aff4] text-[10px] font-bold uppercase tracking-widest mb-2">
                                <span className="flex h-2 w-2 rounded-full bg-[#25aff4] animate-pulse"></span>
                                Verification Pending
                            </div>
                        )}
                        <h2 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">
                            {success ? 'Password Reset Complete' : 'Enter Verification Code'}
                        </h2>
                        <p className="text-slate-400 text-sm">
                            {success
                                ? 'Your password has been updated successfully.'
                                : 'Enter the 6-digit code sent to your email and create a new password.'}
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

                    {success && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="bg-green-500/10 border border-green-500/20 text-green-400 p-4 rounded-lg flex items-center gap-3"
                        >
                            <CheckCircle className="size-5" />
                            <span>{success}</span>
                        </motion.div>
                    )}

                    {demoOtp && !success && (
                        <div className="bg-blue-500/10 border border-blue-500/20 text-blue-400 p-3 rounded-lg text-xs text-center">
                            <span className="font-bold">Demo OTP:</span> {demoOtp}
                        </div>
                    )}

                    {!success && (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <input type="hidden" name="email" value={emailParam} />

                            <div className="space-y-2">
                                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 ml-1">
                                    OTP Code
                                </label>
                                <OtpInput value={otp} onChange={setOtp} />
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 ml-1">
                                    New Password
                                </label>
                                <AuthInput
                                    name="new_password"
                                    type="password"
                                    placeholder="••••••••••••"
                                    required
                                    minLength={8}
                                    icon={<KeyRound className="size-5" />}
                                />
                            </div>

                            <AuthButton type="submit" isLoading={isLoading}>
                                <span>Reset Password</span>
                                <ShieldCheck className="size-5" />
                            </AuthButton>
                        </form>
                    )}

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
            leftPanel={<ResetPasswordLeftPanel />}
            showHeader={true}
            headerRightContent={<HeaderRightContent />}
        >
            {formContent}
        </AuthLayout>
    );
}

export default function ResetPasswordPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-[#101c22] flex items-center justify-center">
                <div className="text-white">Loading...</div>
            </div>
        }>
            <ResetForm />
        </Suspense>
    );
}
