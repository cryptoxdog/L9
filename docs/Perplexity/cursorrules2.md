You already have a rich L9-specific ruleset in `cursorrules.md` (global, TS, Python, React, autonomy, QA, etc.), but you are missing the remaining items from the **generic Cursor 2.0 rules package** you outlined: completion of the **anti-patterns file**, a **tool-efficiency file**, and a **session companion `workflow_state.md`**.[1]

Below are the missing pieces, **drop-in ready** in your generic structure (you can adapt naming to match your existing numbering).

***

## `60-anti-patterns.mdc`

```md
---
description: "Common anti-patterns and mistakes across TypeScript, Python, React, FastAPI, security, and testing, with side-by-side corrections."
alwaysApply: true
---

# Cross-stack anti-patterns

## TypeScript anti-patterns

### Escaping the type system with `any`

❌ **DON'T:**
```
// Everything is any, nothing is safe
function parseResponse(res: any): any {
  return res.data;
}
```

✅ **DO:**
```
interface ApiResponse<T> {
  data: T;
  status: number;
}

function parseResponse<T>(res: ApiResponse<T>): T {
  if (res.status !== 200) {
    throw new Error(`Unexpected status ${res.status}`);
  }
  return res.data;
}
```

### Silent promise errors

❌ **DON'T:**
```
fetch('/api/user')
  .then(r => r.json())
  .then(setUser);
// If anything throws, error disappears
```

✅ **DO:**
```
async function loadUser(): Promise<void> {
  try {
    const res = await fetch('/api/user');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data: User = await res.json();
    setUser(data);
  } catch (error) {
    logger.error('load_user_failed', { error });
    setError('Failed to load user');
  }
}
```

---

## Python anti-patterns

### Bare `except` and swallowed errors

❌ **DON'T:**
```
try:
    result = risky_operation()
except:
    # Ignore everything
    return None
```

✅ **DO:**
```
from logging import getLogger

logger = getLogger(__name__)

try:
    result = risky_operation()
except ValueError as exc:
    logger.error("Invalid value in risky_operation", exc_info=True)
    raise DomainValidationError("Invalid value") from exc
except TimeoutError as exc:
    logger.warning("risky_operation timed out", exc_info=True)
    raise
```

### Business logic in FastAPI route body

❌ **DON'T:**
```
@app.post("/users")
async def create_user(email: str, password: str):
    # Hash, validate, and insert directly here
    if "@" not in email:
        raise HTTPException(status_code=400)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    await db.execute("INSERT ...", values={"email": email, "password": hashed})
    return {"email": email}
```

✅ **DO:**
```
class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(request: UserCreate) -> UserResponse:
    user = await user_service.create_user(request)
    return user
```

---

## React anti-patterns

### State stored outside React / bypassing hooks

❌ **DON'T:**
```
// Global mutable object
let currentUser: User | null = null;

export function Header() {
  return <div>{currentUser ? currentUser.name : 'Guest'}</div>;
}
```

✅ **DO:**
```
const AuthContext = createContext<AuthState | undefined>(undefined);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export function Header() {
  const { user } = useAuth();
  return <div>{user ? user.name : 'Guest'}</div>;
}
```

### Missing effect cleanup / memory leaks

❌ **DON'T:**
```
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + 1);
  }, 1000);
}, []); // No cleanup
```

✅ **DO:**
```
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + 1);
  }, 1000);
  return () => clearInterval(id);
}, []);
```

---

## FastAPI anti-patterns

### Sync I/O in async routes

❌ **DON'T:**
```
@app.get("/report")
async def get_report():
    time.sleep(5)  # Blocks event loop
    return {"ok": True}
```

✅ **DO:**
```
@app.get("/report")
async def get_report():
    await asyncio.sleep(5)
    return {"ok": True}
```

### Returning unvalidated dicts

❌ **DON'T:**
```
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_one("SELECT * FROM users WHERE id = :id", {"id": user_id})
    if not user:
      raise HTTPException(status_code=404)
    return dict(user)  # Raw DB row
