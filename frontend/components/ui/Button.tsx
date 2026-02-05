'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { motion, HTMLMotionProps } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends Omit<HTMLMotionProps<"button">, "children"> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
    size?: 'default' | 'sm' | 'lg' | 'icon';
    isLoading?: boolean;
    children?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'default', isLoading, children, ...props }, ref) => {
        const variants = {
            primary: 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20 border-transparent',
            secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border-secondary',
            outline: 'bg-background border-input hover:bg-accent hover:text-accent-foreground border',
            ghost: 'bg-transparent hover:bg-accent hover:text-accent-foreground border-transparent',
            destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm',
        };

        const sizes = {
            default: 'h-11 px-4 py-2',
            sm: 'h-9 rounded-md px-3',
            lg: 'h-12 rounded-md px-8',
            icon: 'h-10 w-10',
        };

        return (
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                    'inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
                    variants[variant],
                    sizes[size],
                    className
                )}
                ref={ref}
                disabled={isLoading || props.disabled}
                {...props}
            >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {children}
            </motion.button>
        );
    }
);
Button.displayName = 'Button';

export { Button };
