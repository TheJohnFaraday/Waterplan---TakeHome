"""Markdown report + consolidated CSV (bonus scope)."""

import csv
from pathlib import Path

from waterplan.pipeline import LocationResult


def render_markdown(results: list[LocationResult]) -> str:
    lines = []
    for loc in results:
        lines.append(f"# 📍 Location: {loc.location}\n")
        for dim in loc.dimensions:
            lines.append(f"## {dim.emoji} Dimension: {dim.dimension_label}\n")

            if dim.insufficient:
                lines.append(f"**⚠️ INSUFFICIENT SOURCES ({dim.verified_count}/2 verified)**\n")
            if dim.contradiction_note:
                lines.append("**ℹ️ Note: sources disagree**\n")

            for s in dim.sources:
                lines.append(f"- **Data:** {s.data}")
                lines.append(f"  - **Source:** {s.url}")
                lines.append(f'  - **Excerpt:** "{s.excerpt[:300]}"')
                lines.append("  - **Validation:** ✅ MATCH FOUND\n")

            for s in dim.failed_candidates:
                lines.append(f"- **Source:** {s.url}")
                if s.excerpt:
                    lines.append(f'  - **Excerpt (candidate):** "{s.excerpt[:300]}"')
                lines.append(f"  - **Validation:** ❌ [FAILED VALIDATION: {s.error}]\n")

        lines.append("")
    return "\n".join(lines)


def render_csv(results: list[LocationResult], path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["location", "dimension", "status", "data", "url", "excerpt", "error"]
        )
        for loc in results:
            for dim in loc.dimensions:
                for s in dim.sources:
                    writer.writerow(
                        [loc.location, dim.dimension_label, "VERIFIED", s.data, s.url, s.excerpt, ""]
                    )
                for s in dim.failed_candidates:
                    writer.writerow(
                        [loc.location, dim.dimension_label, "FAILED_VALIDATION", "", s.url, s.excerpt, s.error]
                    )
