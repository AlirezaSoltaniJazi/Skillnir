# Common Issues — Frontend Developer

> Troubleshooting guide for common frontend pitfalls across React, Vue, Angular, and modern web stacks.

---

## Hydration Mismatches (SSR/SSG)

### `Hydration failed because the initial UI does not match what was rendered on the server`

**Cause**: Server-rendered HTML differs from client-rendered output. Common triggers: `Date.now()`, `Math.random()`, browser-only APIs (`window`, `localStorage`), conditional rendering based on client state.

**Fix**: Defer browser-only content to `useEffect` / `onMounted`:

```tsx
// ✅ Correct — defer browser-only content
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);

return mounted ? <ClientOnlyWidget /> : <Placeholder />;

// ❌ Wrong — accessing window during SSR
const width = window.innerWidth; // window is undefined on server
```

---

## Infinite Re-renders

### `Maximum update depth exceeded` / `Too many re-renders`

**Cause**: State update inside render path without a guard condition. Common triggers: calling `setState` unconditionally in render, unstable object/function references in `useEffect` deps.

**Fix**: Stabilize references and add guard conditions:

```tsx
// ✅ Correct — stable callback reference
const handleResize = useCallback(() => {
  setWidth(window.innerWidth);
}, []);

useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, [handleResize]);

// ❌ Wrong — new object in every render causes infinite loop
useEffect(() => {
  fetchData(options); // options is a new object each render
}, [options]); // ← this dependency changes every render
```

---

## Stale Closures

### Event handler uses outdated state value

**Cause**: Closure captures state value at creation time, not current value. Common in `setTimeout`, `setInterval`, event listeners.

**Fix**: Use refs for latest value or functional state updates:

```tsx
// ✅ Correct — functional update reads latest state
setCount((prev) => prev + 1);

// ✅ Correct — ref for latest value in callbacks
const countRef = useRef(count);
countRef.current = count;
setTimeout(() => console.log(countRef.current), 1000);

// ❌ Wrong — closure captures stale value
setTimeout(() => console.log(count), 1000); // count is stale
```

---

## Memory Leaks

### State update on unmounted component

**Cause**: Async operation (fetch, setTimeout, subscription) completes after component unmounts.

**Fix**: Cleanup with AbortController or unmount flag:

```tsx
// ✅ Correct — AbortController for fetch cleanup
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/data', { signal: controller.signal })
    .then((res) => res.json())
    .then(setData)
    .catch((err) => {
      if (err.name !== 'AbortError') throw err;
    });

  return () => controller.abort();
}, []);
```

---

## CSS Specificity Conflicts

### Tailwind classes not applying / styles overridden

**Cause**: CSS specificity conflicts between Tailwind utilities, component styles, and third-party CSS. Order of CSS imports matters.

**Fix**:

1. Ensure Tailwind's `@tailwind utilities` loads last
2. Use `!important` sparingly via Tailwind's `!` prefix (`!text-red-500`)
3. Use `@layer` to manage specificity properly
4. Check for conflicting classes (e.g., `hidden` + `flex` on same element)

---

## TypeScript Import Errors

### `Cannot find module '@/components/...'`

**Cause**: Path alias (`@/`) not configured in both TypeScript config AND build tool config.

**Fix**: Configure in both places:

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

```ts
// vite.config.ts
import { resolve } from 'path';
export default defineConfig({
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
});
```

---

## React Key Warnings

### `Each child in a list should have a unique "key" prop`

**Cause**: Missing or non-unique `key` prop on list items. Using array index as key when list can reorder.

**Fix**: Use stable unique IDs:

```tsx
// ✅ Correct — stable unique key
{users.map((user) => <UserCard key={user.id} user={user} />)}

// ⚠️ Acceptable — index key only for static lists that never reorder
{staticLabels.map((label, i) => <span key={i}>{label}</span>)}

// ❌ Wrong — index key on dynamic list
{users.map((user, i) => <UserCard key={i} user={user} />)}
```

---

## CORS Errors

### `Access to fetch has been blocked by CORS policy`

**Cause**: Browser blocks cross-origin requests when the API server doesn't send proper CORS headers.

**Fix**:

1. **Development**: Configure dev server proxy (Vite/Webpack proxy)
2. **Production**: Backend must send `Access-Control-Allow-Origin` header
3. **Never**: Disable CORS in browser or use `no-cors` mode (masks errors)

```ts
// vite.config.ts — dev proxy
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
});
```

---

## Build Size Issues

### Bundle too large / slow initial load

**Cause**: Importing entire libraries, no code splitting, large images inline.

**Fix**:

1. Import only what you use: `import { debounce } from 'lodash-es'` (not `import _ from 'lodash'`)
2. Analyze bundle: `npx vite-bundle-visualizer` or `npx webpack-bundle-analyzer`
3. Lazy-load routes: `React.lazy(() => import('./pages/Dashboard'))`
4. Optimize images: use WebP/AVIF, `next/image`, or manual optimization
5. Check for duplicate dependencies: `npx depcheck`

---

## Dark Mode Flicker

### White flash on page load with dark mode

**Cause**: Dark mode CSS loads after initial render, causing flash of light theme.

**Fix**:

1. Apply dark mode class in a blocking `<script>` in `<head>` before CSS loads
2. Use `color-scheme: dark` meta tag
3. Store preference in cookie (not localStorage) for SSR access

```html
<!-- In <head> — blocking script prevents FOUC -->
<script>
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
</script>
```
