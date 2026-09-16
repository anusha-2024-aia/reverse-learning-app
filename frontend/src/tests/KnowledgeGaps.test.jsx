import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import KnowledgeGaps from '../pages/KnowledgeGaps';
import api from '../api/axios';

vi.mock('../api/axios', () => {
  return {
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

describe('Knowledge Gaps Page Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders weakest topic flagged as CRITICAL knowledge gap with recommendation and metrics', async () => {
    const mockGaps = [
      {
        topic_id: 101,
        topic_name: 'Dynamic Programming & Memoization',
        severity: 'CRITICAL',
        mastery_score: 32,
        recent_score: 25,
        average_score: 35,
        attempts: 4,
        trend: 'DECLINING',
        recommendation: 'Break down subproblems and draw state transition tables before coding.',
      },
      {
        topic_id: 102,
        topic_name: 'Array Traversal',
        severity: 'LOW',
        mastery_score: 88,
        recent_score: 90,
        average_score: 86,
        attempts: 5,
        trend: 'IMPROVING',
        recommendation: 'Solid understanding demonstrated.',
      },
    ];

    api.get.mockResolvedValueOnce({
      data: { gaps: mockGaps },
    });

    render(
      <MemoryRouter>
        <KnowledgeGaps />
      </MemoryRouter>
    );

    // Wait for gaps to render
    await waitFor(() => {
      expect(screen.getByText('Dynamic Programming & Memoization')).toBeInTheDocument();
    });

    // Verify weakest topic details
    expect(screen.getAllByText('CRITICAL')[1]).toBeInTheDocument();
    expect(screen.getByText('32%')).toBeInTheDocument();
    expect(
      screen.getByText('Break down subproblems and draw state transition tables before coding.')
    ).toBeInTheDocument();
  });

  it('filters knowledge gaps by severity when filter buttons are clicked', async () => {
    const mockGaps = [
      {
        topic_id: 101,
        topic_name: 'Dynamic Programming',
        severity: 'CRITICAL',
        mastery_score: 30,
        recent_score: 20,
        average_score: 35,
        attempts: 2,
        trend: 'DECLINING',
        recommendation: 'Practice subproblems',
      },
      {
        topic_id: 102,
        topic_name: 'Graph Traversal',
        severity: 'HIGH',
        mastery_score: 55,
        recent_score: 50,
        average_score: 58,
        attempts: 3,
        trend: 'STABLE',
        recommendation: 'Review BFS queue management',
      },
    ];

    api.get.mockResolvedValueOnce({
      data: { gaps: mockGaps },
    });

    render(
      <MemoryRouter>
        <KnowledgeGaps />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Dynamic Programming')).toBeInTheDocument();
      expect(screen.getByText('Graph Traversal')).toBeInTheDocument();
    });

    // Click CRITICAL filter button
    const criticalFilterBtn = screen.getByRole('button', { name: /^CRITICAL$/i });
    fireEvent.click(criticalFilterBtn);

    // Should only show Dynamic Programming
    expect(screen.getByText('Dynamic Programming')).toBeInTheDocument();
    expect(screen.queryByText('Graph Traversal')).not.toBeInTheDocument();
  });
});
