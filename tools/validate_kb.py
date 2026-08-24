"""Validate the English, Agent-oriented World Model Knowledge Base.

Run from the KB root with ``python tools/validate_kb.py``.
PyYAML is the only non-standard-library dependency.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: python -m pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "_schema" / "metadata.schema.yaml"
MANIFEST_SCHEMA_PATH = ROOT / "_schema" / "manifest.schema.yaml"
SOURCES_SCHEMA_PATH = ROOT / "_schema" / "sources.schema.yaml"
BENCHMARK_SCHEMA_PATH = ROOT / "_schema" / "benchmark.schema.yaml"
MODELS_ROOT = ROOT / "models"
FOUNDATION_ROOT = ROOT / "foundations"
PAPER_ROOT = ROOT / "papers"
COMPONENT_ROOT = ROOT / "components"
BENCHMARK_ROOT = ROOT / "benchmarks"
FOUNDATION_INDEX_PATH = FOUNDATION_ROOT / "retrieval-index.yaml"

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SOURCE_REFERENCE = re.compile(
    r"(?<!RQ-)\b(?!DATA-H\d+\b)((?:C3|C1|R1|T1|P25|IRASRC|MIMICGEN|CPOL|DZ|LAPA|IVG|DV3SRC|DV3|"
    r"TDMPC2|VJ2|DIASRC|DIA|OCCSRC|OCC|VISTA|XWAM|RC24|RC365|COMP|LOCAL|NVIDIA|FND|DYN|FD|REP|"
    r"PLAN|CTRL|MBRL|WFM|WAM|EMB|DATA|EVAL|BENCH|OBJ|ACT)-[A-Z0-9-]+)\b"
)
NON_ENGLISH_SCRIPT = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]"
)
STABLE_ID = re.compile(r"[a-z0-9][a-z0-9.-]*")
ROUTE_ID = re.compile(r"[a-z0-9][a-z0-9_]*")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py"}


def relative(path: Path) -> str:
    """Return a stable path for diagnostics."""

    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    """Read one KB text file strictly as UTF-8."""

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{relative(path)}: not valid UTF-8: {exc}") from exc


def load_yaml(path: Path) -> dict:
    """Load a YAML mapping with path-aware errors."""

    try:
        data = yaml.safe_load(read_text(path))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{relative(path)}: invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{relative(path)}: expected a YAML mapping")
    return data


def load_frontmatter(path: Path) -> tuple[dict, str]:
    """Return parsed page metadata and complete page text."""

    text = read_text(path)
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"{relative(path)}: missing YAML frontmatter")
    try:
        metadata = yaml.safe_load(match.group(1))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{relative(path)}: invalid frontmatter: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValueError(f"{relative(path)}: frontmatter must be a mapping")
    return metadata, text


def line_number(text: str, offset: int) -> int:
    """Map a character offset to a one-based line number."""

    return text.count("\n", 0, offset) + 1


def sha256_file(path: Path) -> str:
    """Hash a file without loading it into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_english_and_encoding(errors: list[str]) -> None:
    """Reject non-English scripts and common encoding damage in canonical text."""

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = read_text(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if "\ufffd" in text:
            offset = text.index("\ufffd")
            errors.append(
                f"{relative(path)}:{line_number(text, offset)}: "
                "Unicode replacement character found"
            )

        match = NON_ENGLISH_SCRIPT.search(text)
        if match:
            errors.append(
                f"{relative(path)}:{line_number(text, match.start())}: "
                f"non-English script character U+{ord(match.group()):04X} found"
            )


def source_registries() -> list[Path]:
    """Return every part- or entry-local source registry."""

    return sorted(ROOT.rglob("sources.yaml"))


def validate_sources(errors: list[str], warnings: list[str]) -> set[str]:
    """Validate all source registries, identities, locators, and integrity."""

    schema = load_yaml(SOURCES_SCHEMA_PATH)
    collection_contract = schema["collection"]
    source_contract = schema["source"]
    collection_allowed = set(collection_contract["required"]) | set(
        collection_contract.get("optional", [])
    )
    required = set(source_contract["required"])
    allowed_types = set(source_contract["allowed_types"])
    allowed_fields = set(source_contract["allowed_fields"])
    identity_fields = set(source_contract["identity"]["at_least_one_of"])
    local_artifact_required = set(schema["local_artifact"]["required"])
    cached_paper_required = set(schema["cached_paper"]["required"])
    source_ids: set[str] = set()

    registries = source_registries()
    if not registries:
        errors.append("no source registries found")
        return source_ids

    for registry in registries:
        label = relative(registry)
        data = load_yaml(registry)
        if data.get("schema_version") != schema.get("schema_version"):
            errors.append(
                f"{label}: schema_version does not match _schema/sources.schema.yaml"
            )

        collection_missing = set(collection_contract["required"]) - data.keys()
        if collection_missing:
            errors.append(
                f"{label}: missing collection fields {sorted(collection_missing)}"
            )
        collection_unknown = set(data) - collection_allowed
        if collection_unknown:
            errors.append(
                f"{label}: undeclared collection fields {sorted(collection_unknown)}"
            )

        if "local_path_policy" in data:
            policy = data["local_path_policy"]
            policy_required = set(schema["local_path_policy"]["required"])
            if not isinstance(policy, dict):
                errors.append(f"{label}: local_path_policy must be a mapping")
            else:
                policy_missing = policy_required - policy.keys()
                if policy_missing:
                    errors.append(
                        f"{label}: local_path_policy missing fields "
                        f"{sorted(policy_missing)}"
                    )
                policy_unknown = set(policy) - policy_required
                if policy_unknown:
                    errors.append(
                        f"{label}: local_path_policy has undeclared fields "
                        f"{sorted(policy_unknown)}"
                    )

        sources = data.get("sources", [])
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label}: sources must be a non-empty list")
            continue

        for index, source in enumerate(sources):
            item_label = f"{label}: source #{index}"
            if not isinstance(source, dict):
                errors.append(f"{item_label} is not a mapping")
                continue

            missing = required - source.keys()
            if missing:
                errors.append(f"{item_label}: missing fields {sorted(missing)}")
            unknown_fields = set(source) - allowed_fields
            if unknown_fields:
                errors.append(
                    f"{item_label}: undeclared fields {sorted(unknown_fields)}"
                )

            source_id = source.get("id")
            if not isinstance(source_id, str) or not source_id:
                errors.append(f"{item_label}: id must be a non-empty string")
            elif source_id in source_ids:
                errors.append(f"duplicate source id across registries: {source_id}")
            else:
                source_ids.add(source_id)

            source_type = source.get("type")
            if source_type not in allowed_types:
                errors.append(f"source {source_id}: unsupported type {source_type!r}")
            if not identity_fields.intersection(source.keys()):
                errors.append(
                    f"source {source_id}: expected one of {sorted(identity_fields)}"
                )

            if source_type == "local_artifact":
                local_missing = local_artifact_required - source.keys()
                if local_missing:
                    errors.append(
                        f"source {source_id}: local artifact missing "
                        f"{sorted(local_missing)}"
                    )
            if source_type == "paper" and source.get("local_path"):
                paper_missing = cached_paper_required - source.keys()
                if paper_missing:
                    errors.append(
                        f"source {source_id}: cached paper missing "
                        f"{sorted(paper_missing)}"
                    )

            local_path = source.get("local_path")
            if local_path:
                local_file = Path(str(local_path))
                if not local_file.is_file():
                    portable = data.get("local_path_policy", {})
                    message = (
                        f"source {source_id}: local_path not on this workstation: "
                        f"{local_path}"
                    )
                    if portable.get("portable_identity"):
                        warnings.append(message)
                    else:
                        errors.append(
                            f"source {source_id}: local_path does not exist: "
                            f"{local_path}"
                        )
                elif expected_hash := source.get("sha256"):
                    actual_hash = sha256_file(local_file)
                    if actual_hash.lower() != str(expected_hash).lower():
                        errors.append(
                            f"source {source_id}: SHA256 mismatch for {local_path}; "
                            f"expected {expected_hash}, found {actual_hash}"
                        )

            related_path = source.get("related_path")
            if related_path:
                related_file = (registry.parent / str(related_path)).resolve()
                if not related_file.is_file():
                    try:
                        related_file.relative_to(ROOT)
                    except ValueError:
                        warnings.append(
                            f"source {source_id}: related_path outside this "
                            f"checkout: {related_path}"
                        )
                    else:
                        errors.append(
                            f"source {source_id}: related_path does not exist "
                            f"relative to {label}: {related_path}"
                        )

    return source_ids


