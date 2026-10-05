"""Moneyss Business brand skin: registration, migration, pre-paint and contrast.

The skin is the fork's default appearance. It is light-only (banknote paper
canvas) with an ink-green rail + sidebar zone that re-declares the full token
set, so text inside the sidebar flips to light colours automatically.
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

import api.config as config

REPO = Path(__file__).resolve().parent.parent
CSS = (REPO / "static" / "style.css").read_text(encoding="utf-8")
BOOT_JS = (REPO / "static" / "boot.js").read_text(encoding="utf-8")
INDEX_HTML = (REPO / "static" / "index.html").read_text(encoding="utf-8")
ROUTES_PY = (REPO / "api" / "routes.py").read_text(encoding="utf-8")
NODE = shutil.which("node")


# ── registration ──────────────────────────────────────────────────────────

def test_moneyss_is_registered_as_light_only_skin():
    assert re.search(r"\{name:'Moneyss', value:'moneyss',[^}]*scheme:'light'\}", BOOT_JS)
    # _activeSkinScheme must honour a built-in scheme, not only extension ones.
    assert "skin.scheme||skin._extScheme" in BOOT_JS
    assert "moneyss:1" in INDEX_HTML
    assert "moneyss" in config._SETTINGS_SKIN_VALUES


def test_brand_assets_exist_and_are_wired():
    for name in ("moneyss-logo.webp", "moneyss-mark.webp", "moneyss-guilloche.svg"):
        assert (REPO / "static" / name).is_file(), name
    assert "static/moneyss-mark.webp" in INDEX_HTML
    assert "static/moneyss-logo.webp" in INDEX_HTML
    assert "static/moneyss-logo.webp" in ROUTES_PY
    manifest = json.loads((REPO / "static" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "Moneyss Business"


# ── server-side default + one-time migration ──────────────────────────────

@pytest.fixture()
def settings_file(tmp_path, monkeypatch):
    f = tmp_path / "settings.json"
    monkeypatch.setattr(config, "SETTINGS_FILE", f)
    return f


def _write(f, payload):
    f.write_text(json.dumps(payload), encoding="utf-8")


def test_new_install_defaults_to_moneyss(settings_file):
    s = config.load_settings()
    assert (s["theme"], s["skin"]) == ("light", "moneyss")


@pytest.mark.parametrize(
    "stored",
    [{"skin": "default"}, {"theme": "dark", "skin": "default"}, {"theme": "oled"}],
)
def test_pre_rebrand_default_skin_is_migrated(settings_file, stored):
    _write(settings_file, stored)
    assert config.load_settings()["skin"] == "moneyss"


def test_pre_rebrand_custom_skin_is_kept(settings_file):
    _write(settings_file, {"theme": "dark", "skin": "mono"})
    assert config.load_settings()["skin"] == "mono"


def test_explicit_default_after_rebrand_sticks(settings_file):
    _write(settings_file, {"skin": "default"})
    config.save_settings({"skin": "default"})
    stored = json.loads(settings_file.read_text(encoding="utf-8"))
    assert stored["moneyss_brand_v1"] is True
    assert stored["skin"] == "default"
    assert config.load_settings()["skin"] == "default"


def test_first_unrelated_save_persists_the_migration(settings_file):
    _write(settings_file, {"skin": "default", "font_size": "large"})
    config.save_settings({"font_size": "small"})
    stored = json.loads(settings_file.read_text(encoding="utf-8"))
    assert stored["skin"] == "moneyss"
    assert stored["moneyss_brand_v1"] is True


# ── pre-paint bootstrap never applies .dark under the light-only skin ─────

_DRIVER = r"""
const fs = require('fs');
const script = fs.readFileSync(process.argv[2], 'utf8');
const store = JSON.parse(process.argv[3] || '{}');
globalThis.localStorage = {
  getItem(k) { return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; },
  setItem(k, v) { store[k] = String(v); },
};
const classes = new Set();
globalThis.document = {
  documentElement: { classList: { add: (c) => classes.add(c) }, dataset: {} },
  querySelectorAll: () => [],
};
globalThis.window = globalThis;
globalThis.matchMedia = () => ({ matches: true });
(0, eval)(script);
process.stdout.write(JSON.stringify({
  classes: [...classes], skin: globalThis.document.documentElement.dataset.skin || null,
}));
"""


def _bootstrap_script():
    for m in re.finditer(r"<script>(.*?)</script>", INDEX_HTML, re.S):
        body = m.group(1)
        if "hermes-theme" in body and "legacy" in body and "skins" in body:
            return body
    raise AssertionError("appearance bootstrap not found")


@pytest.mark.skipif(NODE is None, reason="node required")
@pytest.mark.parametrize("theme,expect_dark", [("dark", False), ("system", False), ("light", False)])
def test_prepaint_moneyss_is_never_dark(theme, expect_dark):
    with tempfile.TemporaryDirectory() as td:
        drv = Path(td) / "d.js"
        scr = Path(td) / "s.js"
        drv.write_text(_DRIVER, encoding="utf-8")
        scr.write_text(_bootstrap_script(), encoding="utf-8")
        store = {"hermes-theme": theme, "hermes-skin": "moneyss"}
        out = subprocess.run([NODE, str(drv), str(scr), json.dumps(store)],
                             capture_output=True, text=True, timeout=60, check=True)
    res = json.loads(out.stdout)
    assert res["skin"] == "moneyss"
    assert ("dark" in res["classes"]) is expect_dark


# ── WCAG AA contrast of the palette tokens ────────────────────────────────

def _block(selector_start):
    i = CSS.index(selector_start)
    j = CSS.index("{", i)
    k = CSS.index("}", j)
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9A-Fa-f]{6})\b", CSS[j:k]))


def _lum(h):
    vals = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in vals]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


PAPER = _block(':root[data-skin="moneyss"],\n:root.dark[data-skin="moneyss"]{')
INK = _block(':root[data-skin="moneyss"] .rail,\n:root[data-skin="moneyss"] .sidebar{')
TEXT_TOKENS = ["--text", "--strong", "--muted", "--em", "--accent", "--accent-text",
               "--blue", "--gold", "--error", "--success", "--warning", "--info", "--code-text"]


@pytest.mark.parametrize("token", TEXT_TOKENS)
@pytest.mark.parametrize("bg", ["--bg", "--sidebar", "--surface", "--code-bg"])
def test_paper_zone_text_meets_aa(token, bg):
    assert _ratio(PAPER[token], PAPER[bg]) >= 4.5, (token, PAPER[token], bg, PAPER[bg])


@pytest.mark.parametrize("token", TEXT_TOKENS)
@pytest.mark.parametrize("bg", ["--bg", "--sidebar", "--surface"])
def test_ink_zone_text_meets_aa(token, bg):
    assert _ratio(INK[token], INK[bg]) >= 4.5, (token, INK[token], bg, INK[bg])


def test_user_bubble_and_primary_button_meet_aa():
    assert _ratio(PAPER["--user-bubble-text"], PAPER["--user-bubble-bg"]) >= 4.5
    # Primary buttons: cream text on green (paper), dark ink on gold (sidebar).
    assert _ratio("#FFFCEE", PAPER["--accent"]) >= 4.5
    assert _ratio("#1C2620", INK["--accent"]) >= 4.5
