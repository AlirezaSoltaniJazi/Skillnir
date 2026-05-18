# Django Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Django-specific overrides.

```
ROLE:     Senior Django engineer / DRF specialist analyzing a production Django codebase
GOAL:     Generate a production-grade Django development skill directory
SCOPE:    Django + Django REST Framework + Channels + Celery + the Django ORM and admin.
          NOT generic Python scripting (use "python"), NOT a frontend SPA (use "frontend"/"js"),
          NOT raw infra (use "infra"/"devops-engineer").
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated Django 5+ engineer who knows ORM traps, migration safety, settings discipline, and DRF idioms — not generic Python advice.

---

## PHASE 1: PROJECT SCAN — Django Only

**Project shape**

- Django version (4.2 LTS / 5.0 / 5.1 / 5.2 LTS) — check `django` pin in `requirements.txt`/`pyproject.toml`/`pip freeze`
- `manage.py` location — root or `src/`-layout
- `wsgi.py` / `asgi.py` presence — sync, async, or both
- Project package vs. apps split — `settings.py` location, `INSTALLED_APPS` shape
- `apps.py` registrations and signal wiring (`ready()`)
- URL conf style (`path()` vs. `re_path()`, namespace pattern, `app_name`)

**Settings + secrets**

- Settings module layout (single `settings.py` vs. `settings/base.py` + `dev.py` + `prod.py` vs. `django-environ` / `django-configurations`)
- Secret loading (`os.environ`, `.env` via `python-decouple`/`django-environ`, AWS Secrets Manager, Vault)
- `DEBUG` discipline — never `True` in prod; `ALLOWED_HOSTS` populated
- `SECRET_KEY` source — env var, not hardcoded
- `DATABASES` configuration — single or multi-db, replicas, `CONN_MAX_AGE`, `OPTIONS`
- Static + media handling — `STATIC_ROOT`, `MEDIA_ROOT`, `STORAGES` (Django 5.1+ dict), S3/GCS via `django-storages`

**ORM + data layer**

- Database backend (PostgreSQL preferred / MySQL / SQLite for dev / Oracle / MSSQL)
- Models: `Meta` options, `__str__`, `db_table`, `indexes`, `constraints`, `ordering` defaults
- Custom managers and querysets (`models.Manager.from_queryset`)
- Migrations folder per app, presence of `--name` discipline, squash history
- Atomic-transaction wrapping (`@transaction.atomic`, `transaction.on_commit`)
- N+1 hotspots — look for `.objects.all()` in templates/views without `select_related`/`prefetch_related`
- Raw SQL usage (`RawSQL`, `connection.cursor()`) — auditable surface
- Postgres-specific features in use (`JSONField`, `ArrayField`, `GIN`, `TrigramExtension`, `unaccent`)

**Views + URL routing**

- Style mix: FBV (`def view(request)`) vs. CBV (`View`, `ListView`, `DetailView`, `FormView`) vs. DRF (`APIView`, `GenericAPIView`, `ViewSet`, `ModelViewSet`)
- Decorator discipline (`@login_required`, `@permission_required`, `@require_http_methods`, `@cache_page`, `@vary_on_headers`)
- DRF serializers (`ModelSerializer` vs. plain `Serializer`), nested serializers, `to_representation` overrides
- DRF permissions (`IsAuthenticated`, `DjangoModelPermissions`, custom `BasePermission`)
- DRF authentication backends (Session, Token, JWT via `djangorestframework-simplejwt`, OAuth via `django-oauth-toolkit`)
- DRF throttling, pagination, filtering (`django-filter`), versioning
- Routing: `router.register()` vs. manual `urlpatterns`; `format_suffix_patterns` usage
- API schema — `drf-spectacular` (OpenAPI 3.1) / `drf-yasg` (legacy)

**Django admin**

- Admin registration discipline (`@admin.register` vs. `admin.site.register`)
- `ModelAdmin` config: `list_display`, `list_filter`, `search_fields`, `readonly_fields`, `raw_id_fields`, `autocomplete_fields`, `prefetch_related` overrides
- Inline classes — `TabularInline` / `StackedInline`
- Custom admin actions, `get_queryset()` filtering
- Admin hardening: `ADMIN_URL` not at `/admin/`, IP allowlist, `django-axes` brute-force protection, 2FA via `django-otp`/`django-allauth-mfa`
- `is_staff` / `is_superuser` boundary

**Forms + validation**

- Form classes (`forms.Form`, `forms.ModelForm`), `clean()` and `clean_<field>()` discipline
- DRF serializer validators (`validate()`, `validate_<field>()`)
- Crispy forms / django-widget-tweaks usage
- CSRF discipline — `{% csrf_token %}` in templates, `csrf_exempt` audit trail

**Templates** (if not API-only)

- Engine (Django Templates / Jinja2)
- Template tags + filters layout (`templatetags/` per app)
- Context processors registered
- Auto-escape default + `|safe` audit
- Static handling — `{% load static %}`, `django-compressor` / `whitenoise`

**Async + real-time**

- Django async views (`async def view(request)`) usage
- Channels installed — `ASGI_APPLICATION`, `CHANNEL_LAYERS` (Redis), consumer style (`AsyncWebsocketConsumer` / `JsonWebsocketConsumer`)
- `django-redis` for cache layer, `CACHES` configuration
- Server-Sent Events (SSE) — `django-eventstream` or hand-rolled

**Background tasks**

- Task framework: Celery (most common) / Django-Q / Huey / `django-tasks` (Django 5.2+ native) / RQ / Dramatiq
- Broker (Redis / RabbitMQ / Amazon SQS) and result backend
- Beat scheduler (`celery-beat` with `django-celery-beat`)
- Task discovery (`@shared_task` vs. `@app.task`)
- Idempotency, retries, exponential backoff, task ack discipline (`acks_late`, `task_reject_on_worker_lost`)
- Periodic tasks layout (`CELERY_BEAT_SCHEDULE`, `crontab` schedules)

**Security middleware + headers**

- Middleware order — `SecurityMiddleware`, `SessionMiddleware`, `CsrfViewMiddleware`, `AuthenticationMiddleware`, `XFrameOptionsMiddleware`
- `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER`
- `CSP` headers — `django-csp` configuration
- `X_FRAME_OPTIONS = "DENY"`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER` (deprecated — relies on CSP now)
- Password validators — `AUTH_PASSWORD_VALIDATORS`
- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`

**Testing**

- Framework — `pytest-django` (recommended) or `django.test.TestCase`
- `factory_boy` / `model_bakery` for fixtures
- `pytest-django` markers (`@pytest.mark.django_db`, `transactional_db`, `django_db_reset_sequences`)
- DRF test client (`APIClient`, `APIRequestFactory`)
- Coverage tooling (`coverage.py`, `pytest-cov`)
- Snapshot testing (`syrupy`) for serializer output
- VCR / HTTP recording for outbound calls

**Performance + observability**

- `django-debug-toolbar` (dev only)
- `django-silk` profiling
- Query counting in tests (`assertNumQueries`, `django-perf-rec`)
- APM integration (Sentry, Datadog, New Relic, OpenTelemetry)
- Caching layers (template fragment cache, `cache_page`, ORM `.cache()` via `django-cachalot`, per-view cache)

**Dependency hygiene**

- `django` LTS vs. non-LTS — security-only window for non-LTS
- `pip-audit` / `safety` in CI
- `django-upgrade` codemod usage history
- Deprecation-warnings policy in CI (`-W error`)

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_django.md`:

