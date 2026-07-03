# OpenCode Config

Personal configuration for [OpenCode](https://opencode.ai).

> **Disclaimer:** Not affiliated with OpenCode. Personal configuration using OpenCode as a platform.

## Setup

1. **Clone the repository:**

   ```bash
   git clone git@github.com:joaomj/skills.git ~/.config/opencode
   ```

2. **Install the custom linter (optional, used by AGENTS.md rules):**

   ```bash
   pip install -e ~/.config/opencode/opencode_lint
   ```

3. **Configure OpenCode:**

   Copy the example config and edit as needed (change models, providers etc):

   ```bash
   cp ~/.config/opencode/opencode.json ~/.config/opencode.json
   ```

   The config sets up provider models, permission rules, and agent settings.

## Updating

```bash
cd ~/.config/opencode && git pull
```

## License

[MIT](LICENSE)
