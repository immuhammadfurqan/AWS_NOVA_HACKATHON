'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

export interface InputProps
    extends React.InputHTMLAttributes<HTMLInputElement> { }

const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, type, ...props }, ref) => {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="w-full"
            >
                <input
                    type={type}
                    className={cn(
                        'flex h-12 w-full rounded-lg glass-input px-3 py-2 text-sm shadow-sm transition-all file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:border-transparent disabled:cursor-not-allowed disabled:opacity-50 hover:bg-accent/50',
                        className
                    )}
                    ref={ref}
                    {...props}
                />
            </motion.div>
        );
    }
);
Input.displayName = 'Input';

export { Input };
