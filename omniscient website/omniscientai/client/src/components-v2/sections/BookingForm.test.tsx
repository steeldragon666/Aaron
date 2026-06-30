import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BookingForm } from './BookingForm';

const SERVICES = [
  { value: 'ai-readiness', label: 'AI Readiness Workshop · 2 days', description: 'For teams exploring AI' },
  { value: 'custom-training', label: 'Custom team training · Bespoke', description: 'Scoped to your workflow' },
  { value: 'exec-briefing', label: 'Executive briefing · Half-day', description: 'For leadership alignment' },
];

/**
 * Fills out step 1 (service selection) and advances to step 2.
 */
function goToStep2(user: typeof fireEvent) {
  user.click(screen.getByLabelText(/AI Readiness Workshop/i));
  user.click(screen.getByRole('button', { name: /Next/i }));
}

/**
 * Fills out step 2 (date) and advances to step 3. Assumes already on step 2.
 */
function goToStep3(user: typeof fireEvent) {
  const dateInput = screen.getByLabelText(/Preferred date/i) as HTMLInputElement;
  user.change(dateInput, { target: { value: '2026-06-01' } });
  user.click(screen.getByRole('button', { name: /Next/i }));
}

describe('BookingForm', () => {
  it('starts on step 1', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    expect(screen.getByText(/Step 1 of 3/i)).toBeInTheDocument();
  });

  it('renders service options as radio cards', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    expect(screen.getByLabelText(/AI Readiness Workshop/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Custom team training/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Executive briefing/i)).toBeInTheDocument();
  });

  it('disables Next button until a service is selected', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    const nextBtn = screen.getByRole('button', { name: /Next/i });
    expect(nextBtn).toBeDisabled();

    fireEvent.click(screen.getByLabelText(/AI Readiness Workshop/i));
    expect(nextBtn).not.toBeDisabled();
  });

  it('advances to step 2 when Next clicked with selection', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    expect(screen.getByText(/Step 2 of 3/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Preferred date/i)).toBeInTheDocument();
  });

  it('allows going back from step 2 to step 1', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    fireEvent.click(screen.getByRole('button', { name: /Back/i }));
    expect(screen.getByText(/Step 1 of 3/i)).toBeInTheDocument();
  });

  it('requires date on step 2', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    expect(screen.getByRole('button', { name: /Next/i })).toBeDisabled();
  });

  it('advances to step 3 with valid step 2', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    goToStep3(fireEvent);
    expect(screen.getByText(/Step 3 of 3/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
  });

  it('requires name, email, company on step 3', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    goToStep3(fireEvent);

    const submitBtn = screen.getByRole('button', { name: /Book|Submit/i });
    expect(submitBtn).toBeDisabled();

    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane Doe' },
    });
    expect(submitBtn).toBeDisabled();

    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'jane@example.com' },
    });
    expect(submitBtn).toBeDisabled();

    fireEvent.change(screen.getByLabelText(/Company/i), {
      target: { value: 'Acme Inc' },
    });
    expect(submitBtn).not.toBeDisabled();
  });

  it('calls onSubmit with collected data', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    goToStep3(fireEvent);

    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane Doe' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'jane@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Company/i), {
      target: { value: 'Acme Inc' },
    });

    fireEvent.click(screen.getByRole('button', { name: /Book|Submit/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          service: 'ai-readiness',
          date: '2026-06-01',
          name: 'Jane Doe',
          email: 'jane@example.com',
          company: 'Acme Inc',
        }),
      );
    });
  });

  it('shows success state after submit', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    goToStep3(fireEvent);

    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane Doe' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'jane@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Company/i), {
      target: { value: 'Acme Inc' },
    });

    fireEvent.click(screen.getByRole('button', { name: /Book|Submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/Thanks/i)).toBeInTheDocument();
    });
  });

  it('disables submit during async submit', async () => {
    let resolve!: () => void;
    const onSubmit = vi.fn(
      () => new Promise<void>((r) => { resolve = r; }),
    );
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    goToStep3(fireEvent);

    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane Doe' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'jane@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Company/i), {
      target: { value: 'Acme Inc' },
    });

    const submitBtn = screen.getByRole('button', { name: /Book|Submit/i });
    fireEvent.click(submitBtn);

    // Button should now be in loading state
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Booking/i })).toBeDisabled();
    });

    await act(async () => {
      resolve();
    });
  });

  it('validates email format on step 3', () => {
    const onSubmit = vi.fn();
    render(<BookingForm services={SERVICES} onSubmit={onSubmit} />);
    goToStep2(fireEvent);
    goToStep3(fireEvent);

    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'not-an-email' },
    });
    fireEvent.change(screen.getByLabelText(/Company/i), {
      target: { value: 'Acme' },
    });

    // Bad email blocks submit
    expect(screen.getByRole('button', { name: /Book|Submit/i })).toBeDisabled();
  });

  it('passes through custom className', () => {
    const onSubmit = vi.fn();
    const { container } = render(
      <BookingForm services={SERVICES} onSubmit={onSubmit} className="custom-booking" />,
    );
    expect(container.querySelector('.custom-booking')).toBeTruthy();
  });
});
