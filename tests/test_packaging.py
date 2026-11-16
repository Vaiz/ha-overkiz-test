"""Offline checks for the HACS override; no Home Assistant runtime is imported."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "overkiz"


class PackagingTests(unittest.TestCase):
    """Guard the distribution boundary and the pinned dependency."""

    def test_hacs_and_manifest(self) -> None:
        """Keep one integration with complete metadata and an immutable library URL."""
        hacs = json.loads((ROOT / "hacs.json").read_text())
        manifest = json.loads((INTEGRATION / "manifest.json").read_text())
        self.assertEqual(hacs["homeassistant"], "2026.11.0")
        self.assertEqual(manifest["domain"], "overkiz")
        self.assertEqual(manifest["version"], "2026.11.0.1")
        for field in ("name", "documentation", "issue_tracker", "codeowners"):
            self.assertTrue(manifest[field])
        self.assertEqual(
            [path.name for path in (ROOT / "custom_components").iterdir()],
            ["overkiz"],
        )
        self.assertEqual(len(manifest["requirements"]), 1)
        name, url = manifest["requirements"][0].split(" @ ")
        self.assertEqual(name, "pyoverkiz[nexity]")
        parsed = urlparse(url)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "github.com")
        self.assertEqual(
            parsed.path,
            "/Vaiz/ha-overkiz-api/archive/d025ac8890afe8c2b0b2cbbb6e46d607d6eea6bc.zip",
        )

    def test_python_syntax_and_local_imports(self) -> None:
        """Parse all integration modules and resolve their relative import targets."""
        for path in INTEGRATION.rglob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.level:
                    base = path.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    if node.module:
                        target = base.joinpath(*node.module.split("."))
                        self.assertTrue(
                            target.with_suffix(".py").is_file()
                            or (target / "__init__.py").is_file(),
                            f"Missing local import {node.module} in {path}",
                        )

    def test_json_and_english_translations(self) -> None:
        """Ship valid JSON and fully resolved English strings with the same keys."""
        for path in ROOT.rglob("*.json"):
            if ".git" not in path.parts and ".venv" not in path.parts:
                json.loads(path.read_text())
        source = json.loads((INTEGRATION / "strings.json").read_text())
        english_path = INTEGRATION / "translations" / "en.json"
        english = json.loads(english_path.read_text())
        self.assertNotIn("[%key:", english_path.read_text())

        def check_keys(original: object, translated: object) -> None:
            if isinstance(original, dict):
                self.assertIsInstance(translated, dict)
                self.assertEqual(original.keys(), translated.keys())
                for key, value in original.items():
                    check_keys(value, translated[key])
            else:
                self.assertIsInstance(translated, str)
                self.assertTrue(translated)

        check_keys(source, english)

    def test_license_and_icon(self) -> None:
        """Keep the upstream license and a real PNG icon in the distribution."""
        self.assertIn("Apache License", (ROOT / "LICENSE.md").read_text())
        self.assertTrue(
            (INTEGRATION / "brand" / "icon.png")
            .read_bytes()
            .startswith(b"\x89PNG\r\n\x1a\n")
        )


if __name__ == "__main__":
    unittest.main()
