from .render import TemplateRenderer
from .extractor import DataExtractor
from .validator import ResponseValidator
from .request_builder import RequestBuilder
import requests


class StepExecutor:
    def __init__(
        self,
        data_extractor: DataExtractor,
        template_renderer: TemplateRenderer,
    ):
        self.data_extractor = data_extractor
        self.template_renderer = template_renderer

    def run_step(self, step: str, context: dict):
        resolved_step = self.template_renderer.render_data(step, context)
        self.request_builder = RequestBuilder(context, resolved_step)
        data = self.request_builder.build()
        response = requests.request(**data)

        if "expect" in resolved_step:
            validator = ResponseValidator(response, resolved_step["expect"])
            validator.check_expectations()

        if "extract" in resolved_step:
            extracted = self.data_extractor.extract(response, resolved_step["extract"])
            context.update(extracted)

        return context