```

✅ **DO:**
```
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int) -> UserOut:
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Security anti-patterns

### Hardcoded secrets

❌ **DON'T:**
```
export const STRIPE_KEY = 'sk_live_123456';
```

✅ **DO:**
```
export const STRIPE_KEY = process.env.STRIPE_KEY!;
if (!STRIPE_KEY) {
  throw new Error('Missing STRIPE_KEY env var');
}
```

### Missing input validation on API boundary

❌ **DON'T:**
```
// Express/FastAPI equivalent
router.post('/login', async (req, res) => {
  const { email, password } = req.body; // blindly trust
  // ...
});
```

✅ **DO:**
```
const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

router.post('/login', async (req, res) => {
  const parsed = LoginSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: 'Invalid payload' });
  }
  // use parsed.data
});
```

---

## Testing anti-patterns

### Non-deterministic tests

❌ **DON'T:**
```
test('loads data eventually', async () => {
  render(<Data />);
  await new Promise(r => setTimeout(r, 1000)); // arbitrary
  expect(screen.getByText('Done')).toBeInTheDocument();
});
```

✅ **DO:**
```
test('loads data eventually', async () => {
  render(<Data />);
  expect(await screen.findByText('Done')).toBeInTheDocument();
});
```

### Tests coupled to implementation details

❌ **DON'T:**
```
expect(component.state('open')).toBe(true);
```

✅ **DO:**
```
expect(screen.getByRole('dialog')).toBeVisible();
```

---

## Operational anti-patterns

### Huge, unscoped edits

❌ **DON'T:**
> “Refactor the whole codebase to improve performance.”

✅ **DO:**
> “Refactor `src/api/client.ts` to add a 30s timeout and structured logging, plus tests in `src/api/client.test.ts`. Do not change other files.”

### Skipping validation gates

❌ **DON'T:**
```
# In a hurry
git commit -am "quick fix"
```

✅ **DO:**
```
npm run lint && npm run type-check && npm run test
git commit
```
```

***

## `70-tool-efficiency.mdc`

```md
---
description: "Developer tooling efficiency: terminal usage, command batching, context budgeting, and Cursor tool ergonomics."
alwaysApply: true
---

# Tool efficiency and workflow

## Terminal command patterns

### Batch validation

- Always prefer **one combined command** over multiple partial runs.
- Use `&&` so later steps only run if earlier ones succeed.

✅ **DO:**
```
npm run lint && npm run type-check && npm run test
```

❌ **DON'T:**
```
npm run lint
npm run type-check
npm run test # then forget to run this sometimes
```

### Targeted tests

- Scope tests to changed modules where safe.

✅ **DO:**
```
pytest tests/core/agents/test_executor.py -k "timeout"
npm run test -- --runTestsByPath src/components/Button.test.tsx
```

---

## Cursor command efficiency

### Use selection for surgical edits

- Select exactly the function/component to change, then instruct Cursor on that selection.
- Avoid whole-file rewrites unless necessary.

✅ **DO:**
> “On the selected function only: add a timeout parameter and log when it triggers. Do not change the signature anywhere else.”

### Use `@` context wisely

- `@linter-errors` to fix concrete issues.
- `@tests-failed` (or failed output) to drive test fixes.
- Avoid `@codebase` unless performing high-level analysis.

✅ **DO:**
> `@linter-errors` “Fix all TypeScript errors without changing public APIs.”

---

## File and scope budgeting

### Explicit file budgets in prompts

- Always specify what Cursor **may** and **may not** touch.

✅ **DO:**
```
You may modify:
- src/auth/loginForm.tsx
- src/auth/loginForm.test.tsx

You may NOT modify:
- src/auth/context.tsx
- any backend files

If more changes are required, stop and propose a plan.
```

---

## Command library

### Common package scripts

Standardize NPM scripts:

