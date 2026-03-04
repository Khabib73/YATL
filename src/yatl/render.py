from jinja2 import Template


class TemplateRenderer:
    def __init__(self):
        pass

    def render_data(self, data, context):
        if isinstance(data, str):
            return Template(data).render(context)
        elif isinstance(data, dict):
            return {
                key: self.render_data(value, context) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self.render_data(item, context) for item in data]
        else:
            return data
