# YATL — Yet Another Testing Language

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Khabib73/YATL?style=social)](https://github.com/Khabib73/YATL)

**YATL** is a declarative, YAML‑based testing language for API testing. If you know HTTP and YAML, you know YATL.

## Why YATL?

Writing API tests in code is cumbersome. YATL turns tests into pure data $—$ declarative, readable, and accessible to every team member.

### The Problem
- **You have to write code** – even for a simple GET request
- **High entry barrier** – need to know programming languages well
- **Complex dependencies** – chaining requests becomes spaghetti code
- **Hard to maintain** – tests become unreadable over time

### The Solution
YATL is a **domain‑specific language** that lets you describe API tests in clean YAML. No imperative code, no hidden magic.

> If you know HTTP and YAML, you know YATL.

## Quick Start


### Your First Test
Create `ping.test.yaml`:

```yaml
name: ping
base_url: google.com

steps:
  - name: access_test
    request:
      method: GET
    expect:
      status: 200
```
## Key Features

- **Declarative syntax** – describe what to test, not how
- **Data extraction & templating** – use Jinja2 to reuse response data
- **Multiple data formats** – JSON, XML, form data, multipart files
- **Parallel execution** – run tests in parallel with `--workers`
- **Skip tests & steps** – disable tests without deleting them
- **Advanced validation** – validate with rules like `gt`, `regex`, `type`

## Example

```yaml
name: User API
base_url: https://api.example.com

steps:
  - name: login
    request:
      method: POST
      url: /auth/login
      body:
        json:
          username: "test"
          password: "secret"
    expect:
      status: 200
    extract:
      token: "response.access_token"

  - name: get_profile
    request:
      method: GET
      url: /profile
      headers:
        Authorization: "Bearer {{ token }}"
    expect:
      status: 200
```

## Installation & Usage

### From PyPI (Coming Soon)
```bash
pip install yatl
```

## Documentation

Full documentation is available in the [`docs/`](docs/) directory:
- [Usage Guide (English)](docs/usage.en.md)
- [Руководство по использованию (Russian)](docs/usage.ru.md)

## CI/CD Integration

YATL fits seamlessly into CI pipelines. Example GitHub Actions workflow:

```yaml
- name: Run YATL tests
  run: yatl tests/ --workers 5
```

## Contributing

We welcome contributions! Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started.
