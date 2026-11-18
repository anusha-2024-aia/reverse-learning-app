import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import StitchLayout from '../components/layout/StitchLayout';
import Dashboard from '../pages/Dashboard';
import KnowledgeGaps from '../pages/KnowledgeGaps';
import StudyRoom from '../pages/StudyRoom';
import SmartRevision from '../pages/SmartRevision';
import ResumeIntelligence from '../pages/ResumeIntelligence';
import MockInterview from '../pages/MockInterview';
import VirtualStudyRoom from '../pages/VirtualStudyRoom';
import AnalyticsPage from '../pages/AnalyticsPage';
import ProfileSettings from '../pages/ProfileSettings';
import LoginPage from '../pages/LoginPage';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';

vi.mock('../api/axios', () => ({
    default: {
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
    }
}));

// Mock Recharts
vi.mock('recharts', async () => {
    const orig = await vi.importActual('recharts');
    return {
        ...orig,
        ResponsiveContainer: ({ children }) => <div data-testid="mock-chart">{children}</div>,
    };
});

describe('Navigation and User Experience Flow Tests', () => {
    const mockUser = { id: 1, name: 'Maya Lin', email: 'maya.lin@berkeley.edu' };
    const mockLogout = vi.fn();

    const renderWithContext = (initialPath = '/') => {
        return render(
            <AuthContext.Provider value={{ user: mockUser, isLoggedIn: true, logout: mockLogout }}>
                <MemoryRouter initialEntries={[initialPath]}>
                    <StitchLayout>
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/knowledge-gaps" element={<KnowledgeGaps />} />
                            <Route path="/study" element={<StudyRoom />} />
                            <Route path="/revision" element={<SmartRevision />} />
                            <Route path="/resume" element={<ResumeIntelligence />} />
                            <Route path="/interview" element={<MockInterview />} />
                            <Route path="/study-room" element={<VirtualStudyRoom />} />
                            <Route path="/analytics" element={<AnalyticsPage />} />
                            <Route path="/profile" element={<ProfileSettings />} />
                            <Route path="/login" element={<LoginPage />} />
                        </Routes>
                    </StitchLayout>
                </MemoryRouter>
            </AuthContext.Provider>
        );
    };

    beforeEach(() => {
        vi.clearAllMocks();
        api.get.mockImplementation((url) => {
            if (url === '/dashboard-data') {
                return Promise.resolve({
                    data: {
                        user: mockUser,
                        summary: { overallScore: 84, streakDays: 14, knowledgeGapCount: 3 },
                        weakestTopics: [{ name: 'Raft Consensus' }],
                        recentActivity: [{ id: 1, topic_name: 'Distributed Systems', score: 85 }],
                        adaptiveRecommendation: { topic_id: 1, topic: { name: 'Raft Consensus & Leader Election' }, reason: 'Midterm Prep' }
                    }
                });
            }
            if (url === '/knowledge-gaps') {
                return Promise.resolve({
                    data: {
                        gaps: [
                            { id: 1, topic_id: 1, topic_name: 'TLB Invalidation', severity: 'CRITICAL', mastery_score: 44, trend: 'DECLINING' }
                        ]
                    }
                });
            }
            if (url === '/curriculums') return Promise.resolve({ data: [] });
            if (url === '/topics') return Promise.resolve({ data: [] });
            if (url === '/revisions') {
                return Promise.resolve({
                    data: {
                        topics_due: 18,
                        today_mastered: 14,
                        retention_rate: 72,
                        due_queue: [{ id: 1, topic_name: 'QuickSort Worst-Case' }]
                    }
                });
            }
            if (url === '/resume/active') return Promise.resolve({ data: { has_resume: true, file_name: 'resume_maya.pdf' } });
            if (url === '/interview/active') return Promise.resolve({ data: { has_active: false } });
            if (url.startsWith('/analytics')) return Promise.resolve({ data: { summary: {}, scoreTrend: [] } });
            if (url === '/auth/profile') return Promise.resolve({ data: { name: 'Maya Lin', email: 'maya.lin@berkeley.edu' } });
            return Promise.resolve({ data: {} });
        });
    });

    it('TEST 1 & 7: renders all sidebar links and navigates Dashboard → Topic Exploration', async () => {
        renderWithContext('/');

        // Verify sections
        expect(screen.getByText('ACADEMIC HUB')).toBeInTheDocument();
        expect(screen.getByText('CAREER ENGINE')).toBeInTheDocument();
        expect(screen.getByText('ACCOUNT')).toBeInTheDocument();

        // Verify links exist
        expect(screen.getByRole('link', { name: /Dashboard/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Knowledge Diagnostic/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Topic Exploration/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Smart Revision Engine/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Resume Gap Audit/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /AI Mock Interview/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Virtual Study Room/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Learning Analytics/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Settings & Profile/i })).toBeInTheDocument();

        // Click Topic Exploration
        const topicLink = screen.getByRole('link', { name: /Topic Exploration/i });
        fireEvent.click(topicLink);

        await waitFor(() => {
            expect(screen.getByText(/Consensus Protocols/i)).toBeInTheDocument();
        });
    });

    it('TEST 2: navigates Topic Exploration → Knowledge Diagnostic', async () => {
        renderWithContext('/study');

        // Click Knowledge Diagnostic button in StudyRoom
        const diagnosticBtn = await screen.findByRole('button', { name: /Knowledge Diagnostic →/i });
        fireEvent.click(diagnosticBtn);

        await waitFor(() => {
            expect(screen.getByText(/Knowledge Diagnostic & Readiness/i)).toBeInTheDocument();
        });
    });

    it('TEST 3: navigates Dashboard → Smart Revision', async () => {
        renderWithContext('/');

        // Click Start Today / Review button in upcoming revisions
        const revisionLink = screen.getByRole('link', { name: /Smart Revision Engine/i });
        fireEvent.click(revisionLink);

        await waitFor(() => {
            expect(screen.getByText(/Smart Spaced Repetition Engine/i)).toBeInTheDocument();
        });
    });

    it('TEST 4: navigates Resume Gap Audit → AI Mock Interview', async () => {
        renderWithContext('/resume');

        const interviewBtn = await screen.findByRole('button', { name: /Practice Mock Interview →/i });
        fireEvent.click(interviewBtn);

        await waitFor(() => {
            expect(screen.getByText(/Software Engineer — Distributed Systems/i)).toBeInTheDocument();
        });
    });

    it('TEST 5: navigates Virtual Study Room → Dashboard', async () => {
        renderWithContext('/study-room');

        const backBtn = await screen.findByRole('button', { name: /Dashboard/i });
        fireEvent.click(backBtn);

        await waitFor(() => {
            expect(screen.getByText(/Cognitive Mastery Index/i)).toBeInTheDocument();
        });
    });

    it('TEST 6: navigates Learning Analytics → Dashboard', async () => {
        renderWithContext('/analytics');

        const backBtn = await screen.findByRole('button', { name: /Dashboard/i });
        fireEvent.click(backBtn);

        await waitFor(() => {
            expect(screen.getByText(/Cognitive Mastery Index/i)).toBeInTheDocument();
        });
    });

    it('TEST 8: Profile → Logout triggers auth logout', async () => {
        renderWithContext('/profile');

        const logoutButtons = screen.getAllByRole('button', { name: /logout/i });
        fireEvent.click(logoutButtons[0]);

        expect(mockLogout).toHaveBeenCalledTimes(1);
    });

    it('TEST 9: toggles desktop collapse state and mobile drawer', async () => {
        renderWithContext('/');

        // Toggle collapse
        const collapseBtn = screen.getByTitle(/Collapse sidebar/i);
        fireEvent.click(collapseBtn);

        // Sidebar is collapsed -> expand button available
        expect(screen.getByTitle(/Expand sidebar/i)).toBeInTheDocument();

        // Expand sidebar again
        fireEvent.click(screen.getByTitle(/Expand sidebar/i));
        expect(screen.getByText('ACADEMIC HUB')).toBeInTheDocument();

        // Mobile drawer open
        const hamburgerBtn = screen.getByLabelText(/Open navigation menu/i);
        fireEvent.click(hamburgerBtn);

        expect(screen.getByLabelText(/Close navigation drawer/i)).toBeInTheDocument();
    });
});
