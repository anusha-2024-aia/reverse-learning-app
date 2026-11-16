import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import MockInterview from '../pages/MockInterview';
import api from '../api/axios';

vi.mock('../api/axios', () => {
  return {
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

// Mock recharts ResponsiveContainer to avoid SVG measurement errors in jsdom
vi.mock('recharts', async () => {
  const original = await vi.importActual('recharts');
  return {
    ...original,
    ResponsiveContainer: ({ children }) => <div data-testid="mock-chart">{children}</div>,
  };
});

describe('MockInterview Component Communication Display Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays valid communication score of zero without suppressing it', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/resume/active') {
        return Promise.resolve({ data: { has_resume: false } });
      }
      if (url === '/interview/active') {
        return Promise.resolve({ data: { has_active: false } });
      }
      return Promise.reject(new Error(`Unhandled GET: ${url}`));
    });

    api.post.mockImplementation((url) => {
      if (url === '/interview/start') {
        return Promise.resolve({
          data: {
            interview_id: 999,
            question_id: 1,
            question: 'What is a closure in JavaScript?',
            current_step: 1,
            total_questions: 1,
            category: 'TECHNICAL',
            difficulty: 'MEDIUM',
          },
        });
      }
      if (url === '/interview/answer') {
        return Promise.resolve({
          data: {
            is_complete: true,
            current_step: 1,
            new_difficulty: 'MEDIUM',
            old_difficulty: 'MEDIUM',
            difficulty_change: 'MAINTAINED',
            eval_result: {
              overall_score: 80,
              feedback: 'Great technical answer.',
            },
            communication_analysis: {
              communication_score: 0,
              clarity_score: 0,
              grammar_score: 0,
              speaking_pace: 'Good',
              words_per_minute: 120,
              filler_word_count: 0,
            },
            report: {
              overall_score: 80,
              technical_score: 80,
              communication_score: 0,
              project_knowledge_score: 80,
              problem_solving_score: 80,
              ai_insight: 'Interview completed with full evaluation.',
              strengths: ['Clear explanation'],
              weaknesses: ['Add more concrete examples'],
              recommended_preparation: ['Review closures'],
              progression: [{ question_number: 1, difficulty: 'MEDIUM', score: 80 }],
              communication_summary: {
                total_answers_analyzed: 1,
                has_voice_data: true,
                average_communication_score: 0,
                average_clarity_score: 0,
                average_grammar_score: 0,
                average_vocabulary_score: 0,
                average_structure_score: 0,
                average_wpm: 120,
                overall_speaking_pace: 'Good',
                total_filler_words: 0,
                top_filler_words: [],
                grammar_improvements: [],
              },
            },
          },
        });
      }
      return Promise.reject(new Error(`Unhandled POST: ${url}`));
    });

    render(
      <MemoryRouter>
        <MockInterview />
      </MemoryRouter>
    );

    // Click start interview button
    const startBtn = await screen.findByRole('button', { name: /Start Adaptive Interview/i });
    fireEvent.click(startBtn);

    // Wait for active question
    const questionEl = await screen.findByText(/What is a closure in JavaScript\?/i);
    expect(questionEl).toBeInTheDocument();

    // Type answer
    const textarea = screen.getByPlaceholderText(/Explain your approach/i);
    fireEvent.change(textarea, { target: { value: 'A closure is a function bundled with its lexical environment.' } });

    // Submit answer
    const submitBtn = screen.getByRole('button', { name: /Submit & Generate Final Report/i });
    fireEvent.click(submitBtn);

    // Verify final report communication summary renders valid zero scores
    await waitFor(() => {
      expect(screen.getByText(/Overall Communication: 0%/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Clarity:/i)).toBeInTheDocument();
    expect(screen.getByText(/Grammar:/i)).toBeInTheDocument();
    expect(screen.getAllByText(/0%/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/~120 WPM/i)).toBeInTheDocument();
  });
});
