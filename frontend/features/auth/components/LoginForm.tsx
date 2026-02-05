'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { Eye, EyeOff, Shield, Lock, LogIn } from 'lucide-react';
import {
    AuthLayout,
    AarlpLogo,
    AgentActiveBadge,
    AuthInput,
    AuthButton,
    AuthDivider,
    GoogleIcon
} from './AuthLayout';

// Testimonial Card Component
function TestimonialCard() {
    return (
        <div className="auth-glass-card rounded-xl p-8 max-w-md relative overflow-hidden group">
            <div className="absolute inset-0 bg-[#25aff4]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="flex flex-col gap-4 relative z-10">
                <div className="flex gap-1">
                    {[...Array(5)].map((_, i) => (
                        <span key={i} className="text-[#25aff4] text-sm">★</span>
                    ))}
                </div>
                <p className="text-xl font-medium leading-relaxed italic text-white">
                    &ldquo;AARLP&apos;s AI agents reduced our time-to-hire by 60%. The command interface is second to none.&rdquo;
                </p>
                <div className="flex items-center gap-4 mt-2">
                    <div className="size-10 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center overflow-hidden">
                        <span className="text-sm font-bold text-[#25aff4]">MV</span>
                    </div>
                    <div>
                        <p className="text-sm font-bold text-white">Marcus Vane</p>
                        <p className="text-xs text-slate-500">Talent Acquisition Director</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Left Panel Content for Login Page
function LoginLeftPanel() {
    return (
        <div className="flex flex-col justify-between h-full p-12 lg:p-16">
            {/* Top Section */}
            <div>
                <div className="flex items-center gap-3 mb-12">
                    <AarlpLogo className="size-8 text-[#25aff4]" />
                    <span className="text-2xl font-bold tracking-tight uppercase">AARLP Recruiter</span>
                </div>

                <AgentActiveBadge className="mb-8" />

                <h1 className="text-4xl lg:text-5xl font-bold leading-tight mb-6 max-w-xl">
                    The next frontier of <span className="text-[#25aff4]">Recruitment Intelligence</span>.
                </h1>
                <p className="text-slate-400 text-lg max-w-lg">
                    Access your recruiter dashboard to manage autonomous talent-sourcing agents.
                    Optimized high-speed authentication for authorized personnel only.
                </p>
            </div>

            {/* Bottom Section - Testimonial */}
            <TestimonialCard />
        </div>
    );
}

export function LoginForm() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        const formData = new FormData(e.currentTarget);
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        try {
            const response = await api.post('/auth/login', { email, password });

            // Unified Token Storage Strategy
            localStorage.setItem('token', response.data.access_token);
            Cookies.set('token', response.data.access_token, { expires: 7, path: '/' });

            router.push('/dashboard');

        } catch (err: unknown) {
            console.error(err);
            const errorObj = err as { response?: { data?: { detail?: string } } };
            const msg = errorObj.response?.data?.detail || 'Something went wrong';
            setError(msg);
        } finally {
            setIsLoading(false);
        }
    };

    const formContent = (
        <div className="auth-glass-card rounded-xl p-8 lg:p-10 shadow-2xl">
            <div className="flex flex-col gap-2 mb-8">
                <div className="text-[#25aff4] text-xs font-bold uppercase tracking-widest mb-1">Recruiter Access Only</div>
                <h2 className="text-3xl font-bold tracking-tight text-white">Sign In</h2>
                <p className="text-slate-400 text-sm">Welcome back. Enter your administrative credentials.</p>
            </div>

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
                <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300 ml-1">Work Email</label>
                    <AuthInput
                        name="email"
                        type="email"
                        placeholder="recruiter@aarlp.ai"
                        required
                        autoComplete="email"
                        icon={<Shield className="size-5" />}
                    />
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between items-center ml-1">
                        <label className="text-sm font-medium text-slate-300">Security Key</label>
                        <Link href="/forgot-password" className="text-xs text-[#25aff4] hover:underline font-medium">
                            Forgot Credentials?
                        </Link>
                    </div>
                    <AuthInput
                        name="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        required
                        autoComplete="current-password"
                        icon={<Lock className="size-5" />}
                        rightIcon={
                            <button type="button" onClick={() => setShowPassword(!showPassword)}>
                                {showPassword ? <Eye className="size-5" /> : <EyeOff className="size-5" />}
                            </button>
                        }
                    />
                </div>

                <div className="flex items-center gap-2 ml-1">
                    <input
                        type="checkbox"
                        id="remember"
                        className="w-4 h-4 bg-[#182b34] border-[#315668] rounded text-[#25aff4] focus:ring-[#25aff4] focus:ring-offset-[#101c22] cursor-pointer"
                    />
                    <label htmlFor="remember" className="text-sm text-slate-400 cursor-pointer select-none">
                        Remember this workstation
                    </label>
                </div>

                <AuthButton type="submit" isLoading={isLoading} className="mt-4">
                    <span>Sign In</span>
                    <LogIn className="size-5" />
                </AuthButton>
            </form>

            <AuthDivider text="Or continue with" />

            <AuthButton variant="secondary" type="button">
                <GoogleIcon />
                <span className="font-semibold">Sign in with Google</span>
            </AuthButton>

            <p className="text-center text-sm text-slate-400 mt-8">
                Don&apos;t have an account?{' '}
                <Link href="/register" className="text-[#25aff4] hover:underline font-semibold">
                    Sign up
                </Link>
            </p>
        </div>
    );

    return (
        <AuthLayout leftPanel={<LoginLeftPanel />}>
            {formContent}
        </AuthLayout>
    );
}
