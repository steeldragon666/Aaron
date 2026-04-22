import { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'id'> {
  id?: string;
  label?: string;
  hint?: string;
  error?: string;
  valueDisplay?: (value: number) => string;
  min: number;
  max: number;
}

const base =
  'w-full appearance-none bg-transparent cursor-pointer ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-4 ' +
  'disabled:opacity-40 disabled:cursor-not-allowed';

export const Slider = forwardRef<HTMLInputElement, SliderProps>(
  (
    {
      id: idProp,
      label,
      hint,
      error,
      valueDisplay,
      min,
      max,
      value,
      defaultValue,
      className,
      ...rest
    },
    ref,
  ) => {
    const generatedId = useId();
    const id = idProp ?? generatedId;
    const hasError = Boolean(error);

    const numericValue = Number(value ?? defaultValue ?? min);
    const percent = max > min ? ((numericValue - min) / (max - min)) * 100 : 0;
    const displayValue = valueDisplay ? valueDisplay(numericValue) : String(numericValue);

    const trackBackground = `linear-gradient(to right, var(--blue) 0%, var(--blue) ${percent}%, var(--line) ${percent}%, var(--line) 100%)`;

    return (
      <div className="flex flex-col gap-2">
        {label && (
          <div className="flex items-center justify-between gap-4">
            <label htmlFor={id} className="text-[14px] font-medium text-ink">
              {label}
            </label>
            <span className="mono-badge">{displayValue}</span>
          </div>
        )}
        <input
          ref={ref}
          id={id}
          type="range"
          min={min}
          max={max}
          value={value}
          defaultValue={defaultValue}
          aria-invalid={hasError || undefined}
          aria-describedby={
            hasError ? `${id}-error` : hint ? `${id}-hint` : undefined
          }
          className={cn(base, className)}
          style={{ background: trackBackground }}
          {...rest}
        />
        {hasError ? (
          <span id={`${id}-error`} className="text-[13px] text-[#D94B4B]">
            {error}
          </span>
        ) : hint ? (
          <span id={`${id}-hint`} className="text-[13px] text-ink-3">
            {hint}
          </span>
        ) : null}
      </div>
    );
  },
);
Slider.displayName = 'Slider';
