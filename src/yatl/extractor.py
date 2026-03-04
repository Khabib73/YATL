class DataExtractor:
    def __init__(self):
        pass

    def extract(self, response, extract_spec):
        extracted = {}
        if response.headers.get("content-type") == "application/json":
            resp_json = response.json()
        else:
            resp_json = None

        for key, path in extract_spec.items():
            if path is None:
                if resp_json and key in resp_json:
                    extracted[key] = resp_json[key]
                else:
                    raise ValueError(f"Поле '{key}' не найдено в JSON-ответе")
            else:
                if resp_json and path in resp_json:
                    extracted[key] = resp_json[path]
                else:
                    raise ValueError(f"Не удалось извлечь '{key}' по пути '{path}'")

        return extracted
