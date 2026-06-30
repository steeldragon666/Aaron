import { useState, type FormEvent } from 'react';
import { cn } from '@/lib/utils';
import {
  Card,
  Input,
  Textarea,
  RadioCard,
  MonoBadge,
  Lede,
} from '@/components-v2/ui';

/**
 * BookingForm — 3-step booking wizard.
 *
 * Used on the Book page and as a sticky sidebar on Workshop Detail. Plain
 * <button type="button"> elements drive step navigation (styled to match the
 * Button primitive's variants) and a final <button type="submit"> fires the
 * provided `onSubmit` async callback.
 *
 * Flow:
 *   1. Service selection — RadioCard group; Next disabled until one is picked.
 *   2. Preferred date + time window — `<input type="date">` and a RadioCard
 *      row for morning / afternoon / flexible.
 *   3. Contact + notes — name, email, company (required), phone + notes
 *      (optional). Submit fires the callback.
 *
 * On successful submit the form is replaced by a compact "Thanks" confirmation.
 * The submitting state disables the submit button and swaps its label to
 * "Booking..." until the caller resolves the promise.
 */

export interface BookingFormData {
  service: string;
  date: string;
  timePreference: string;
  name: string;
  email: string;
  company: string;
  phone?: string;
  notes?: string;
}

interface BookingFormProps {
  services: Array<{ value: string; label: string; description?: string }>;
  onSubmit: (data: BookingFormData) => Promise<void>;
  className?: string;
}

const TIME_OPTIONS = [
  { value: 'morning', label: 'Morning 9-12' },
  { value: 'afternoon', label: 'Afternoon 1-4' },
  { value: 'flexible', label: 'Flexible' },
];

// Shared button style fragments — mirror the Button primitive's variants but as
// plain <button>s so the wizard can toggle state without submitting the form.
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
const secondaryBtn = cn(
  buttonBase,
  'bg-paper text-ink border-[1.5px] border-ink hover:bg-paper-2',
);

// Minimal email regex — "something@something.something". Validation on the
// client side is advisory; the server still owns the canonical check.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function BookingForm({ services, onSubmit, className }: BookingFormProps) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<BookingFormData>({
    service: '',
    date: '',
    timePreference: 'flexible',
    name: '',
    email: '',
    company: '',
    phone: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  const update = <K extends keyof BookingFormData>(
    key: K,
    value: BookingFormData[K],
  ) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const step1Valid = Boolean(data.service);
  const step2Valid = Boolean(data.date);
  const step3Valid =
    Boolean(data.name) &&
    Boolean(data.email) &&
    EMAIL_RE.test(data.email) &&
    Boolean(data.company);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!step3Valid || submitting) return;
    setSubmitting(true);
    try {
      await onSubmit(data);
      setSucceeded(true);
    } finally {
      setSubmitting(false);
    }
  };

  if (succeeded) {
    return (
      <div className={cn('flex flex-col gap-4', className)} aria-live="polite">
        <Card tone="paper-2">
          <h3 className="font-semibold text-[22px] leading-tight text-ink">
            Thanks — we&apos;ll be in touch.
          </h3>
          <Lede className="mt-3">
            Your booking request is in. A named practitioner will reply within
            one business day with a calendar invite.
          </Lede>
        </Card>
      </div>
    );
  }

  const progressPct = (step / 3) * 100;

  return (
    <div className={cn('flex flex-col gap-6', className)} aria-live="polite">
      {/* Progress indicator */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <MonoBadge>Step {step} of 3</MonoBadge>
        </div>
        <div
          role="progressbar"
          aria-valuenow={step}
          aria-valuemin={1}
          aria-valuemax={3}
          className="h-1 w-full rounded-full bg-line overflow-hidden"
        >
          <div
            className="h-full bg-blue transition-all duration-[240ms] ease-[cubic-bezier(0.2,0.9,0.2,1)]"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Step body */}
      <Card tone="paper">
        {step === 1 && (
          <div className="flex flex-col gap-4">
            <h3 className="font-semibold text-[20px] leading-tight text-ink">
              What are you booking?
            </h3>
            <div className="flex flex-col gap-3">
              {services.map((svc) => (
                <RadioCard
                  key={svc.value}
                  name="service"
                  value={svc.value}
                  label={svc.label}
                  description={svc.description}
                  checked={data.service === svc.value}
                  onChange={(v) => update('service', v)}
                />
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="flex flex-col gap-5">
            <h3 className="font-semibold text-[20px] leading-tight text-ink">
              When suits you?
            </h3>
            <Input
              type="date"
              label="Preferred date"
              value={data.date}
              onChange={(e) => update('date', e.target.value)}
              required
            />
            <div className="flex flex-col gap-2">
              <span className="text-[14px] font-medium text-ink">
                Time preference
              </span>
              <div className="flex flex-col gap-3">
                {TIME_OPTIONS.map((opt) => (
                  <RadioCard
                    key={opt.value}
                    name="timePreference"
                    value={opt.value}
                    label={opt.label}
                    checked={data.timePreference === opt.value}
                    onChange={(v) => update('timePreference', v)}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <h3 className="font-semibold text-[20px] leading-tight text-ink">
              Your details
            </h3>
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
              label="Company *"
              type="text"
              value={data.company}
              onChange={(e) => update('company', e.target.value)}
              required
              autoComplete="organization"
            />
            <Input
              label="Phone"
              type="tel"
              value={data.phone}
              onChange={(e) => update('phone', e.target.value)}
              autoComplete="tel"
            />
            <Textarea
              label="Notes"
              rows={3}
              value={data.notes}
              onChange={(e) => update('notes', e.target.value)}
              placeholder="Anything you'd like us to know in advance"
            />

            <div className="mt-2 flex flex-wrap items-center gap-3">
              <button
                type="button"
                className={secondaryBtn}
                onClick={() => setStep(2)}
                disabled={submitting}
              >
                Back
              </button>
              <button
                type="submit"
                className={primaryBtn}
                disabled={!step3Valid || submitting}
              >
                {submitting ? 'Booking...' : 'Book session'}
                {!submitting && <span aria-hidden>→</span>}
              </button>
            </div>
          </form>
        )}
      </Card>

      {/* Step 1 / 2 navigation — step 3 owns its own nav inside the form */}
      {step !== 3 && (
        <div className="flex flex-wrap items-center gap-3">
          {step > 1 && (
            <button
              type="button"
              className={secondaryBtn}
              onClick={() => setStep((s) => s - 1)}
            >
              Back
            </button>
          )}
          <button
            type="button"
            className={primaryBtn}
            onClick={() => setStep((s) => s + 1)}
            disabled={step === 1 ? !step1Valid : !step2Valid}
          >
            Next
            <span aria-hidden>→</span>
          </button>
        </div>
      )}
    </div>
  );
}
