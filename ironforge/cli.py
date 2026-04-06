"""CLI entry point for Ironforge."""

import argparse
import json
from dataclasses import asdict

from ironforge.intake.flow import run_intake
from ironforge.program.builder import build_program
from ironforge.output.formatter import render


def main():
    parser = argparse.ArgumentParser(
        description="Ironforge — Evidence-Based Workout Program Designer",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    # Run intake questionnaire
    profile = run_intake()

    # Build program
    program = build_program(profile)

    # Output
    if args.format == "json":
        # Convert enums to strings for JSON serialization
        def _convert(obj):
            if hasattr(obj, "name") and hasattr(obj, "value"):
                return obj.name
            raise TypeError(f"Cannot serialize {type(obj)}")

        data = asdict(program)
        print(json.dumps(data, indent=2, default=_convert))
    else:
        output = render(program)
        print(output)


if __name__ == "__main__":
    main()
