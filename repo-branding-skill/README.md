# repo-branding

**A Claude Code skill that generates a complete brand kit for GitHub repositories.**

Turn any repo into a polished, professional-looking project in seconds. Just type `/repo-branding` and get a full set of brand assets generated via Gemini image generation.

## What It Does

This skill analyzes your repository (name, description, language, domain) and generates:

- **Light and dark PNG banners** for your README
- **Light and dark square logos** that work as favicons or app icons
- **A social preview image** (1280x640) for GitHub link sharing
- **A design brief** (`DESIGN_BRIEF.json`) documenting all brand decisions
- **A `<picture>` element** in your README that automatically switches banners based on the viewer's GitHub theme

Everything is tailored to your specific project -- colors, metaphors, and style are all derived from what your repo actually does.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- A **Gemini API key** (free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey))
  - Set via `export GEMINI_API_KEY="your-key-here"` or `export GOOGLE_API_KEY="your-key-here"`
- Python 3.8+ with `pip` available (the skill auto-installs the `google-genai` SDK)

## Installation

**Option A: Install through skill-harness**

```bash
./skill-harness install --packs=repo-branding-skill --packs-only
```

**Option B: Install via Claude CLI**

```bash
claude skill add /path/to/repo-branding-skill
```

**Option C: Manual install**

Copy `SKILL.md` from this repository to:

```
~/.claude/skills/repo-branding/SKILL.md
```

## Usage

Open Claude Code in any git repository and type:

```
/repo-branding
```

The skill will:

1. Analyze your repo's README, package manifest, language, and structure
2. Generate a design brief with tailored colors, metaphors, and style
3. Create all brand images via Gemini
4. Update your README with a theme-aware banner

## Generated Assets

After running, you'll find these files in your project:

```
assets/
  DESIGN_BRIEF.json     Design brief (editable -- rerun to regenerate)
  banner.light.png      README banner (light theme)
  banner.dark.png       README banner (dark theme)
  logo.light.png        Square logo (light background)
  logo.dark.png         Square logo (dark background)
  social-preview.png    GitHub social preview (1280x640)
```

## Theme-Aware README Banner

The skill inserts a `<picture>` element into your README that automatically displays the correct banner based on the viewer's GitHub theme preference:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.dark.png" />
  <source media="(prefers-color-scheme: light)" srcset="assets/banner.light.png" />
  <img src="assets/banner.light.png" alt="Project banner" width="100%" />
</picture>
```

Users on GitHub dark mode see the dark banner. Users on light mode see the light banner. It works natively in the browser with no JavaScript.

## Setting the Social Preview

After generating assets, upload the social preview on GitHub:

**Settings > General > Social preview > Upload `assets/social-preview.png`**

This controls the image shown when your repo is shared on social media, Slack, Discord, etc.

## Related repos

- [`45ck/frontier-agent-playbook`](https://github.com/45ck/frontier-agent-playbook) - shared doctrine and repo-local instruction files for frontier-agent operating assumptions
- [`45ck/skill-harness`](https://github.com/45ck/skill-harness) - suite installer that can install this skill alongside the broader 45ck skill network

## Credits

Powered by [Gemini image generation](https://ai.google.dev/) for high-quality AI-generated brand assets.

## License

MIT License. See [LICENSE](LICENSE) for details.
