import { Sidebar } from '@/features/dashboard/components/Sidebar';
import { Header } from '@/features/dashboard/components/Header';
import { ToastProvider } from '@/components/ui/Toast';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ToastProvider>
            <div className="min-h-screen bg-background">
                <Sidebar />
                <div className="pl-64">
                    <Header />
                    <main className="p-6">
                        <div className="mx-auto max-w-7xl animate-in fade-in slide-in-from-bottom-4 duration-500">
                            {children}
                        </div>
                    </main>
                </div>
            </div>
        </ToastProvider>
    );
}
