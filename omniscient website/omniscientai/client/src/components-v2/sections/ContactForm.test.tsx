import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ContactForm } from './ContactForm';

function fillValid() {
  fireEvent.change(screen.getByLabelText(/Name/i), {
    target: { value: 'Jane Doe' },
  });
  fireEvent.change(screen.getByLabelText(/Email/i), {
    target: { value: 'jane@example.com' },
  });
  fireEvent.change(screen.getByLabelText(/Enquiry type/i), {
    target: { value: 'workshop' },
  });
  fireEvent.change(screen.getByLabelText(/Message/i), {
    target: {
      value: 'This is at least twenty characters of message content.',
    },
  });
}

describe('ContactForm', () => {
  it('renders all form fields', () => {
    const onSubmit = vi.fn();
    render(<ContactForm onSubmit={onSubmit} />);
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Company/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Enquiry type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Message/i)).toBeInTheDocument();
  });

  it('submit button is disabled until required fields filled', () => {
    const onSubmit = vi.fn();
    render(<ContactForm onSubmit={onSubmit} />);
    const submitBtn = screen.getByRole('button', { name: /Send/i });
    expect(submitBtn).toBeDisabled();

    fillValid();
    expect(submitBtn).not.toBeDisabled();
  });

  it('validates email format', () => {
    const onSubmit = vi.fn();
    render(<ContactForm onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'not-an-email' },
    });
    fireEvent.change(screen.getByLabelText(/Enquiry type/i), {
      target: { value: 'workshop' },
    });
    fireEvent.change(screen.getByLabelText(/Message/i), {
      target: {
        value: 'This is at least twenty characters of message content.',
      },
    });

    expect(screen.getByRole('button', { name: /Send/i })).toBeDisabled();
  });

  it('validates message minimum length', () => {
    const onSubmit = vi.fn();
    render(<ContactForm onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText(/Name/i), {
      target: { value: 'Jane' },
    });
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'jane@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Enquiry type/i), {
      target: { value: 'workshop' },
    });
    fireEvent.change(screen.getByLabelText(/Message/i), {
      target: { value: 'too short' },
    });

    expect(screen.getByRole('button', { name: /Send/i })).toBeDisabled();
  });

  it('calls onSubmit with form data', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<ContactForm onSubmit={onSubmit} />);
    fillValid();
    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Jane Doe',
          email: 'jane@example.com',
          enquiryType: 'workshop',
          message: 'This is at least twenty characters of message content.',
        }),
      );
    });
  });

  it('shows loading state during submit', async () => {
    let resolve!: () => void;
    const onSubmit = vi.fn(
      () => new Promise<void>((r) => { resolve = r; }),
    );
    render(<ContactForm onSubmit={onSubmit} />);
    fillValid();

    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Sending/i })).toBeDisabled();
    });

    await act(async () => {
      resolve();
    });
  });

  it('shows success state after submit', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<ContactForm onSubmit={onSubmit} />);
    fillValid();

    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await waitFor(() => {
      expect(screen.getByText(/Thanks for reaching out/i)).toBeInTheDocument();
    });
  });

  it('shows error message if submit rejects', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('Network down'));
    render(<ContactForm onSubmit={onSubmit} />);
    fillValid();

    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    // Form stays editable — the name input is still in the document.
    expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
  });

  it('passes through custom className', () => {
    const onSubmit = vi.fn();
    const { container } = render(
      <ContactForm onSubmit={onSubmit} className="custom-contact" />,
    );
    expect(container.querySelector('.custom-contact')).toBeTruthy();
  });
});
