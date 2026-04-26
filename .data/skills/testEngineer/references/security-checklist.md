# Security Testing Checklist

> Authentication, authorization, injection, and OWASP-aligned security verification checklists for test automation.

---

## Authentication Testing

**Severity: Critical | OWASP: A07:2021 — Identification and Authentication Failures**

- [ ] Test login with valid credentials (happy path)
- [ ] Test login with invalid password
- [ ] Test login with non-existent user
- [ ] Test account lockout after N failed attempts
- [ ] Test session expiration and forced re-login
- [ ] Test "remember me" token validity and expiration
- [ ] Test password reset flow end-to-end
- [ ] Test MFA/2FA flows (TOTP, SMS, email)
- [ ] Test OAuth/SSO redirect flows and callback handling
- [ ] Verify session invalidation on logout
- [ ] Verify session invalidation on password change
- [ ] Test concurrent session limits (if applicable)

## Authorization Testing

**Severity: Critical | OWASP: A01:2021 — Broken Access Control**

- [ ] Test role-based access (admin vs user vs guest)
- [ ] Test accessing another user's resources (IDOR)
- [ ] Test privilege escalation (user -> admin endpoints)
- [ ] Test horizontal access (user A accessing user B's data)
- [ ] Test API endpoints without authentication token
- [ ] Test with expired authentication token
- [ ] Test with tampered/forged JWT
- [ ] Verify CORS policy on API responses
- [ ] Test file access controls (uploaded files, reports)

## Input Validation / Injection Testing

**Severity: High | OWASP: A03:2021 — Injection**

- [ ] Test SQL injection in search/filter inputs
- [ ] Test XSS in text inputs (stored and reflected)
- [ ] Test command injection in file upload filenames
- [ ] Test path traversal in file download endpoints
- [ ] Test SSRF in URL input fields
- [ ] Verify input length limits are enforced
- [ ] Test special characters in all text fields
- [ ] Verify error messages don't leak internal details

## Sensitive Data Exposure

**Severity: High | OWASP: A02:2021 — Cryptographic Failures**

- [ ] Verify passwords are never returned in API responses
- [ ] Verify tokens/secrets are not logged
- [ ] Verify PII is masked in UI where expected
- [ ] Test that error pages don't expose stack traces
- [ ] Verify HTTPS enforcement (no mixed content)
- [ ] Verify sensitive headers (Authorization) are not cached

## Test Infrastructure Security

**Severity: Medium**

- [ ] Test credentials stored in environment variables, never in code
- [ ] Test data cleanup removes all sensitive created data
- [ ] CI/CD secrets are injected, not committed
- [ ] Test reports don't contain credentials or tokens
- [ ] Screenshot/video captures don't expose sensitive data
- [ ] Mock servers don't expose real API keys

## Security Test Patterns

### Authentication Setup Helper

```typescript
// Centralized auth helper — tokens from env vars, never hard-coded
export class AuthHelper {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getAuthToken(role: 'admin' | 'user' | 'guest'): Promise<string> {
    const credentials = {
      admin: { email: process.env.TEST_ADMIN_EMAIL!, password: process.env.TEST_ADMIN_PASSWORD! },
      user: { email: process.env.TEST_USER_EMAIL!, password: process.env.TEST_USER_PASSWORD! },
      guest: { email: 'guest@test.com', password: 'guest123' },
    };

    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials[role]),
    });

    const data = await response.json();
    return data.token;
  }
}
```

### IDOR Test Pattern

```typescript
test('should not allow user A to access user B resources', async ({ request }) => {
  const userAToken = await authHelper.getAuthToken('user');
  const userBResourceId = 'user-b-resource-id';

  const response = await request.get(`/api/resources/${userBResourceId}`, {
    headers: { Authorization: `Bearer ${userAToken}` },
  });

  expect(response.status()).toBe(403);
});
```

### XSS Input Test

```typescript
const xssPayloads = [
  '<script>alert("xss")</script>',
  '"><img src=x onerror=alert(1)>',
  "'; DROP TABLE users; --",
  '{{constructor.constructor("return this")()}}',
];

for (const payload of xssPayloads) {
  test(`should sanitize XSS payload: ${payload.substring(0, 20)}...`, async ({ page }) => {
    await searchPage.search(payload);
    const content = await page.content();
    expect(content).not.toContain(payload);
  });
}
```
