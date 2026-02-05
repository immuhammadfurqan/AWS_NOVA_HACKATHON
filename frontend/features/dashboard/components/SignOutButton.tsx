'use client';

import { LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

export function SignOutButton() {
    const router = useRouter();

    return (
        <button
            className={cn(
                "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                "text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
            )}
            onClick={() => {
                localStorage.removeItem('token');
                window.location.href = '/login';
            }}
            aria-label="Sign Out"
        >
            <LogOut className="h-4 w-4" />
            <span>Sign Out</span>
        </button>
    );
}
