'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

import { ReactNode } from 'react';

interface SidebarItemProps {
    name: string;
    href: string;
    icon: ReactNode;
}

export function SidebarItem({ name, href, icon }: SidebarItemProps) {
    const pathname = usePathname();
    // Using startsWith logic for better sub-route highlighting
    // Jobs is the new root, so /jobs, /jobs/new, /jobs/[id] should all highlight "Jobs"
    const isActive = pathname === href || pathname?.startsWith(href + '/');

    return (
        <Link href={href}>
            <motion.div
                whileHover={{ x: 4 }}
                className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors relative',
                    isActive
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
            >
                {icon}
                <span>{name}</span>
                {isActive && (
                    <motion.div
                        layoutId="sidebar-active"
                        className="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-1 bg-primary rounded-r-full"
                    />
                )}
            </motion.div>
        </Link>
    );
}
