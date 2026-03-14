## Yatl - Yet Another Testing Language

Yatl is a simple testing language that allows you to write tests in YAML. If you know HTTP and Yaml, you know Yatl. This lowers entry threshold for creating API tests in our team.
You can using this framework to write tests for your applications and integration to CI/CD.

for example, create **example.test.yaml** and write the following code:

```yaml
name: test clck.ru
base_url: https://clck.ru
steps:
- name: test clck.ru
  request:
    method: GET
    params:
      url: 'https://ya.ru'
  extract:
    text_responce: text
  expect:
    status: 200
    body:
      text: "{{ text_responce }}"
```

## Usage

To use Yatl, create a test file in YAML format.
The test file should contain the following fields:

```yaml
- name: the name of the test
  variables: the global variables to be used in the test
- steps: a list of steps to be executed
    - name: the name of the step
      request: the request to be made
        url: the url to be requested
        method: the http method to be used
        headers: the headers to be used
        body:
          json: the body to be sent as json
        params: the params to be used
      expect: the expected response
        status: the expected status code
        json: the expected json response
      extract: the variables to be extracted
```

File name should be suffix **.test.yaml**