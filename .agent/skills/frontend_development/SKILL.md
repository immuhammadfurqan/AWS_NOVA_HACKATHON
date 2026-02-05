---
name: frontend_development
description: Build and optimize Next.js 14 frontend components with TypeScript, Tailwind, and theme support
---

# Next.js Frontend Development Skill

## Purpose
Build high-quality, type-safe, and accessible components for the AARLP Next.js frontend. This skill covers App Router patterns, Server/Client components, theming, and performance optimization.

## Frontend Architecture

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth routes (login, register)
│   ├── (dashboard)/       # Protected app routes
│   ├── layout.tsx         # Root layout
│   └── providers.tsx      # Context providers
├── components/            # Reusable UI components
│   ├── ui/               # Base UI primitives
│   ├── layout/           # Layout components (Sidebar, Header)
│   └── theme/            # Theme toggle, providers
├── features/             # Feature-specific components
│   ├── jobs/             # Job management UI
│   ├── candidates/       # Candidate views
│   └── dashboard/        # Dashboard widgets
├── lib/                  # Utilities
│   ├── api.ts           # API client
│   ├── types.ts         # TypeScript types
│   └── utils.ts         # Helper functions
└── styles/
    └── globals.css       # Global styles + Tailwind
```

## Component Patterns

### 1. Server Components (Default)

Use for data fetching, SEO, and static content:

```typescript
// app/(dashboard)/jobs/page.tsx
import { getJobs } from '@/lib/api';
import { JobCard } from '@/features/jobs/JobCard';

// Server Component (async allowed)
export default async function JobsPage() {
  // Fetch on server
  const jobs = await getJobs();
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">My Jobs</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
    </div>
  );
}

// Enable ISR (Incremental Static Regeneration)
export const revalidate = 60; // Revalidate every 60 seconds
```

### 2. Client Components

Use for interactivity, hooks, and browser APIs:

```typescript
'use client'; // Required at top

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';

export function JobWizard() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({});
  
  const handleSubmit = async () => {
    const response = await fetch('/api/jobs/create', {
      method: 'POST',
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    // Handle response
  };
  
  return (
    <div className="space-y-6">
      <h2>Create Job - Step {step}/4</h2>
      {/* Form steps */}
      <Button onClick={handleSubmit}>
        Next
      </Button>
    </div>
  );
}
```

### 3. Hybrid Pattern (Server + Client)

```typescript
// app/(dashboard)/jobs/[id]/page.tsx (Server Component)
import { getJob } from '@/lib/api';
import { JobActions } from './JobActions'; // Client component

export default async function JobDetailPage({ params }: { params: { id: string } }) {
  // Fetch on server
  const job = await getJob(params.id);
  
  return (
    <div>
      {/* Server-rendered content */}
      <h1>{job.title}</h1>
      <p>{job.company}</p>
      
      {/* Client-side interactivity */}
      <JobActions jobId={job.id} />
    </div>
  );
}

// JobActions.tsx (Client Component)
'use client';

export function JobActions({ jobId }: { jobId: string }) {
  const handleApprove = async () => {
    await fetch(`/api/jobs/${jobId}/approve`, { method: 'POST' });
  };
  
  return <button onClick={handleApprove}>Approve JD</button>;
}
```

## Theming (Light/Dark Mode)

### Setup (Already in AARLP)

```typescript
// app/providers.tsx
'use client';

import { ThemeProvider } from 'next-themes';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  );
}

// app/layout.tsx
import { Providers } from './providers';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
```

### Theme-Aware Components

```typescript
// components/theme/ThemeToggle.tsx
'use client';

import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  
  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800"
    >
      <Sun className="h-5 w-5 dark:hidden" />
      <Moon className="h-5 w-5 hidden dark:block" />
    </button>
  );
}
```

### Tailwind Theme Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Use class-based dark mode
  theme: {
    extend: {
      colors: {
        // Brand colors
        primary: {
          50: '#f0fdfc',
          100: '#ccfbf6',
          500: '#06b6d4', // Cyan
          600: '#0891b2',
          900: '#164e63',
        },
        // Dark mode backgrounds
        dark: {
          bg: '#0a0a0a',
          card: '#1a1a1a',
          border: '#2a2a2a',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      }
    }
  }
}
```

