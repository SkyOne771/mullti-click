# Project workflow

This public portfolio project is https://github.com/SkyOne771/mullti-click.

- Keep the README accurate when changing installation, controls, behavior, requirements, or limitations. Record user-visible changes in CHANGELOG.md.
- Before publishing code changes, run `python -m unittest discover -s tests -v`, `python -m compileall -q multiclick tests tools`, `python tools/package.py`, and `git diff --check`.
- The owner has requested that completed project work stay published on GitHub. Unless the user asks for local-only work or a review-only task, commit and push the task's completed changes to the current intended branch. Preserve unrelated user edits; do not include them without authorization. Never force-push or bypass repository protections.
- Verify the remote branch reflects the commit before saying GitHub is up to date. Inspect the CI result after publishing; report pending or failing checks accurately.
- Never generate real system mouse input in automated tests. Keep native hooks nonblocking and preserve the filtering that prevents recursive clicks.
- Do not claim full Windows end-to-end verification based on mocked tests or structure checks. Keep manual verification limits visible in the documentation.
