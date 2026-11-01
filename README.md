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

## Notes

- Mock site: prices, charts, account data and forms are samples. Demo forms collect no payment details.
- Libraries load from public CDNs (GSAP, Lenis, Three.js) and fonts from Google Fonts.

## 1 Percent Club

A second site built from the same template, in black, red and chrome: `1percentclub/` (main page `index.html`,
member desk `account.html`). The Pages workflow publishes it at `/1percentclub/` next to 88FX.
