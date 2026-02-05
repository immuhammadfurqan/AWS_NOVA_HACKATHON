'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
    id: string;
    type: ToastType;
    message: string;
    duration?: number;
}

interface ToastContextType {
    toast: (type: ToastType, message: string, duration?: number) => void;
    success: (message: string) => void;
    error: (message: string) => void;
    warning: (message: string) => void;
    info: (message: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within ToastProvider');
    }
    return context;
}

const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
};

const styles = {
    success: 'bg-green-500/10 border-green-500/20 text-green-400',
    error: 'bg-red-500/10 border-red-500/20 text-red-400',
    warning: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    info: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
};

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const addToast = useCallback((type: ToastType, message: string, duration = 4000) => {
        const id = Math.random().toString(36).substring(2, 9);
        setToasts((prev) => [...prev, { id, type, message, duration }]);

        if (duration > 0) {
            setTimeout(() => removeToast(id), duration);
        }
    }, [removeToast]);

    const value: ToastContextType = {
        toast: addToast,
        success: (message) => addToast('success', message),
        error: (message) => addToast('error', message),
        warning: (message) => addToast('warning', message),
        info: (message) => addToast('info', message),
    };

    return (
        <ToastContext.Provider value={value}>
            {children}
            <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
                <AnimatePresence>
                    {toasts.map((toast) => {
                        const Icon = icons[toast.type];
                        return (
                            <motion.div
                                key={toast.id}
                                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, x: 100, scale: 0.95 }}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-sm shadow-lg ${styles[toast.type]}`}
                            >
                                <Icon className="h-5 w-5 flex-shrink-0" />
                                <p className="text-sm font-medium flex-1">{toast.message}</p>
                                <button
                                    onClick={() => removeToast(toast.id)}
                                    className="text-current opacity-60 hover:opacity-100 transition-opacity"
                                    aria-label="Dismiss notification"
                                >
                                    <X className="h-4 w-4" />
                                </button>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
            </div>
        </ToastContext.Provider>
    );
}
