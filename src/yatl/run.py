import os
from .step_executor import StepExecutor
from .extractor import DataExtractor
from .render import TemplateRenderer
import concurrent.futures
from .utils import create_context, load_yaml_test, search_files


class Runner:
    """Orchestrates the execution of YAML-based test suites.

    Loads test specifications from YAML files, runs each step sequentially,
    and maintains a context that is passed between steps.
    """

    def __init__(
        self,
        data_extractor: DataExtractor,
        template_render: TemplateRenderer,
    ):
        """Initializes the runner with required services.

        Args:
            data_extractor: Used to extract values from HTTP responses.
            template_render: Used to render templates in test steps.
        """
        self.data_extractor = data_extractor
        self.template_render = template_render
        self.step_executor = StepExecutor(data_extractor, template_render)

    def _is_skipped_test(self, test_spec: dict, result_info: list[str]):
        """Checks if a test is skipped based on the "scip" flag.

        Args:
            test_spec: The parsed YAML dictionary.

        Returns:
            True if the test is skipped, False otherwise.
        """
        if test_spec.get("skip", False):
            result_info.append(f"Test {test_spec.get('name', '')} skipped")
            return True
        return False

    def _is_skipped_step(self, step: dict, result_info: list[str]):
        """Checks if a step is skipped based on the "skip" flag.

        Args:
            step: The parsed YAML dictionary.

        Returns:
            True if the step is skipped, False otherwise.
        """
        if step.get("skip", False):
            result_info.append(f"Step {step.get('name', '')} skipped")
            return True
        return False

    def _print_progress(self, result_info: list[str]):
        """Prints progress messages to the console.

        Args:
            result_info: List of messages to print.
        """
        for line in result_info:
            print(line)

    def run_test(self, yaml_path: str):
        """Executes a single test file.

        Loads the test, creates the initial context, runs each step in order,
        and prints progress messages. The context is updated after each step
        with extracted values.

        Args:
            yaml_path: Path to the test YAML file.
        """
        result_info = []
        result_info.append("-" * 10)
        test_spec: dict = load_yaml_test(yaml_path)
        if test_spec is None:
            return
        context = create_context(test_spec)
        if self._is_skipped_test(test_spec, result_info):
            return
        result_info.append(f"Run test: {test_spec.get('name', '')}")
        steps = test_spec.get("steps", [])
        for i, step in enumerate(steps, start=1):
            step: dict
            if step is None:
                continue
            if self._is_skipped_step(step, result_info):
                continue
            result_info.append(f"Step {i}: {step.get('name', '')}")
            context = self.step_executor.run_step(step, context)

        self._print_progress(result_info)

    def run_all_tests(self, max_workers=None):
        """Discovers and runs all test files in the current working directory.

        Searches recursively for files ending with .test.yaml or .test.yml,
        executes each one, and prints separators between tests.

        Args:
            max_workers: Maximum number of threads to use. If None, uses
                the default of `min(32, os.cpu_count() + 4)`.
        """
        files = search_files(os.getcwd(), ".", [])

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.run_test, file): file for file in files}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Test {futures[future]} failed with error: {e}")


if __name__ == "__main__":
    runner = Runner(
        DataExtractor(),
        TemplateRenderer(),
    )
    runner.run_all_tests(max_workers=10)
