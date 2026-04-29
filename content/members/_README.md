# Members

One Markdown file per member. Filename pattern `NN-slug.md` where `NN` controls
display order and `slug` becomes the URL: `01-big.md` → `/members/big.html`.

## Front matter fields

| Field        | Required | Notes                                                   |
|--------------|----------|---------------------------------------------------------|
| `name`       | yes      | Thai full name                                          |
| `nickname`   | yes      | English short name. Used to match articles' `author:`.  |
| `nickname_th`| no       | Thai short name                                         |
| `role`       | yes      | e.g. President, Vice President / Editor, Member         |
| `email`      | no       |                                                         |
| `interests`  | no       | Comma-separated, freeform                               |
| `photo`      | no       | Filename inside `static/img/members/`. Square crop.     |

The body (after the front matter `---`) is freeform Markdown bio shown on the
member's profile page.

## Adding a new member

1. Create `content/members/NN-firstname.md` with the front matter above.
2. Drop a square photo (≥ 400×400, JPG or PNG) into `static/img/members/` matching
   the `photo:` filename. Skip the photo and the card will show their initials.
3. Run `python3 scripts/build.py`. New profile page is at `/members/<slug>.html`.
4. Article author bylines that match `nickname` (case-insensitive) become
   clickable links to that profile and render an author bio card at the end of
   the article automatically.
