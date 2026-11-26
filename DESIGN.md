# wheredidit design system

Read this before changing the site's UI. Do not introduce a new direction; extend this one. English only. Values below come from `docs/index.html` as of this commit.

## Concept

A search box first: describe the file in your own words and see why each file matched.

Theme: light.

## Color tokens

| Token | Value | Role |
|---|---|---|
| `--bg` | `#fff7ed` | page background |
| `--fg` | `#2a1b0e` | body text |
| `--mut` | `#8a6a4a` | secondary text (AA on bg) |
| `--card` | `#ffffff` | card and panel surface |
| `--line` | `#f1d9bd` | borders and dividers |
| `--acc` | `#c2410c` | primary action, links, focus ring |
| `--accfg` | `#fff` | text on accent |
| `--code` | `#2a1b0e` | code block background |
| `--codefg` | `#ffe9d2` | code block text |
| `--warn` | `#c2410c` | warning border and limits |

Contrast: every text node on the page is checked against WCAG AA (4.5:1, 3:1 for large text) with a script in the repo owner's QA harness. Keep it passing when you change a color.

## Type

| Token | Stack | Role |
|---|---|---|
| `--arabic` | `'Alexandria',sans-serif` | Arabic font stack |
| `--body` | `'Sora','Alexandria',system-ui,sans-serif` | body font stack |
| `--head` | `'Fraunces','Alexandria',system-ui,sans-serif` | heading font stack |

Font sizes in use: `.86rem`, `1.5rem`, `1rem`, `.9rem`, `.72rem`, `clamp(2.1rem,8.5vw,3.4rem)`, `1.25rem`, `clamp(2.4rem,8vw,4.4rem)`, `1.2rem`, `1.3rem`, `.88rem`, `2rem`.

## Spacing, radius, elevation

- Spacing values in use: `2px`, `4px`, `6px`, `8px`, `10px`, `11px`, `12px`, `14px`, `16px`, `26px`, `34px`, `40px`. Prefer these; do not add new ones.
- Radius: `--r` (22px). Use the token, not literals.
- Elevation: `0 10px 0 var(--fg)`, `0 6px 0 var(--fg)`

## Motion

- Durations in use: `.05s`, `.15s`, `.25s`, `.2s`, `.34s`, `.35s`, `.42s`, `1s`.
- Curves: `cubic-bezier(.16,1,.3,1)`, `cubic-bezier(.22,1.36,.32,1)`.
- Every animation sits behind `prefers-reduced-motion: reduce`, which turns animation and transition off.
- Motion shows state or order. It is never decoration.

## Components and states

- Button `.btn` (filled) and `.btn.alt` (outline): min height 44px, visible `:focus-visible` outline (2px accent), hover and active states.
- Card `.card`, warning card `.card.warn` (left border in `--warn`).
- Language toggle `.langtoggle` with `aria-pressed`.
- Code block `pre`: always LTR, monospace.
- Status words use `.ok b` and `.no b` colors (AA checked).

## RTL rules

- The language toggle sets `dir` and `lang` on `<html>`. Arabic text uses the `--arabic` font and line-height 1.75.
- Use logical CSS (`margin-inline`, `inset-inline-start`, `text-align:start`). No `left` or `right` for layout.
- Letter-spacing is 0 and text-transform none in Arabic.
- Code, terminal output and demo panels stay LTR (`direction:ltr`). Install and demo output stay English.
- Arabic is Egyptian-leaning plain language. Brand names and commands stay Latin.

## Microcopy voice

Plain, specific, honest about limits. Say what it does and what it does not. No hype, no invented numbers.

Examples from the site:

1. Find the file by what was inside it.
2. matched 2 of 4 words: comparison, internet
3. Local only. No cloud, no account.
4. OCR needs tesseract installed. Handwriting is poor.
5. Date words: last week, yesterday

## Do / Don't

| Do | Don't |
|---|---|
| Lead with the search box | Lead with a feature list |
| Show the matched words | Show a bare file list |
| Keep the pill radius (22px) | Mix sharp and round |
| One warm accent | Add a second accent |
| State OCR limits | Imply it reads everything |

## Known hard-coded values (should become tokens)

These literal colors appear in the CSS outside `:root`: `#17703f`, `#2e9e5b`, `#5b4430`, `#6b4a2b`, `#a8281b`, `#c0392b`, `#ea580c`, `#ffd9b0`, `#ffedd5`.
Also: status colors in `.ok b` and `.no b`, and several literal pixel sizes in component CSS. Move them into tokens next time that block is touched.
