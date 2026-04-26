/**
 * One-line description of the component.
 *
 * @example
 * <ComponentName title="Hello" variant="primary" />
 */

import type { ReactNode } from 'react';
import clsx from 'clsx';

// ── Types ──────────────────────────────────────────────

export interface ComponentNameProps {
  /** Primary text content */
  title: string;
  /** Optional secondary text */
  subtitle?: string;
  /** Visual variant */
  variant?: 'default' | 'primary' | 'outlined';
  /** Content projection */
  children?: ReactNode;
  /** Optional click handler — makes the component interactive */
  onClick?: () => void;
  /** Additional CSS classes from consumer */
  className?: string;
}

// ── Constants ──────────────────────────────────────────

const VARIANT_CLASSES = {
  default: 'bg-white border border-gray-200 dark:bg-gray-800 dark:border-gray-700',
  primary: 'bg-indigo-50 border border-indigo-200 dark:bg-indigo-900/20 dark:border-indigo-800',
  outlined: 'bg-transparent border-2 border-gray-300 dark:border-gray-600',
} as const;

// ── Component ──────────────────────────────────────────

export function ComponentName({
  title,
  subtitle,
  variant = 'default',
  children,
  onClick,
  className,
}: ComponentNameProps) {
  const isInteractive = !!onClick;

  return (
    <div
      className={clsx(
        'rounded-lg p-4 transition-shadow',
        VARIANT_CLASSES[variant],
        isInteractive && 'cursor-pointer hover:shadow-md',
        className,
      )}
      onClick={onClick}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      onKeyDown={
        isInteractive
          ? (e) => { if (e.key === 'Enter' || e.key === ' ') onClick(); }
          : undefined
      }
    >
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        {title}
      </h3>
      {subtitle && (
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {subtitle}
        </p>
      )}
      {children && (
        <div className="mt-3">{children}</div>
      )}
    </div>
  );
}
