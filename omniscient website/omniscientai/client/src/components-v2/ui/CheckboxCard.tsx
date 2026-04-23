import { forwardRef, useId } from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CheckboxCardProps {
  name?: string;
  value: string;
  label: string;
  description?: string;
  checked?: boolean;
  defaultChecked?: boolean;
  onChange?: (value: string, checked: boolean) => void;
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

export const CheckboxCard = forwardRef<HTMLInputElement, CheckboxCardProps>(
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
          type="checkbox"
          name={name}
          value={value}
          checked={checked}
          defaultChecked={defaultChecked}
          disabled={disabled}
          onChange={(e) => onChange?.(value, e.target.checked)}
          aria-describedby={descriptionId}
          className="sr-only"
        />
        {/* Visual checkbox indicator: 18px square with Check icon when checked */}
        <span
          aria-hidden
          className={cn(
            'mt-0.5 flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-sm border',
            isChecked ? 'border-ink' : 'border-line',
          )}
        >
          {isChecked && <Check className="h-3 w-3 text-blue" strokeWidth={2.5} />}
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
CheckboxCard.displayName = 'CheckboxCard';
