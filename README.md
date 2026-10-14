# Stutter Shot Studio — support site

Public support, help and privacy pages for the Stutter Shot Studio app, served with
GitHub Pages from the root of this repository.

| Page | URL |
| --- | --- |
| Support | `https://rafeek.github.io/stuttershot-support/` |
| Help | `https://rafeek.github.io/stuttershot-support/help.html` |
| Privacy policy | `https://rafeek.github.io/stuttershot-support/privacy.html` |

Support and privacy go in App Store Connect under the app's information; the app's
Help menu opens the help page.

`.nojekyll` disables Jekyll processing — these are plain static files.

## Editing

Edit the HTML directly and push; Pages redeploys within a minute or two. `help.html`
is generated from `HELP.md` in the app's repository (`../StopMotion`): edit that, then
run `python3 gen_help.py` here.

Every page opens with the same site header — the brand plus a menu bar linking all
three pages, the current one marked `aria-current="page"`. `NAV` in `gen_help.py` is
the master copy; `index.html` and `privacy.html` carry it by hand, so change all three
when adding a page.
