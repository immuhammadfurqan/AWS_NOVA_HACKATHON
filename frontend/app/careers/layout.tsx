import { Metadata } from 'next';
import { CareersLayoutClient } from './layout-client';

export const metadata: Metadata = {
    title: 'Careers | AARLP',
    description: 'Explore job opportunities and join our team. Find the perfect role for your skills and career goals.',
    openGraph: {
        title: 'Careers | AARLP',
        description: 'Explore job opportunities and join our team.',
        type: 'website',
    },
};

export default function CareersLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <CareersLayoutClient>{children}</CareersLayoutClient>;
}
