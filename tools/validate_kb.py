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
MODEL_ROOT = ROOT / "models" / "cosmos3-nano"
FOUNDATION_ROOT = ROOT / "foundations"
MANIFEST_PATH = MODEL_ROOT / "manifest.yaml"
AGENT_INDEX_PATH = MODEL_ROOT / "agent-index.yaml"
FOUNDATION_INDEX_PATH = FOUNDATION_ROOT / "retrieval-index.yaml"

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SOURCE_REFERENCE = re.compile(
    r"(?<!RQ-)\b(?!DATA-H\d+\b)((?:C3|C1|R1|T1|P25|LOCAL|NVIDIA|FND|DYN|FD|REP|"
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


def validate_sources(errors: list[str]) -> set[str]:
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
                    errors.append(
                        f"source {source_id}: local_path does not exist: {local_path}"
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
                    errors.append(
                        f"source {source_id}: related_path does not exist relative "
                        f"to {label}: {related_path}"
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
        if target and not (path.parent / target).resolve().exists():
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

        for source_id in SOURCE_REFERENCE.findall(text):
            referenced_source_ids.add(source_id)
            if source_id not in source_ids:
                errors.append(
                    f"{relative(path)}: unknown source reference {source_id}"
                )

        is_model_page = path.parent == MODEL_ROOT
        is_foundation_page = path.is_relative_to(FOUNDATION_ROOT)
        is_foundation_topic = is_foundation_page and path.name != "README.md"
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
        if is_model_page or is_foundation_page:
            if "## Retrieval metadata" not in text:
                errors.append(f"{relative(path)}: missing '## Retrieval metadata'")
            for label in retrieval_labels:
                if label not in text:
                    errors.append(
                        f"{relative(path)}: retrieval metadata missing label {label!r}"
                    )
            if re.search(r"\b(?:TODO|TBD)\b", text):
                errors.append(f"{relative(path)}: unfinished placeholder found")
            minimum_length = 1600 if is_foundation_topic else 1200
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
    """Validate the three-part layout and model-entry file contract."""

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

    required_model_files = set(schema["cosmos3_nano_required_files"])
    actual_model_files = {
        path.name for path in MODEL_ROOT.iterdir() if path.is_file()
    }
    missing = required_model_files - actual_model_files
    if missing:
        errors.append(f"Cosmos3-Nano entry missing files: {sorted(missing)}")

    stale_files = {"project-relevance.md", "open-questions.md"}
    remaining_stale = stale_files & actual_model_files
    if remaining_stale:
        errors.append(
            f"Cosmos3-Nano entry contains stale human-facing paths: "
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

    papers_root = ROOT / "papers"
    paper_files = [path for path in papers_root.rglob("*") if path.is_file()]
    if {path.name for path in paper_files} != {"README.md"}:
        errors.append(
            "papers/ must remain content-empty in this version; "
            f"found {[relative(path) for path in paper_files]}"
        )

    retired = ("concepts", "literature", "evaluation", "resources", "research", "_meta")
    for name in retired:
        path = ROOT / name
        if path.exists() and any(path.rglob("*")):
            errors.append(
                f"retired Cosmos-centric top-level path still contains files: {name}/"
            )


def validate_manifest(errors: list[str]) -> None:
    """Validate model identity, reproduction state, and document ownership."""

    manifest = load_yaml(MANIFEST_PATH)
    schema = load_yaml(MANIFEST_SCHEMA_PATH)
    contract = schema["manifest"]

    if manifest.get("schema_version") != schema.get("schema_version"):
        errors.append(
            "manifest.yaml: schema_version does not match _schema/manifest.schema.yaml"
        )

    missing = set(contract["required"]) - manifest.keys()
    if missing:
        errors.append(f"manifest.yaml: missing fields {sorted(missing)}")
    if manifest.get("entity_type") not in set(contract["entity_type_values"]):
        errors.append(
            f"manifest.yaml: invalid entity_type {manifest.get('entity_type')!r}"
        )

    checkpoint = manifest.get("checkpoint", {})
    checkpoint_missing = set(schema["checkpoint"]["required"]) - checkpoint.keys()
    if checkpoint_missing:
        errors.append(
            f"manifest.yaml: checkpoint missing {sorted(checkpoint_missing)}"
        )

    revisions = manifest.get("revisions", {})
    revision_missing = set(schema["revisions"]["required"]) - revisions.keys()
    if revision_missing:
        errors.append(
            f"manifest.yaml: revisions missing {sorted(revision_missing)}"
        )

    interfaces = manifest.get("interfaces", {})
    interface_missing = set(schema["interfaces"]["required"]) - interfaces.keys()
    if interface_missing:
        errors.append(
            f"manifest.yaml: interfaces missing {sorted(interface_missing)}"
        )
    if interfaces.get("canonical_owner") != "modalities-and-io.md":
        errors.append(
            "manifest.yaml: interfaces.canonical_owner must be modalities-and-io.md"
        )
    contracts = interfaces.get("contracts", [])
    if not isinstance(contracts, list) or not contracts:
        errors.append("manifest.yaml: interfaces.contracts must be a non-empty list")
    else:
        required_contract_fields = set(schema["interfaces"]["contract_required"])
        seen_modes: set[str] = set()
        for index, mode_contract in enumerate(contracts):
            if not isinstance(mode_contract, dict):
                errors.append(
                    f"manifest.yaml: interface contract #{index} is not a mapping"
                )
                continue
            mode_missing = required_contract_fields - mode_contract.keys()
            if mode_missing:
                errors.append(
                    f"manifest.yaml: interface contract #{index} missing "
                    f"{sorted(mode_missing)}"
                )
            mode = mode_contract.get("mode")
            if not isinstance(mode, str) or not mode:
                errors.append(
                    f"manifest.yaml: interface contract #{index} has invalid mode"
                )
            elif mode in seen_modes:
                errors.append(f"manifest.yaml: duplicate interface mode {mode}")
            else:
                seen_modes.add(mode)
            for field in ("inputs", "outputs"):
                values = mode_contract.get(field)
                if not isinstance(values, list) or not values:
                    errors.append(
                        f"manifest.yaml: interface {mode} {field} must be non-empty"
                    )

    reproduction = manifest.get("reproduction", {})
    reproduction_missing = set(schema["reproduction"]["required"]) - reproduction.keys()
    if reproduction_missing:
        errors.append(
            f"manifest.yaml: reproduction missing {sorted(reproduction_missing)}"
        )
    if reproduction.get("canonical_owner") != "reproduction.md":
        errors.append(
            "manifest.yaml: reproduction.canonical_owner must be reproduction.md"
        )
    registry_heading = reproduction.get("registry_heading")
    if isinstance(registry_heading, str):
        reproduction_text = read_text(MODEL_ROOT / "reproduction.md")
        if f"## {registry_heading}" not in reproduction_text:
            errors.append(
                "manifest.yaml: reproduction.registry_heading does not exist in reproduction.md"
            )

    documents = manifest.get("documents", {})
    if not isinstance(documents, dict):
        errors.append("manifest.yaml: documents must be a mapping")
        documents = {}
    route_missing = set(schema["documents"]["required_routes"]) - documents.keys()
    if route_missing:
        errors.append(
            f"manifest.yaml: documents missing ownership entries {sorted(route_missing)}"
        )
    for name, target in documents.items():
        if not isinstance(target, str) or not (MODEL_ROOT / target).resolve().is_file():
            errors.append(f"manifest document {name}: missing {target}")

    if documents.get("agent_index") != AGENT_INDEX_PATH.name:
        errors.append("manifest document agent_index must resolve to agent-index.yaml")


def validate_agent_index(schema: dict, errors: list[str]) -> None:
    """Validate machine-readable retrieval metadata and referenced document paths."""

    index = load_yaml(AGENT_INDEX_PATH)
    contract = schema["agent_index"]
    missing = set(contract["required"]) - index.keys()
    if missing:
        errors.append(f"agent-index.yaml: missing fields {sorted(missing)}")
    if index.get("schema_version") != contract.get("supported_schema_version"):
        errors.append(
            "agent-index.yaml: unsupported schema_version; update metadata.schema.yaml "
            "with the retrieval contract"
        )

    try:
        overview_metadata, _ = load_frontmatter(MODEL_ROOT / "README.md")
    except ValueError as exc:
        errors.append(str(exc))
        overview_metadata = {}
    if index.get("model_entry") != overview_metadata.get("id"):
        errors.append(
            "agent-index.yaml: model_entry must equal the Cosmos3-Nano README id"
        )

    def validate_model_path(owner: str, target: object) -> None:
        if not isinstance(target, str):
            errors.append(f"agent-index.yaml: {owner} path must be a string")
            return
        path = Path(target)
        resolved = (MODEL_ROOT / path).resolve()
        if (
            path.is_absolute()
            or not resolved.is_relative_to(MODEL_ROOT.resolve())
            or not resolved.is_file()
        ):
            errors.append(
                f"agent-index.yaml: {owner} references missing path {target!r}"
            )

    validate_model_path("entrypoint", index.get("entrypoint"))

    canonical_owners = index.get("canonical_owners", {})
    if not isinstance(canonical_owners, dict) or not canonical_owners:
        errors.append("agent-index.yaml: canonical_owners must be a non-empty mapping")
    else:
        for owner, target in canonical_owners.items():
            validate_model_path(f"canonical owner {owner}", target)
        manifest_documents = set(load_yaml(MANIFEST_PATH).get("documents", {}).values())
        owned_documents = set(canonical_owners.values())
        unowned_documents = manifest_documents - owned_documents
        if unowned_documents:
            errors.append(
                "agent-index.yaml: manifest documents without a canonical owner "
                f"{sorted(unowned_documents)}"
            )

    forbidden_control_fields = {
        "retrieval_policy",
        "routes",
        "context_bundles",
        "global_stop_rules",
    }
    present_control_fields = forbidden_control_fields & index.keys()
    if present_control_fields:
        errors.append(
            "agent-index.yaml: workflow-control fields are not allowed in the "
            f"knowledge-guidance index: {sorted(present_control_fields)}"
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
        errors.append("agent-index.yaml: authority_boundary must be a mapping")
    else:
        authority_missing = authority_required - authority.keys()
        if authority_missing:
            errors.append(
                "agent-index.yaml: authority_boundary missing fields "
                f"{sorted(authority_missing)}"
            )
        if authority.get("mode") != "knowledge_guidance_without_orchestration":
            errors.append(
                "agent-index.yaml: authority_boundary.mode must be "
                "knowledge_guidance_without_orchestration"
            )
        non_authorities = authority.get("does_not_define")
        if not isinstance(non_authorities, list) or not non_authorities:
            errors.append(
                "agent-index.yaml: authority_boundary.does_not_define must be non-empty"
            )

    profiles = index.get("retrieval_profiles", [])
    if not isinstance(profiles, list) or not profiles:
        errors.append("agent-index.yaml: retrieval_profiles must be a non-empty list")
        profiles = []
    profile_required = set(contract["profile_required"])
    profile_ids: set[str] = set()
    for position, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            errors.append(
                f"agent-index.yaml: retrieval profile #{position} is not a mapping"
            )
            continue
        profile_missing = profile_required - profile.keys()
        if profile_missing:
            errors.append(
                f"agent-index.yaml: retrieval profile #{position} missing "
                f"{sorted(profile_missing)}"
            )
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not ROUTE_ID.fullmatch(profile_id):
            errors.append(f"agent-index.yaml: invalid profile id {profile_id!r}")
        elif profile_id in profile_ids:
            errors.append(f"agent-index.yaml: duplicate profile id {profile_id}")
        else:
            profile_ids.add(profile_id)

        for field in ("related_intents", "query_terms", "knowledge_supported"):
            values = profile.get(field)
            if not isinstance(values, list) or not values or not all(
                isinstance(item, str) and item.strip() for item in values
            ):
                errors.append(
                    f"agent-index.yaml: profile {profile_id} {field} must be a "
                    "non-empty string list"
                )

        primary_documents = profile.get("primary_documents")
        if not isinstance(primary_documents, list) or not primary_documents:
            errors.append(
                f"agent-index.yaml: profile {profile_id} primary_documents "
                "must be non-empty"
            )
        else:
            for target in primary_documents:
                validate_model_path(f"profile {profile_id} primary document", target)

        additional = profile.get("additional_documents")
        if not isinstance(additional, dict):
            errors.append(
                f"agent-index.yaml: profile {profile_id} additional_documents "
                "must be a mapping"
            )
        else:
            for topic, targets in additional.items():
                if not isinstance(targets, list) or not targets:
                    errors.append(
                        f"agent-index.yaml: profile {profile_id} additional topic "
                        f"{topic} must contain documents"
                    )
                    continue
                for target in targets:
                    validate_model_path(
                        f"profile {profile_id} additional topic {topic}", target
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
    try:
        schema = load_yaml(SCHEMA_PATH)
        validate_english_and_encoding(errors)
        source_ids = validate_sources(errors)
        referenced_source_ids = validate_pages(schema, source_ids, errors)
        orphan_sources = source_ids - referenced_source_ids
        if orphan_sources:
            errors.append(
                f"source registries: unreferenced source IDs {sorted(orphan_sources)}"
            )
        validate_structure(schema, errors)
        validate_manifest(errors)
        validate_agent_index(schema, errors)
        validate_foundation_index(schema, errors)
        validate_removed_taxonomy(errors)
    except ValueError as exc:
        errors.append(str(exc))

    if errors:
        print(f"KB validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    page_count = sum(1 for _ in ROOT.rglob("*.md"))
    model_pages = sum(1 for _ in MODEL_ROOT.glob("*.md"))
    foundation_pages = sum(
        1 for path in FOUNDATION_ROOT.rglob("*.md") if path.name != "README.md"
    )
    source_count = sum(
        len(load_yaml(path).get("sources", [])) for path in source_registries()
    )
    model_profile_count = len(
        load_yaml(AGENT_INDEX_PATH).get("retrieval_profiles", [])
    )
    foundation_profile_count = len(
        load_yaml(FOUNDATION_INDEX_PATH).get("retrieval_profiles", [])
    )
    print(
        "KB validation passed: "
        f"3 content parts, {page_count} pages, {foundation_pages} Foundation topics, "
        f"{model_pages} Cosmos3-Nano pages, {source_count} sources, "
        f"{foundation_profile_count} Foundation and {model_profile_count} model "
        "knowledge-guidance retrieval profiles."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
