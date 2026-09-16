import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import EvaluationFeedback from '../components/EvaluationFeedback';

describe('Evaluation Feedback Component Tests', () => {
  const mockFeedback = {
    overall_score: 85,
    attempt_number: 1,
    summary: 'Great explanation of memory allocation and heap vs stack principles.',
    strengths: [
      'Correctly identified stack frame lifecycle',
      'Accurate distinction between stack and heap memory',
    ],
    knowledge_gaps: [
      {
        concept: 'Garbage Collection Triggers',
        severity: 'HIGH',
        evidence: 'Did not detail mark-and-sweep thresholds',
      },
    ],
    dimensions: {
      technicalAccuracy: { score: 90, feedback: 'Highly accurate description of pointers' },
      conceptUnderstanding: { score: 85, feedback: 'Understands stack pointers well' },
      completeness: { score: 80, feedback: 'Covers most core principles' },
    },
    correct_version: 'The stack stores local primitives and reference pointers, while heap holds objects.',
    follow_up_question: 'How does stack overflow occur during deep recursion?',
    next_recommendation: {
      topic_id: 15,
      topic_name: 'Garbage Collection Algorithms',
      action_type: 'PRACTICE',
      reason: 'Bridge your identified gap in GC triggers.',
    },
    concept_coverage: {
      required_count: 4,
      covered_count: 3,
      coverage_percentage: 75.0,
      covered_concepts: ['Stack Memory', 'Heap Memory', 'Pointers'],
      missing_concepts: ['Mark and Sweep'],
      details: [
        { concept: 'Stack Memory', covered: true, matched_evidence: 'stack' },
        { concept: 'Heap Memory', covered: true, matched_evidence: 'heap' },
        { concept: 'Pointers', covered: true, matched_evidence: 'pointers' },
        { concept: 'Mark and Sweep', covered: false, matched_evidence: null }
      ]
    }
  };

  it('renders overall score, AI summary, strengths, dimensions breakdown, and knowledge gaps', () => {
    render(
      <MemoryRouter>
        <EvaluationFeedback
          feedback={mockFeedback}
          studentExplanation="Stack memory holds local function variables and call frames."
          onContinue={vi.fn()}
          onRetry={vi.fn()}
        />
      </MemoryRouter>
    );

    // Verify overall score percentage
    expect(screen.getAllByText('85%')[0]).toBeInTheDocument();

    // Verify AI summary
    expect(
      screen.getByText(/Great explanation of memory allocation and heap vs stack principles/i)
    ).toBeInTheDocument();

    // Verify strengths rendered
    expect(screen.getByText('Correctly identified stack frame lifecycle')).toBeInTheDocument();
    expect(
      screen.getByText('Accurate distinction between stack and heap memory')
    ).toBeInTheDocument();

    // Verify knowledge gap rendered
    expect(screen.getByText('Garbage Collection Triggers')).toBeInTheDocument();
    expect(screen.getByText('HIGH SEVERITY')).toBeInTheDocument();

    // Verify ideal answer
    expect(
      screen.getByText(
        /"The stack stores local primitives and reference pointers, while heap holds objects\."/i
      )
    ).toBeInTheDocument();

    // Verify follow-up question
    expect(
      screen.getByText('How does stack overflow occur during deep recursion?')
    ).toBeInTheDocument();
  });

  it('renders deterministic concept coverage section with covered and missing concepts', () => {
    render(
      <MemoryRouter>
        <EvaluationFeedback
          feedback={mockFeedback}
          studentExplanation="Stack memory explanation."
          onContinue={vi.fn()}
          onRetry={vi.fn()}
        />
      </MemoryRouter>
    );

    // Verify Concept Coverage heading and percentage
    expect(screen.getByText('Concept Coverage')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('3 / 4 concepts covered')).toBeInTheDocument();

    // Verify covered concepts
    expect(screen.getByText('✓ Stack Memory')).toBeInTheDocument();
    expect(screen.getByText('✓ Heap Memory')).toBeInTheDocument();

    // Verify missing concept
    expect(screen.getByText('• Mark and Sweep')).toBeInTheDocument();
  });

  it('triggers onContinue and onRetry callbacks when action buttons are clicked', () => {
    const handleContinue = vi.fn();
    const handleRetry = vi.fn();

    render(
      <MemoryRouter>
        <EvaluationFeedback
          feedback={mockFeedback}
          studentExplanation="Stack memory explanation."
          onContinue={handleContinue}
          onRetry={handleRetry}
        />
      </MemoryRouter>
    );

    const retryBtn = screen.getByRole('button', { name: /retry this topic/i });
    const continueBtn = screen.getByRole('button', { name: /continue next topic/i });

    fireEvent.click(retryBtn);
    expect(handleRetry).toHaveBeenCalledTimes(1);

    fireEvent.click(continueBtn);
    expect(handleContinue).toHaveBeenCalledTimes(1);
  });
});