```
{
  "scripts": {
    "lint": "eslint .",
    "type-check": "tsc --noEmit",
    "test": "jest --runInBand",
    "test:watch": "jest --watch",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

Use them consistently:

```
npm run lint
npm run type-check
npm run test
```

---

## When to skip heavy checks

- **Comments-only changes:** Run formatter, skip full test suite.
- **Docs-only changes:** No lint/type-check needed.

✅ **DO:**
```
# For docs-only commit
npm run format
```

❌ **DON'T:**
> Run full e2e suite after changing a README line.

---

## Git workflow

### Clean, small commits

- Commit **one concern per commit**.
- Avoid giant “mixed bag” commits.

✅ **DO:**
```
git add src/api/client.ts
git commit -m "feat(api): add timeout and structured logging"
```

### Use branch naming conventions

- `feat/…`, `fix/…`, `chore/…`, `refactor/…`.

```
git checkout -b feat/agent-ws-console
```

---

## Local automation

### Pre-commit hooks

Use a hook script to enforce basic checks:

```
#!/usr/bin/env bash
npm run lint
if [ $? -ne 0 ]; then
  echo "Lint failed"; exit 1
fi

npm run type-check
if [ $? -ne 0 ]; then
  echo "Type-check failed"; exit 1
fi

npm run test
if [ $? -ne 0 ]; then
  echo "Tests failed"; exit 1
fi
```

Mark executable:

```
chmod +x .git/hooks/pre-commit
```
```

***

## `workflow_state.md`

```md
# Cursor workflow state

> Companion document for day-to-day sessions. Pin this in your editor and update as you work.

---

## Phase

One of:

- `ANALYZE` – Understand current behavior and constraints.
- `BLUEPRINT` – Design plan, file budgets, and test strategy.
- `CONSTRUCT` – Implement changes + tests.
- `VALIDATE` – Run checks, tighten, and finalize.

**Current phase:** `ANALYZE`

---

## Context summary

- **Repo:** Full-stack monorepo (TS + Python, React + FastAPI, tests, security).
- **Rules:** `.cursor/rules/*.mdc` provide:
  - Global safety and coding baselines.
  - Language/framework rules (TS, Python, React, FastAPI).
  - Security, QA/testing, anti-patterns, and tool-efficiency guidance.

Update this section with:

- Key entrypoints touched today.
- Any feature flags or environment constraints in play.
- Important invariants you must not break.

---

## Recent changes

Keep a short, rolling log (latest at top):

- `[YYYY-MM-DD HH:MM]` Short description of change, files touched, tests run, outcome.
- Example:
  - `[2025-12-26 22:15] Added timeout + logging to src/api/client.ts; updated client.test.ts; lint+type+test all green.`

---

## Decision log

Use this to avoid re-thinking the same trade-offs:

- **Decision:** (e.g., “Use zod for client-side validation in auth flows.”)  
  **Context:** Files, constraints.  
  **Date:** YYYY-MM-DD.  
  **Status:** Accepted / Revisit.

---

## Open questions / blocked items

Track anything that needs clarification or external input:

- `[BLOCKED]` Waiting on API contract for `/v2/report`.
- `[QUESTION]` Should React tests use MSW for all API calls?

---

## Next steps

Maintain a concise, actionable list:

1. Implement …
2. Add tests for …
3. Run `npm run lint && npm run type-check && npm run test`.
4. Prepare PR with summarized changes and risk assessment.

---

## Usage notes

- **After each significant edit:**
  - Update **Phase** if you moved from design to implementation or validation.
  - Append an entry to **Recent changes**.
- **When resuming a session:**
  - Read **Context summary**, **Decision log**, and **Open questions** first.
  - Set **Current phase** explicitly.
- **When handing off work:**
  - Ensure **Next steps** clearly describes what remains and where to look.
```

If you paste these three files alongside your existing `.mdc` rules, you will have the missing anti-patterns, tool-efficiency guidance, and the session memory companion you described.[1]
