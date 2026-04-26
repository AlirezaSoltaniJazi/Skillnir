# API / Integration Test Patterns

> HTTP client patterns, request building, response validation, auth handling, and mock server usage with full examples.

---

## API Client Abstraction

### TypeScript (Playwright API Testing)

```typescript
import { APIRequestContext, expect } from '@playwright/test';

interface ApiResponse<T> {
  status: number;
  data: T;
  headers: Record<string, string>;
}

export class BaseApiClient {
  constructor(
    protected readonly request: APIRequestContext,
    protected readonly baseUrl: string,
    protected token?: string,
  ) {}

  protected headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    const response = await this.request.get(`${this.baseUrl}${path}`, {
      headers: this.headers(),
    });
    return {
      status: response.status(),
      data: await response.json(),
      headers: response.headers(),
    };
  }

  async post<T>(path: string, body: unknown): Promise<ApiResponse<T>> {
    const response = await this.request.post(`${this.baseUrl}${path}`, {
      headers: this.headers(),
      data: body,
    });
    return {
      status: response.status(),
      data: await response.json(),
      headers: response.headers(),
    };
  }

  async delete(path: string): Promise<number> {
    const response = await this.request.delete(`${this.baseUrl}${path}`, {
      headers: this.headers(),
    });
    return response.status();
  }
}
```

### Domain-Specific Client

```typescript
import { BaseApiClient } from './BaseApiClient';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface CreateUserPayload {
  email: string;
  name: string;
  password: string;
}

export class UsersApiClient extends BaseApiClient {
  async createUser(payload: CreateUserPayload): Promise<User> {
    const response = await this.post<User>('/api/users', payload);
    expect(response.status).toBe(201);
    return response.data;
  }

  async getUser(id: string): Promise<User> {
    const response = await this.get<User>(`/api/users/${id}`);
    expect(response.status).toBe(200);
    return response.data;
  }

  async deleteUser(id: string): Promise<void> {
    const status = await this.delete(`/api/users/${id}`);
    expect(status).toBe(204);
  }

  async listUsers(): Promise<User[]> {
    const response = await this.get<User[]>('/api/users');
    expect(response.status).toBe(200);
    return response.data;
  }
}
```

---

## Python API Client (requests / httpx)

```python
import httpx
from dataclasses import dataclass


@dataclass
class ApiResponse:
    status: int
    data: dict | list | None
    headers: dict


class BaseApiClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url
        self.token = token

    def _headers(self) -> dict:
        h = {'Content-Type': 'application/json'}
        if self.token:
            h['Authorization'] = f'Bearer {self.token}'
        return h

    def get(self, path: str) -> ApiResponse:
        r = httpx.get(f'{self.base_url}{path}', headers=self._headers())
        return ApiResponse(status=r.status_code, data=r.json(), headers=dict(r.headers))

    def post(self, path: str, body: dict) -> ApiResponse:
        r = httpx.post(f'{self.base_url}{path}', json=body, headers=self._headers())
        return ApiResponse(status=r.status_code, data=r.json(), headers=dict(r.headers))

    def delete(self, path: str) -> int:
        r = httpx.delete(f'{self.base_url}{path}', headers=self._headers())
        return r.status_code
```

---

## API Test Spec Examples

### CRUD Lifecycle Test

```typescript
import { test, expect } from '@playwright/test';
import { UsersApiClient } from '../clients/UsersApiClient';
import { createUniqueEmail } from '../fixtures/users';

test.describe('Users API', () => {
  let client: UsersApiClient;
  let createdUserId: string;

  test.beforeAll(async ({ request }) => {
    client = new UsersApiClient(request, process.env.BASE_URL!, process.env.AUTH_TOKEN);
  });

  test.afterAll(async () => {
    if (createdUserId) {
      await client.deleteUser(createdUserId);
    }
  });

  test('should create a new user', async () => {
    const user = await client.createUser({
      email: createUniqueEmail(),
      name: 'Test User',
      password: 'SecurePass123!',
    });

    createdUserId = user.id;
    expect(user.email).toContain('@');
    expect(user.name).toBe('Test User');
  });

  test('should retrieve created user', async () => {
    const user = await client.getUser(createdUserId);
    expect(user.id).toBe(createdUserId);
    expect(user.name).toBe('Test User');
  });

  test('should return 404 for non-existent user', async () => {
    const response = await client.get('/api/users/non-existent-id');
    expect(response.status).toBe(404);
  });
});
```

### Response Schema Validation

```typescript
import { test, expect } from '@playwright/test';

// JSON schema validation
const userSchema = {
  type: 'object',
  required: ['id', 'email', 'name', 'createdAt'],
  properties: {
    id: { type: 'string', pattern: '^[a-f0-9-]{36}$' },
    email: { type: 'string', format: 'email' },
    name: { type: 'string', minLength: 1 },
    createdAt: { type: 'string', format: 'date-time' },
  },
  additionalProperties: false,
};

test('user response matches schema', async ({ request }) => {
  const response = await request.get('/api/users/known-id');
  const body = await response.json();

  // Validate with ajv, zod, or custom validator
  expect(validateSchema(body, userSchema)).toBe(true);
});
```

---

## Auth Token Management

```typescript
// Token cache — avoid re-authenticating for every test
let tokenCache: Map<string, { token: string; expiresAt: number }> = new Map();

export async function getAuthToken(role: string, baseUrl: string): Promise<string> {
  const cached = tokenCache.get(role);
  if (cached && cached.expiresAt > Date.now()) {
    return cached.token;
  }

  const credentials = getCredentialsForRole(role); // from env vars
  const response = await fetch(`${baseUrl}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  const data = await response.json();
  tokenCache.set(role, {
    token: data.token,
    expiresAt: Date.now() + (data.expiresIn * 1000) - 60000, // refresh 1 min early
  });

  return data.token;
}
```

---

## Mock Server Patterns

### MSW (Mock Service Worker) — for JS/TS

```typescript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      email: 'test@example.com',
      name: 'Mock User',
    });
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 'new-id', ...body }, { status: 201 });
  }),

  http.delete('/api/users/:id', () => {
    return new HttpResponse(null, { status: 204 });
  }),
];

export const mockServer = setupServer(...handlers);
```

### Python (responses / respx)

```python
import responses


@responses.activate
def test_get_user():
    responses.get(
        'https://api.example.com/users/123',
        json={'id': '123', 'name': 'Test User'},
        status=200,
    )

    client = UsersApiClient('https://api.example.com')
    response = client.get('/users/123')

    assert response.status == 200
    assert response.data['name'] == 'Test User'
```
