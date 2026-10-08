# Coding Guidelines

These guidelines are generic. They apply to any project in any language unless the
project's own profile (Appendix C) overrides a specific rule. They were first written
for a web UI project and generalised, so they cover services, libraries, scripts and
user interfaces alike.

**How to adopt in a project**

1. Copy this file into the repository root, or link to it from `CONTRIBUTING.md`.
2. Fill in Appendix C (project profile): stack, tooling commands, directory layout, and
   any rule the project changes. Keep the profile short; everything else stays as is.
3. Enforce what can be enforced with tooling (formatter, linter, type checker, tests in
   CI). A rule that tooling can check should never be left to review.

**Rule wording.** *MUST* and *MUST NOT* are hard rules; a reviewer blocks on them.
*SHOULD* is the default; deviating needs a one-line reason in the PR or a code comment.
*MAY* is optional.

---

## 1. Principles

1. **Readability over cleverness.** Code is read far more often than it is written.
   Prefer the obvious implementation. If a trick is needed, explain why in a comment.
2. **Small, single-purpose units.** A function does one thing; a module owns one
   concern; a PR makes one change.
3. **Make illegal states unrepresentable.** Use types, enums and constructors so that
   invalid data cannot be built, rather than validating it everywhere it is used.
4. **Fail loudly and early.** Validate at the boundary (user input, network, files,
   environment). Inside the boundary, trust the types and do not re-check.
5. **Explicit over implicit.** No hidden global state, no action at a distance, no magic
   values. Dependencies are passed in, not reached for.
6. **Boring technology.** Use the standard library and well-maintained, widely used
   dependencies. Add a dependency only when it removes real code or risk.
7. **Delete what is unused.** Dead code, commented-out code, unused flags and stale
   TODOs are removed, not kept "just in case". Version control remembers.
8. **Consistency wins.** When this document and the surrounding code disagree, follow
   the surrounding code within that file and raise the inconsistency separately.

---

## 2. Repository layout and module boundaries

- One top-level directory per concern (for example `src/`, `tests/`, `docs/`,
  `scripts/`, `config/`). The project profile names the exact layout.
- Group code by **feature or domain**, not by technical kind. Prefer
  `orders/{model,service,api}` over `models/order`, `services/order`, `api/order`.
- Each module has a clear public surface. Everything else is private by convention
  (`_name`, `internal/`, non-exported) or by the language's visibility rules.
- Dependencies point inward: UI or transport → application logic → domain → nothing.
  Domain code MUST NOT import from transport, UI, database or framework layers.
- No circular imports. If two modules need each other, extract the shared part.
- Shared utilities live in one place (`common/`, `utils/`) and MUST stay small and
  generic. A "util" that knows about one feature belongs to that feature.
- Generated files are committed only when the build cannot regenerate them, and are
  marked as generated at the top. Never edit a generated file by hand.

---

## 3. Naming

- Names say **what** something is or does, not how. `remainingBudget`, not `tmp2`.
- Use full words. Abbreviations are allowed only when they are universal in the domain
  (`id`, `url`, `http`, `isin`, `pnl`) and used consistently.
- Booleans read as predicates: `isReady`, `hasAccess`, `canRetry`, `shouldSkip`.
- Functions are verbs or verb phrases: `fetchOrders`, `computeFees`, `toCsv`.
  Pure transformations MAY use `to…`/`as…`; predicates use `is…`/`has…`.
- Collections are plural (`orders`), single items singular (`order`). Maps name both
  key and value when it helps: `orderById`, `pricesByIsin`.
- Constants are named by meaning, not value: `MAX_RETRIES`, never `THREE`.
- Match the language's casing convention exactly (profile lists it). Mixing styles in
  one codebase is a defect.
- One name per concept across the codebase. Do not call the same thing `user`,
  `account` and `customer` in different files.
- File names match the main thing they export. One primary export per file.
- Avoid negated names (`notFound`, `disableX`) when a positive form works; double
  negatives in conditions are forbidden.

---

## 4. Code structure

**Functions**
- Keep functions short enough to read without scrolling. A function longer than about
  40 lines, or nested more than 3 levels deep, SHOULD be split.
