'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { User } from 'lucide-react';

interface UserProfile {
    email: string;
    full_name: string;
}

import { ModeToggle } from '@/components/ui/mode-toggle';

export function Header() {
    const [user, setUser] = useState<UserProfile | null>(null);

    useEffect(() => {
        api.get('/users/me')
            .then(res => setUser(res.data))
            .catch(console.error);
    }, []);

    return (
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/95 px-6 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <h1 className="text-lg font-semibold text-foreground">
                Dashboard
            </h1>

            <div className="flex items-center gap-4">
                <ModeToggle />
                <div className="flex items-center gap-3">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-foreground">{user?.full_name || 'User'}</p>
                        <p className="text-xs text-muted-foreground">{user?.email}</p>
                    </div>
                    <div className="h-9 w-9 rounded-full bg-muted border border-border flex items-center justify-center text-muted-foreground">
                        <User className="h-5 w-5" />
                    </div>
                </div>
            </div>
        </header>
    );
}
