# TODO: Fix Broken Links on GitHub Pages

Status: [ ] In progress

## Approved Plan Steps (Sequential):

1. [x] **Edit key files**: index.html, .github/profile/README.md, docs/mkdocs-site/mkdocs.yml, CONTRIBUTING.md (exact replacements for repo/docs URLs)

2. [x] **Global MD replacements**: ~20 MD files - leadarchitect-ai/portfolio-system-architect → Control39/cognitive-systems-architecture (use search_files + edit_file)

3. [x] **Fix badges/workflows**: Update CI badge URLs from leadarchitect-ai to Control39
4. [x] **Rebuild Sphinx docs**: cd docs/api && make html

5. [x] **Update sitemap.xml/mkdocs if needed**
6. [x] **Commit changes**: git add . && git commit -m "fix: broken links..."
7. [x] **Push to remotes**: git push origin main && git push github main:gh-pages

8. [ ] **Verify site**: Check https://control39.github.io/cognitive-systems-architecture/

## Progress Tracking
- Completed:
- Next step:

