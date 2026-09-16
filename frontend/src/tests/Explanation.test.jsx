import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import StudyRoom from '../pages/StudyRoom';
import api from '../api/axios';

vi.mock('../api/axios', () => {
  return {
    default: {
      get: vi.fn(),
      post: vi.fn(),
    },
  };
});

describe('Explanation Flow Tests in StudyRoom', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('allows user to select topic, type explanation text, submit and triggers evaluation API call with loading state', async () => {
    const mockCurricula = [{ id: 1, name: 'Computer Science Core' }];
    const mockTopics = [
      { id: 10, name: 'Recursion and Stack Frames', category: 'Algorithms', description: 'Understanding call stacks and base cases.' },
    ];

    api.get.mockImplementation((url) => {
      if (url === '/curricula') {
        return Promise.resolve({ data: { curricula: mockCurricula } });
      }
      if (url === '/topics') {
        return Promise.resolve({ data: { topics: mockTopics } });
      }
      if (url === '/topics/10') {
        return Promise.resolve({ data: mockTopics[0] });
      }
      return Promise.reject(new Error(`Unhandled GET: ${url}`));
    });

    let resolveEvaluate;
    const evaluatePromise = new Promise((resolve) => {
      resolveEvaluate = resolve;
    });
    api.post.mockReturnValueOnce(evaluatePromise);

    render(
      <MemoryRouter>
        <StudyRoom />
      </MemoryRouter>
    );

    // Wait for topic dropdown to populate
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /1\. Recursion and Stack Frames/i })).toBeInTheDocument();
    });

    // Select topic
    const topicSelect = screen.getByLabelText(/^Topic$/i);
    fireEvent.change(topicSelect, { target: { value: '10' } });

    // Wait for topic details to load
    await waitFor(() => {
      expect(screen.getByText(/Topic: Recursion and Stack Frames/i)).toBeInTheDocument();
    });

    // Enter explanation text (> 10 chars)
    const textarea = screen.getByPlaceholderText(/Start explaining Recursion and Stack Frames here\.\.\./i);
    const userExplanation = 'Recursion is a method where the solution to a problem depends on solutions to smaller instances of the same problem.';
    fireEvent.change(textarea, { target: { value: userExplanation } });

    expect(textarea.value).toBe(userExplanation);

    // Click Submit
    const submitButton = screen.getByRole('button', { name: /submit for evaluation/i });
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);

    // Verify loading state is shown
    expect(screen.getByRole('button', { name: /evaluating\.\.\./i })).toBeInTheDocument();

    // Verify API called with exact parameters
    expect(api.post).toHaveBeenCalledWith('/evaluate', {
      topic_id: 10,
      topic: 'Recursion and Stack Frames',
      explanation: userExplanation,
      learning_mode: 'technical',
    });

    // Resolve evaluate call to complete test cleanly
    resolveEvaluate({
      data: {
        overall_score: 90,
        summary: 'Excellent explanation of recursive principles.',
        strengths: ['Identified base cases', 'Clear stack framing'],
      },
    });
  });
});
