# Neocities tools

Tools for easing management of a neocities site. Very lo-fi.

- `ncpush`: syncs the `render` directory by default with neocities, recursively. Takes an optional first argument for the directory to sync.
- `ncrender`: a static blog generator. Reads from `posts` and outputs to `render`. Generates indices and an RSS feed. It tries not to regenerate the entire website every time; use the optional `-f` argument to force a full rebuild.
- `posthelp`: helper script for making posts, meant to be used interactively

## Dependencies

- ```python3```
- ```curl``` for access to neocities. As in the binary ```curl```, not ```libcurl``` or python bindings.
-  That's all

## Workflow

The directory structure for a website will look like this. Symlinks are followed.

	.
	├── config
	├── ncpush
	├── ncrender
	├── posthelp
	├── posts
	├── render/
	│   ├── articles/
	│   ├── index.html
	│   ├── rss.xml
	└── templates/

Use `posthelp` to create new notes (short, tweet-like) or articles (long-form blog posts). It'll place the files in the right place. Notes, and the title and first paragraph of articles are appended in the `posts` file. Field entries are separated with the ASCII `Record Separator` character and double newlines. `ncrender` will render the new indices and rss feeds if and only if there have been changes, and `ncpush` will push changes to neocities.