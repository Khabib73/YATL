import os
from utils import search_files
from step_executor import StepExecutor
from extractor import DataExtractor
from render import TemplateRenderer

if __name__ == "__main__":
    path = os.getcwd()
    data_extractor = DataExtractor()
    template_render = TemplateRenderer()
    step_executor = StepExecutor(data_extractor, template_render)
    print("-" * 10)
    for file in search_files(path, ".", []):
        step_executor.run_test(file)
        print("-" * 10)
