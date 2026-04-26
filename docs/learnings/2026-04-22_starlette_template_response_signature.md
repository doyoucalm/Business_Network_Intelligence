# Learning — 2026-04-22: Starlette TemplateResponse Signature Trap

## The bug

After Stage 3 deployment, every admin page returned **HTTP 500** with:
```
TypeError: unhashable type: 'dict'
```

Stack trace pointed deep into Jinja2's `Environment.get_template()`:
```python
cache_key = (weakref.ref(self.loader), name)
template = self.cache.get(cache_key)  # ← TypeError here
```

## Wrong rabbit hole (~7 minutes lost)

The error message points at Jinja2 internals. The instinct is to debug Jinja2:
- Is the loader broken?
- Is the cache corrupted?
- Is `name` somehow a dict?

The implementer (Gemini CLI) chased all three before instrumenting `get_template` with a debug wrapper that revealed:
```
get_template called with: {'request': ..., 'chapter': ..., 'meetings': [], ...}
type: <class 'dict'>
```

`name` was the **context dict**, not the template name string.

## Root cause

The 4 new route files used the **deprecated** Starlette TemplateResponse signature:

```python
# OLD (deprecated in Starlette 0.27, removed by 1.0):
return templates.TemplateResponse("admin/meetings.html", {
    "request": request,
    "chapter": chapter,
    ...
})

# NEW (required in Starlette 1.0):
return templates.TemplateResponse(
    request,
    "admin/meetings.html",
    {"chapter": chapter, ...}
)
```

The container runs Starlette 1.0.0. With the old signature, the context dict gets shoved into the `name` parameter slot internally, ending up as `name` in `get_template(name)` → unhashable cache key → `TypeError`.

## Wrong fix proposed

The implementer initially proposed **downgrading Starlette to 0.40** to restore the old API. This is backwards:
- Starlette 1.0 is current; downgrading is regression debt.
- FastAPI pins Starlette ranges; arbitrary downgrade may break FastAPI.
- The old API is **dead**, not "missing" — intentionally removed.

## Right fix

Update every `TemplateResponse(name, context)` call to `TemplateResponse(request, name, context)`. Done in commit `54decdc` across 4 route files.

After fix, all admin pages returned 200.

## Lessons

1. **Deep stack traces mislead.** The error appeared in Jinja2 but originated in user code. Always check the calling convention before suspecting the library.
2. **Read API deprecation notes.** Starlette 0.27 (mid-2024) deprecated this signature with a clear migration path. The Stage 3 implementer's pattern memory predates the change — agents trained on older tutorials will reproduce the old form by default.
3. **The "right fix" is never to downgrade a current library to match old code.** Always migrate the code forward. Downgrades trap you in dependency conflicts later.
4. **Smoke-test before declaring done.** "All files exist and look right" ≠ "the routes return 200." A single curl to one admin page would have caught this immediately. Future stages: include `curl -o /dev/null -w "%{http_code}\n" <every-route>` in the done-criteria.

## Migration pattern for any future TemplateResponse call

```python
# Search:
grep -rn "TemplateResponse(" app/

# Each match should be of the form:
templates.TemplateResponse(request, "name.html", {"key": value, ...})

# If "request" appears inside the dict — it's the OLD form, fix it.
```

## Cross-reference

This is the same class of bug as the Member.role / member_roles two-source-of-truth issue (BLOCK D earlier today): a deprecated pattern lingers in code while the framework moves on. Pattern: **on every dependency upgrade, scan for deprecated API calls before the next deploy**, not after the next 500.
