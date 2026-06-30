import { useState, type FormEvent } from 'react';
import { Link } from 'wouter';
import { cn } from '@/lib/utils';
import {
  Card,
  Input,
  Textarea,
  Select,
  Lede,
} from '@/components-v2/ui';

/**
 * ContactForm — single-page contact form.
 *
 * Used on the Contact page. Fields sit inside a paper-2 Card so the form
 * stands out on the page's paper canvas. Validation is client-side advisory:
 * name, email, enquiry type, and a 20-char minimum message are required;
 * email format is checked with a light regex. The canonical check still
 * lives on the server.
 *
 * Submit states:
 *   - idle    — normal editable form
 *   - loading — submit button disabled, label swaps to "Sending..."
 *   - success — form swapped for a "Thanks" confirmation + link to /services
 *   - error   — inline alert above the form, form stays editable
 */

export interface ContactFormData {
  name: string;
  email: string;
  company?: string;
  enquiryType: string;
  message: string;
}

interface ContactFormProps {
  onSubmit: (data: ContactFormData) => Promise<void>;
  className?: string;
}

const ENQUIRY_OPTIONS = [
  { value: 'workshop', label: 'Workshop inquiry' },
  { value: 'consulting', label: 'Consulting engagement' },
  { value: 'speaking', label: 'Speaking/podcast' },
  { value: 'other', label: 'Other' },
];

const MESSAGE_MIN = 20;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const buttonBase =
  'inline-flex items-center gap-2 font-semibold rounded-md ' +
  'px-[22px] py-[14px] text-[15px] ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'cursor-pointer';

const primaryBtn = cn(buttonBase, 'bg-blue text-paper border-0 hover:bg-blue-deep');

export function ContactForm({ onSubmit, className }: ContactFormProps) {
  const [data, setData] = useState<ContactFormData>({
    name: '',
    email: '',
    company: '',
    enquiryType: '',
    message: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [succeeded, setSucceeded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = <K extends keyof ContactFormData>(
    key: K,
    value: ContactFormData[K],
  ) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const valid =
    Boolean(data.name) &&
    Boolean(data.email) &&
    EMAIL_RE.test(data.email) &&
    Boolean(data.enquiryType) &&
    data.message.trim().length >= MESSAGE_MIN;

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!valid || submitting) return;
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit(data);
      setSucceeded(true);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Something went wrong. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  if (succeeded) {
    return (
      <div className={cn('flex flex-col gap-4', className)} aria-live="polite">
        <Card tone="paper-2">
          <h3 className="font-semibold text-[22px] leading-tight text-ink">
            Thanks for reaching out.
          </h3>
          <Lede className="mt-3">
            We&apos;ll be in touch within 2 business days.
          </Lede>
          <div className="mt-4">
            <Link
              href="/services"
              className="text-blue font-semibold hover:underline"
            >
              Explore our services →
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col gap-3', className)}>
      <div aria-live="polite">
        {error && (
          <div
            role="alert"
            className="rounded-md border border-[#D94B4B] bg-[#FDECEC] px-4 py-3 text-[14px] text-[#D94B4B]"
          >
            {error}
          </div>
        )}
      </div>
      <Card tone="paper-2">
        <form className="flex flex-col gap-4" onSubmit={handleSubmit} noValidate>
          <Input
            label="Name *"
            type="text"
            value={data.name}
            onChange={(e) => update('name', e.target.value)}
            required
            autoComplete="name"
          />
          <Input
            label="Email *"
            type="email"
            value={data.email}
            onChange={(e) => update('email', e.target.value)}
            required
            autoComplete="email"
          />
          <Input
            label="Company"
            type="text"
            value={data.company}
            onChange={(e) => update('company', e.target.value)}
            autoComplete="organization"
          />
          <Select
            label="Enquiry type *"
            value={data.enquiryType}
            onChange={(e) => update('enquiryType', e.target.value)}
            required
          >
            <option value="" disabled>
              Choose one
            </option>
            {ENQUIRY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </Select>
          <Textarea
            label="Message *"
            rows={5}
            value={data.message}
            onChange={(e) => update('message', e.target.value)}
            required
            minLength={MESSAGE_MIN}
            hint={`At least ${MESSAGE_MIN} characters — tell us what you're working on.`}
          />

          <div className="mt-2">
            <button
              type="submit"
              className={primaryBtn}
              disabled={!valid || submitting}
            >
              {submitting ? 'Sending...' : 'Send message'}
              {!submitting && <span aria-hidden>→</span>}
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}