- Prefer at most 3 or 4 positional parameters. Beyond that, pass an options object,
  dataclass or struct.
- Return early. Guard clauses at the top beat deep `if/else` ladders.
- A function either **does** something (side effects) or **computes** something
  (returns a value). Avoid mixing them. Pure functions are the default; side effects
  are pushed to the edges and named clearly (`save…`, `send…`, `write…`).
- No boolean "mode" parameters that switch behaviour (`render(data, true)`). Use two
  functions or an enum.
- Do not mutate arguments. Return new values. Where mutation is needed for performance,
  the function name or docstring says so.

**Control flow and expressions**
- No magic numbers or strings. Name them as constants with a comment on their origin.
- Prefer exhaustive `switch`/`match` over `if` chains on enums, and make the compiler or
  linter enforce exhaustiveness where the language supports it.
- Avoid clever one-liners and nested ternaries. Split into named intermediate values.
- Comparisons and arithmetic on money, time and quantities use the project's chosen
  types (decimal, duration, timezone-aware datetime), never raw floats or naive dates.

**Modules and classes**
- Prefer plain functions and data over classes. Use a class when there is real state
  with invariants to protect.
- Composition over inheritance. Inheritance depth beyond one level needs justification.
- Interfaces/protocols define boundaries that have more than one implementation or that
  tests need to replace (a broker client, a clock, a filesystem). Do not add an
  interface for a thing with exactly one implementation and no test seam.
- Constructors do not do I/O. Anything that can fail at runtime happens in an explicit
  `init`/`connect`/`load` step.

---

## 5. Types and data

- Use the language's static typing wherever it exists. New code is fully typed; `any`,
  `object`, untyped `dict` and friends are forbidden at public boundaries.
- Model domain concepts as named types (`OrderId`, `Money`, `Percent`), not as bare
  strings and numbers, when confusion between them would be a bug.
- Prefer immutable data (frozen dataclasses, `readonly`, `const`, records). Mutable
  state has a single owner.
- Optional values are explicit (`Optional`, `| undefined`, `Option`). Never use sentinel
  values such as `-1`, `""` or `0` to mean "absent".
- Parse, don't validate: convert external input into a typed value once at the boundary
  and pass the typed value inward.
- Serialisation formats (JSON, YAML, CSV, DB rows) have one schema definition that is
  used for both reading and writing. Schema changes are versioned and migrated.

---

## 6. Error handling

- Errors are part of the API. Each public function documents what it raises or returns
  on failure.
- Use the language's native mechanism consistently (exceptions, `Result`, error
  returns). Do not mix styles within one layer.
- Catch only what you can handle. A `catch`/`except` block MUST do one of: recover,
  translate into a domain error, add context and re-raise, or log and re-raise at the
  top level. Swallowing errors silently is forbidden.
- Never catch the broadest error type except at a top-level boundary (request handler,
  CLI entry point, job runner), and there it MUST log with the stack trace.
- Error messages say what failed, with which inputs (never secrets), and if possible
  what to do. "Something went wrong" is not a message.
- Distinguish **expected** failures (validation, not found, permission) from
  **unexpected** ones (bugs, infrastructure). Expected failures are typed and handled;
  unexpected ones propagate and alert.
- Retries are explicit, bounded, and use backoff. Retrying a non-idempotent operation
  requires an idempotency key.
- Fail closed for anything that moves money, deletes data or changes access.

---

## 7. Logging, metrics and observability

- Use the project's logging library, never `print`/`console.log` in committed code,
  except in CLIs whose purpose is to print.
- Structured logs (key/value fields) over free text. Include a correlation or request id
  where one exists.
- Log levels: `error` for things needing action, `warn` for degraded but handled,
  `info` for lifecycle and business events, `debug` for diagnostics off by default.
- Never log secrets, tokens, passwords, full card or account numbers, or personal data
  beyond what the project profile explicitly allows.
- Log once per event at the place that understands it. Do not log the same error at
  every layer as it propagates.
- Anything users or operators depend on (jobs, queues, external calls) exposes a metric
  or a health check.

