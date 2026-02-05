import type { Metadata } from "next";
import { ThemeToggle } from "@/components/theme-toggle";

export const metadata: Metadata = {
  title: "AARLP - Agentic Recruitment Lifecycle Platform",
  description: "Automate your entire hiring pipeline with AI Agents.",
};

export default function Home() {
  return (
    <div className="bg-[var(--landing-bg)] font-sans text-[var(--landing-text)] overflow-x-hidden selection:bg-[var(--landing-primary)] selection:text-white min-h-screen relative transition-colors duration-300">
      {/* Top Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-4 md:px-8">
        <div className="glass mx-auto max-w-7xl rounded-full px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 md:gap-4">
            <div className="size-8 text-white flex items-center justify-center bg-[var(--landing-primary)] rounded-lg shadow-sm">
              <span className="material-symbols-outlined text-xl">smart_toy</span>
            </div>
            <h1 className="text-[var(--landing-text)] text-lg font-bold tracking-tight">AARLP</h1>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-[var(--landing-text-muted)]">
            <a className="hover:text-[var(--landing-primary)] transition-colors" href="#">
              Platform
            </a>
            <a className="hover:text-[var(--landing-primary)] transition-colors" href="#">
              Solutions
            </a>
            <a className="hover:text-[var(--landing-primary)] transition-colors" href="#">
              Pricing
            </a>
            <a className="hover:text-[var(--landing-primary)] transition-colors" href="#">
              API
            </a>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <a
              className="hidden md:block text-sm font-medium text-[var(--landing-text-muted)] hover:text-[var(--landing-text)] transition-colors"
              href="/login"
            >
              Log in
            </a>
            <a href="/register" className="bg-[var(--landing-btn-bg)] text-[var(--landing-btn-text)] text-sm font-semibold px-4 py-2 rounded-full transition-all shadow-lg hover:shadow-xl">
              Get Started
            </a>
          </div>
        </div>
      </nav>

      {/* Main Content Wrapper */}
      <div className="relative min-h-screen pt-24 md:pt-32 pb-20">
        {/* Background Gradients */}
        <div className="absolute inset-0 bg-[image:var(--landing-hero-gradient)] pointer-events-none transition-all duration-500"></div>
        <div className="absolute top-[20%] left-[10%] w-[500px] h-[500px] bg-[var(--landing-primary)] rounded-full blur-[100px] pointer-events-none opacity-20"></div>
        <div className="absolute top-[40%] right-[10%] w-[400px] h-[400px] bg-purple-500 rounded-full blur-[100px] pointer-events-none opacity-20"></div>

        <div className="container mx-auto px-4 md:px-6 relative z-10 max-w-7xl">
          {/* Hero Section */}
          <div className="flex flex-col items-center text-center gap-8 mb-20 md:mb-32">
            {/* Status Pill */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-600 dark:text-emerald-400 mb-2 animate-pulse-slow backdrop-blur-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Agent Active: Screening Candidate #842...
            </div>
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] max-w-4xl text-[var(--landing-text)]">
              Automate Your Entire <br className="hidden md:block" />
              <span className="text-gradient">Hiring Pipeline with AI Agents</span>
            </h1>
            <p className="text-lg md:text-xl text-[var(--landing-text-muted)] max-w-2xl leading-relaxed">
              Deploy autonomous recruiting agents to source, screen, and schedule top talent 24/7.
              Zero friction, infinite scale.
            </p>
            <div className="flex flex-col sm:flex-row items-center gap-4 mt-4 w-full sm:w-auto">
              <button className="w-full sm:w-auto h-12 px-8 rounded-lg bg-[var(--landing-primary)] text-white font-bold text-sm tracking-wide shadow-glow hover:bg-[var(--landing-primary-glow)] transition-all flex items-center justify-center gap-2 group">
                Start Hiring with AI
                <span className="material-symbols-outlined text-lg group-hover:translate-x-1 transition-transform">
                  arrow_forward
                </span>
              </button>
              <button className="w-full sm:w-auto h-12 px-8 rounded-lg glass-card text-[var(--landing-text)] font-semibold text-sm tracking-wide hover:bg-white/5 transition-all flex items-center justify-center gap-2 border border-[var(--landing-glass-border)]">
                <span className="material-symbols-outlined text-lg text-[var(--landing-primary)]">play_circle</span>
                View Live Demo
              </button>
            </div>

            {/* Abstract Hero Visual */}
            <div className="w-full mt-16 relative">
              <div className="absolute inset-0 bg-gradient-to-t from-[var(--landing-bg)] via-transparent to-transparent z-10 h-full w-full pointer-events-none"></div>
              <div className="relative w-full aspect-[16/9] md:aspect-[21/9] rounded-xl overflow-hidden glass border border-[var(--landing-glass-border)] shadow-2xl animate-float">
                <div
                  className="absolute inset-0 bg-cover bg-center opacity-60 mix-blend-screen dark:opacity-40"
                  style={{
                    backgroundImage:
                      "url('https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2832&auto=format&fit=crop')",
                  }}
                  data-alt="Abstract 3D node network visualization glowing blue on dark background"
                ></div>

                {/* Floating UI Elements over Image */}
                <div className="absolute top-1/4 left-1/4 p-4 rounded-lg glass-card border-l-4 border-l-green-500 max-w-[200px] hidden md:block bg-white/90 dark:bg-transparent">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="size-6 rounded-full bg-green-500/20 flex items-center justify-center text-green-500">
                      <span className="material-symbols-outlined text-sm">check</span>
                    </div>
                    <span className="text-xs font-bold text-slate-800 dark:text-white">Match Found</span>
                  </div>
                  <div className="h-2 w-full bg-slate-200 dark:bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500 w-[92%]"></div>
                  </div>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 mt-1 block">92% Semantic Match</span>
                </div>

                <div className="absolute bottom-1/3 right-1/4 p-4 rounded-lg glass-card border-l-4 border-l-[var(--landing-primary)] max-w-[240px] hidden md:block bg-white/90 dark:bg-transparent">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="size-6 rounded-full bg-[var(--landing-primary)]/20 flex items-center justify-center text-[var(--landing-primary)]">
                      <span className="material-symbols-outlined text-sm">graphic_eq</span>
                    </div>
                    <span className="text-xs font-bold text-slate-800 dark:text-white">Voice Screen Active</span>
                  </div>
                  <div className="flex items-center gap-1 h-4">
                    <div className="w-1 h-2 bg-[var(--landing-primary)] rounded-full animate-[pulse_1s_ease-in-out_infinite]"></div>
                    <div className="w-1 h-3 bg-[var(--landing-primary)] rounded-full animate-[pulse_1.1s_ease-in-out_infinite]"></div>
                    <div className="w-1 h-4 bg-[var(--landing-primary)] rounded-full animate-[pulse_1.2s_ease-in-out_infinite]"></div>
                    <div className="w-1 h-2 bg-[var(--landing-primary)] rounded-full animate-[pulse_1.3s_ease-in-out_infinite]"></div>
                    <div className="w-1 h-3 bg-[var(--landing-primary)] rounded-full animate-[pulse_0.9s_ease-in-out_infinite]"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bento Grid Features */}
          <div className="flex flex-col gap-10 mb-20">
            <div className="flex flex-col gap-4 text-center md:text-left md:items-start max-w-2xl">
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-[var(--landing-text)]">
                The Agentic Recruitment Engine
              </h2>
              <p className="text-[var(--landing-text-muted)] text-lg">
                Our autonomous agents handle the heavy lifting, from parsing requirements to conducting
                voice interviews.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[minmax(280px,auto)]">
              {/* Feature 1: JD Generation (Large) */}
              <div className="glass-card rounded-2xl p-8 md:col-span-2 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--landing-primary)]/5 rounded-full blur-[80px] -mr-16 -mt-16 pointer-events-none"></div>
                <div className="relative z-10 flex flex-col h-full justify-between gap-6">
                  <div>
                    <div className="w-12 h-12 rounded-lg bg-indigo-500/20 text-indigo-500 flex items-center justify-center mb-4 border border-indigo-500/30">
                      <span className="material-symbols-outlined text-2xl">auto_fix_high</span>
                    </div>
                    <h3 className="text-xl font-bold text-[var(--landing-text)] mb-2">
                      Intelligent JD Generation
                    </h3>
                    <p className="text-[var(--landing-text-muted)] text-sm leading-relaxed max-w-md">
                      Paste raw hiring manager notes and let our agents architect the perfect Job
                      Description. Optimized for search and candidate conversion instantly.
                    </p>
                  </div>
                  {/* Visual representation */}
                  <div className="bg-white dark:bg-surface-dark rounded-lg p-4 border border-[var(--landing-glass-border)] font-mono text-xs text-slate-600 dark:text-slate-300 shadow-inner">
                    <div className="flex gap-2 mb-3">
                      <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                      <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                      <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
                    </div>
                    <p className="typing-effect text-emerald-500">&gt; Generating requirements...</p>
                    <p className="text-slate-500 mt-1">
                      Found: "Senior React Developer", "5+ YOE", "Remote"
                    </p>
                    <p className="text-slate-900 dark:text-white mt-2 font-semibold">Role: Senior Frontend Engineer</p>
                    <p className="text-slate-500 dark:text-slate-400">
                      We are seeking an experienced engineer to lead our frontend architecture...
                    </p>
                  </div>
                </div>
              </div>

              {/* Feature 2: Semantic Matching */}
              <div className="glass-card rounded-2xl p-8 relative overflow-hidden group">
                <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-emerald-500/10 to-transparent pointer-events-none"></div>
                <div className="relative z-10 flex flex-col h-full justify-between gap-6">
                  <div>
                    <div className="w-12 h-12 rounded-lg bg-emerald-500/20 text-emerald-500 flex items-center justify-center mb-4 border border-emerald-500/30">
                      <span className="material-symbols-outlined text-2xl">hub</span>
                    </div>
                    <h3 className="text-xl font-bold text-[var(--landing-text)] mb-2">Semantic Matching</h3>
                    <p className="text-[var(--landing-text-muted)] text-sm leading-relaxed">
                      Vector-based search that understands potential over keywords. We match based on
                      context, not just text overlap.
                    </p>
                  </div>
                  <div
                    className="h-32 w-full rounded-lg bg-cover bg-center opacity-60 mix-blend-overlay border border-[var(--landing-glass-border)]"
                    style={{
                      backgroundImage:
                        "url('https://images.unsplash.com/photo-1558494949-ef526b0042a0?q=80&w=2670&auto=format&fit=crop')",
                    }}
                    data-alt="Abstract network of connected dots representing vector embeddings"
                  ></div>
                </div>
              </div>

              {/* Feature 3: Voice Prescreening */}
              <div className="glass-card rounded-2xl p-8 relative overflow-hidden group">
                <div className="relative z-10 flex flex-col h-full justify-between gap-6">
                  <div>
                    <div className="w-12 h-12 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center mb-4 border border-rose-500/30">
                      <span className="material-symbols-outlined text-2xl">mic</span>
                    </div>
                    <h3 className="text-xl font-bold text-[var(--landing-text)] mb-2">Voice Prescreening</h3>
                    <p className="text-[var(--landing-text-muted)] text-sm leading-relaxed">
                      AI agents conduct first-round phone screens with real-time sentiment analysis
                      and technical vetting.
                    </p>
                  </div>
                  <div className="flex items-center justify-center h-24 gap-1">
                    <div className="w-1.5 bg-rose-500 h-8 rounded-full animate-[pulse_0.8s_ease-in-out_infinite]"></div>
                    <div className="w-1.5 bg-rose-500 h-12 rounded-full animate-[pulse_1.2s_ease-in-out_infinite]"></div>
                    <div className="w-1.5 bg-rose-500 h-16 rounded-full animate-[pulse_1s_ease-in-out_infinite]"></div>
                    <div className="w-1.5 bg-rose-500 h-10 rounded-full animate-[pulse_1.4s_ease-in-out_infinite]"></div>
                    <div className="w-1.5 bg-rose-500 h-6 rounded-full animate-[pulse_0.9s_ease-in-out_infinite]"></div>
                  </div>
                </div>
              </div>

              {/* Feature 4: Stateful Orchestration (Large) */}
              <div className="glass-card rounded-2xl p-8 md:col-span-2 relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-64 h-64 bg-blue-500/5 rounded-full blur-[80px] -ml-16 -mt-16 pointer-events-none"></div>
                <div className="relative z-10 flex flex-col md:flex-row h-full gap-8">
                  <div className="flex-1">
                    <div className="w-12 h-12 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center mb-4 border border-blue-500/30">
                      <span className="material-symbols-outlined text-2xl">account_tree</span>
                    </div>
                    <h3 className="text-xl font-bold text-[var(--landing-text)] mb-2">Stateful Orchestration</h3>
                    <p className="text-[var(--landing-text-muted)] text-sm leading-relaxed mb-6">
                      Full state management of every candidate interaction in real-time. Watch your
                      pipeline move itself.
                    </p>
                    <button className="text-sm font-bold text-[var(--landing-primary)] hover:text-[var(--landing-text)] flex items-center gap-1 transition-colors">
                      Explore the API{" "}
                      <span className="material-symbols-outlined text-sm">arrow_forward</span>
                    </button>
                  </div>
                  <div className="flex-1 bg-white dark:bg-surface-dark/50 rounded-xl border border-[var(--landing-glass-border)] p-4 flex flex-col gap-3 max-h-[220px] overflow-hidden relative shadow-sm">
                    <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-white dark:from-surface-dark to-transparent z-20"></div>
                    <div className="flex items-center gap-3 p-2 rounded bg-slate-50 dark:bg-white/5 border border-[var(--landing-glass-border)]">
                      <div className="size-2 rounded-full bg-green-500"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-slate-800 dark:text-white truncate">
                          Offer Extended: Sarah J.
                        </p>
                        <p className="text-[10px] text-slate-500">2 mins ago</p>
                      </div>
                      <span className="material-symbols-outlined text-slate-500 text-sm">
                        check_circle
                      </span>
                    </div>
                    <div className="flex items-center gap-3 p-2 rounded bg-white dark:bg-white/5 border border-[var(--landing-glass-border)]">
                      <div className="size-2 rounded-full bg-yellow-500 animate-pulse"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-slate-800 dark:text-white truncate">
                          Scheduling Interview: Mike R.
                        </p>
                        <p className="text-[10px] text-slate-500">5 mins ago</p>
                      </div>
                      <span className="material-symbols-outlined text-slate-500 text-sm">
                        schedule
                      </span>
                    </div>
                    <div className="flex items-center gap-3 p-2 rounded bg-white dark:bg-white/5 border border-[var(--landing-glass-border)] opacity-60">
                      <div className="size-2 rounded-full bg-slate-500"></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-slate-800 dark:text-white truncate">
                          Application Received: Davin C.
                        </p>
                        <p className="text-[10px] text-slate-500">12 mins ago</p>
                      </div>
                      <span className="material-symbols-outlined text-slate-500 text-sm">
                        inbox
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="relative py-20 px-4 md:px-20 text-center rounded-3xl border border-[var(--landing-glass-border)] overflow-hidden glass-card">
            <div className="absolute inset-0 bg-gradient-to-r from-[var(--landing-primary)]/10 via-purple-500/10 to-[var(--landing-primary)]/10 z-0"></div>
            <div className="relative z-10 flex flex-col items-center gap-6">
              <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-[var(--landing-text)] max-w-2xl">
                Ready to automate your <br /> recruiting pipeline?
              </h2>
              <p className="text-[var(--landing-text-muted)] text-lg max-w-lg">
                Join 500+ forward-thinking companies hiring with autonomous agents today.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 mt-4">
                <button className="bg-[var(--landing-btn-bg)] text-[var(--landing-btn-text)] font-bold px-8 py-3 rounded-lg hover:opacity-90 transition-colors shadow-lg">
                  Get Started Now
                </button>
                <button className="bg-transparent border border-[var(--landing-glass-border)] text-[var(--landing-text)] font-semibold px-8 py-3 rounded-lg hover:bg-white/5 transition-colors">
                  Talk to Sales
                </button>
              </div>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-20 border-t border-[var(--landing-glass-border)] pt-10 pb-10 bg-[var(--landing-footer-bg)] backdrop-blur-sm">
            <div className="flex flex-col md:flex-row justify-between gap-10">
              <div className="flex flex-col gap-4 max-w-xs">
                <div className="flex items-center gap-2">
                  <div className="size-6 text-white flex items-center justify-center bg-[var(--landing-primary)] rounded border border-[var(--landing-primary)]/20 shadow-sm">
                    <span className="material-symbols-outlined text-sm">smart_toy</span>
                  </div>
                  <span className="text-[var(--landing-text)] font-bold text-lg">AARLP</span>
                </div>
                <p className="text-[var(--landing-text-muted)] text-sm">
                  The first complete agentic workflow for modern recruiting teams. Design the future
                  of work.
                </p>
                <div className="flex gap-4 mt-2">
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] transition-colors" href="#">
                    <span className="material-symbols-outlined text-xl">dataset</span>
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] transition-colors" href="#">
                    <span className="material-symbols-outlined text-xl">hub</span>
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] transition-colors" href="#">
                    <span className="material-symbols-outlined text-xl">rss_feed</span>
                  </a>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8 w-full md:w-auto">
                <div className="flex flex-col gap-3">
                  <h4 className="text-[var(--landing-text)] font-semibold text-sm">Product</h4>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Agents
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Workflows
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Integrations
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Changelog
                  </a>
                </div>
                <div className="flex flex-col gap-3">
                  <h4 className="text-[var(--landing-text)] font-semibold text-sm">Resources</h4>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Documentation
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    API Reference
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Community
                  </a>
                </div>
                <div className="flex flex-col gap-3">
                  <h4 className="text-[var(--landing-text)] font-semibold text-sm">Company</h4>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    About
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Careers
                  </a>
                  <a className="text-[var(--landing-text-muted)] hover:text-[var(--landing-primary)] text-sm transition-colors" href="#">
                    Legal
                  </a>
                </div>
                <div className="flex flex-col gap-3">
                  <h4 className="text-[var(--landing-text)] font-semibold text-sm">Status</h4>
                  <div className="flex items-center gap-2">
                    <div className="size-2 rounded-full bg-green-500"></div>
                    <span className="text-[var(--landing-text-muted)] text-sm">All Systems Operational</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-12 pt-8 border-t border-white/5 text-center text-[var(--landing-text-muted)] text-sm">
              © 2024 AARLP Inc. All rights reserved.
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
