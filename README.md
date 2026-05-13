# NLT

NLT is a PRD-driven Python service scaffold. The repository currently focuses on
turning a Markdown product requirements document into a structured feature
backlog and exposing that backlog through a tiny standard-library HTTP API.

> Note: no PRD file is currently checked into this repository. The code accepts a
> PRD path at runtime so a future PRD can drive the implementation without
> changing the package layout.

## What is included

- A Markdown PRD parser that extracts feature sections, priorities, descriptions,
  and acceptance criteria.
- A small HTTP server with health and feature-list endpoints.
- A CLI for parsing a PRD or serving it over HTTP.
- Unit tests that document the supported PRD shape.

## Expected PRD shape

The parser is intentionally permissive. It treats level-two or level-three
headings as feature boundaries and recognizes priority labels and task-list
acceptance criteria.

```markdown
## Feature: User onboarding
Priority: high

Users can create an account and complete an onboarding flow.

Acceptance Criteria:
- [ ] New users can register with an email address.
- [ ] Users see the first-step checklist after signing in.
```

## CLI usage

Parse a PRD and print JSON:

```bash
python -m nlt parse path/to/PRD.md
```

Serve the parsed PRD over HTTP:

```bash
python -m nlt serve path/to/PRD.md --host 127.0.0.1 --port 8000
```

Then open:

- `GET /healthz` for process health.
- `GET /api/features` for parsed PRD features.
