import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

type Variant = 'primary' | 'secondary' | 'ghost';
type Size = 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  arrow?: boolean;
}

const base =
  'inline-flex items-center gap-2 font-semibold rounded-md ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'cursor-pointer';

const variants: Record<Variant, string> = {
  primary: 'bg-blue text-paper border-0 hover:bg-blue-deep',
  secondary: 'bg-paper text-ink border-[1.5px] border-ink hover:bg-paper-2',
  ghost: 'bg-transparent text-ink border-0 hover:bg-paper-2',
};

const sizes: Record<Size, string> = {
  md: 'px-4 py-2 text-[14px]',
  lg: 'px-[22px] py-[14px] text-[15px]',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'lg', arrow, className, children, ...rest }, ref) => (
    <button
      ref={ref}
      className={cn(base, variants[variant], sizes[size], className)}
      {...rest}
    >
      {children}
      {arrow && <span aria-hidden>→</span>}
    </button>
  )
);
Button.displayName = 'Button';
