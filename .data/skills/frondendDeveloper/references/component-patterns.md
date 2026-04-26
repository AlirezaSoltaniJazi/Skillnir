# Component Patterns — Frontend Developer

> Full code examples for UI component patterns across modern frontend frameworks. Referenced from SKILL.md Key Patterns table.

---

## Standard Component Pattern (React TSX)

Components are typed functional components with a props interface:

```tsx
// path/to/your/components/ui/StatCard.tsx
import type { ReactNode } from 'react';

export interface StatCardProps {
  value: string | number;
  label: string;
  icon?: ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'error';
  onClick?: () => void;
}

export function StatCard({
  value,
  label,
  icon,
  color = 'primary',
  onClick,
}: StatCardProps) {
  return (
    <div
      className={`stat-card stat-card--${color} ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      {icon && <span className="stat-card__icon">{icon}</span>}
      <span className="stat-card__value">{value}</span>
      <span className="stat-card__label">{label}</span>
    </div>
  );
}
```

**Rules**:

- One component per file, filename matches component name (PascalCase)
- Props interface exported and named `{ComponentName}Props`
- Typed default values via destructuring defaults
- Accessibility: `role`, `tabIndex`, `onKeyDown` for clickable non-button elements
- Named export (not default) — default exports only for page-level route components

---

## Standard Component Pattern (Vue SFC)

```vue
<!-- path/to/your/components/ui/StatCard.vue -->
<script setup lang="ts">
interface Props {
  value: string | number;
  label: string;
  icon?: string;
  color?: 'primary' | 'success' | 'warning' | 'error';
  clickable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  clickable: false,
});

const emit = defineEmits<{
  click: [];
}>();
</script>

<template>
  <div
    :class="['stat-card', `stat-card--${props.color}`, { 'cursor-pointer': props.clickable }]"
    :role="props.clickable ? 'button' : undefined"
    :tabindex="props.clickable ? 0 : undefined"
    @click="props.clickable && emit('click')"
    @keydown.enter="props.clickable && emit('click')"
  >
    <span v-if="props.icon" class="stat-card__icon">{{ props.icon }}</span>
    <span class="stat-card__value">{{ props.value }}</span>
    <span class="stat-card__label">{{ props.label }}</span>
  </div>
</template>
```

**Rules**:

- `<script setup lang="ts">` for Composition API with TypeScript
- Props typed via `defineProps<Props>()` with `withDefaults` for defaults
- Events typed via `defineEmits<{ eventName: [payload] }>()`
- Template uses `:class` array syntax for conditional classes

---

## Composition Pattern — Slots/Children

React (children):
```tsx
export interface CardProps {
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function Card({ title, children, footer }: CardProps) {
  return (
    <div className="card">
      <div className="card__header">
        <h3>{title}</h3>
      </div>
      <div className="card__body">{children}</div>
      {footer && <div className="card__footer">{footer}</div>}
    </div>
  );
}
```

Vue (slots):
```vue
<template>
  <div class="card">
    <div class="card__header">
      <h3>{{ title }}</h3>
    </div>
    <div class="card__body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>
```

**Rules**:

- Prefer composition (children/slots) over prop-drilling for content
- Type `children` as `ReactNode` (React) or use named slots (Vue)
- Check for optional slots/children before rendering wrapper elements

---

## Custom Hook Pattern

```tsx
// path/to/your/hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

Vue composable equivalent:
```ts
// path/to/your/composables/useDebounce.ts
import { ref, watch, type Ref } from 'vue';

export function useDebounce<T>(source: Ref<T>, delay: number): Ref<T> {
  const debounced = ref(source.value) as Ref<T>;

  watch(source, (newVal) => {
    const timer = setTimeout(() => { debounced.value = newVal; }, delay);
    return () => clearTimeout(timer);
  });

  return debounced;
}
```

**Rules**:

- Prefix with `use` — always (`useAuth`, `useDebounce`, `usePagination`)
- Generic types where applicable (`<T>`)
- Cleanup side effects (clear timeouts, unsubscribe, abort controllers)
- Return typed values — never return `any`

---

## Error Boundary Pattern

```tsx
// path/to/your/components/ErrorBoundary.tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  fallback: ReactNode;
  children: ReactNode;
  onError?: (error: Error, info: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    this.props.onError?.(error, info);
  }

  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}
```

**Rules**:

- Wrap at route level — not around every component
- Provide meaningful fallback UI (not just "Something went wrong")
- Report errors to monitoring service via `onError` callback
- In Vue: use `onErrorCaptured`. In Angular: use `ErrorHandler`.

---

## Page / Route Component Pattern

```tsx
// path/to/your/pages/Dashboard.tsx (or app/dashboard/page.tsx for Next.js)
import { Suspense } from 'react';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { PageHeader } from '@/components/layout/PageHeader';
import { DashboardStats } from '@/components/features/DashboardStats';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';

export default function DashboardPage() {
  return (
    <main className="page page--dashboard">
      <PageHeader title="Dashboard" subtitle="Overview of your project" />
      <ErrorBoundary fallback={<p>Failed to load dashboard stats.</p>}>
        <Suspense fallback={<LoadingSkeleton />}>
          <DashboardStats />
        </Suspense>
      </ErrorBoundary>
    </main>
  );
}
```

**Rules**:

- Page components are default-exported (convention for file-based routing)
- Always include `<PageHeader>` or equivalent for consistent layout
- Wrap data-dependent sections in `ErrorBoundary` + `Suspense`
- Use semantic HTML (`<main>`, `<section>`, `<nav>`)
