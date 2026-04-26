# Test Patterns — Frontend Developer

> Component and E2E testing strategies, mock patterns, and test organization with full examples.

---

## What to Test

| Category               | Test Strategy                              | Example                                   |
| ---------------------- | ------------------------------------------ | ----------------------------------------- |
| Component rendering    | Render with props, assert output           | Button renders label, shows icon          |
| User interactions      | Simulate click/type, assert state change   | Form submit triggers callback with data   |
| Conditional rendering  | Render with various props, assert presence  | Error message shown when `error` prop set |
| Hooks / composables    | Call with inputs, assert outputs            | `useDebounce` returns debounced value     |
| State transitions      | Trigger action, assert new state            | Auth store logout clears user             |
| Accessibility          | Check roles, labels, keyboard navigation    | Button has accessible name, form labels   |
| Error boundaries       | Throw in child, assert fallback renders     | Error boundary shows fallback UI          |

## What NOT to Test

- Framework internals (React reconciliation, Vue reactivity engine)
- Third-party library behavior (React Query caching, Zod validation logic)
- CSS visual output (use visual regression tools instead)
- Implementation details (internal state names, hook internals)
- Trivial components with no logic (a `<div>` wrapper with a class)

---

## Component Test Structure

```tsx
// path/to/your/components/ui/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders the label text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Click me</Button>);
    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledOnce();
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('applies variant class', () => {
    render(<Button variant="primary">Click me</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn--primary');
  });
});
```

**Rules**:

- Use `screen.getByRole` as first choice — matches how users find elements
- Use `userEvent` (not `fireEvent`) for realistic interaction simulation
- One assertion per test (or tightly related assertions)
- Descriptive test names: `it('shows error message when validation fails')`

---

## Testing Custom Hooks

```tsx
// path/to/your/hooks/useDebounce.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 300));
    expect(result.current).toBe('hello');
  });

  it('updates value after delay', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: 'hello' } },
    );

    rerender({ value: 'world' });
    expect(result.current).toBe('hello'); // Not yet updated

    act(() => { vi.advanceTimersByTime(300); });
    expect(result.current).toBe('world'); // Now updated
  });
});
```

---

## Testing Forms

```tsx
// path/to/your/components/features/CreateUserForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { CreateUserForm } from './CreateUserForm';

describe('CreateUserForm', () => {
  it('submits valid data', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(<CreateUserForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText('Name'), 'Jane Doe');
    await user.type(screen.getByLabelText('Email'), 'jane@example.com');
    await user.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        name: 'Jane Doe',
        email: 'jane@example.com',
        role: 'viewer',
      });
    });
  });

  it('shows validation errors for empty required fields', async () => {
    const user = userEvent.setup();
    render(<CreateUserForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
});
```

---

## Mocking API Calls

```tsx
// path/to/your/hooks/useUsers.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi } from 'vitest';
import { useUsers } from './useUsers';

// Mock the API layer — not the fetching library
vi.mock('@/lib/api/users', () => ({
  fetchUsers: vi.fn(),
}));

import { fetchUsers } from '@/lib/api/users';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe('useUsers', () => {
  it('returns user list on success', async () => {
    const mockUsers = [{ id: '1', name: 'Jane' }];
    vi.mocked(fetchUsers).mockResolvedValueOnce(mockUsers);

    const { result } = renderHook(() => useUsers(), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockUsers);
    });
  });

  it('returns error on failure', async () => {
    vi.mocked(fetchUsers).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useUsers(), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
  });
});
```

**Rules**:

- Mock at the API layer (service functions) — not at fetch/axios level
- Create fresh QueryClient per test to avoid shared cache
- Test loading, success, and error states
- Use `vi.mocked()` for type-safe mock assertions

---

## E2E Test Pattern (Playwright)

```tsx
// path/to/your/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Seed auth state or mock API
    await page.goto('/dashboard');
  });

  test('displays stats cards', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByText('Active users')).toBeVisible();
  });

  test('navigates to user list on card click', async ({ page }) => {
    await page.getByRole('button', { name: /active users/i }).click();
    await expect(page).toHaveURL('/users');
  });

  test('shows error state on API failure', async ({ page }) => {
    await page.route('**/api/stats', (route) =>
      route.fulfill({ status: 500, body: 'Server error' }),
    );
    await page.goto('/dashboard');
    await expect(page.getByText('Failed to load')).toBeVisible();
  });
});
```

**Rules**:

- Test user flows, not implementation details
- Use role-based selectors (`getByRole`) — matches accessibility
- Mock API at network level for error/edge-case testing
- Keep E2E tests focused — don't duplicate unit test coverage
