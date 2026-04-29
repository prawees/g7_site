# RAMA G7 Website — UI Kit

A high-fidelity interactive prototype of g7.prawees.com rebuilt with React.

## Screens
- **Editorial Index** — hero intro + post list cards
- **Article View** — article header, body, Vancouver references
- **About** — club description, leadership, contact
- **Join** — membership interest form with inline validation

## Components
| File | Description |
|---|---|
| `Masthead.jsx` | Dark ink header; 3-col grid; nav with active state |
| `PostCard.jsx` | Numbered list item; hover tint + title color shift |
| `ArticleView.jsx` | Full article layout; section headers; references block |
| `Footer.jsx` | 2-col dark footer; Thai description; social links |

## Font stack (humanized)
- Display/Body: Source Serif 4 + Noto Serif Thai
- UI: IBM Plex Sans + Sarabun
- Mono: IBM Plex Mono

All sourced from Google Fonts CDN.

## Notes
- The prototype uses `window.scrollTo` for page transitions (no router needed)
- Components are exported to `window.*` for cross-script sharing in Babel
- Paper grain texture applied via fixed SVG `body::before`
- All components are cosmetic-only; form submits are mocked
