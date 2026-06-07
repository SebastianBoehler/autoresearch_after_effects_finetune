from pathlib import Path
from types import SimpleNamespace

from after_effects_pipeline.overlap_visual_review import (
    build_overlap_visual_review,
    render_overlap_visual_review_markdown,
)


def test_overlap_visual_review_builds_pair_sheet(tmp_path):
    contact_dir = tmp_path / "contacts"
    contact_dir.mkdir()
    _write_image(contact_dir / "a.png", "red")
    _write_image(contact_dir / "b.png", "blue")

    payload = build_overlap_visual_review(
        render_overlap={
            "potential_overlaps": [
                {
                    "a": "a",
                    "b": "b",
                    "score": 0.91,
                    "split_a": "train",
                    "split_b": "test",
                    "same_split": False,
                    "shared_signals": ["aspect=landscape"],
                }
            ]
        },
        contact_sheet_dir=contact_dir,
        output_dir=tmp_path / "out",
        runner=_fake_runner,
    )

    assert payload["summary"]["pair_count"] == 1
    assert payload["summary"]["ok_count"] == 1
    assert Path(payload["pairs"][0]["output_path"]).exists()
    assert "a / b" in render_overlap_visual_review_markdown(payload)


def test_overlap_visual_review_reports_missing_contact_sheet(tmp_path):
    payload = build_overlap_visual_review(
        render_overlap={
            "potential_overlaps": [
                {"a": "a", "b": "missing", "score": 0.9, "shared_signals": []}
            ]
        },
        contact_sheet_dir=tmp_path,
        output_dir=tmp_path / "out",
        runner=_fake_runner,
    )

    assert payload["summary"]["ok_count"] == 0
    assert payload["pairs"][0]["ok"] is False
    assert payload["pairs"][0]["missing"]


def _write_image(path: Path, color: str) -> None:
    path.write_bytes(color.encode("ascii"))


def _fake_runner(command, capture_output, check):
    Path(command[-1]).write_bytes(b"fake image")
    return SimpleNamespace(returncode=0, stderr=b"")
