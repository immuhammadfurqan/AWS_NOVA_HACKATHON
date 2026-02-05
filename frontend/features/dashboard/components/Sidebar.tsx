import Link from 'next/link';
import {
    Briefcase,
    Users,
    Calendar,
    Settings,
    LayoutDashboard,
} from 'lucide-react';
import { SidebarItem } from './SidebarItem';
import { SignOutButton } from './SignOutButton';

const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { name: 'Jobs', href: '/jobs', icon: <Briefcase className="h-4 w-4" /> },
    { name: 'Candidates', href: '/candidates', icon: <Users className="h-4 w-4" /> },
    { name: 'Interviews', href: '/interviews', icon: <Calendar className="h-4 w-4" /> },
    { name: 'Settings', href: '/settings', icon: <Settings className="h-4 w-4" /> },
];

export function Sidebar() {
    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-16 items-center px-6">
                <Link href="/dashboard" className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-primary/80 shadow-lg shadow-primary/20" />
                    <span className="text-xl font-bold tracking-tight text-foreground">AARLP</span>
                </Link>
            </div>

            <div className="flex flex-col gap-1 px-3 py-4">
                {menuItems.map((item) => (
                    <SidebarItem
                        key={item.href}
                        name={item.name}
                        href={item.href}
                        icon={item.icon}
                    />
                ))}
            </div>

            <div className="absolute bottom-4 left-0 w-full px-3">
                <SignOutButton />
            </div>
        </aside>
    );
}
