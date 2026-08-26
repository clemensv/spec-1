import json
from pathlib import Path

import pytest
import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


ROOT = Path(__file__).parent.parent
SAMPLE_PATTERNS = ("*.cereg", "*.cereg.yaml", "*.xreg.json")


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key ({key})",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _sample_files():
    samples = []
    for sample_root in (ROOT / "core" / "samples", ROOT / "cloudevents" / "samples"):
        for pattern in SAMPLE_PATTERNS:
            samples.extend(sample_root.rglob(pattern))
    return sorted(set(samples))


@pytest.mark.parametrize("sample", _sample_files(), ids=lambda path: str(path.relative_to(ROOT)))
def test_sample_has_unique_keys(sample):
    with sample.open(encoding="utf-8") as sample_file:
        if sample.name.endswith(".yaml"):
            yaml.load(sample_file, Loader=_UniqueKeyLoader)
        else:
            json.load(sample_file, object_pairs_hook=_unique_json_object)