---

## 8. Configuration and secrets

- Configuration comes from the environment or a config file, never from code
  constants. Defaults live in one place and are documented.
- Every config value is validated at startup with a clear error naming the key.
- Secrets MUST NOT be committed, logged or printed. They are injected via environment
  variables or a secrets manager. `.env` files are git-ignored; an `.env.example` with
  placeholder values is committed.
- Feature flags are temporary. Each flag records its owner and removal condition.

---

## 9. Dependencies

- Pin versions with a lock file, and commit the lock file.
- Adding a dependency needs: a maintained upstream, a compatible licence, a reason in
  the PR description, and no reasonable standard-library alternative.
- Keep dependencies updated on a schedule. Security advisories are fixed within the
  project's agreed window (profile).
- Wrap third-party libraries that are likely to change or be replaced (payment, broker,
  analytics, UI widget kits) behind a thin internal interface.
- Never vendor or copy library code without recording its origin and licence.

---

## 10. Testing

**What to test**
- Every bug fix comes with a test that fails before the fix and passes after.
- Public functions and modules have unit tests for the happy path, each documented
  failure mode, and boundary values (empty, one, many, max, negative, zero, unicode).
- Logic that touches money, time zones, permissions, or state machines is tested
  exhaustively, including transitions that must be impossible.
- Integration tests cover each real external boundary (database, HTTP, files, queues)
  at least once per code path that uses it.
- UI components are tested through behaviour (what the user sees and does), not through
  implementation details.

**How to test**
- Tests are deterministic. No real time, randomness, network or shared mutable state.
  Inject a clock, seed randomness, and use fakes or recorded fixtures.
- One behaviour per test, named so the failure message explains the broken rule:
  `rejects_order_when_quantity_exceeds_cap`.
- Arrange, act, assert, in that order, with blank lines between them. No logic
  (loops, conditionals) in test bodies; use parametrised cases instead.
- Prefer fakes and in-memory implementations over mocks. Mock only at the boundary you
  own. Never mock the thing under test.
- Test data is built by small factory helpers with sensible defaults, so tests show only
  what matters to them.
- Flaky tests are fixed or deleted the day they are found. Skipping, quarantining or
  retrying a flaky test to get green is forbidden.

**Coverage**
- The project profile sets a minimum line or branch coverage gate. Coverage is a floor
  that catches untested files, not a goal; a tested file with poor assertions is worse
  than an honest gap.

---

## 11. Performance

- Correct first, then measure, then optimise. Do not optimise without a measurement that
  shows a problem and a target that says when it is fixed.
- Avoid known traps by default: N+1 queries, unbounded result sets, loading whole files
  into memory, string concatenation in loops, synchronous I/O on hot paths, re-rendering
  whole trees on every change.
- Set timeouts and size limits on every external call and every queue.
- Record the measurement and the before/after numbers in the PR for any change made for
  performance.

---

## 12. Security

- Validate and type all input at the boundary. Treat everything from users, networks,
  files and third parties as hostile.
- Use parameterised queries. String-built SQL, shell commands or HTML is forbidden.
- Output is escaped for its context (HTML, URL, shell, SQL). Use the framework's
  escaping, never hand-rolled.
- Authentication and authorisation checks live in one place (middleware, decorator,
  guard) and are applied by default, with explicit opt-out for public routes.
- Secrets, tokens and session identifiers are never in URLs, logs, error messages or
  client-side storage beyond what the platform requires.
- Dependencies are scanned for known vulnerabilities in CI.
- Anything that spends money, deletes data, or changes access needs: an explicit
  confirmation path, an audit record, and a test for the denial case.
- Cryptography: use the platform library; never implement primitives; never hard-code
  keys.

---

## 13. Comments and documentation

- Comments explain **why**, not what. If a comment restates the code, delete it; if the
  code needs the comment to be understood, consider renaming or restructuring first.
- Every public module, class and function has a docstring or doc comment: one sentence
  on purpose, then parameters, return value, errors, and any non-obvious contract
  (ordering, thread safety, units, time zones).
- `TODO`/`FIXME` comments include an owner or ticket reference and a condition for
  removal. Untracked TODOs are removed at review.
