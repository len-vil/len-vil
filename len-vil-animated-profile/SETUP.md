# Set up your animated GitHub profile

This folder is prepared for the special GitHub profile repository `len-vil/len-vil`.

## 1. Upload the files

1. Open https://github.com/len-vil/len-vil
2. Choose **Add file → Upload files**.
3. Upload everything in this folder, keeping the directory structure (`assets`, `cards`, `scripts`, `.github/workflows`, `data`).
4. Commit to the `main` branch.

The repo was checked on 23 November 2026 and was empty, so this adds a new `README.md` rather than replacing an existing one.

## 2. Run the first contribution refresh

1. Open the repository's **Actions** tab.
2. Select **Refresh animated profile cards**.
3. Choose **Run workflow**.
4. After it finishes, reload https://github.com/len-vil.

The workflow runs daily at 06:17 UTC and updates the contribution graph from GitHub's public contribution calendar. It does not use placeholder contribution counts or a personal access token.

## 3. Preview the SVGs locally (optional)

```bash
python -m pip install -r scripts/requirements.txt
python scripts/fetch_contributions.py
python scripts/render_profile.py
```

For a non-animated screenshot-ready render:

```bash
# Windows PowerShell
$env:STATIC="1"
python scripts/render_profile.py
```

Set `STATIC=0` or open a new terminal to restore animation output.

## Personal details included

- Lenvil Pinto
- MCA student, St. Joseph Engineering College, Mangaluru
- VARTHA, CropGenius, CareConnect, TrustLens and CashVision
- React, TypeScript, Flutter, Python, Java and Supabase

Update these directly in `scripts/render_profile.py` and rerun the renderer if your details change.