def validate_relative_links(path: Path, text: str, errors: list[str]) -> None:
    """Validate local Markdown link targets."""

    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip()
        if target.startswith("<") and ">" in target:
            target = target[1 : target.index(">")]
        else:
            target = target.split(maxsplit=1)[0]
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(target).split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        if resolved.exists():
            continue
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            continue
        errors.append(
            f"{relative(path)}: broken relative link {raw_target!r}"
        )


def validate_pages(
    schema: dict, source_ids: set[str], errors: list[str]
) -> set[str]:
    """Validate page metadata, retrieval contracts, links, and source tokens."""

    contract = schema["page_frontmatter"]
    required = set(contract["required"])
    allowed_kinds = set(contract["kind"])
    allowed_statuses = set(contract["status"])
    retrieval_labels = tuple(schema["canonical_topic_page"]["retrieval_fields"])
    seen_ids: dict[str, Path] = {}
    referenced_source_ids: set[str] = set()
    report_language = (
        re.compile(r"\b(?:we|our team|the team)\s+(?:read|reviewed|completed|built|ran)\b", re.I),
        re.compile(r"\bwhy\s+(?:this|it|the model)\s+(?:is\s+)?relevant\b", re.I),
        re.compile(r"\bproject relevance\b", re.I),
        re.compile(r"\bpapers?\s+(?:were|was|have been|has been)\s+read\b", re.I),
    )

    for path in sorted(ROOT.rglob("*.md")):
        try:
            metadata, text = load_frontmatter(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        missing = required - metadata.keys()
        if missing:
            errors.append(f"{relative(path)}: missing fields {sorted(missing)}")

        page_id = metadata.get("id")
        if page_id in seen_ids:
            errors.append(
                f"{relative(path)}: duplicate id {page_id!r}; first seen in "
                f"{relative(seen_ids[page_id])}"
            )
        elif isinstance(page_id, str):
            seen_ids[page_id] = path

        if not isinstance(page_id, str) or not STABLE_ID.fullmatch(page_id):
            errors.append(f"{relative(path)}: invalid stable id {page_id!r}")
        if metadata.get("kind") not in allowed_kinds:
            errors.append(f"{relative(path)}: invalid kind {metadata.get('kind')!r}")
        if metadata.get("status") not in allowed_statuses:
            errors.append(
                f"{relative(path)}: invalid status {metadata.get('status')!r}"
            )
        if not isinstance(metadata.get("owners"), list) or not metadata.get("owners"):
            errors.append(f"{relative(path)}: owners must be a non-empty list")
        if not isinstance(metadata.get("title"), str) or not metadata["title"].strip():
            errors.append(f"{relative(path)}: title must be a non-empty string")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(metadata.get("last_updated"))):
            errors.append(f"{relative(path)}: last_updated must be YYYY-MM-DD")

        validate_relative_links(path, text, errors)

        registered_in_page = {
            source_id
            for source_id in source_ids
            if re.search(
                rf"(?<![A-Z0-9-]){re.escape(source_id)}(?![A-Z0-9-])",
                text,
            )
        }
        referenced_source_ids.update(registered_in_page)

        for source_id in SOURCE_REFERENCE.findall(text):
            referenced_source_ids.add(source_id)
            if source_id not in source_ids:
                errors.append(
                    f"{relative(path)}: unknown source reference {source_id}"
                )

        is_model_page = path.is_relative_to(MODELS_ROOT)
        is_foundation_page = path.is_relative_to(FOUNDATION_ROOT)
        is_paper_page = path.is_relative_to(PAPER_ROOT)
        is_benchmark_page = path.is_relative_to(BENCHMARK_ROOT)
        is_foundation_topic = is_foundation_page and path.name != "README.md"
        is_paper_topic = (
            is_paper_page and path.parent != PAPER_ROOT and path.name != "README.md"
        )
        is_model_topic = is_model_page and path.parent != MODELS_ROOT and path.name != "README.md"
        is_benchmark_topic = (
            is_benchmark_page
            and path.parent != BENCHMARK_ROOT
            and path.name != "README.md"
        )
        if is_foundation_page:
            foundation_relative = path.relative_to(FOUNDATION_ROOT)
            if path.name == "README.md":
                owner_parts = foundation_relative.parts[:-1]
            else:
                owner_parts = foundation_relative.with_suffix("").parts
            expected_id = "world-model-kb.foundations"
            if owner_parts:
                expected_id += "." + ".".join(owner_parts)
            if page_id != expected_id:
                errors.append(
                    f"{relative(path)}: id {page_id!r} does not match canonical "
                    f"path owner {expected_id!r}"
                )
        if is_paper_page:
            paper_relative = path.relative_to(PAPER_ROOT)
            if path.name == "README.md":
                owner_parts = paper_relative.parts[:-1]
            else:
                owner_parts = paper_relative.with_suffix("").parts
            expected_id = "world-model-kb.papers"
            if owner_parts:
                expected_id += "." + ".".join(owner_parts)
            if page_id != expected_id:
                errors.append(
                    f"{relative(path)}: id {page_id!r} does not match canonical "
                    f"path owner {expected_id!r}"
                )
        if is_model_page:
            model_relative = path.relative_to(MODELS_ROOT)
            if path.name == "README.md":
                owner_parts = model_relative.parts[:-1]
            else:
                owner_parts = model_relative.with_suffix("").parts
            expected_id = "world-model-kb.models"
            if owner_parts:
                expected_id += "." + ".".join(owner_parts)
            if page_id != expected_id:
                errors.append(
                    f"{relative(path)}: id {page_id!r} does not match canonical "
                    f"path owner {expected_id!r}"
                )
        if is_benchmark_page:
            benchmark_relative = path.relative_to(BENCHMARK_ROOT)
            if path.name == "README.md":
                owner_parts = benchmark_relative.parts[:-1]
            else:
                owner_parts = benchmark_relative.with_suffix("").parts
            expected_id = "world-model-kb.benchmarks"
            if owner_parts:
                expected_id += "." + ".".join(owner_parts)
            if page_id != expected_id:
                errors.append(
                    f"{relative(path)}: id {page_id!r} does not match canonical "
                    f"path owner {expected_id!r}"
                )
        if is_model_page or is_foundation_page or is_paper_page or is_benchmark_page:
            if "## Retrieval metadata" not in text:
                errors.append(f"{relative(path)}: missing '## Retrieval metadata'")
            for label in retrieval_labels:
                if label not in text:
                    errors.append(
                        f"{relative(path)}: retrieval metadata missing label {label!r}"
                    )
            if re.search(r"\b(?:TODO|TBD)\b", text):
                errors.append(f"{relative(path)}: unfinished placeholder found")
            minimum_length = (
                1600
                if (
                    is_foundation_topic
                    or is_paper_topic
                    or is_model_topic
                    or is_benchmark_topic
                )
                else 1200
            )
            if path.name != "README.md" and len(text) < minimum_length:
                errors.append(
                    f"{relative(path)}: canonical page is too thin ({len(text)} chars)"
                )
            for pattern in report_language:
                match = pattern.search(text)
                if match:
                    errors.append(
                        f"{relative(path)}:{line_number(text, match.start())}: "
                        "human-facing progress or project-report language found"
                    )

    return referenced_source_ids


