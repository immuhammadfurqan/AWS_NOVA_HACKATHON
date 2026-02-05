'use client';

import Link from 'next/link';
import { ReactNode } from 'react';

// AARLP Logo SVG component
export function AarlpLogo({ className = "size-8" }: { className?: string }) {
    return (
        <svg className={className} fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path d="M39.5563 34.1455V13.8546C39.5563 15.708 36.8773 17.3437 32.7927 18.3189C30.2914 18.916 27.263 19.2655 24 19.2655C20.737 19.2655 17.7086 18.916 15.2073 18.3189C11.1227 17.3437 8.44365 15.708 8.44365 13.8546V34.1455C8.44365 35.9988 11.1227 37.6346 15.2073 38.6098C17.7086 39.2069 20.737 39.5564 24 39.5564C27.1288 39.5564 30.2914 39.2069 32.7927 38.6098C36.8773 37.6346 39.5563 35.9988 39.5563 34.1455Z" fill="currentColor"></path>
            <path clipRule="evenodd" d="M10.4485 13.8519C10.4749 13.9271 10.6203 14.246 11.379 14.7361C12.298 15.3298 13.7492 15.9145 15.6717 16.3735C18.0007 16.9296 20.8712 17.2655 24 17.2655C27.1288 17.2655 29.9993 16.9296 32.3283 16.3735C34.2508 15.9145 35.702 15.3298 36.621 14.7361C37.3796 14.246 37.5251 13.9271 37.5515 13.8519C37.5287 13.7876 37.4333 13.5973 37.0635 13.2931C36.5266 12.8516 35.6288 12.3647 34.343 11.9175C31.79 11.0295 28.1333 10.4437 24 10.4437C19.8667 10.4437 16.2099 11.0295 13.657 11.9175C12.3712 12.3647 11.4734 12.8516 10.9365 13.2931C10.5667 13.5973 10.4713 13.7876 10.4485 13.8519ZM37.5563 18.7877C36.3176 19.3925 34.8502 19.8839 33.2571 20.2642C30.5836 20.9025 27.3973 21.2655 24 21.2655C20.6027 21.2655 17.4164 20.9025 14.7429 20.2642C13.1498 19.8839 11.6824 19.3925 10.4436 18.7877V34.1275C10.4515 34.1545 10.5427 34.4867 11.379 35.027C12.298 35.6207 13.7492 36.2054 15.6717 36.6644C18.0007 37.2205 20.8712 37.5564 24 37.5564C27.1288 37.5564 29.9993 37.2205 32.3283 36.6644C34.2508 36.2054 35.702 35.6207 36.621 35.027C37.4573 34.4867 37.5485 34.1546 37.5563 34.1275V18.7877ZM41.5563 13.8546V34.1455C41.5563 36.1078 40.158 37.5042 38.7915 38.3869C37.3498 39.3182 35.4192 40.0389 33.2571 40.5551C30.5836 41.1934 27.3973 41.5564 24 41.5564C20.6027 41.5564 17.4164 41.1934 14.7429 40.5551C12.5808 40.0389 10.6502 39.3182 9.20848 38.3869C7.84205 37.5042 6.44365 36.1078 6.44365 34.1455L6.44365 13.8546C6.44365 12.2684 7.37223 11.0454 8.39581 10.2036C9.43325 9.3505 10.8137 8.67141 12.343 8.13948C15.4203 7.06909 19.5418 6.44366 24 6.44366C28.4582 6.44366 32.5797 7.06909 35.657 8.13948C37.1863 8.67141 38.5667 9.3505 39.6042 10.2036C40.6278 11.0454 41.5563 12.2684 41.5563 13.8546Z" fill="currentColor" fillRule="evenodd"></path>
        </svg>
    );
}

// Agent Active Badge
export function AgentActiveBadge({ className = "" }: { className?: string }) {
    return (
        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#25aff4]/20 border border-[#25aff4]/40 auth-agent-pulse ${className}`}>
            <span className="size-2 rounded-full bg-[#25aff4] shadow-[0_0_8px_#25aff4]"></span>
            <span className="text-xs font-semibold text-[#25aff4] tracking-widest uppercase">Agent Active</span>
        </div>
    );
}

