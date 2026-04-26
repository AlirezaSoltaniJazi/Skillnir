# State Patterns — Frontend Developer

> State management and data fetching patterns with full examples across frameworks.

---

## State Location Decision Tree

| State Type       | Where It Lives                        | Example                          |
| ---------------- | ------------------------------------- | -------------------------------- |
| UI-only          | Component-local (`useState`/`ref`)    | Modal open/close, input value    |
| Shared UI        | Context / Composable / Service        | Theme, sidebar collapsed         |
| Server cache     | Data-fetching library (React Query)   | API responses, list data         |
| Global app       | State manager (Zustand/Pinia/NgRx)    | Auth user, feature flags         |
| URL-derived      | URL search params / route params      | Filters, pagination, sort order  |
| Persistent       | localStorage + state sync             | User preferences, onboarding     |

**Rules**:

- Default to the simplest option — component-local first
- Lift state only when two+ components need it
- Server state belongs in a caching layer — not in global store
- URL state for anything a user should be able to bookmark or share

---

## Component-Local State

React:
```tsx
import { useState, useCallback } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  const increment = useCallback(() => {
    setCount((prev) => prev + 1);
  }, []);

  return (
    <button onClick={increment} aria-label={`Count: ${count}. Click to increment.`}>
      {count}
    </button>
  );
}
```

Vue:
```vue
<script setup lang="ts">
import { ref } from 'vue';

const count = ref(0);
const increment = () => { count.value++; };
</script>

<template>
  <button @click="increment" :aria-label="`Count: ${count}. Click to increment.`">
    {{ count }}
  </button>
</template>
```

---

## Server State with React Query

```tsx
// path/to/your/hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchUsers, createUser } from '@/lib/api/users';
import type { User, CreateUserInput } from '@/types/user';

export function useUsers() {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: fetchUsers,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation<User, Error, CreateUserInput>({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

Usage in component:
```tsx
export function UserList() {
  const { data: users, isLoading, error } = useUsers();
  const createUser = useCreateUser();

  if (isLoading) return <LoadingSkeleton />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <ul role="list">
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

**Rules**:

- Define `queryKey` as a structured array: `['entity', { filters }]`
- Set `staleTime` based on data freshness needs
- Invalidate related queries on mutations
- Handle loading/error/success states — never just `data`

---

## Global State with Zustand (React)

```tsx
// path/to/your/store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (user: User, token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      login: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
      isAuthenticated: () => get().token !== null,
    }),
    { name: 'auth-storage' },
  ),
);
```

## Global State with Pinia (Vue)

```ts
// path/to/your/store/auth.ts
import { defineStore } from 'pinia';
import type { User } from '@/types/user';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);

  const isAuthenticated = computed(() => token.value !== null);

  function login(newUser: User, newToken: string) {
    user.value = newUser;
    token.value = newToken;
  }

  function logout() {
    user.value = null;
    token.value = null;
  }

  return { user, token, isAuthenticated, login, logout };
});
```

**Rules**:

- Keep stores small and focused (one per domain: auth, cart, ui)
- Derive computed values — never duplicate state
- Typed store interface — never use `any`
- Use middleware for persistence — don't write to localStorage directly

---

## URL State

```tsx
// path/to/your/hooks/useFilters.ts
import { useSearchParams } from 'react-router-dom';

export function useFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = {
    search: searchParams.get('q') ?? '',
    category: searchParams.get('cat') ?? 'all',
    page: Number(searchParams.get('page') ?? '1'),
    sort: searchParams.get('sort') ?? 'newest',
  };

  const setFilter = (key: string, value: string) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) {
        next.set(key, value);
      } else {
        next.delete(key);
      }
      next.set('page', '1'); // Reset page on filter change
      return next;
    });
  };

  return { filters, setFilter };
}
```

**Rules**:

- Use URL state for filters, pagination, sort order — anything bookmarkable
- Parse and validate URL params — never trust raw strings
- Reset dependent params when parent changes (e.g., reset page on filter change)

---

## Form State

```tsx
// path/to/your/components/features/CreateUserForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'editor', 'viewer']),
});

type CreateUserForm = z.infer<typeof createUserSchema>;

export function CreateUserForm({ onSubmit }: { onSubmit: (data: CreateUserForm) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { role: 'viewer' },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register('name')} aria-invalid={!!errors.name} />
        {errors.name && <span role="alert">{errors.name.message}</span>}
      </div>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} aria-invalid={!!errors.email} />
        {errors.email && <span role="alert">{errors.email.message}</span>}
      </div>
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create User'}
      </button>
    </form>
  );
}
```

**Rules**:

- Separate validation schema from component — reuse across forms and API
- Use `zodResolver` / `yupResolver` — don't write custom validation logic
- Display errors per-field with `role="alert"` for screen readers
- Use `aria-invalid` on invalid fields
- Disable submit during submission to prevent double-submit
