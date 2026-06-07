from after_effects_pipeline.video_contact_sheet import (
    render_contact_sheet_markdown,
    sheet_filter,
    sheet_rows,
)


def test_sheet_rows_rounds_up_to_cover_max_frames():
    assert sheet_rows(columns=12, max_frames=96) == 8
    assert sheet_rows(columns=10, max_frames=91) == 10


def test_sheet_filter_samples_every_requested_frame_step():
    vf = sheet_filter(frame_step=3, thumb_width=120, columns=12, rows=8)

    assert "select='not(mod(n\\,3))'" in vf
    assert "scale=120:-1" in vf
    assert "tile=12x8" in vf


def test_contact_sheet_markdown_joins_analysis_notes():
    payload = {
        "case_count": 1,
        "frame_step": 3,
        "thumb_width": 120,
        "max_frames": 96,
        "output_dir": "/repo/artifacts/visual_analysis/contact_sheets",
        "cases": [
            {
                "case_id": "sample",
                "output_path": "/repo/artifacts/visual_analysis/contact_sheets/sample.png",
                "ok": True,
            }
        ],
    }
    analysis = {
        "cases": [
            {
                "case_id": "sample",
                "notes": ["steady_motion"],
                "warnings": ["dense_foreground"],
            }
        ]
    }

    markdown = render_contact_sheet_markdown(payload, analysis)

    assert "[open](contact_sheets/sample.png)" in markdown
    assert "steady_motion" in markdown
    assert "dense_foreground" in markdown