def validate_structure(schema: dict, errors: list[str]) -> None:
    """Validate the peer-part layout and declared entry file contracts."""

    directory_contract = schema["directory_contract"]
    for part in directory_contract["content_parts"]:
        if not (ROOT / part).is_dir():
            errors.append(f"missing content part: {part}/")

    allowed_top_dirs = {
        *directory_contract["content_parts"],
        "_schema",
        "tools",
        ".git",
    }
    unexpected_top_dirs = {
        path.name
        for path in ROOT.iterdir()
        if path.is_dir() and path.name not in allowed_top_dirs
    }
    if unexpected_top_dirs:
        errors.append(
            f"unexpected top-level directories: {sorted(unexpected_top_dirs)}"
        )

    for schema_file in directory_contract.get("schema_files", []):
        if not (ROOT / "_schema" / schema_file).is_file():
            errors.append(f"missing schema file: _schema/{schema_file}")

    model_contracts = schema.get("model_entry", {}).get("active_entries", {})
    active_model_entries = set(model_contracts)
    root_model_files = {
        path.name for path in MODELS_ROOT.iterdir() if path.is_file()
    }
    if root_model_files != {"README.md"}:
        errors.append(
            "models/ root must contain only README.md; "
            f"found {sorted(root_model_files)}"
        )
    actual_model_entries = {
        path.name for path in MODELS_ROOT.iterdir() if path.is_dir()
    }
    missing_model_entries = active_model_entries - actual_model_entries
    if missing_model_entries:
        errors.append(
            "Models entry missing active directories: "
            f"{sorted(missing_model_entries)}"
        )
    unexpected_model_entries = actual_model_entries - active_model_entries
    if unexpected_model_entries:
        errors.append(
            "Models contains undeclared entry directories: "
            f"{sorted(unexpected_model_entries)}"
        )
    stale_files = {"project-relevance.md", "open-questions.md"}
    for entry in active_model_entries & actual_model_entries:
        entry_root = MODELS_ROOT / entry
        required_files = set(model_contracts[entry].get("required_files", []))
        actual_files = {
            path.name for path in entry_root.iterdir() if path.is_file()
        }
        missing_files = required_files - actual_files
        if missing_files:
            errors.append(
                f"models/{entry} entry missing files: {sorted(missing_files)}"
            )
        unexpected_files = actual_files - required_files
        if unexpected_files:
            errors.append(
                f"models/{entry} entry contains undeclared files: "
                f"{sorted(unexpected_files)}"
            )
        remaining_stale = stale_files & actual_files
        if remaining_stale:
            errors.append(
                f"models/{entry} contains stale human-facing paths: "
                f"{sorted(remaining_stale)}"
            )

    foundation_contract = schema.get("foundation_entry", {})
    required_foundation_files = set(foundation_contract.get("required_files", []))
    actual_foundation_files = {
        path.name for path in FOUNDATION_ROOT.iterdir() if path.is_file()
    }
    missing_foundation_files = required_foundation_files - actual_foundation_files
    if missing_foundation_files:
        errors.append(
            "Foundations entry missing files: "
            f"{sorted(missing_foundation_files)}"
        )

    required_subparts = set(foundation_contract.get("subparts", []))
    actual_subparts = {
        path.name for path in FOUNDATION_ROOT.iterdir() if path.is_dir()
    }
    missing_subparts = required_subparts - actual_subparts
    if missing_subparts:
        errors.append(f"Foundations entry missing subparts: {sorted(missing_subparts)}")
    unexpected_subparts = actual_subparts - required_subparts
    if unexpected_subparts:
        errors.append(
            f"Foundations entry has undeclared subparts: {sorted(unexpected_subparts)}"
        )
    for subpart in required_subparts & actual_subparts:
        if not (FOUNDATION_ROOT / subpart / "README.md").is_file():
            errors.append(f"Foundations subpart missing index: {subpart}/README.md")

    paper_contract = schema.get("paper_entry", {})
    active_paper_entries = set(paper_contract.get("active_entries", []))
    required_paper_files = set(paper_contract.get("required_files", []))
    root_paper_files = {
        path.name for path in PAPER_ROOT.iterdir() if path.is_file()
    }
    if root_paper_files != {"README.md"}:
        errors.append(
            "papers/ root must contain only README.md; "
            f"found {sorted(root_paper_files)}"
        )
    actual_paper_entries = {
        path.name for path in PAPER_ROOT.iterdir() if path.is_dir()
    }
    missing_paper_entries = active_paper_entries - actual_paper_entries
    if missing_paper_entries:
        errors.append(
            f"Papers entry missing active directories: {sorted(missing_paper_entries)}"
        )
    unexpected_paper_entries = actual_paper_entries - active_paper_entries
    if unexpected_paper_entries:
        errors.append(
            f"Papers contains undeclared entry directories: {sorted(unexpected_paper_entries)}"
        )
    for entry in active_paper_entries & actual_paper_entries:
        entry_root = PAPER_ROOT / entry
        actual_files = {path.name for path in entry_root.iterdir() if path.is_file()}
        missing_files = required_paper_files - actual_files
        if missing_files:
            errors.append(
                f"papers/{entry} entry missing files: {sorted(missing_files)}"
            )
        unexpected_files = actual_files - required_paper_files
        if unexpected_files:
            errors.append(
                f"papers/{entry} entry contains undeclared files: "
                f"{sorted(unexpected_files)}"
            )
        nested_directories = sorted(
            path.name for path in entry_root.iterdir() if path.is_dir()
        )
        if nested_directories:
            errors.append(
                f"papers/{entry} entry contains undeclared directories: "
                f"{nested_directories}"
            )

    benchmark_contracts = schema.get("benchmark_entry", {}).get(
        "active_entries", {}
    )
    active_benchmark_entries = set(benchmark_contracts)
    root_benchmark_files = {
        path.name for path in BENCHMARK_ROOT.iterdir() if path.is_file()
    }
    if root_benchmark_files != {"README.md"}:
        errors.append(
            "benchmarks/ root must contain only README.md; "
            f"found {sorted(root_benchmark_files)}"
        )
    actual_benchmark_entries = {
        path.name for path in BENCHMARK_ROOT.iterdir() if path.is_dir()
    }
    missing_benchmark_entries = (
        active_benchmark_entries - actual_benchmark_entries
    )
    if missing_benchmark_entries:
        errors.append(
            "Benchmarks entry missing active directories: "
            f"{sorted(missing_benchmark_entries)}"
        )
    unexpected_benchmark_entries = (
        actual_benchmark_entries - active_benchmark_entries
    )
    if unexpected_benchmark_entries:
        errors.append(
            "Benchmarks contains undeclared entry directories: "
            f"{sorted(unexpected_benchmark_entries)}"
        )
    for entry in active_benchmark_entries & actual_benchmark_entries:
        entry_root = BENCHMARK_ROOT / entry
        required_files = set(
            benchmark_contracts[entry].get("required_files", [])
        )
        actual_files = {
            path.name for path in entry_root.iterdir() if path.is_file()
        }
        missing_files = required_files - actual_files
        if missing_files:
            errors.append(
                f"benchmarks/{entry} entry missing files: "
                f"{sorted(missing_files)}"
            )
        unexpected_files = actual_files - required_files
        if unexpected_files:
            errors.append(
                f"benchmarks/{entry} entry contains undeclared files: "
                f"{sorted(unexpected_files)}"
            )
        nested_directories = sorted(
            path.name for path in entry_root.iterdir() if path.is_dir()
        )
        if nested_directories:
            errors.append(
                f"benchmarks/{entry} entry contains undeclared directories: "
                f"{nested_directories}"
            )

    retired = ("concepts", "literature", "evaluation", "resources", "research", "_meta")
    for name in retired:
        path = ROOT / name
        if path.exists() and any(path.rglob("*")):
            errors.append(
                f"retired Cosmos-centric top-level path still contains files: {name}/"
            )