1. **Django Edition** — version, LTS status, EOL date
2. **App Topology** — list of `INSTALLED_APPS` apps and their responsibilities
3. **Settings Layout** — how `DEBUG`, `DATABASES`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CACHES` are sourced
4. **View Style** — FBV / CBV / DRF distribution with file pointers
5. **ORM Hotspots** — top 5 queries / managers / signals that need care; N+1 risks
6. **Migration Posture** — squashed history, manual `RunPython`, data migrations, locking risks
7. **Async Surface** — async views, Channels, Celery topology
8. **Security Baseline** — middleware order, header coverage, admin hardening, auth + perm model
9. **Testing Discipline** — fixtures, factories, query-count assertions
10. **Things to ALWAYS do** in this project (e.g., wrap migrations in atomic blocks)
11. **Things to NEVER do** in this project (e.g., `objects.all()` in serializer fields)

---

## PHASE 2.5: ADDITIONAL CRAFT — Django Standards

### 2.5a. Django release cadence + LTS

| Version | Released | LTS? | Mainstream support | Extended support (LTS) |
| ------- | -------- | ---- | ------------------ | ---------------------- |
| 4.2     | Apr 2023 | LTS  | until Dec 2023     | until Apr 2026         |
| 5.0     | Dec 2023 | No   | Apr 2025           | —                      |
| 5.1     | Aug 2024 | No   | Apr 2026           | —                      |
| 5.2     | Apr 2025 | LTS  | until Dec 2026     | until Apr 2028         |

Rule: production projects pin to an LTS unless they have a strong reason. The skill MUST recommend an upgrade path when a non-LTS version is detected near EOL.

### 2.5b. ORM patterns — the N+1 killers

| Pattern                                                 | Use when                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------- |
| `select_related("fk", "fk__nested")`                    | Forward FK / OneToOne — single SQL JOIN                             |
| `prefetch_related("reverse_set", "m2m")`                | Reverse FK / ManyToMany — separate query, joined in Python          |
| `Prefetch(queryset=...)` with `to_attr=...`             | Custom filter on prefetch + avoid clobbering default related_set    |
| `only(...)` / `defer(...)`                              | Wide tables where most columns are unused                           |
| `.annotate(...)` + `.aggregate(...)`                    | Push computation into SQL instead of Python loops                   |
| `.values()` / `.values_list(flat=True)`                 | Skip model instantiation when you only need raw fields              |
| `.iterator(chunk_size=N)`                               | Streaming large result sets without loading all rows into memory    |
| `bulk_create(..., update_conflicts=True)` (Django 4.1+) | Bulk upserts; avoid `save()` in a loop                              |
| `update_or_create(defaults={...})`                      | Single object upsert; race-condition-safe under `select_for_update` |
| `F()` / `Q()` expressions                               | Atomic updates without read-modify-write                            |

### 2.5c. Migration safety — zero-downtime rules

1. **Never combine schema + data migration in one file** — split into separate migrations to keep them atomic and re-runnable.
2. **Add columns nullable first**, backfill data, then make `NOT NULL` in a follow-up migration. Postgres `ALTER COLUMN SET NOT NULL` is fast (just a constraint check) on Django 4.2+.
3. **Adding an index on a large table** — use `AddIndexConcurrently` (Postgres) and run it in a migration with `atomic = False`.
4. **Renaming a column** — use `RenameField` only when no live deploys read the old column. Otherwise: add new, dual-write, backfill, switch reads, drop old (4 deploys).
5. **Dropping a column** — first deploy code that doesn't reference it; only then drop it.
6. **`RunPython` operations** must take `(apps, schema_editor)`, use `apps.get_model("app", "Model")`, and include `reverse_code` (or `migrations.RunPython.noop` with a comment explaining irreversibility).
7. **Lock-sensitive operations** — wrap with `LOCK_TIMEOUT` to fail fast rather than block writes.
8. **Squash history** when migration count exceeds ~50 per app; verify with a fresh DB rebuild before merging.

### 2.5d. DRF idioms — the right tool for the level

| Need                                | Reach for                                                                |
| ----------------------------------- | ------------------------------------------------------------------------ |
| Standard CRUD over one model        | `ModelViewSet` + `DefaultRouter`                                         |
| Custom action on a model            | `@action(detail=True, methods=["post"])` on the ViewSet                  |
| Non-CRUD endpoint (e.g., `/login/`) | `APIView` with explicit `post()` method                                  |
| Read-only API                       | `ReadOnlyModelViewSet`                                                   |
| Heavy nested writes                 | Override `create()` / `update()` on the serializer; wrap in `atomic`     |
| File uploads                        | `MultiPartParser`, `FileUploadParser`; validate MIME via `python-magic`  |
| Streaming response                  | `StreamingHttpResponse`; for DRF use a `Renderer` that yields            |
| OpenAPI schema                      | `drf-spectacular` with explicit `@extend_schema` on every viewset/action |

### 2.5e. Admin hardening checklist

1. Move admin off `/admin/` — `ADMIN_URL = "ops-console-7x2j/"` in env-driven config.
2. Enforce 2FA via `django-otp` or SSO via `django-allauth`.
3. Brute-force protection via `django-axes` (lockout after N failed attempts).
4. Audit log of every admin write — `django-simple-history` or `django-auditlog`.
5. Disable `is_superuser` for day-to-day staff; grant minimal `is_staff` + per-model permissions.
6. Restrict admin IP range at the load balancer / WAF when possible.
7. Disable raw-SQL widgets and `RawIdWidget` for FK to sensitive models if leakage is a concern.

### 2.5f. Celery patterns

- **Task signature**: keep tasks pure functions taking primitive args (IDs, not model instances) — model instances don't pickle cleanly.
- **Idempotency**: design tasks to be safe to retry; use a unique idempotency key in a `RedisLock` or a DB unique constraint.
- **`bind=True`** when you need `self.retry()` or `self.request.id`.
- **`acks_late=True` + `task_reject_on_worker_lost=True`** for at-least-once delivery (default is at-most-once).
- **`autoretry_for=(NetworkError,)` + `retry_backoff=True`** for retryable failures; use `retry_jitter=True` to avoid thundering herd.
- **Periodic tasks** — declare in `CELERY_BEAT_SCHEDULE` with `crontab` schedules and an explicit `expires` so missed runs don't pile up.
- **Result backend hygiene** — don't store large payloads in the result backend; use `ignore_result=True` for fire-and-forget.

---

## PHASE 3: BEST PRACTICES (numbered by priority)

1. **Always parameterize queries** — never `.raw()` with f-string interpolation; use `params=[...]`. Same for `connection.cursor().execute(sql, [params])`.
2. **Always wrap multi-step writes in `transaction.atomic`** and use `transaction.on_commit(callback)` for post-commit side effects (Celery dispatch, webhook, email).
3. **Always use `select_for_update()`** when reading-then-writing a row across concurrent requests. Combine with `nowait=True` or `skip_locked=True` for back-pressure-friendly queues.
4. **Always pin `DEBUG=False`** in production and verify `ALLOWED_HOSTS` is non-empty; the skill MUST recommend a startup assertion.
5. **Always set `CONN_MAX_AGE` and `CONN_HEALTH_CHECKS`** (Django 4.1+) for persistent connections; pgbouncer in front for high-fanout.
6. **Always use `bulk_create` / `bulk_update`** for >5 rows; never call `.save()` in a loop.
7. **Always exclude `secret`/`token`/`password` fields** from DRF serializer `Meta.fields = "__all__"` — be explicit.
8. **Always use `@admin.register(Model)`** decorator over `site.register(Model, ModelAdmin)` — keeps registration with the class.
9. **Never expose `is_superuser`** through DRF; restrict the user serializer to safe fields.
10. **Never use `objects.all()[:N]`** when you want pagination — use DRF's `PageNumberPagination` or `CursorPagination` (cursor is safer for stable order under churn).
11. **Never put business logic in `signals`** if it can live in the model `save()` or a service function — signals are hard to trace.
12. **Never disable CSRF globally** — exempt per-view with documented reason; prefer same-site cookie + `Referer` checking for APIs.

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Django task — models, migrations, views, DRF serializers/viewsets, admin, signals, middleware, settings, ORM optimization, Celery tasks, Channels consumers, Django auth/permissions, testing with pytest-django.

**`allowed-tools`**: `Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Bash(manage.py:*) Bash(django-admin:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (DRF endpoint, ORM N+1, migration safety, admin tweak, async view, Celery task)
2. **Do NOT Use** — cross-references to sibling skills (`python` for non-Django scripts, `frontend` for SPA, `database` for raw SQL/Alembic, `api-design` for cross-framework OpenAPI)
3. **Architecture** — apps layout, URL routing, settings module strategy, ASGI vs. WSGI
4. **ORM Patterns** — rule table only; full examples in `references/orm-patterns.md`
5. **Migration Safety** — zero-downtime ladder + locking rules; full examples in `references/migrations.md`
6. **DRF Recipes** — numbered steps only ("Add a new endpoint", "Add a custom action")
7. **Admin Standards** — rule list + hardening checklist
8. **Async + Celery** — when to use which; idempotency rules
9. **Settings + Secrets** — env-driven loading, `DEBUG=False` assertion, `STORAGES` dict (Django 5.1+)
10. **Security** — middleware order + header rules + full checklist link in `references/security-checklist.md`
11. **Testing Standards** — pytest-django markers, factory_boy patterns, query-count assertions
12. **Anti-Patterns** — the `Never` table from Phase 3
13. **References** — Django docs, DRF docs, books (Two Scoops, Django for APIs), real-world post-mortems
14. **Adaptive Interaction Protocols** — Django-specific signals (e.g., "OperationalError: deadlock detected" for Diagnostic, "another viewset like X" for Efficient, "what does @action do" for Teaching), correction accumulation, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/orm-patterns.md` — full `select_related`/`prefetch_related`/`Prefetch`/annotations/raw SQL guard rails examples
- `references/views-and-drf.md` — FBV/CBV/DRF decision tree, ViewSet recipes, custom permissions, throttling, pagination
- `references/migrations.md` — zero-downtime migration ladder with worked examples (add column, rename, drop, big-table index, data migration)
- `references/admin-hardening.md` — admin URL, 2FA, axes, allauth/SSO, audit log, IP allowlist
- `references/celery-patterns.md` — task signatures, idempotency, retry policy, beat schedules, result backend
- `references/security-checklist.md` — OWASP for Django (CSRF, SQL injection, SSRF, open redirects, file upload validation, secret management, dependency audit)
- `references/code-style.md` — import order, model `Meta`, manager naming, signal layout, app structure
- `references/test-patterns.md` — `pytest-django`, fixtures vs. factory_boy, `assertNumQueries`, `APIClient`, snapshot serializer outputs
- `references/common-issues.md` — `OperationalError`, `OperationalError: deadlock detected`, `IntegrityError`, `Cannot resolve keyword`, `circular import`
- `references/ai-interaction-guide.md` — what to delegate to AI (boilerplate models, serializers, factory) vs. keep human (data migrations on prod data, multi-deploy rename, raw SQL)
- `assets/django-settings-template.py` — env-driven `base.py` + `dev.py` + `prod.py` skeleton
- `assets/drf-viewset-template.py` — opinionated ViewSet + serializer pair
- `assets/celery-task-template.py` — idempotent task skeleton with retry policy
- `assets/migration-template.py` — atomic data migration with reverse_code
- `scripts/check-django.sh` — wraps `python manage.py check --deploy`, `python manage.py makemigrations --dry-run --check`, `pip-audit`

---

## SUB-AGENT RECOMMENDATIONS

| Agent             | Role                                                              | Tools                          | Spawn When                                                         |
| ----------------- | ----------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------ |
| migration-auditor | Read-only — review migrations for locking + reversibility risk    | Read Glob Grep                 | Migration PR review, deploy gating, big-table operations           |
| orm-reviewer      | Read-only — scan querysets for N+1 / select_related opportunities | Read Glob Grep                 | View / serializer PR review, performance audit                     |
| test-writer       | Pytest-django test generation following project fixtures          | Read Edit Write Glob Grep Bash | "write tests for this view/model", new app creation, coverage gaps |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules (e.g., always run `migration-auditor` before a migration PR is merged)
3. Link to `agents/` for full definitions

Add to suggested reference files:

- `agents/migration-auditor.md` — read-only migration safety agent
- `agents/orm-reviewer.md` — read-only ORM performance agent
- `agents/test-writer.md` — pytest-django test generation agent

---

## EXECUTION ORDER

```
[ ] 1. Scan project for Django version, settings layout, apps, ORM hotspots, DRF surface, Celery topology (Phase 1)
[ ] 2. Synthesize app topology, ORM hotspots, migration posture, async surface, security baseline (Phase 2)
[ ] 3. Generate SKILL.md with numbered rule lists + Phase 2.5 standards
[ ] 4. Generate INJECT.md (50-150 token quick ref — must include "wrap in transaction.atomic", "select_related/prefetch_related", "DEBUG=False in prod")
[ ] 5. Generate LEARNED.md (empty template with section headers)
[ ] 6. Generate the 10+ reference files (Phase 4)
[ ] 7. Generate the 4+ asset templates (Phase 5)
[ ] 8. Generate scripts/check-django.sh
[ ] 9. Generate agents/ files if delegation warranted
[ ] 10. Run quality gates (base)
```

---

## SOURCES

- Django release schedule + LTS — [docs.djangoproject.com/en/dev/internals/release-process/](https://docs.djangoproject.com/en/dev/internals/release-process/)
- Django ORM optimization — [docs.djangoproject.com/en/5.2/topics/db/optimization/](https://docs.djangoproject.com/en/5.2/topics/db/optimization/)
- Django REST Framework — [www.django-rest-framework.org](https://www.django-rest-framework.org/)
- pytest-django — [pytest-django.readthedocs.io](https://pytest-django.readthedocs.io/)
- Celery best practices — [docs.celeryq.dev/en/stable/userguide/tasks.html](https://docs.celeryq.dev/en/stable/userguide/tasks.html)
- Two Scoops of Django — Daniel & Audrey Roy Greenfeld
- Django for APIs — William S. Vincent
- OWASP Top 10 for Django — [owasp.org/Top10/](https://owasp.org/Top10/)
- Zero-downtime migrations — [github.com/3YOURMIND/django-pg-zero-downtime-migrations](https://github.com/3YOURMIND/django-pg-zero-downtime-migrations)
