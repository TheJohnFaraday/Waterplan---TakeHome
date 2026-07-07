#!/usr/bin/env python3
"""CLI entrypoint. See README.md for usage."""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from waterplan import config
from waterplan.llm_client import AnthropicLLMClient
from waterplan.pipeline import Pipeline
from waterplan.report import render_csv, render_markdown

BANNER = r"""
                                          .  .  .
                                        .  ~  .  ~  .
                                      (   W A T E R   )
                                        '  .  '  .  '
                    __        __    _
                    \ \      / /_ _| |_ ___ _ __ _ __  | | __ _ _ __
                     \ \ /\ / / _` | __/ _ \ '__| '_ \ | |/ _` | '_ \
                      \ V  V / (_| | ||  __/ |  | |_) || | (_| | | | |
                       \_/\_/ \__,_|\__\___|_|  | .__/ |_|\__,_|_| |_|
                                                 |_|
                              ~ risk research tool ~
"""


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Waterplan water-risk research tool")
    parser.add_argument(
        "--locations",
        nargs="*",
        default=config.DEFAULT_LOCATIONS,
        help="Locations to research (default: the 3 example locations from the brief)",
    )
    parser.add_argument("--output", default=f"{config.OUTPUT_DIR}/report.md", help="Markdown output path")
    parser.add_argument("--csv", default=f"{config.OUTPUT_DIR}/report.csv", help="Consolidated CSV output path")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    llm = AnthropicLLMClient(api_key=api_key)
    pipeline = Pipeline(llm=llm)

    results = asyncio.run(pipeline.run(args.locations))

    markdown = render_markdown(results)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(markdown, encoding="utf-8")
    render_csv(results, args.csv)

    print(markdown)
    print(f"\n[Report written to {args.output} and {args.csv}]")


if __name__ == "__main__":
    main()