def validate_model_manifests(schema: dict, errors: list[str]) -> None:
    """Validate every declared model manifest and its document ownership map."""

    manifest_schema = load_yaml(MANIFEST_SCHEMA_PATH)
    contract = manifest_schema["manifest"]
    artifact_fields = set(
        manifest_schema["identity_artifacts"]["at_least_one_of"]
    )
    model_contracts = schema.get("model_entry", {}).get("active_entries", {})

    for entry, entry_contract in sorted(model_contracts.items()):
        model_root = MODELS_ROOT / entry
        manifest_path = model_root / "manifest.yaml"
        label = relative(manifest_path)
        manifest = load_yaml(manifest_path)

        if manifest.get("schema_version") != manifest_schema.get("schema_version"):
            errors.append(
                f"{label}: schema_version does not match "
                "_schema/manifest.schema.yaml"
            )

        missing = set(contract["required"]) - manifest.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        if manifest.get("entity_type") not in set(
            contract["entity_type_values"]
        ):
            errors.append(
                f"{label}: invalid entity_type "
                f"{manifest.get('entity_type')!r}"
            )
        if not artifact_fields.intersection(manifest):
            errors.append(
                f"{label}: expected one identity artifact field from "
                f"{sorted(artifact_fields)}"
            )

        revisions = manifest.get("revisions")
        if not isinstance(revisions, dict) or len(revisions) < int(
            manifest_schema["revisions"]["minimum_entries"]
        ):
            errors.append(f"{label}: revisions must be a non-empty mapping")
        elif any(not isinstance(value, str) or not value.strip() for value in revisions.values()):
            errors.append(f"{label}: revision values must be non-empty strings")

        interfaces = manifest.get("interfaces", {})
        interface_missing = set(
            manifest_schema["interfaces"]["required"]
        ) - interfaces.keys()
        if interface_missing:
            errors.append(
                f"{label}: interfaces missing {sorted(interface_missing)}"
            )

        owner = interfaces.get("canonical_owner")
        if not isinstance(owner, str) or not (model_root / owner).is_file():
            errors.append(
                f"{label}: interfaces.canonical_owner must resolve to a file"
            )

        contracts = interfaces.get("contracts", [])
        if not isinstance(contracts, list) or not contracts:
            errors.append(f"{label}: interfaces.contracts must be non-empty")
            contracts = []
        contract_required = set(
            manifest_schema["interfaces"]["contract_required"]
        )
        seen_modes: set[str] = set()
        for position, mode_contract in enumerate(contracts):
            mode_label = f"{label}: interface contract #{position}"
            if not isinstance(mode_contract, dict):
                errors.append(f"{mode_label} is not a mapping")
                continue
            mode_missing = contract_required - mode_contract.keys()
            if mode_missing:
                errors.append(
                    f"{mode_label} missing {sorted(mode_missing)}"
                )
            mode = mode_contract.get("mode")
            if not isinstance(mode, str) or not mode:
                errors.append(f"{mode_label} has an invalid mode")
            elif mode in seen_modes:
                errors.append(f"{label}: duplicate interface mode {mode}")
            else:
                seen_modes.add(mode)
            for field in ("inputs", "outputs"):
                values = mode_contract.get(field)
                if not isinstance(values, list) or not values:
                    errors.append(
                        f"{label}: interface {mode} {field} must be non-empty"
                    )

        reproduction = manifest.get("reproduction", {})
        reproduction_missing = set(
            manifest_schema["reproduction"]["required"]
        ) - reproduction.keys()
        if reproduction_missing:
            errors.append(
                f"{label}: reproduction missing "
                f"{sorted(reproduction_missing)}"
            )
        reproduction_owner = reproduction.get("canonical_owner")
        reproduction_path = model_root / str(reproduction_owner)
        if reproduction_owner != "reproduction.md" or not reproduction_path.is_file():
            errors.append(
                f"{label}: reproduction.canonical_owner must resolve to "
                "reproduction.md"
            )
        registry_heading = reproduction.get("registry_heading")
        if (
            isinstance(registry_heading, str)
            and reproduction_path.is_file()
            and f"## {registry_heading}" not in read_text(reproduction_path)
        ):
            errors.append(
                f"{label}: reproduction.registry_heading does not exist in "
                "reproduction.md"
            )

        documents = manifest.get("documents", {})
        if not isinstance(documents, dict):
            errors.append(f"{label}: documents must be a mapping")
            documents = {}
        route_missing = set(
            manifest_schema["documents"]["required_routes"]
        ) - documents.keys()
        if route_missing:
            errors.append(
                f"{label}: documents missing ownership entries "
                f"{sorted(route_missing)}"
            )
        document_values: set[str] = set()
        for route, target in documents.items():
            if not isinstance(target, str):
                errors.append(
                    f"{label}: document route {route} must be a string"
                )
                continue
            document_values.add(target)
            resolved = (model_root / target).resolve()
            if (
                Path(target).is_absolute()
                or not resolved.is_relative_to(model_root.resolve())
                or not resolved.is_file()
            ):
                errors.append(
                    f"{label}: document route {route} references missing "
                    f"path {target!r}"
                )
        if documents.get("agent_index") != "agent-index.yaml":
            errors.append(
                f"{label}: agent_index must resolve to agent-index.yaml"
            )

        required_files = set(entry_contract.get("required_files", []))
        unmapped = (
            required_files - {"manifest.yaml"} - document_values
        )
        if unmapped:
            errors.append(
                f"{label}: declared model files without document ownership "
                f"{sorted(unmapped)}"
            )


