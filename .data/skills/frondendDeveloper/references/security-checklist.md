# Security Checklist — Frontend Developer

> XSS prevention, CSP, sanitization, auth, and dependency auditing checklists.

---

## XSS Prevention (Severity: Critical)

- [ ] Never use `dangerouslySetInnerHTML` (React) / `v-html` (Vue) / `[innerHTML]` (Angular) with user-provided content
- [ ] Never construct HTML strings with user input — use framework templating
- [ ] Sanitize any HTML that MUST be rendered (use DOMPurify or equivalent)
- [ ] Escape user data in URLs — prevent `javascript:` protocol injection
- [ ] Validate and sanitize URL search params before rendering or using in API calls
- [ ] Never use `eval()`, `new Function()`, or `document.write()` with dynamic content

```tsx
// ✅ Safe — framework auto-escapes
<p>{userInput}</p>
<span>{{ userInput }}</span>

// ✅ Safe — sanitized HTML when rendering is absolutely required
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(htmlContent) }} />

// ❌ Dangerous — raw user HTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ❌ Dangerous — user data in href
<a href={userInput}>Link</a>  // Could be javascript:alert(1)

// ✅ Safe — validate URL protocol
const safeHref = /^https?:\/\//.test(userInput) ? userInput : '#';
<a href={safeHref}>Link</a>
```

---

## Authentication & Authorization (Severity: Critical)

- [ ] Store auth tokens in `httpOnly` cookies — never in localStorage or sessionStorage
- [ ] Include CSRF token in state-changing requests if using cookie-based auth
- [ ] Validate auth state on route transitions — don't rely solely on UI guards
- [ ] Clear all auth state on logout (memory, cookies, cached queries)
- [ ] Never expose tokens in URL parameters or browser history
- [ ] Implement token refresh — don't let users work with expired tokens silently

```tsx
// ✅ Safe — auth check in route guard
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <LoadingSkeleton />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return children;
}

// ❌ Dangerous — token in localStorage
localStorage.setItem('token', authToken); // Accessible to XSS attacks
```

---

## Content Security Policy (Severity: High)

- [ ] Set `Content-Security-Policy` header — restrict `script-src` to `'self'`
- [ ] Avoid `'unsafe-inline'` for scripts — use nonces or hashes
- [ ] Restrict `style-src` — allow `'self'` and trusted CDNs only
- [ ] Set `frame-ancestors 'none'` to prevent clickjacking
- [ ] Set `form-action 'self'` to prevent form hijacking
- [ ] Test CSP with `Content-Security-Policy-Report-Only` before enforcing

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{random}';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.YOUR_PROJECT.com;
  frame-ancestors 'none';
  form-action 'self';
```

---

## Dependency Security (Severity: High)

- [ ] Run `npm audit` / `pnpm audit` in CI — fail on critical/high severity
- [ ] Pin major versions in `package.json` — use lockfile for exact versions
- [ ] Review changelogs before major dependency upgrades
- [ ] Use `npm ls <package>` to find transitive dependencies with vulnerabilities
- [ ] Enable Dependabot or Renovate for automated security updates
- [ ] Never install packages from untrusted sources — verify package names (typosquatting)

---

## Sensitive Data (Severity: High)

- [ ] Never commit `.env` files with real secrets to version control
- [ ] Use `NEXT_PUBLIC_` / `VITE_` prefixes only for truly public values
- [ ] Never log auth tokens, passwords, or PII to browser console
- [ ] Mask sensitive fields in forms (`type="password"`, `autocomplete="off"` for OTP)
- [ ] Never include API keys in client-side bundles — proxy through backend

```tsx
// ✅ Safe — public config only
const apiUrl = import.meta.env.VITE_API_URL; // OK — this is a URL, not a secret

// ❌ Dangerous — secret in client bundle
const apiKey = import.meta.env.VITE_API_SECRET; // Visible in browser source!
```

---

## Input Validation (Severity: Medium)

- [ ] Validate all form inputs on client AND server — client validation is UX, not security
- [ ] Sanitize file upload names and validate MIME types
- [ ] Limit input lengths to prevent abuse (textarea max length, file size limits)
- [ ] Use allowlists, not denylists, for input validation
- [ ] Validate redirect URLs against an allowlist — prevent open redirects

```tsx
// ✅ Safe — allowlist for redirect
const ALLOWED_REDIRECTS = ['/dashboard', '/profile', '/settings'];
const redirect = ALLOWED_REDIRECTS.includes(params.redirect)
  ? params.redirect
  : '/dashboard';

// ❌ Dangerous — open redirect
window.location.href = params.redirect; // Could redirect to malicious site
```

---

## Third-Party Integrations (Severity: Medium)

- [ ] Load third-party scripts with `integrity` attribute (SRI)
- [ ] Sandbox third-party iframes with `sandbox` attribute
- [ ] Review permissions requested by third-party SDKs
- [ ] Use `rel="noopener noreferrer"` on external links with `target="_blank"`

```html
<!-- ✅ Safe — SRI hash for CDN script -->
<script
  src="https://cdn.example.com/lib.js"
  integrity="sha384-abc123..."
  crossorigin="anonymous"
></script>

<!-- ✅ Safe — sandboxed iframe -->
<iframe src="https://embed.example.com" sandbox="allow-scripts allow-same-origin"></iframe>

<!-- ✅ Safe — external link -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">External</a>
```