// Google Icon
export function GoogleIcon({ className = "w-5 h-5" }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
        </svg>
    );
}

interface AuthLayoutProps {
    children: ReactNode;
    leftPanel: ReactNode;
    showHeader?: boolean;
    headerRightContent?: ReactNode;
}

// Main Auth Layout Component
export function AuthLayout({ children, leftPanel, showHeader = false, headerRightContent }: AuthLayoutProps) {
    return (
        <div className="min-h-screen w-full bg-[#101c22] text-white font-display">
            {/* Optional Fixed Header */}
            {showHeader && (
                <header className="fixed top-0 w-full z-50 flex items-center justify-between px-6 lg:px-12 py-4 border-b border-[#223c49]/50 bg-[#101c22]/80 backdrop-blur-md">
                    <Link href="/" className="flex items-center gap-3">
                        <AarlpLogo className="size-8 text-[#25aff4]" />
                        <span className="text-xl font-bold tracking-tight">AARLP</span>
                    </Link>
                    {headerRightContent}
                </header>
            )}

            <div className={`flex min-h-screen w-full ${showHeader ? 'pt-16' : ''}`}>
                {/* Left Panel - Hidden on mobile */}
                <div className="hidden lg:flex lg:w-1/2 relative auth-bg-left overflow-hidden">
                    <div className="auth-gradient-overlay"></div>
                    <div className="auth-bg-grid absolute inset-0 opacity-20"></div>
                    <div className="relative z-10 w-full h-full flex flex-col">
                        {leftPanel}
                    </div>
                    {/* Subtle glow at bottom right */}
                    <div className="absolute bottom-0 right-0 w-64 h-64 bg-[#25aff4]/10 blur-[100px] rounded-full -mr-32 -mb-32"></div>
                </div>

                {/* Right Panel - Form */}
                <div className="flex-1 bg-[#101c22] flex items-center justify-center p-6 sm:p-12 relative overflow-hidden">
                    {/* Background glows for mobile */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-[#25aff4]/10 rounded-full blur-[100px]"></div>
                    <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#25aff4]/5 rounded-full blur-[120px]"></div>

                    {/* Form Container */}
                    <div className="w-full max-w-[480px] z-10">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Auth Input Component
interface AuthInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    icon?: ReactNode;
    rightIcon?: ReactNode;
}

export function AuthInput({ icon, rightIcon, className = "", ...props }: AuthInputProps) {
    return (
        <div className="relative group">
            {icon && (
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-[#25aff4] transition-colors">
                    {icon}
                </span>
            )}
            <input
                className={`w-full bg-[#182b34] border border-[#315668]/50 rounded-lg py-3.5 ${icon ? 'pl-12' : 'pl-4'} ${rightIcon ? 'pr-12' : 'pr-4'} text-white placeholder:text-slate-500 focus:outline-none focus:border-[#25aff4] focus:ring-1 focus:ring-[#25aff4]/30 transition-all ${className}`}
                {...props}
            />
            {rightIcon && (
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 cursor-pointer hover:text-white transition-colors">
                    {rightIcon}
                </span>
            )}
        </div>
    );
}

// Auth Button Component
interface AuthButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary';
    isLoading?: boolean;
    children: ReactNode;
}

export function AuthButton({ variant = 'primary', isLoading, children, className = "", ...props }: AuthButtonProps) {
    const baseStyles = "w-full font-bold py-4 rounded-lg flex items-center justify-center gap-2 transition-all duration-300 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed";

    const variantStyles = {
        primary: "bg-[#25aff4] hover:bg-[#25aff4]/90 text-[#101c22] auth-glow-button",
        secondary: "bg-white/5 hover:bg-white/10 border border-white/10 text-white"
    };

    return (
        <button
            className={`${baseStyles} ${variantStyles[variant]} ${className}`}
            disabled={isLoading}
            {...props}
        >
            {isLoading ? (
                <div className="size-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : children}
        </button>
    );
}

// Auth Divider
export function AuthDivider({ text }: { text: string }) {
    return (
        <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-[#101c22]/50 px-3 text-slate-500 tracking-widest backdrop-blur-sm">{text}</span>
            </div>
        </div>
    );
}
