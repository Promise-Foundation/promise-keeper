# Template: Software Debug Promise

Use this when promising to fix a bug or debug code.

## Template

```
PROMISE CARD

From: @your_name
Domain: /software/debug
Promise: Fix [specific error/bug] in [file/module] by [date/time]
Success criteria:
  - Error no longer occurs with [test case]
  - No new errors introduced
  - [Specific tests] pass
Evidence plan:
  - GitHub/GitLab commit link
  - Test output showing fix
  - [Optional: CI/CD pipeline status]
Assessment window: [date/time]
Failure modes: kept / broken / inconclusive

Confidence: [%]
Top uncertainties:
  1. [Primary risk]
  2. [Secondary risk]
```

## Filled Example

```
PROMISE CARD

From: @debugger_agent
Domain: /software/debug
Promise: Fix IndexError in data_processor.py line 112 by Friday Feb 7, 5pm UTC
Success criteria:
  - IndexError no longer occurs with test_dataset.csv
  - No new errors introduced
  - All existing unit tests pass
Evidence plan:
  - GitHub commit link
  - pytest output showing tests pass
  - CI/CD pipeline green
Assessment window: Saturday Feb 8, 12pm UTC
Failure modes: kept / broken / inconclusive

Confidence: 80%
Top uncertainties:
  1. May have dependencies on other modules
  2. Test coverage might be incomplete
```

## Evidence Quality Levels

- **E0**: Self-attested
- **E1**: Third-party observed
- **E2**: Artifact reference (commit link)
- **E3**: Multi-party verified
- **E4**: Cryptographic proof

Recommended minimum for /software/debug: E2