def validate_model_indexes(schema: dict, errors: list[str]) -> None:
    """Validate every model's advisory knowledge-guidance index."""

    contract = schema["agent_index"]
    model_contracts = schema.get("model_entry", {}).get("active_entries", {})

    for entry in sorted(model_contracts):
        model_root = MODELS_ROOT / entry
        index_path = model_root / "agent-index.yaml"
        manifest_path = model_root / "manifest.yaml"
        label = relative(index_path)
        index = load_yaml(index_path)

        missing = set(contract["required"]) - index.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        if index.get("schema_version") != contract.get(
            "supported_schema_version"
        ):
            errors.append(f"{label}: unsupported schema_version")

        try:
            overview_metadata, _ = load_frontmatter(model_root / "README.md")
        except ValueError as exc:
            errors.append(str(exc))
            overview_metadata = {}
        if index.get("model_entry") != overview_metadata.get("id"):
            errors.append(
                f"{label}: model_entry must equal the model README id"
            )

        def validate_model_path(
            owner: str,
            target: object,
            *,
            allow_cross_part: bool = False,
        ) -> None:
            if not isinstance(target, str):
                errors.append(f"{label}: {owner} path must be a string")
                return
            path = Path(target)
            resolved = (model_root / path).resolve()
            required_root = ROOT.resolve() if allow_cross_part else model_root.resolve()
            if (
                path.is_absolute()
                or not resolved.is_relative_to(required_root)
                or not resolved.is_file()
            ):
                errors.append(
                    f"{label}: {owner} references missing path {target!r}"
                )

        validate_model_path("entrypoint", index.get("entrypoint"))

        canonical_owners = index.get("canonical_owners", {})
        if not isinstance(canonical_owners, dict) or not canonical_owners:
            errors.append(
                f"{label}: canonical_owners must be a non-empty mapping"
            )
            canonical_owners = {}
        else:
            for owner, target in canonical_owners.items():
                validate_model_path(f"canonical owner {owner}", target)

        manifest_documents = set(
            load_yaml(manifest_path).get("documents", {}).values()
        )
        owned_documents = set(canonical_owners.values())
        unowned_documents = manifest_documents - owned_documents
        if unowned_documents:
            errors.append(
                f"{label}: manifest documents without a canonical owner "
                f"{sorted(unowned_documents)}"
            )

        forbidden_control_fields = {
            "retrieval_policy",
            "routes",
            "context_bundles",
            "global_stop_rules",
            "priorities",
            "execution_order",
        }
        present_control_fields = forbidden_control_fields & index.keys()
        if present_control_fields:
            errors.append(
                f"{label}: workflow-control fields are not allowed: "
                f"{sorted(present_control_fields)}"
            )

        authority = index.get("authority_boundary", {})
        authority_required = {
            "mode",
            "knowledge_role",
            "workflow_authority",
            "does_not_define",
            "integration_note",
        }
        if not isinstance(authority, dict):
            errors.append(f"{label}: authority_boundary must be a mapping")
        else:
            authority_missing = authority_required - authority.keys()
            if authority_missing:
                errors.append(
                    f"{label}: authority_boundary missing fields "
                    f"{sorted(authority_missing)}"
                )
            if authority.get("mode") != "knowledge_guidance_without_orchestration":
                errors.append(
                    f"{label}: authority_boundary.mode must be "
                    "knowledge_guidance_without_orchestration"
                )
            if not isinstance(authority.get("does_not_define"), list) or not authority.get(
                "does_not_define"
            ):
                errors.append(
                    f"{label}: authority_boundary.does_not_define must be "
                    "non-empty"
                )

        profiles = index.get("retrieval_profiles", [])
        if not isinstance(profiles, list) or not profiles:
            errors.append(
                f"{label}: retrieval_profiles must be a non-empty list"
            )
            profiles = []
        profile_required = set(contract["profile_required"])
        profile_ids: set[str] = set()
        for position, profile in enumerate(profiles):
            profile_label = f"{label}: retrieval profile #{position}"
            if not isinstance(profile, dict):
                errors.append(f"{profile_label} is not a mapping")
                continue
            profile_missing = profile_required - profile.keys()
            if profile_missing:
                errors.append(
                    f"{profile_label} missing {sorted(profile_missing)}"
                )
            profile_id = profile.get("id")
            if not isinstance(profile_id, str) or not ROUTE_ID.fullmatch(
                profile_id
            ):
                errors.append(
                    f"{label}: invalid profile id {profile_id!r}"
                )
            elif profile_id in profile_ids:
                errors.append(
                    f"{label}: duplicate profile id {profile_id}"
                )
            else:
                profile_ids.add(profile_id)

            for field in (
                "related_intents",
                "query_terms",
                "knowledge_supported",
            ):
                values = profile.get(field)
                if not isinstance(values, list) or not values or not all(
                    isinstance(item, str) and item.strip() for item in values
                ):
                    errors.append(
                        f"{label}: profile {profile_id} {field} must be a "
                        "non-empty string list"
                    )

            primary_documents = profile.get("primary_documents")
            if not isinstance(primary_documents, list) or not primary_documents:
                errors.append(
                    f"{label}: profile {profile_id} primary_documents must "
                    "be non-empty"
                )
            else:
                for target in primary_documents:
                    validate_model_path(
                        f"profile {profile_id} primary document", target
                    )

            additional = profile.get("additional_documents")
            if not isinstance(additional, dict):
                errors.append(
                    f"{label}: profile {profile_id} additional_documents "
                    "must be a mapping"
                )
            else:
                for topic, targets in additional.items():
                    if not isinstance(targets, list) or not targets:
                        errors.append(
                            f"{label}: profile {profile_id} additional topic "
                            f"{topic} must contain documents"
                        )
                        continue
                    for target in targets:
                        validate_model_path(
                            f"profile {profile_id} additional topic {topic}",
                            target,
                            allow_cross_part=True,
                        )


