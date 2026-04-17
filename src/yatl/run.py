import concurrent.futures
import yaml
from typing import Any
from .step_executor import StepExecutor
from .extractor import DataExtractor
from .render import TemplateRenderer
from .utils import create_context, search_files
from .colors import (
    success,
    skipped,
    error,
    info,
    header,
)


def load_test_yaml(yaml_path: str) -> dict[Any, Any] | None:
    """Loads and parses a YAML test file.

    Args:
        yaml_path: Path to the .test.yaml or .test.yml file.

    Returns:
        The parsed YAML as a dictionary, or None if the file is not found."
    """
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            test_specification = yaml.safe_load(f)
            return test_specification
    except FileNotFoundError:
        return None


def is_skipped_test(test_specification: dict[Any, Any]) -> bool:
    """Checks if a test is skipped based on the "skip" flag.

    Args:
        test_specification: The parsed YAML dictionary.

    Returns:
        True if the test is skipped, False otherwise.
    """
    return test_specification.get("skip", False)


def is_skipped_step(step: dict[Any, Any]) -> bool:
    """Checks if a step is skipped based on the "skip" flag.

    Args:
        step: The parsed YAML dictionary.

    Returns:
        True if the step is skipped, False otherwise.
    """
    return step.get("skip", False)


class Reporter:
    """Simple reporter that collects and prints messages."""

    def __init__(self):
        self.info = []

    def add_info(self, info: str) -> None:
        self.info.append(info)

    def print_info(self) -> None:
        for line in self.info:
            print(line)
        self.info.clear()


def run_tests_concurrently(runner, test_path: str = ".", max_workers: int = 10) -> None:
    """Runs all tests in parallel.

    Args:
        runner: Runner instance with a run_test method.
        test_path: Path to directory containing test files.
        max_workers: Maximum number of worker threads.
    """
    files = search_files(test_path)
    if not files:
        print(skipped(f"No .test.yaml files found in {test_path}"))
        return

    print(info(f"Found {len(files)} test file(s)"))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(runner.run_test, file): file for file in files}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(error(f"Test {futures[future]} failed with error: {e}"))


class Runner:
    """Orchestrates the execution of YAML-based test suites.

    Loads test specifications from YAML files, runs each step sequentially,
    and maintains a context that is passed between steps.
    """

    def __init__(self, step_executor: StepExecutor):
        """Initializes the runner with required services.

        Args:
            step_executor: Executes individual test steps.
        """
        self.step_executor = step_executor

    def _execute_step(
        self,
        step_number: int,
        step: dict,
        context: dict,
        reporter: Reporter,
    ) -> dict[Any, Any]:
        """Execute a single step.

        Args:
            step: Parsed YAML dictionary.
            context: Current context dictionary.
            reporter: Reporter instance for logging.

        Returns:
            Updated context dictionary.
        """
        if step is None:
            return context

        if is_skipped_step(step):
            reporter.add_info(
                skipped(f"Step {step_number}: {step.get('name', '')} skipped")
            )
            return context
        else:
            reporter.add_info(info(f"Step {step_number}: {step.get('name', '')}"))

            if step.get("description"):
                reporter.add_info(info(f"description: {step.get('description', '')}"))
            elif step.get("desc"):
                reporter.add_info(info(f"description: {step.get('desc', '')}"))

            return self.step_executor.run_step(step, context)

    def run_test(self, yaml_path: str) -> None:
        """Executes a single test file.

        Loads the test, creates the initial context, runs each step in order,
        and prints progress messages. The context is updated after each step
        with extracted values.

        Args:
            yaml_path: Path to the test YAML file.
        """
        test_specification = load_test_yaml(yaml_path)
        if test_specification is None:
            return

        context = create_context(test_specification)
        reporter = Reporter()

        if is_skipped_test(test_specification):
            reporter.add_info(
                skipped(f"Test {test_specification.get('name', '')} skipped")
            )
            reporter.print_info()
            return

        reporter.add_info(header("-" * 10))
        reporter.add_info(header(f"Run test: {test_specification.get('name', '')}"))

        steps: list[dict] = test_specification.get("steps", [])

        for i, step in enumerate(steps, start=1):
            context = self._execute_step(i, step, context, reporter)

        reporter.add_info(success("Test passed"))
        reporter.print_info()


if __name__ == "__main__":
    runner = Runner(StepExecutor(DataExtractor(), TemplateRenderer()))
    run_tests_concurrently(runner, max_workers=10)
