# Code Style — Frontend Developer

> TypeScript conventions, import order, formatting rules, and naming with full examples.

---

## Import Order

Four groups, separated by blank lines:

```tsx
// 1. Node built-ins (rare in frontend, but possible)
import { readFileSync } from 'node:fs';

// 2. Third-party packages
import { useQuery } from '@tanstack/react-query';
import { z } from 'zod';
import clsx from 'clsx';

// 3. Aliased local imports
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/hooks/useAuth';
import type { User } from '@/types/user';

// 4. Relative imports (co-located files only)
import { formatPrice } from './utils';
import styles from './ProductCard.module.css';
```

**Rules**:

- Node built-ins first (use `node:` prefix)
- Third-party packages second
- Aliased local (`@/`, `~/`, `#/`) imports third
- Relative imports last (only for co-located files)
- Separate type-only imports: `import type { X } from 'y'`
- Never use wildcard imports (`import * as`)
- Never use side-effect-only imports without comment justifying why

---

## TypeScript Conventions

```tsx
// ✅ Correct — typed props interface
export interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: ReactNode;
  onClick?: () => void;
}

// ✅ Correct — discriminated union for complex state
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

// ✅ Correct — generic utility type
type ApiResponse<T> = {
  data: T;
  meta: { page: number; total: number };
};

// ❌ Wrong — using `any`
const data: any = fetchData(); // Use proper type or `unknown`

// ❌ Wrong — suppressing errors
// @ts-ignore
const result = unsafeOperation(); // Fix the type instead
```

**Rules**:

- Use `interface` for object shapes (extendable), `type` for unions/intersections
- Prefer union types over enums (`'sm' | 'md' | 'lg'` not `enum Size {}`)
- Use `unknown` instead of `any` when type is truly unknown — then narrow
- Use `satisfies` operator for type-safe object literals
- Generic types for reusable utilities (`ApiResponse<T>`, `AsyncState<T>`)

---

## Component File Template

```tsx
// path/to/your/components/ui/ComponentName.tsx

import type { ReactNode } from 'react';
import clsx from 'clsx';

export interface ComponentNameProps {
  /** Primary content */
  title: string;
  /** Optional secondary text */
  subtitle?: string;
  /** Visual variant */
  variant?: 'default' | 'outlined' | 'filled';
  /** Content projection */
  children?: ReactNode;
}

export function ComponentName({
  title,
  subtitle,
  variant = 'default',
  children,
}: ComponentNameProps) {
  return (
    <div className={clsx('component-name', `component-name--${variant}`)}>
      <h3 className="component-name__title">{title}</h3>
      {subtitle && (
        <p className="component-name__subtitle">{subtitle}</p>
      )}
      {children && (
        <div className="component-name__content">{children}</div>
      )}
    </div>
  );
}
```

---

## Naming Conventions

| Entity           | Convention                         | Example                              |
| ---------------- | ---------------------------------- | ------------------------------------ |
| Component file   | PascalCase + extension             | `StatCard.tsx`, `StatCard.vue`       |
| Component name   | PascalCase                         | `StatCard`, `UserProfile`            |
| Props interface  | PascalCase + `Props`               | `StatCardProps`, `UserProfileProps`  |
| Hook / composable| camelCase with `use` prefix        | `useAuth`, `useDebounce`            |
| Utility file     | camelCase                          | `formatDate.ts`, `parseQuery.ts`     |
| Constant         | SCREAMING_SNAKE_CASE               | `API_BASE_URL`, `MAX_RETRIES`       |
| Type alias       | PascalCase                         | `AsyncState`, `ApiResponse`          |
| CSS module        | camelCase in JS, kebab-case in CSS | `styles.cardBody` → `.card-body`    |
| CSS class         | kebab-case (BEM or utility)        | `stat-card__label`, `text-primary`  |
| Route path        | kebab-case                         | `/user-profile`, `/dashboard`       |
| Event handler     | `on` + noun + verb or `handle` prefix | `onSubmit`, `handleDelete`       |
| Boolean prop      | `is`/`has`/`can`/`should` prefix   | `isDisabled`, `hasError`, `canEdit` |

---

## Conditional Classes

Use a utility like `clsx` or `classnames` — never string concatenation:

```tsx
// ✅ Correct — clsx for conditional classes
import clsx from 'clsx';

<div className={clsx(
  'card',
  variant === 'outlined' && 'card--outlined',
  isActive && 'card--active',
  className, // allow consumer to extend
)} />

// ❌ Wrong — string concatenation
<div className={`card ${isActive ? 'card--active' : ''}`} />

// ❌ Wrong — ternary for multiple conditions
<div className={`card ${variant === 'outlined' ? 'card--outlined' : ''} ${isActive ? 'card--active' : ''}`} />
```

---

## Tailwind CSS Conventions (if used)

```tsx
// ✅ Correct — utility-first, logical grouping
<div className="flex items-center gap-3 rounded-lg bg-white p-4 shadow-sm dark:bg-gray-800">
  <span className="text-2xl font-bold text-gray-900 dark:text-white">{value}</span>
  <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
</div>

// ✅ Correct — extract common patterns to components, not @apply
export function Badge({ children, color }: BadgeProps) {
  return (
    <span className={clsx(
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
      COLOR_CLASSES[color],
    )}>
      {children}
    </span>
  );
}

// ❌ Wrong — @apply for everything (defeats utility-first purpose)
// .badge { @apply inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium; }
```

**Class order**: Layout → Spacing → Size → Typography → Colors → Effects → Responsive → Dark mode

---

## JSDoc Conventions

```tsx
/**
 * Displays a key metric with optional trend indicator.
 *
 * @example
 * <StatCard value="1,234" label="Active users" trend="up" />
 */
export function StatCard({ value, label, trend }: StatCardProps) { ... }
```

- JSDoc on exported components and hooks
- `@example` with usage snippet for complex components
- Props documented via interface comments (`/** description */`)