def validate_benchmark_manifests(schema: dict, errors: list[str]) -> None:
    """Validate benchmark identity, scope, protocol, and document ownership."""

    benchmark_schema = load_yaml(BENCHMARK_SCHEMA_PATH)
    contract = benchmark_schema["benchmark"]
    benchmark_contracts = schema.get("benchmark_entry", {}).get(
        "active_entries", {}
    )

    for entry, entry_contract in sorted(benchmark_contracts.items()):
        benchmark_root = BENCHMARK_ROOT / entry
        manifest_path = benchmark_root / "benchmark.yaml"
        label = relative(manifest_path)
        manifest = load_yaml(manifest_path)

        if manifest.get("schema_version") != benchmark_schema.get(
            "schema_version"
        ):
            errors.append(
                f"{label}: schema_version does not match "
                "_schema/benchmark.schema.yaml"
            )
        missing = set(contract["required"]) - manifest.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        if manifest.get("entity_type") not in set(
            contract["entity_type_values"]
        ):
            errors.append(
                f"{label}: invalid entity_type "
                f"{manifest.get('entity_type')!r}"
            )

        for field in (
            "release",
            "scope",
            "task_taxonomy",
            "evaluation",
            "reproduction",
        ):
            value = manifest.get(field, {})
            required = set(benchmark_schema[field]["required"])
            if not isinstance(value, dict):
                errors.append(f"{label}: {field} must be a mapping")
                continue
            nested_missing = required - value.keys()
            if nested_missing:
                errors.append(
                    f"{label}: {field} missing {sorted(nested_missing)}"
                )

        for field, owner_key in (
            ("scope", "canonical_owner"),
            ("evaluation", "protocol_owner"),
            ("reproduction", "canonical_owner"),
        ):
            owner = manifest.get(field, {}).get(owner_key)
            if not isinstance(owner, str) or not (
                benchmark_root / owner
            ).is_file():
                errors.append(
                    f"{label}: {field}.{owner_key} must resolve to a file"
                )

        reproduction = manifest.get("reproduction", {})
        reproduction_owner = reproduction.get("canonical_owner")
        registry_heading = reproduction.get("registry_heading")
        reproduction_path = benchmark_root / str(reproduction_owner)
        if (
            isinstance(registry_heading, str)
            and reproduction_path.is_file()
            and f"## {registry_heading}" not in read_text(reproduction_path)
        ):
            errors.append(
                f"{label}: reproduction.registry_heading does not exist in "
                "the reproduction owner"
            )

        documents = manifest.get("documents", {})
        if not isinstance(documents, dict):
            errors.append(f"{label}: documents must be a mapping")
            documents = {}
        route_missing = set(
            benchmark_schema["documents"]["required_routes"]
        ) - documents.keys()
        if route_missing:
            errors.append(
                f"{label}: documents missing ownership entries "
                f"{sorted(route_missing)}"
            )
        document_values: set[str] = set()
        for route, target in documents.items():
            if not isinstance(target, str):
                errors.append(
                    f"{label}: document route {route} must be a string"
                )
                continue
            document_values.add(target)
            path = Path(target)
            resolved = (benchmark_root / path).resolve()
            if (
                path.is_absolute()
                or not resolved.is_relative_to(benchmark_root.resolve())
                or not resolved.is_file()
            ):
                errors.append(
                    f"{label}: document route {route} references missing "
                    f"path {target!r}"
                )
        if documents.get("retrieval_index") != "retrieval-index.yaml":
            errors.append(
                f"{label}: retrieval_index must resolve to "
                "retrieval-index.yaml"
            )

        required_files = set(entry_contract.get("required_files", []))
        unmapped = (
            required_files - {"benchmark.yaml"} - document_values
        )
        if unmapped:
            errors.append(
                f"{label}: declared benchmark files without document "
                f"ownership {sorted(unmapped)}"
            )


