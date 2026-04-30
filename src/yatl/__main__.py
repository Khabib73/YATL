"""CLI entry point for YATL."""

import argparse

from .run import Runner, run_tests_concurrently
from .extractor import DataExtractor
from .render import TemplateRenderer
from .validator import ResponseValidator


def main():
    parser = argparse.ArgumentParser(description="Yet Another Testing Language")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to directory containing .yatl.yaml files (default: current directory)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=10,
        help="Number of worker threads (default: 10)",
    )

    args = parser.parse_args()

    runner = Runner(DataExtractor(), TemplateRenderer(), ResponseValidator)

    run_tests_concurrently(runner, test_path=args.path, max_workers=args.workers)


if __name__ == "__main__":
    main()
