import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import CurrentFocusCard from '../components/adaptive/CurrentFocusCard';

describe('Adaptive Learning Component Tests', () => {
  it('SCENARIO A — LOWER SCORE: renders foundation / review recommendation correctly', () => {
    const mockLowerScoreRec = {
      topic_id: 12,
      action_type: 'REVIEW',
      reason: 'Mastery score dropped below 50%. Foundational review recommended.',
      target_concept: 'Base Cases & Call Stacks',
      difficulty: 'BEGINNER',
      topic: { id: 12, name: 'Recursion Fundamentals' },
    };

    render(
      <MemoryRouter>
        <CurrentFocusCard recommendation={mockLowerScoreRec} />
      </MemoryRouter>
    );

    // Verify Action Type and Topic Name
    expect(screen.getByText('REVIEW')).toBeInTheDocument();
    expect(screen.getByText('Recursion Fundamentals')).toBeInTheDocument();

    // Verify Focus Concept
    expect(screen.getByText('Focus: Base Cases & Call Stacks')).toBeInTheDocument();

    // Verify Reason & Difficulty
    expect(
      screen.getByText('Mastery score dropped below 50%. Foundational review recommended.')
    ).toBeInTheDocument();
    expect(screen.getByText('BEGINNER')).toBeInTheDocument();
  });

  it('SCENARIO B — HIGHER SCORE: renders advanced / next-level recommendation correctly', () => {
    const mockHigherScoreRec = {
      topic_id: 88,
      action_type: 'MOVE_FORWARD',
      reason: 'Excellent overall score of 95%. Ready for next level algorithms.',
      target_concept: 'Shortest Path Optimizations',
      difficulty: 'ADVANCED',
      topic: { id: 88, name: 'Dijkstra & A* Pathfinding' },
    };

    render(
      <MemoryRouter>
        <CurrentFocusCard recommendation={mockHigherScoreRec} />
      </MemoryRouter>
    );

    // Verify Action Type and Topic Name
    expect(screen.getByText('MOVE_FORWARD')).toBeInTheDocument();
    expect(screen.getByText('Dijkstra & A* Pathfinding')).toBeInTheDocument();

    // Verify Focus Concept
    expect(screen.getByText('Focus: Shortest Path Optimizations')).toBeInTheDocument();

    // Verify Reason & Difficulty
    expect(
      screen.getByText('Excellent overall score of 95%. Ready for next level algorithms.')
    ).toBeInTheDocument();
    expect(screen.getByText('ADVANCED')).toBeInTheDocument();
  });
});
