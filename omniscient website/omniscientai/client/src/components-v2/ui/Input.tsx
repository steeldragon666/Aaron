import { InputHTMLAttributes, forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  id?: string;
  label?: string;
  hint?: string;
  error?: string;
}

const inputBase =
  'block w-full rounded-md border px-4 py-2 text-[15px] ' +
  'bg-paper text-ink placeholder:text-ink-3 ' +
  'transition-colors duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'disabled:opacity-40 disabled:cursor-not-allowed';

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ id: idProp, label, hint, error, className, ...rest }, ref) => {
    const generatedId = useId();
    const id = idProp ?? generatedId;
    const hasError = Boolean(error);

    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={id} className="text-[14px] font-medium text-ink">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          aria-invalid={hasError || undefined}
          aria-describedby={
            hasError ? `${id}-error` : hint ? `${id}-hint` : undefined
          }
          className={cn(
            inputBase,
            hasError ? 'border-[#D94B4B]' : 'border-line',
            className,
          )}
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
Input.displayName = 'Input';
