import { SelectHTMLAttributes, forwardRef, useId } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id'> {
  id?: string;
  label?: string;
  hint?: string;
  error?: string;
}

const selectBase =
  'block w-full appearance-none rounded-md border pl-4 pr-10 py-2 text-[15px] ' +
  'bg-paper text-ink ' +
  'transition-colors duration-[180ms] ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'disabled:opacity-40 disabled:cursor-not-allowed';

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ id: idProp, label, hint, error, className, children, ...rest }, ref) => {
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
        <div className="relative">
          <select
            ref={ref}
            id={id}
            aria-invalid={hasError || undefined}
            aria-describedby={
              hasError ? `${id}-error` : hint ? `${id}-hint` : undefined
            }
            className={cn(
              selectBase,
              hasError ? 'border-[#D94B4B]' : 'border-line',
              className,
            )}
            {...rest}
          >
            {children}
          </select>
          <ChevronDown
            aria-hidden
            className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-3"
          />
        </div>
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
Select.displayName = 'Select';
