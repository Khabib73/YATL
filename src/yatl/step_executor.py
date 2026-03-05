from render import TemplateRenderer
from extractor import DataExtractor
from validator import ResponseValidator
from request_builder import RequestBuilder
import requests
import yaml


class StepExecutor:
    def __init__(
        self,
        data_extractor: DataExtractor,
        template_renderer: TemplateRenderer,
    ):
        self.data_extractor = data_extractor
        self.template_renderer = template_renderer

    def run_step(self, step, context):
        resolved_step = self.template_renderer.render_data(step, context)
        self.request_builder = RequestBuilder(step, context, resolved_step)
        response = requests.request(**self.request_builder.build())
        if "expect" in resolved_step:
            validator = ResponseValidator(response, resolved_step["expect"])
            validator.check_expectations()

        if "extract" in resolved_step:
            extracted = self.data_extractor.extract(response, resolved_step["extract"])
            context.update(extracted)

        return context

    def create_context(self, test_spec: dict):
        context = {}
        for k, v in test_spec.items():
            if k == "steps":
                return context
            context[k] = v
        return context

    def run_test(self, yaml_path: str):
        with open(yaml_path, "r", encoding="utf-8") as f:
            test_spec: dict = yaml.safe_load(f)

        context = self.create_context(test_spec)

        print(f"Run test: {test_spec.get('name', '')}")
        steps = test_spec.get("steps", [])
        for i, step in enumerate(steps, start=1):
            print(f"Step {i}: {step.get('name', '')}")
            context = self.run_step(step, context)

        print("Test has been completed")
