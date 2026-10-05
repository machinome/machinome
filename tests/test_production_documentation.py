from pathlib import Path


def test_public_reference_documents_lazy_independent_draft_contract():
    root = Path(__file__).resolve().parents[1]
    api = (root / "docs/reference/api.rst").read_text()
    for term in (
        "machinome.production.profile",
        "Production[Model]",
        "machinome.production.item",
        "machinome.model",
        "unverified-direct-binding",
        "geometry",
        "draft",
        "unknown_occurrences",
        "files/<sha256>/<basename>",
        "local links",
        "homogeneous-solid",
    ):
        assert term in api
    changelog = (root / "docs/project/changelog.rst").read_text()
    assert (
        "Independent production profiles"
        in changelog.split("Machinome 0.7.1")[0]
    )
