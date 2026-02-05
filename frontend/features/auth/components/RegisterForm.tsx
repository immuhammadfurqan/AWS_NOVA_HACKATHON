'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { User, AtSign, Lock, Eye, EyeOff } from 'lucide-react';
import {
    AuthLayout,
    AarlpLogo,
    AgentActiveBadge,
    AuthInput,
    AuthButton,
    AuthDivider,
    GoogleIcon
} from './AuthLayout';

// Left Panel Content for Register Page
function RegisterLeftPanel() {
    return (
        <div className="flex flex-col justify-between h-full p-12 lg:p-16 relative">
            {/* Background Image Pattern */}
            <div
                className="absolute inset-0 opacity-20 pointer-events-none"
                style={{
                    backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDdB1yL5Va2S1OLKLyP9fkDbswoIF1rXXIFkBnktGScK9AJVf2FWun6EkxHY2FOptPauJcsgPyN5yQWJVIs6uK6a6BmGTVIqsQGNCAd4Wxu09dhqsMsyG4tFeohn4mj8hke4KD0Qh3oBHuVRozXBFcow9_FpedYh9uQBPG2n-vjvGlCQcz6MUgSCg07QcKZiOW7vOW8_vCORUnW1q0Ln1i9F7xH_veBNnhL2cZQwWPHbV4uLJ-dJjPxaWlnrTeJ6kBb2TWMs8YYeiSC')",
                    backgroundSize: 'cover',
                    backgroundPosition: 'center'
                }}
            ></div>

            {/* Top Section */}
            <div className="relative z-10">
                <div className="flex items-center gap-3 mb-12">
                    <AarlpLogo className="size-8 text-[#25aff4]" />
                    <span className="text-2xl font-bold tracking-tight uppercase">AARLP</span>
                </div>

                <AgentActiveBadge className="mb-8" />
            </div>

            {/* Middle Section - Headline */}
            <div className="relative z-10">
                <h1 className="text-3xl lg:text-4xl font-bold leading-tight mb-4">
                    Redefining Intelligence in <span className="text-[#25aff4]">Talent Acquisition</span>.
                </h1>
                <p className="text-slate-400 text-lg max-w-md">
                    Join the world&apos;s most advanced autonomous recruiting ecosystem.
                </p>
            </div>

            {/* Bottom Section - Stats */}
            <div className="relative z-10 flex gap-8">
                <div className="flex flex-col">
                    <span className="text-3xl font-bold text-white">12k+</span>
                    <span className="text-xs text-slate-500 uppercase tracking-widest">Active Agents</span>
                </div>
                <div className="flex flex-col">
                    <span className="text-3xl font-bold text-white">94%</span>
                    <span className="text-xs text-slate-500 uppercase tracking-widest">Match Accuracy</span>
                </div>
            </div>
        </div>
    );
}

export function RegisterForm() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        const formData = new FormData(e.currentTarget);
        const full_name = formData.get('full_name') as string;
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        try {
            await api.post('/auth/register', {
                email,
                password,
                full_name,
                is_active: true,
                is_superuser: false
            });

            // Redirect to verification
            router.push(`/verify-otp?email=${encodeURIComponent(email)}`);

        } catch (err: unknown) {
            console.error(err);
            const errorObj = err as { response?: { data?: { detail?: string } } };
            setError(errorObj.response?.data?.detail || 'Registration failed');
        } finally {
            setIsLoading(false);
        }
    };

    const formContent = (
        <div className="auth-glass-card rounded-xl p-8 lg:p-10 shadow-2xl">
            <header className="mb-8">
                <h1 className="text-white tracking-tight text-2xl lg:text-3xl font-bold leading-tight mb-2">
                    Create Your Recruiter Workspace
                </h1>
                <p className="text-slate-400 text-sm">
                    Empower your hiring workflow with autonomous AI agents.
                </p>
            </header>

            {error && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm mb-6"
                >
                    {error}
                </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
                <div className="space-y-1.5">
                    <label className="text-slate-300 text-xs font-bold uppercase tracking-wider">Full Name</label>
                    <AuthInput
                        name="full_name"
                        type="text"
                        placeholder="e.g. Alexander Vance"
                        required
                        icon={<User className="size-5" />}
                    />
                </div>

                <div className="space-y-1.5">
                    <label className="text-slate-300 text-xs font-bold uppercase tracking-wider">Business Email</label>
                    <AuthInput
                        name="email"
                        type="email"
                        placeholder="name@company.ai"
                        required
                        autoComplete="email"
                        icon={<AtSign className="size-5" />}
                    />
                </div>

                <div className="space-y-1.5">
                    <label className="text-slate-300 text-xs font-bold uppercase tracking-wider">Secure Password</label>
                    <AuthInput
                        name="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••••••"
                        required
                        minLength={8}
                        icon={<Lock className="size-5" />}
                        rightIcon={
                            <button type="button" onClick={() => setShowPassword(!showPassword)}>
                                {showPassword ? <Eye className="size-5" /> : <EyeOff className="size-5" />}
                            </button>
                        }
                    />
                </div>

                <AuthButton type="submit" isLoading={isLoading} className="mt-6">
                    Start Hiring
                </AuthButton>
            </form>

            <AuthDivider text="Or continue with" />

            <AuthButton variant="secondary" type="button">
                <GoogleIcon />
                <span className="font-semibold">Sign up with Google</span>
            </AuthButton>

            <footer className="mt-8 text-center">
                <p className="text-slate-400 text-sm">
                    Already have a workspace?{' '}
                    <Link href="/login" className="text-[#25aff4] hover:underline font-semibold">
                        Log in
                    </Link>
                </p>
            </footer>

            {/* Footer Links */}
            <div className="mt-8 flex justify-center gap-6 text-xs text-slate-500 uppercase tracking-widest">
                <Link href="#" className="hover:text-slate-300 transition-colors">Terms</Link>
                <Link href="#" className="hover:text-slate-300 transition-colors">Privacy</Link>
                <Link href="#" className="hover:text-slate-300 transition-colors">Support</Link>
            </div>
        </div>
    );

    return (
        <AuthLayout leftPanel={<RegisterLeftPanel />}>
            {formContent}
        </AuthLayout>
    );
}
