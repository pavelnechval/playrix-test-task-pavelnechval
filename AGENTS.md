# Instructions for coding agents (Codex and others)

This repository's tool is a Claude Code skill: `.claude/skills/card-set/SKILL.md`. Claude Code loads it automatically.

Any other agent: when you are asked to make a card set (a set theme plus free-form wishes, for example "Сделай набор карточек для коллекции «Кино»: жанр — детектив, 3 варианта"):

1. Read `.claude/skills/card-set/SKILL.md` and follow it exactly, together with every file it tells you to read.
2. Run all commands from the repository root, as the skill shows them (`python -I pipeline/...`).
3. The images are made through the Gemini API with the key in the `GEMINI_API_KEY` environment variable (see `README.md`). Never print, log or commit API keys.
4. If a command stops with "The Gemini API balance is empty", tell the user to top it up and run the same command again.

The reference images in `references/` are the property of Playrix (`references/NOTICE.md`). Use them only as generation references.