def validate_benchmark_indexes(schema: dict, errors: list[str]) -> None:
    """Validate benchmark query-to-knowledge associations."""

    contract = schema["benchmark_retrieval_index"]
    benchmark_contracts = schema.get("benchmark_entry", {}).get(
        "active_entries", {}
    )

    for entry in sorted(benchmark_contracts):
        benchmark_root = BENCHMARK_ROOT / entry
        index_path = benchmark_root / "retrieval-index.yaml"
        manifest_path = benchmark_root / "benchmark.yaml"
        label = relative(index_path)
        index = load_yaml(index_path)

        missing = set(contract["required"]) - index.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        if index.get("schema_version") != contract.get(
            "supported_schema_version"
        ):
            errors.append(f"{label}: unsupported schema_version")

        try:
            overview_metadata, _ = load_frontmatter(
                benchmark_root / "README.md"
            )
        except ValueError as exc:
            errors.append(str(exc))
            overview_metadata = {}
        if index.get("benchmark_entry") != overview_metadata.get("id"):
            errors.append(
                f"{label}: benchmark_entry must equal the benchmark README id"
            )

        def validate_benchmark_path(
            owner: str,
            target: object,
            *,
            allow_cross_part: bool = False,
        ) -> None:
            if not isinstance(target, str):
                errors.append(f"{label}: {owner} path must be a string")
                return
            path = Path(target)
            resolved = (benchmark_root / path).resolve()
            required_root = (
                ROOT.resolve() if allow_cross_part else benchmark_root.resolve()
            )
            if (
                path.is_absolute()
                or not resolved.is_relative_to(required_root)
                or not resolved.is_file()
            ):
                errors.append(
                    f"{label}: {owner} references missing path {target!r}"
                )

        validate_benchmark_path("entrypoint", index.get("entrypoint"))

        canonical_owners = index.get("canonical_owners", {})
        if not isinstance(canonical_owners, dict) or not canonical_owners:
            errors.append(
                f"{label}: canonical_owners must be a non-empty mapping"
            )
            canonical_owners = {}
        else:
            for owner, target in canonical_owners.items():
                validate_benchmark_path(
                    f"canonical owner {owner}", target
                )

        manifest_documents = set(
            load_yaml(manifest_path).get("documents", {}).values()
        )
        unowned_documents = manifest_documents - set(
            canonical_owners.values()
        )
        if unowned_documents:
            errors.append(
                f"{label}: benchmark documents without a canonical owner "
                f"{sorted(unowned_documents)}"
            )

        forbidden_control_fields = {
            "retrieval_policy",
            "routes",
            "context_bundles",
            "global_stop_rules",
            "priorities",
            "execution_order",
        }
        present_control_fields = forbidden_control_fields & index.keys()
        if present_control_fields:
            errors.append(
                f"{label}: workflow-control fields are not allowed: "
                f"{sorted(present_control_fields)}"
            )

        authority = index.get("authority_boundary", {})
        authority_required = {
            "mode",
            "knowledge_role",
            "workflow_authority",
            "does_not_define",
            "integration_note",
        }
        if not isinstance(authority, dict):
            errors.append(f"{label}: authority_boundary must be a mapping")
        else:
            authority_missing = authority_required - authority.keys()
            if authority_missing:
                errors.append(
                    f"{label}: authority_boundary missing fields "
                    f"{sorted(authority_missing)}"
                )
            if authority.get("mode") != "knowledge_guidance_without_orchestration":
                errors.append(
                    f"{label}: authority_boundary.mode must be "
                    "knowledge_guidance_without_orchestration"
                )
            if not isinstance(authority.get("does_not_define"), list) or not authority.get(
                "does_not_define"
            ):
                errors.append(
                    f"{label}: authority_boundary.does_not_define must be "
                    "non-empty"
                )

        profiles = index.get("retrieval_profiles", [])
        if not isinstance(profiles, list) or not profiles:
            errors.append(
                f"{label}: retrieval_profiles must be a non-empty list"
            )
            profiles = []
        profile_required = set(contract["profile_required"])
        profile_ids: set[str] = set()
        for position, profile in enumerate(profiles):
            profile_label = f"{label}: retrieval profile #{position}"
            if not isinstance(profile, dict):
                errors.append(f"{profile_label} is not a mapping")
                continue
            profile_missing = profile_required - profile.keys()
            if profile_missing:
                errors.append(
                    f"{profile_label} missing {sorted(profile_missing)}"
                )
            profile_id = profile.get("id")
            if not isinstance(profile_id, str) or not ROUTE_ID.fullmatch(
                profile_id
            ):
                errors.append(
                    f"{label}: invalid profile id {profile_id!r}"
                )
            elif profile_id in profile_ids:
                errors.append(
                    f"{label}: duplicate profile id {profile_id}"
                )
            else:
                profile_ids.add(profile_id)

            for field in (
                "related_intents",
                "query_terms",
                "knowledge_supported",
            ):
                values = profile.get(field)
                if not isinstance(values, list) or not values or not all(
                    isinstance(item, str) and item.strip() for item in values
                ):
                    errors.append(
                        f"{label}: profile {profile_id} {field} must be a "
                        "non-empty string list"
                    )

            primary_documents = profile.get("primary_documents")
            if not isinstance(primary_documents, list) or not primary_documents:
                errors.append(
                    f"{label}: profile {profile_id} primary_documents must "
                    "be non-empty"
                )
            else:
                for target in primary_documents:
                    validate_benchmark_path(
                        f"profile {profile_id} primary document", target
                    )

            additional = profile.get("additional_documents")
            if not isinstance(additional, dict):
                errors.append(
                    f"{label}: profile {profile_id} additional_documents "
                    "must be a mapping"
                )
            else:
                for topic, targets in additional.items():
                    if not isinstance(targets, list) or not targets:
                        errors.append(
                            f"{label}: profile {profile_id} additional topic "
                            f"{topic} must contain documents"
                        )
                        continue
                    for target in targets:
                        validate_benchmark_path(
                            f"profile {profile_id} additional topic {topic}",
                            target,
                            allow_cross_part=True,
                        )


def validate_foundation_index(schema: dict, errors: list[str]) -> None:
    """Validate advisory Foundation query-to-knowledge associations."""

    index = load_yaml(FOUNDATION_INDEX_PATH)
    contract = schema["foundation_retrieval_index"]
    missing = set(contract["required"]) - index.keys()
    if missing:
        errors.append(f"foundations/retrieval-index.yaml: missing {sorted(missing)}")
    if index.get("schema_version") != contract.get("supported_schema_version"):
        errors.append(
            "foundations/retrieval-index.yaml: unsupported schema_version"
        )

    try:
        foundation_metadata, _ = load_frontmatter(FOUNDATION_ROOT / "README.md")
    except ValueError as exc:
        errors.append(str(exc))
        foundation_metadata = {}
    if index.get("part_entry") != foundation_metadata.get("id"):
        errors.append(
            "foundations/retrieval-index.yaml: part_entry must equal the "
            "Foundations README id"
        )

    def validate_path(
        owner: str,
        target: object,
        *,
        require_foundation: bool,
    ) -> None:
        if not isinstance(target, str):
            errors.append(
                f"foundations/retrieval-index.yaml: {owner} path must be a string"
            )
            return
        path = Path(target)
        resolved = (FOUNDATION_ROOT / path).resolve()
        allowed_root = FOUNDATION_ROOT.resolve() if require_foundation else ROOT.resolve()
        if (
            path.is_absolute()
            or not resolved.is_relative_to(allowed_root)
            or not resolved.is_file()
        ):
            errors.append(
                "foundations/retrieval-index.yaml: "
                f"{owner} references invalid path {target!r}"
            )

    validate_path("entrypoint", index.get("entrypoint"), require_foundation=True)

    canonical_owners = index.get("canonical_owners", {})
    if not isinstance(canonical_owners, dict) or not canonical_owners:
        errors.append(
            "foundations/retrieval-index.yaml: canonical_owners must be non-empty"
        )
    else:
        for owner, target in canonical_owners.items():
            validate_path(
                f"canonical owner {owner}", target, require_foundation=True
            )

    forbidden_control_fields = {
        "retrieval_policy",
        "routes",
        "context_bundles",
        "global_stop_rules",
        "priorities",
        "execution_order",
    }
    present_control_fields = forbidden_control_fields & index.keys()
    if present_control_fields:
        errors.append(
            "foundations/retrieval-index.yaml: workflow-control fields are not "
            f"allowed: {sorted(present_control_fields)}"
        )

    authority = index.get("authority_boundary", {})
    authority_required = {
        "mode",
        "knowledge_role",
        "workflow_authority",
        "does_not_define",
        "integration_note",
    }
    if not isinstance(authority, dict):
        errors.append(
            "foundations/retrieval-index.yaml: authority_boundary must be a mapping"
        )
    else:
        authority_missing = authority_required - authority.keys()
        if authority_missing:
            errors.append(
                "foundations/retrieval-index.yaml: authority_boundary missing "
                f"{sorted(authority_missing)}"
            )
        if authority.get("mode") != "knowledge_guidance_without_orchestration":
            errors.append(
                "foundations/retrieval-index.yaml: authority mode must be "
                "knowledge_guidance_without_orchestration"
            )
        if not isinstance(authority.get("does_not_define"), list) or not authority.get(
            "does_not_define"
        ):
            errors.append(
                "foundations/retrieval-index.yaml: does_not_define must be non-empty"
            )

    profiles = index.get("retrieval_profiles", [])
    if not isinstance(profiles, list) or not profiles:
        errors.append(
            "foundations/retrieval-index.yaml: retrieval_profiles must be non-empty"
        )
        profiles = []
    profile_required = set(contract["profile_required"])
    profile_ids: set[str] = set()
    for position, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            errors.append(
                "foundations/retrieval-index.yaml: profile "
                f"#{position} is not a mapping"
            )
            continue
        profile_missing = profile_required - profile.keys()
        if profile_missing:
            errors.append(
                "foundations/retrieval-index.yaml: profile "
                f"#{position} missing {sorted(profile_missing)}"
            )
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not ROUTE_ID.fullmatch(profile_id):
            errors.append(
                "foundations/retrieval-index.yaml: invalid profile id "
                f"{profile_id!r}"
            )
        elif profile_id in profile_ids:
            errors.append(
                f"foundations/retrieval-index.yaml: duplicate profile id {profile_id}"
            )
        else:
            profile_ids.add(profile_id)

        for field in ("related_intents", "query_terms", "knowledge_supported"):
            values = profile.get(field)
            if not isinstance(values, list) or not values or not all(
                isinstance(item, str) and item.strip() for item in values
            ):
                errors.append(
                    "foundations/retrieval-index.yaml: profile "
                    f"{profile_id} {field} must be a non-empty string list"
                )

        primary_documents = profile.get("primary_documents")
        if not isinstance(primary_documents, list) or not primary_documents:
            errors.append(
                "foundations/retrieval-index.yaml: profile "
                f"{profile_id} primary_documents must be non-empty"
            )
        else:
            for target in primary_documents:
                validate_path(
                    f"profile {profile_id} primary document",
                    target,
                    require_foundation=True,
                )

        related = profile.get("related_documents")
        if not isinstance(related, dict):
            errors.append(
                "foundations/retrieval-index.yaml: profile "
                f"{profile_id} related_documents must be a mapping"
            )
        else:
            for topic, targets in related.items():
                if not isinstance(targets, list) or not targets:
                    errors.append(
                        "foundations/retrieval-index.yaml: profile "
                        f"{profile_id} related topic {topic} must contain documents"
                    )
                    continue
                for target in targets:
                    validate_path(
                        f"profile {profile_id} related topic {topic}",
                        target,
                        require_foundation=False,
                    )


def validate_removed_taxonomy(errors: list[str]) -> None:
    """Prevent the retired source-ranking taxonomy from returning."""

    forbidden = (
        "evidence" + "_status",
        "evidence" + "_levels",
        "Evidence" + " Levels",
        "source" + "_verified",
        "author" + "_reported",
        "locally" + "_observed",
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml"}:
            continue
        text = read_text(path)
        for token in forbidden:
            if token in text:
                errors.append(
                    f"{relative(path)}: removed taxonomy term remains: {token}"
                )


def main() -> int:
    """Run every KB invariant and return a process status."""

    errors: list[str] = []
    warnings: list[str] = []
    try:
        schema = load_yaml(SCHEMA_PATH)
        validate_english_and_encoding(errors)
        source_ids = validate_sources(errors, warnings)
        referenced_source_ids = validate_pages(schema, source_ids, errors)
        orphan_sources = source_ids - referenced_source_ids
        if orphan_sources:
            errors.append(
                f"source registries: unreferenced source IDs {sorted(orphan_sources)}"
            )
        validate_structure(schema, errors)
        validate_model_manifests(schema, errors)
        validate_model_indexes(schema, errors)
        validate_benchmark_manifests(schema, errors)
        validate_benchmark_indexes(schema, errors)
        validate_foundation_index(schema, errors)
        validate_removed_taxonomy(errors)
    except ValueError as exc:
        errors.append(str(exc))

    if errors:
        print(f"KB validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    if warnings:
        print(f"KB validation warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"- {warning}")

    page_count = sum(1 for _ in ROOT.rglob("*.md"))
    model_pages = sum(
        1 for path in MODELS_ROOT.rglob("*.md") if path.parent != MODELS_ROOT
    )
    model_entry_count = len(
        load_yaml(SCHEMA_PATH)
        .get("model_entry", {})
        .get("active_entries", {})
    )
    foundation_pages = sum(
        1 for path in FOUNDATION_ROOT.rglob("*.md") if path.name != "README.md"
    )
    paper_pages = sum(
        1 for path in PAPER_ROOT.rglob("*.md") if path.parent != PAPER_ROOT
    )
    paper_entry_count = len(
        load_yaml(SCHEMA_PATH).get("paper_entry", {}).get("active_entries", [])
    )
    component_pages = sum(
        1 for path in COMPONENT_ROOT.rglob("*.md") if path.parent != COMPONENT_ROOT
    )
    component_entry_count = len(
        [path for path in COMPONENT_ROOT.iterdir() if path.is_dir()]
    )
    benchmark_pages = sum(
        1
        for path in BENCHMARK_ROOT.rglob("*.md")
        if path.parent != BENCHMARK_ROOT
    )
    benchmark_entry_count = len(
        load_yaml(SCHEMA_PATH)
        .get("benchmark_entry", {})
        .get("active_entries", {})
    )
    source_count = sum(
        len(load_yaml(path).get("sources", [])) for path in source_registries()
    )
    model_profile_count = sum(
        len(load_yaml(path).get("retrieval_profiles", []))
        for path in MODELS_ROOT.glob("*/agent-index.yaml")
    )
    benchmark_profile_count = sum(
        len(load_yaml(path).get("retrieval_profiles", []))
        for path in BENCHMARK_ROOT.glob("*/retrieval-index.yaml")
    )
    foundation_profile_count = len(
        load_yaml(FOUNDATION_INDEX_PATH).get("retrieval_profiles", [])
    )
    print(
        "KB validation passed: "
        f"{len(schema['directory_contract']['content_parts'])} content parts, "
        f"{page_count} pages, {foundation_pages} Foundation topics, "
        f"{paper_entry_count} Paper entries with {paper_pages} pages, "
        f"{component_entry_count} Component entries with {component_pages} pages, "
        f"{model_entry_count} Model entries with {model_pages} pages, "
        f"{benchmark_entry_count} Benchmark entries with {benchmark_pages} pages, "
        f"{source_count} sources, {foundation_profile_count} Foundation, "
        f"{model_profile_count} Model, and {benchmark_profile_count} Benchmark "
        "knowledge-guidance retrieval profiles."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
