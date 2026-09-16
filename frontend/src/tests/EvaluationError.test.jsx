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

describe('Evaluation API Error Handling Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const setupStudyRoom = async () => {
    api.get.mockImplementation((url) => {
      if (url === '/curricula') return Promise.resolve({ data: { curricula: [{ id: 1, name: 'CS' }] } });
      if (url === '/topics') return Promise.resolve({ data: { topics: [{ id: 5, name: 'Binary Trees', category: 'Data Structures' }] } });
      if (url === '/topics/5') return Promise.resolve({ data: { id: 5, name: 'Binary Trees', category: 'Data Structures' } });
      return Promise.reject(new Error(`Unhandled: ${url}`));
    });

    render(
      <MemoryRouter>
        <StudyRoom />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('option', { name: /1\. Binary Trees/i })).toBeInTheDocument();
    });

    const topicSelect = screen.getByLabelText(/^Topic$/i);
    fireEvent.change(topicSelect, { target: { value: '5' } });

    await waitFor(() => {
      expect(screen.getByText(/Topic: Binary Trees/i)).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(/Start explaining Binary Trees here\.\.\./i);
    fireEvent.change(textarea, { target: { value: 'A binary tree is a tree data structure in which each node has at most two children.' } });
  };

  it('handles HTTP 500 server error gracefully without crashing and displays clean error message', async () => {
    await setupStudyRoom();

    api.post.mockRejectedValueOnce({
      response: {
        status: 500,
        data: { detail: 'Internal AI evaluation service error. Please try again later.' },
      },
    });

    const submitButton = screen.getByRole('button', { name: /submit for evaluation/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Internal AI evaluation service error. Please try again later.')).toBeInTheDocument();
    });

    // Verify button goes back to enabled submit state
    expect(screen.getByRole('button', { name: /submit for evaluation/i })).not.toBeDisabled();
  });

  it('handles HTTP 429 rate limit error gracefully and displays rate limit warning', async () => {
    await setupStudyRoom();

    api.post.mockRejectedValueOnce({
      response: {
        status: 429,
        data: { detail: 'Too many requests. Please wait a moment and try again.' },
      },
    });

    const submitButton = screen.getByRole('button', { name: /submit for evaluation/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Too many requests. Please wait a moment and try again./i)).toBeInTheDocument();
    });

    // Verify application did not crash and state remains intact
    expect(screen.getByPlaceholderText(/Start explaining Binary Trees here\.\.\./i)).toBeInTheDocument();
  });
});
