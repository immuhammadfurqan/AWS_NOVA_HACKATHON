'use client';

import { ToastProvider } from '@/components/ui/Toast';

export function CareersLayoutClient({ children }: { children: React.ReactNode }) {
    return (
        <ToastProvider>
            <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
                <nav className="border-b border-border/50 backdrop-blur-sm fixed top-0 left-0 right-0 z-50 bg-background/80">
                    <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
                        <a href="/" className="text-xl font-bold text-primary">
                            AARLP
                        </a>
                        <a
                            href="/login"
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                        >
                            Recruiter Login
                        </a>
                    </div>
                </nav>
                <main className="pt-20 pb-12">
                    {children}
                </main>
                <footer className="border-t border-border/50 py-8 text-center text-sm text-muted-foreground">
                    <p>© {new Date().getFullYear()} AARLP. AI-Powered Recruitment.</p>
                </footer>
            </div>
        </ToastProvider>
    );
}
