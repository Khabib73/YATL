## Yatl - Yet Another Testing Language

Yatl is a testing language that allows you to write tests in YAML.

## Installation

```bash
pip install yatl
```

## Usage

To use Yatl, create a test file in YAML format.

```yaml
name: first test

steps:
  - name: first step
    request:
      url: https://google.com
      method: GET
    expect:
      status: 200
```

To run the test, use the following command:

```bash
yatl run test.yaml
```

To run all tests in a directory, use the following command:

```bash
yatl run tests/
```