## Styling Patterns

### Glassmorphism (AARLP Style)

```typescript
// components/ui/GlassCard.tsx
export function GlassCard({ children, className = '' }: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`
      backdrop-blur-xl
      bg-white/80 dark:bg-gray-900/80
      border border-gray-200/50 dark:border-gray-700/50
      rounded-2xl
      shadow-xl
      p-6
      ${className}
    `}>
      {children}
    </div>
  );
}

// Usage
<GlassCard>
  <h2>Job Details</h2>
  <p>Content goes here</p>
</GlassCard>
```

### Gradient Accents

```typescript
// components/ui/GradientText.tsx
export function GradientText({ children }: { children: React.ReactNode }) {
  return (
    <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
      {children}
    </span>
  );
}

// Usage
<h1 className="text-4xl font-bold">
  <GradientText>AI-Powered Recruitment</GradientText>
</h1>
```

## TypeScript Best Practices

### Type Definitions

```typescript
// lib/types.ts

// API response types
export interface Job {
  id: string;
  title: string;
  company_name: string;
  location: string;
  employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT';
  experience_level: 'JUNIOR' | 'MID' | 'SENIOR';
  workflow_status: WorkflowStatus;
  jd_content?: string;
  created_at: string;
  updated_at: string;
}

export interface Candidate {
  id: string;
  job_id: string;
  name: string;
  email: string;
  resume_url: string;
  semantic_score: number;
  status: 'PENDING' | 'SHORTLISTED' | 'REJECTED';
}

// Component props type
export interface JobCardProps {
  job: Job;
  onApprove?: (jobId: string) => void;
  showActions?: boolean;
}

// Form data type
export interface JobFormData {
  title: string;
  company_name: string;
  location: string;
  employment_type: string;
  experience_level: string;
  description?: string;
}
```

### Type-Safe API Client

```typescript
// lib/api.ts
import { Job, Candidate } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

// Typed API functions
export const api = {
  jobs: {
    list: () => fetchAPI<Job[]>('/jobs/'),
    get: (id: string) => fetchAPI<Job>(`/jobs/${id}`),
    create: (data: JobFormData) => fetchAPI<Job>('/jobs/create', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
  candidates: {
    list: (jobId: string) => fetchAPI<Candidate[]>(`/jobs/${jobId}/candidates`),
  },
};

// Usage with type safety
const jobs = await api.jobs.list(); // TypeScript knows jobs is Job[]
```

## Performance Optimization

### 1. Image Optimization

```typescript
import Image from 'next/image';

// Automatic optimization, lazy loading, WebP conversion
<Image
  src="/company-logo.png"
  alt="Company Logo"
  width={200}
  height={100}
  priority={false} // Only true for above-fold images
  placeholder="blur"
  blurDataURL="data:image/..." // Optional blur placeholder
/>
```

### 2. Code Splitting

```typescript
import dynamic from 'next/dynamic';

// Lazy load heavy components
const JobEditor = dynamic(() => import('@/features/jobs/JobEditor'), {
  loading: () => <div>Loading editor...</div>,
  ssr: false // Don't render on server
});

export function JobDetail() {
  const [showEditor, setShowEditor] = useState(false);
  
  return (
    <div>
      <button onClick={() => setShowEditor(true)}>Edit JD</button>
      {showEditor && <JobEditor />}
    </div>
  );
}
```

### 3. Memoization