- Each repository has a `README` that lets a new contributor run, test and build the
  project within 15 minutes using only the commands it lists.
- Architecture decisions that affect more than one module are recorded as short
  decision records (what was decided, why, alternatives, date) in `docs/`.
- Documentation changes ship in the same PR as the code they describe.

---

## 14. Version control

**Branches**
- `main` (or the profile's default branch) is always releasable. Work happens on short-
  lived branches named `<type>/<short-description>`, for example `feat/order-retry`,
  `fix/nav-rounding`, `chore/bump-deps`.
- Branches live days, not weeks. Large work is split into incremental PRs behind a flag
  if needed.
- Never rewrite history on a shared branch. Rebase or squash only your own unpublished
  commits.

**Commits**
- Each commit is a single logical change that builds and passes tests on its own.
- Subject line: imperative mood, at most 72 characters, no trailing period, optionally
  prefixed with a type and scope: `fix(orders): round quantity before placing`.
  Allowed types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`,
  `ci`, `revert`.
- Body explains why the change is needed and anything surprising about how. Reference
  the issue or requirement id.
- Do not commit secrets, build output, editor settings, or large binaries (profile lists
  size limits and any LFS use).

**Pull requests**
- One concern per PR. Refactors are separate from behaviour changes. A reviewer should
  be able to read the whole diff in one sitting (as a guide, under 400 changed lines).
- The description states: what changed, why, how it was tested, and anything the
  reviewer should look at first. Screenshots or recordings for UI changes.
- CI MUST be green before review is requested. The author resolves conflicts, not the
  reviewer.
- The author merges after approval, using the repository's merge strategy (profile).
  Nobody merges their own PR without review except for trivial, pre-agreed cases.

---

## 15. Code review

**Author**
- Review your own diff first. Remove debugging leftovers, stray formatting changes and
  unrelated edits.
- Respond to every comment: fix it, or explain why not. Resolve threads only when the
  reviewer's point is addressed.

**Reviewer**
- Respond within one working day, or say when you can.
- Review for: correctness, tests, security, naming, and whether the change matches its
  stated intent. Do not review formatting that a tool enforces.
- Distinguish blocking from optional comments. Prefix non-blocking ones with `nit:` or
  `optional:`.
- Comment on the code, not the person. Ask questions when intent is unclear rather than
  assuming.
- Approve when the change is an improvement and safe to ship, not when it is perfect.

---

## 16. Tooling and automation

Every project MUST have, wired into CI and runnable locally with one command each:

| Check | Purpose | Blocking |
|---|---|---|
| Formatter | One style, no debate (`prettier`, `ruff format`, `gofmt`, …) | Yes |
| Linter | Catches bugs and banned patterns | Yes |
| Type checker | Where the language has one | Yes |
| Unit tests | Fast, run on every push | Yes |
| Integration tests | Slower, run on every PR | Yes |
| Dependency audit | Known vulnerabilities | Yes, per profile window |
| Build | The artefact that ships | Yes |

- Formatting and import ordering are never discussed in review; the tool decides.
- Linter rules are enabled in the strictest sensible preset; disabling a rule is a
  project-wide decision recorded in the profile, not an inline suppression. Inline
  suppressions need a comment explaining why.
- Pre-commit hooks run the formatter and linter locally so CI rarely fails on them.

---

## 17. Definition of done

A change is done when all of the following hold:

- [ ] Behaviour matches the requirement or ticket, including edge cases listed there.
- [ ] New and changed code is typed, formatted, lint-clean and documented.
- [ ] Tests cover the change (happy path, failure modes, boundaries) and all tests pass.
- [ ] No secrets, debug output, dead code or unrelated changes in the diff.
- [ ] Logs, metrics and error messages are adequate for someone debugging this in
      production without the author.
- [ ] README, docs and config examples are updated if behaviour or setup changed.
- [ ] The PR description explains what, why and how it was verified.
- [ ] Reviewed and approved; CI green on the final commit.

---

## Appendix A: Web UI addendum

Applies to browser-facing projects (for example a React or similar component-based UI).
These rules add to, and never replace, the generic ones above.

- **Components are small and pure.** A component renders from props and local state.
  Data fetching, side effects and business logic live in hooks, services or a state
  layer, not in render code.
- **One component per file**, named like the file. Co-locate its styles, tests and
  stories next to it.
- **Props are typed** and documented. Avoid prop drilling deeper than two levels; use
  context or composition instead.
- **State lives as low as possible** and is lifted only when shared. Server state is
  handled by a dedicated data-fetching layer with caching and error states, not stored
  by hand in global state.
- **Every async view has loading, empty, error and success states**, and each is tested.
- **Accessibility is a requirement**: semantic HTML, keyboard operability, visible
  focus, labels for every input, sufficient colour contrast, and no information carried
  by colour alone. Run an accessibility linter in CI.
- **No inline styles or magic pixel values.** Use the design system's tokens (spacing,
  colour, typography). Hard-coded colours and fonts are a defect.
- **User-facing strings are externalised** for translation and never concatenated into
  sentences; use templates with named placeholders.
- **Performance budget**: define bundle-size and interaction-latency budgets in the
  profile and enforce them in CI. Lazy-load routes and heavy widgets.
- **Never trust the client**: all authorisation and validation is repeated on the
  server; client checks are for user experience only.
- **No direct DOM manipulation** outside of clearly isolated adapters.

## Appendix B: Backend, service and script addendum

Applies to APIs, workers, batch jobs, data pipelines and CLIs.

- **Idempotent operations** wherever a retry or replay is possible. Every write that
  can be repeated carries an idempotency key or is naturally idempotent.
- **One writer per store.** Shared state has a single owning process or module; others
  read through it or through read-only views.
- **Time**: store and compute in UTC with timezone-aware types; convert at the edge for
  display. Calendars (business days, trading sessions, holidays) are data, not code.
- **Money and quantities** use exact decimal types with explicit rounding rules per
  domain. Floating point is for science, not ledgers.
- **Database access** goes through a single layer; migrations are versioned, reversible
  where possible, and run in CI against a fresh database.
- **Long-running jobs** are resumable, log progress, and emit a heartbeat. A job that
  cannot finish fails loudly rather than hanging.
- **CLIs** have `--help`, exit non-zero on failure, print errors to stderr, and never
  prompt interactively when stdin is not a terminal.
- **External calls** have a timeout, bounded retries with backoff, and a circuit for
  repeated failure. Rate limits are respected by construction (a limiter in the client),
  not by hoping.
- **Scripts in the repository** are reproducible: they take inputs as arguments, declare
  their dependencies, and write outputs to a named location. A script's captured output
  that is quoted in docs is committed next to it so numbers can be regenerated.

## Appendix C: Project profile (template)

Copy this section into the adopting project and fill it in. Anything not listed here
follows the generic rules above.

```
Project:            <name, e.g. arc-ui-tekion-web>
Default branch:     <main>
Merge strategy:     <squash | rebase | merge>
Language(s):        <TypeScript 5.x / Python 3.12 / …>
Runtime/toolchain:  <Node 20 + pnpm / uv / …>
Casing:             <files kebab-case, types PascalCase, vars camelCase, …>
Layout:             <src/features/<feature>/{components,hooks,api,tests}, …>

Commands
  install:          <pnpm install | uv sync>
  format:           <pnpm format | ruff format .>
  lint:             <pnpm lint | ruff check .>
  typecheck:        <pnpm typecheck | mypy .>
  test:             <pnpm test | pytest>
  build:            <pnpm build | …>

Gates
  coverage floor:   <80% lines>
  bundle budget:    <n kB gzipped per route (UI only)>
  vuln fix window:  <7 days high/critical, 30 days other>
  max file size:    <1 MB; larger via LFS>

Overrides (rule → project value, one line each, with reason)
  §3 abbreviations allowed:   <id, url, dto, …>
  §16 disabled lint rules:    <rule: reason>
  §14 commit types:           <as generic | project list>
  Logging of personal data:   <what is permitted, and where>

Owners / reviewers:  <team or CODEOWNERS path>
```
