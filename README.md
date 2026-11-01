# 88FX

Your trading journey. All in one place.

Static website for 88FX: the main page (`index.html`) and the member desk (`account.html`).
No build step; open `index.html` in a browser to preview locally.

## Publishing

The workflow in `.github/workflows/pages.yml` publishes the site to GitHub Pages on every push to `main`.

One-time setup on GitHub:

1. **Settings → Pages → Build and deployment → Source:** choose **GitHub Actions**.
2. **Custom domain** (optional): enter your domain (e.g. `www.88fx.com`) and save, then add these DNS records at your registrar:

   | Type  | Name  | Value                     |
   |-------|-------|---------------------------|
   | CNAME | `www` | `alyph88fx-ops.github.io` |
   | A     | `@`   | `185.199.108.153`         |
   | A     | `@`   | `185.199.109.153`         |
   | A     | `@`   | `185.199.110.153`         |
   | A     | `@`   | `185.199.111.153`         |

3. When the DNS check passes, tick **Enforce HTTPS**.

## Proposal

`proposal.html` is the APEX proposal (a blueprint for trading brand growth): a pitch for a new IB business structure (one shared trading
ecosystem with a portfolio of trading brands on top), with 88FX and 1 Percent Club as the portfolio brands.
It opens on the APEX Summit mark and runs in the APEX chrome skin; the switch in the nav re-skins it as 88FX or
1 Percent Club, and `proposal.html#88fx` or `proposal.html#1pc` opens it in that skin. Published at `/proposal.html`.

Presenting on iPad: open the published page in Safari, tap Share → Add to Home Screen, then launch it from the
home-screen icon (`proposal-icon.png`) for a full-screen view. The dock in the bottom-right corner has Present,
previous and next; next/previous step through every scene, and a keyboard or Bluetooth clicker works too
(arrows, space, Page Up/Down, F for present mode).

## APEX logo concepts

`apex.html` presents six minimal, chromatic logo directions for APEX, each shown with its wordmark, app icon, light
version and a 16px test. Choosing one restyles the "in use" mockups (business card, app icon, website, social profile,
engraved plate) and shows a bar to copy the pick. Published at `/apex.html`.

## Notes

- Mock site: prices, charts, account data and forms are samples. Demo forms collect no payment details.
- Libraries load from public CDNs (GSAP, Lenis, Three.js) and fonts from Google Fonts.

## 1 Percent Club

A second site built from the same template, in black, red and chrome: `1percentclub/` (main page `index.html`,
member desk `account.html`). The Pages workflow publishes it at `/1percentclub/` next to 88FX.
