import { forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';

interface RadioCardProps {
  name: string;
  value: string;
  label: string;
  description?: string;
  checked?: boolean;
  defaultChecked?: boolean;
  onChange?: (value: string) => void;
  disabled?: boolean;
  className?: string;
  id?: string;
}

const labelBase =
  'relative flex items-start gap-3 p-4 rounded-lg bg-paper ' +
  'cursor-pointer transition-shadow duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:shadow-[0_1px_2px_rgb(15_17_21_/_0.06),_0_1px_1px_rgb(15_17_21_/_0.04)] ' +
  'has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-blue-glow has-[:focus-visible]:outline-offset-2 ' +
  'has-[:disabled]:opacity-40 has-[:disabled]:cursor-not-allowed ' +
  'has-[:disabled]:hover:shadow-none';

export const RadioCard = forwardRef<HTMLInputElement, RadioCardProps>(
  (
    {
      id: idProp,
      name,
      value,
      label,
      description,
      checked,
      defaultChecked,
      onChange,
      disabled,
      className,
    },
    ref,
  ) => {
    const generatedId = useId();
    const id = idProp ?? generatedId;
    const descriptionId = description ? `${id}-desc` : undefined;

    // Visual selected state reflects checked prop (controlled) or defaultChecked
    // (uncontrolled). Uncontrolled toggles won't visually update without a
    // wrapper state, which matches the controlled-first intent of the quiz.
    const isChecked = checked ?? defaultChecked ?? false;

    return (
      <label
        htmlFor={id}
        className={cn(
          labelBase,
          isChecked ? 'border-[1.5px] border-ink' : 'border border-line',
          className,
        )}
      >
        <input
          ref={ref}
          id={id}
          type="radio"
          name={name}
          value={value}
          checked={checked}
          defaultChecked={defaultChecked}
          disabled={disabled}
          onChange={(e) => onChange?.(e.target.value)}
          aria-describedby={descriptionId}
          className="sr-only"
        />
        {/* Visual radio indicator: 18px ring with 10px disc when checked */}
        <span
          aria-hidden
          className={cn(
            'mt-0.5 flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-full border',
            isChecked ? 'border-ink' : 'border-line',
          )}
        >
          {isChecked && <span className="h-2.5 w-2.5 rounded-full bg-blue" />}
        </span>
        <span className="flex-1">
          <span className="block text-ink font-medium">{label}</span>
          {description && (
            <span
              id={descriptionId}
              className="mt-1 block text-[14px] text-ink-3"
            >
              {description}
            </span>
          )}
        </span>
      </label>
    );
  },
);
RadioCard.displayName = 'RadioCard';
