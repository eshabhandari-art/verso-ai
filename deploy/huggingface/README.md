---
title: Verso AI
emoji: 📚
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Verso — Learn Smarter, Scroll Better

Hugging Face Space for [eshabhandari-art/verso-ai](https://github.com/eshabhandari-art/verso-ai),
originally built by the Verso AI team ([Verso-AI-Blaziken/verso-ai](https://github.com/Verso-AI-Blaziken/verso-ai)).

This Space contains only `Dockerfile` and `README.md`. The Dockerfile clones the GitHub repo at build time,
so to deploy new code: push to GitHub, then **Settings → Factory rebuild** on the Space.

Set a `JWT_SECRET` secret in the Space settings, otherwise logins reset on every restart.
Data (SQLite database, uploads, generated videos) is not persistent on the free tier.