```typescript
'use client';

import { useMemo, useCallback } from 'react';

export function CandidateList({ candidates }: { candidates: Candidate[] }) {
  // Memoize expensive computation
  const sortedCandidates = useMemo(() => {
    return [...candidates].sort((a, b) => b.semantic_score - a.semantic_score);
  }, [candidates]);
  
  // Memoize callback
  const handleSelect = useCallback((id: string) => {
    console.log('Selected:', id);
  }, []);
  
  return (
    <ul>
      {sortedCandidates.map((c) => (
        <li key={c.id} onClick={() => handleSelect(c.id)}>
          {c.name} - Score: {c.semantic_score}
        </li>
      ))}
    </ul>
  );
}
```

## State Management

### 1. React Context (Global State)

```typescript
// lib/contexts/AuthContext.tsx
'use client';

import { createContext, useContext, useState } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  
  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    setUser(data.user);
  };
  
  const logout = () => setUser(null);
  
  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

### 2. URL State (Search Params)

```typescript
'use client';

import { useSearchParams, useRouter } from 'next/navigation';

export function JobFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const currentType = searchParams.get('type') || 'all';
  
  const handleFilterChange = (type: string) => {
    const params = new URLSearchParams(searchParams);
    params.set('type', type);
    router.push(`/jobs?${params.toString()}`);
  };
  
  return (
    <select value={currentType} onChange={(e) => handleFilterChange(e.target.value)}>
      <option value="all">All Jobs</option>
      <option value="active">Active</option>
      <option value="draft">Draft</option>
    </select>
  );
}
```

## Form Handling

### With React Hook Form + Zod

```typescript
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Validation schema
const jobSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters'),
  company_name: z.string().min(2),
  location: z.string(),
  employment_type: z.enum(['FULL_TIME', 'PART_TIME', 'CONTRACT']),
});

type JobFormData = z.infer<typeof jobSchema>;

export function JobCreateForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<JobFormData>({
    resolver: zodResolver(jobSchema),
  });
  
  const onSubmit = async (data: JobFormData) => {
    await api.jobs.create(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label>Job Title</label>
        <input {...register('title')} className="input" />
        {errors.title && <p className="text-red-500">{errors.title.message}</p>}
      </div>
      
      <button type="submit">Create Job</button>
    </form>
  );
}
```

## Testing

```typescript
// __tests__/components/JobCard.test.tsx
import { render, screen } from '@testing-library/react';
import { JobCard } from '@/features/jobs/JobCard';

describe('JobCard', () => {
  const mockJob = {
    id: '123',
    title: 'Senior Engineer',
    company_name: 'TechCorp',
    location: 'Remote',
    // ... other fields
  };
  
  it('renders job title', () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText('Senior Engineer')).toBeInTheDocument();
  });
  
  it('calls onApprove when approved', async () => {
    const mockApprove = jest.fn();
    render(<JobCard job={mockJob} onApprove={mockApprove} />);
    
    const approveButton = screen.getByRole('button', { name: /approve/i });
    approveButton.click();
    
    expect(mockApprove).toHaveBeenCalledWith('123');
  });
});
```

## Best Practices Checklist

- [ ] Use Server Components by default (add 'use client' only when needed)
- [ ] Implement proper TypeScript types for all props and API responses
- [ ] Support light and dark themes for all components
- [ ] Use `next/image` for all images
- [ ] Lazy load heavy components with `dynamic`
- [ ] Implement proper error handling and loading states
- [ ] Use semantic HTML (button, nav, header, main, article)
- [ ] Add ARIA labels for accessibility
- [ ] Test on mobile viewports (responsive design)
- [ ] Extract reusable components to `components/ui`
- [ ] Use Tailwind utilities, avoid inline styles
- [ ] Validate forms with Zod schemas

---

## Related Skills

- **[api_testing](../api_testing/SKILL.md)** - Testing React components and frontend integration
- **[jd_optimization](../jd_optimization/SKILL.md)** - Rendering optimized JDs in job detail pages
- **[workflow_management](../workflow_management/SKILL.md)** - Polling workflow status for real-time UI updates

---

## Resources

- Next.js Docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs
- next-themes: https://github.com/pacocoursey/next-themes
- React Hook Form: https://react-hook-form.com/
- Zod: https://zod.dev/
- AARLP Frontend: `frontend/`
