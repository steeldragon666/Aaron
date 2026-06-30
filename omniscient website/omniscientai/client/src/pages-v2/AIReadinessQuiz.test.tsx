/**
 * Smoke tests for the v2 AIReadinessQuiz page. Covers the wizard's three-step
 * flow: intro screen renders, Start button advances to the first question,
 * selection enables Next, advancing through all ten questions lands on the
 * result screen with a Book CTA, and Back returns to the previous question.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HelmetProvider } from 'react-helmet-async';
import AIReadinessQuiz from './AIReadinessQuiz';
import { QUIZ_QUESTIONS } from '@/lib/data';

function renderQuiz() {
  return render(
    <HelmetProvider>
      <AIReadinessQuiz />
    </HelmetProvider>,
  );
}

// Advance from intro into the question flow.
function startQuiz() {
  fireEvent.click(screen.getByRole('button', { name: /Start assessment/i }));
}

// Pick the first option (score=1) on the currently-rendered question,
// then click Next / See results.
function answerAndAdvance() {
  const radios = screen.getAllByRole('radio');
  fireEvent.click(radios[0]);
  const next = screen.getByTestId('next-button');
  fireEvent.click(next);
}

describe('AIReadinessQuiz page', () => {
  it('renders the intro screen initially with Start CTA', () => {
    renderQuiz();
    expect(
      screen.getByRole('heading', { level: 1, name: /AI Readiness Quiz/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Start assessment/i }),
    ).toBeInTheDocument();
  });

  it('clicking Start advances to the first question', () => {
    renderQuiz();
    startQuiz();
    expect(screen.getByText(/Question 1 of 10/i)).toBeInTheDocument();
    // The first question's text should now be on screen.
    expect(screen.getByText(QUIZ_QUESTIONS[0].question)).toBeInTheDocument();
  });

  it('Next is disabled until an option is selected', () => {
    renderQuiz();
    startQuiz();
    const next = screen.getByTestId('next-button') as HTMLButtonElement;
    expect(next.disabled).toBe(true);
    // After selecting the first radio option, Next becomes enabled.
    fireEvent.click(screen.getAllByRole('radio')[0]);
    expect(next.disabled).toBe(false);
  });

  it('Back is disabled on question 1', () => {
    renderQuiz();
    startQuiz();
    const back = screen.getByTestId('back-button') as HTMLButtonElement;
    expect(back.disabled).toBe(true);
  });

  it('Back on question > 1 returns to the previous question', () => {
    renderQuiz();
    startQuiz();
    // Answer Q1 and move to Q2.
    answerAndAdvance();
    expect(screen.getByText(/Question 2 of 10/i)).toBeInTheDocument();
    // Press Back — should land on Q1 again.
    fireEvent.click(screen.getByTestId('back-button'));
    expect(screen.getByText(/Question 1 of 10/i)).toBeInTheDocument();
  });

  it('advancing through all questions lands on the result screen', () => {
    renderQuiz();
    startQuiz();
    // Answer all 10 questions by selecting the first option (score=1) each time.
    for (let i = 0; i < QUIZ_QUESTIONS.length; i += 1) {
      answerAndAdvance();
    }
    // Result screen shows the "Result" eyebrow and a /100 score.
    expect(screen.getByText(/^Result$/i)).toBeInTheDocument();
    expect(screen.getByTestId('result-score')).toHaveTextContent('/100');
  });

  it('result screen shows the Book a diagnostic call CTA linking to /book', () => {
    renderQuiz();
    startQuiz();
    for (let i = 0; i < QUIZ_QUESTIONS.length; i += 1) {
      answerAndAdvance();
    }
    const bookLinks = screen.getAllByRole('link', {
      name: /Book a diagnostic call/i,
    });
    expect(
      bookLinks.some((link) => link.getAttribute('href') === '/book'),
    ).toBe(true);
  });
});
