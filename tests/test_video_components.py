from after_effects_pipeline.video_components import foreground_component_metrics


def test_blank_frame_has_no_foreground_components():
    frame = bytes([0, 0, 0] * 24)

    metrics = foreground_component_metrics(frame, 6, 4, 0, 0, 0, stride=1)

    assert metrics == {
        "component_count": 0.0,
        "largest_component_ratio": 0.0,
        "largest_component_share": 0.0,
        "edge_touch_component_ratio": 0.0,
    }


def test_separated_blocks_count_as_two_components():
    frame = _frame(8, 4, [(1, 1, 2, 2), (5, 1, 2, 2)])

    metrics = foreground_component_metrics(frame, 8, 4, 0, 0, 0, stride=1)

    assert metrics["component_count"] == 2.0
    assert metrics["largest_component_ratio"] == 4 / 32
    assert metrics["largest_component_share"] == 0.5
    assert metrics["edge_touch_component_ratio"] == 0.0


def test_merged_block_is_one_dominant_component():
    frame = _frame(8, 4, [(1, 1, 5, 2)])

    metrics = foreground_component_metrics(frame, 8, 4, 0, 0, 0, stride=1)

    assert metrics["component_count"] == 1.0
    assert metrics["largest_component_share"] == 1.0
    assert metrics["largest_component_ratio"] == 10 / 32


def _frame(width, height, boxes):
    pixels = bytearray([0, 0, 0] * width * height)
    for x0, y0, box_width, box_height in boxes:
        for y in range(y0, y0 + box_height):
            for x in range(x0, x0 + box_width):
                index = (y * width + x) * 3
                pixels[index : index + 3] = bytes([255, 255, 255])
    return bytes(pixels)
