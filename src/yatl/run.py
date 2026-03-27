import os
from .step_executor import StepExecutor
from .extractor import DataExtractor
from .render import TemplateRenderer
import concurrent.futures
from .utils import create_context, search_files
import yaml
from typing import Any


class TestLoader:
    """Loads test specifications from YAML files."""

    def __init__(self):
        pass

    def load(self, yaml_path: str) -> dict[Any, Any] | None:
        """Loads and parses a YAML test file.

        Args:
            yaml_path: Path to the .test.yaml or .test.yml file.

        Returns:
            The parsed YAML as a dictionary, or None if the file is empty.
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            test_specification = yaml.safe_load(f)

        if test_specification is None:
            return None
        return test_specification


class SkipChecker:
    """
    Checks if a test or step is skipped based on the "skip" flag.
    Returns:
        True if the test or step is skipped, False otherwise."""

    def __init__(self):
        """Initializes the skip checker."""
        pass

    def is_skipped_test(self, test_specification: dict[Any, Any]) -> bool:
        """Checks if a test is skipped based on the "skip" flag.

        Args:
            test_specification: The parsed YAML dictionary.

        Returns:
            True if the test is skipped, False otherwise.
        """
        if test_specification.get("skip", False):
            return True
        return False

    def is_skipped_step(self, step: dict[Any, Any]) -> bool:
        """Checks if a step is skipped based on the "skip" flag.

        Args:
            step: The parsed YAML dictionary.

        Returns:
            True if the step is skipped, False otherwise.
        """
        if step.get("skip", False):
            return True
        return False


class Reporter:
    """Reports the results of test executions."""

    def __init__(self):
        """Initializes the reporter."""
        self.info = []

    def add_info(self, info: str) -> None:
        """Adds an information message to the reporter.

        Args:
            info: The message to add.
        """
        self.info.append(info)

    def print_info(self) -> None:
        """Prints the information messages to the console."""
        for line in self.info:
            print(line)


class ConcurrencyManager:
    """Manages concurrency for test executions."""

    def __init__(self, runner: Runner, max_workers: int = 10):
        """Initializes the concurrency manager.

        Args:
            max_workers: The maximum number of workers to use.
        """
        self.runner = runner
        self.max_workers = max_workers
        self.files = search_files(os.getcwd(), ".", [])

    def run_tests(self) -> None:
        """Runs all tests in parallel.

        Returns:
            None
        """

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = {
                executor.submit(self.runner.run_test, file): file for file in self.files
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Test {futures[future]} failed with error: {e}")


class Runner:
    """Orchestrates the execution of YAML-based test suites.

    Loads test specifications from YAML files, runs each step sequentially,
    and maintains a context that is passed between steps.
    """

    def __init__(
        self,
        step_executor: StepExecutor,
        reporter: Reporter,
        skip_cheker: SkipChecker,
        test_loader: TestLoader,
    ):
        """Initializes the runner with required services.

        Args:
            data_extractor: Used to extract values from HTTP responses.
            template_render: Used to render templates in test steps.
        """
        self.step_executor = step_executor
        self.reporter = reporter
        self.skip_cheker = skip_cheker
        self.test_loader = test_loader

    def _execute_step(
        self,
        step_number,
        step: dict,
        context: dict,
    ) -> dict[Any, Any]:
        """Execute a single step.

        Args:
            step: Parsed YAML dictionary.
            context: Current context dictionary.

        Returns:
            Updated context dictionary.
        """
        if step is None:
            return context

        if self.skip_cheker.is_skipped_step(step):
            self.reporter.add_info(
                f"Step {step_number}: {step.get('name', '')} skipped"
            )
            return context
        else:
            self.reporter.add_info(f"Step {step_number}: {step.get('name', '')}")
            return self.step_executor.run_step(step, context)

    def run_test(self, yaml_path: str) -> None:
        """Executes a single test file.

        Loads the test, creates the initial context, runs each step in order,
        and prints progress messages. The context is updated after each step
        with extracted values.

        Args:
            yaml_path: Path to the test YAML file.
        """
        test_specification = self.test_loader.load(yaml_path)

        if test_specification is None:
            return

        context = create_context(test_specification)

        if self.skip_cheker.is_skipped_test(test_specification):
            self.reporter.add_info(f"Test {test_specification.get('name', '')} skipped")
            self.reporter.print_info()
            return

        self.reporter.add_info("-" * 10)
        self.reporter.add_info(f"Run test: {test_specification.get('name', '')}")
        steps: list[dict] = test_specification.get("steps", [])

        for i, step in enumerate(steps, start=1):
            context = self._execute_step(i, step, context)

        self.reporter.print_info()


if __name__ == "__main__":
    runner = Runner(
        StepExecutor(DataExtractor(), TemplateRenderer()),
        Reporter(),
        SkipChecker(),
        TestLoader(),
    )
    concurrency_manager = ConcurrencyManager(runner, max_workers=10)
    concurrency_manager.run_tests()
