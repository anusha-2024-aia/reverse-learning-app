import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import api from '../api/axios';

vi.mock('../api/axios', () => {
  return {
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

describe('Dashboard Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with user metrics and learning intelligence when data loaded', async () => {
    const mockDashboardData = {
      user: { name: 'Feynman Learner' },
      summary: { overallScore: 82, streakDays: 5, totalEvaluations: 12 },
      aiInsight: { text: 'You show high proficiency in Data Structures.' },
      recommendedAction: { title: 'Review Graphs', description: 'Practice graph traversal' },
      strongestTopics: [{ id: 1, name: 'Array Operations', score: 95 }],
      weakestTopics: [{ id: 2, name: 'Dynamic Programming', score: 45 }],
      progress: [{ date: '2026-09-01', score: 75 }, { date: '2026-09-10', score: 82 }],
      recentActivity: [{ id: 101, topic_name: 'Binary Trees', score: 85, created_at: '2026-09-12' }],
      roadmapSummary: null,
      revisionSummary: null,
      resumeSummary: null,
    };

    const mockAdaptiveRec = {
      topic_id: 2,
      action_type: 'EXPLAIN',
      reason: 'Low previous score, foundational review needed',
      target_concept: 'Memoization',
      difficulty: 'INTERMEDIATE',
      topic: { id: 2, name: 'Dynamic Programming' },
    };

    api.get.mockImplementation((url) => {
      if (url === '/dashboard-data') {
        return Promise.resolve({ data: mockDashboardData });
      }
      if (url === '/adaptive-learning/recommendation') {
        return Promise.resolve({ data: mockAdaptiveRec });
      }
      return Promise.reject(new Error(`Unhandled GET endpoint: ${url}`));
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // Verify loading spinner initially or wait for content
    await waitFor(() => {
      expect(screen.getAllByText(/Dynamic Programming/i)[0]).toBeInTheDocument();
    });

    // Verify overall score displayed
    expect(
      screen.getByText((content, element) => element?.tagName.toLowerCase() === 'div' && element.textContent === '82%')
    ).toBeInTheDocument();

    // Verify adaptive focus displayed
    expect(screen.getByText(/Your Next Learning Step/i)).toBeInTheDocument();
    expect(screen.getByText(/Low previous score, foundational review needed/i)).toBeInTheDocument();
  });

  it('renders empty welcome state when overall score is 0 and no recent activity', async () => {
    const mockEmptyDashboard = {
      user: { name: 'New Student' },
      summary: { overallScore: 0 },
      recentActivity: [],
    };

    api.get.mockImplementation((url) => {
      if (url === '/dashboard-data') {
        return Promise.resolve({ data: mockEmptyDashboard });
      }
      if (url === '/adaptive-learning/recommendation') {
        return Promise.resolve({ data: null });
      }
      return Promise.reject(new Error(`Unhandled GET endpoint: ${url}`));
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Welcome to Reverse Learning/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Start First Evaluation/i)).toBeInTheDocument();
  });

  it('renders error retry banner when dashboard API fails', async () => {
    api.get.mockRejectedValue(new Error('Network Error'));

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Unable to load your learning data/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
});
