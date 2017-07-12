# Neocities tools

Tools for easing management of a neocities site.

- ```ncpush```: pushes the ```render``` directory or the directory that's the first argument to neocities, recursively. Also deletes files.
- ```ncrender```: a static blog generator. Reads from ```posts``` and outputs to ```render```. Generates an index, an RSS feed, and pages for each article.
- ```postnote```: helper script for posting notes (short unstructured posts, like tweets). Uses your default editor (```$EDITOR```), and the format is HTML-like.

## Dependencies

- ```python3```
- ```lxml``` for parsing XML/XHTML
- ```jinja2``` for serialising in XML/XHTML
- ```curl``` for access to neocities. As in the binary ```curl```, not ```libcurl``` or python bindings.

## Workflow

The directory structure for a website will look like this. Symlinks are followed.

	.
	├── config
	├── ncpush
	├── ncrender
	├── postnote
	├── posts <- this is your source directory
	│   ├── articles
	│   │   └── your articles go here (if any)
	│   └── notes
	│       └── your notes go here (if any)
	├── render
	│   └── this is what's uploaded. You can put your JS/CSS/images here too.
	└── templates

An example:

	> cp ~/Documents/my_nice_article.html ./posts/articles
	> ./postnote
		In editor: I'm writing a <strong>great</strong> tweet!
	> ./ncrender
	> ./ncpush
		you will be asked for your credentials

The looks if a website are determined by the templates and your stylesheet. You're supposed to edit the templates if you want something more intricate than the default. All utilities read from the current working directory. Also edit / symlink / copy the config file, which has a few commonly changed variables, such as your URL or your desired name.

## XML format

Files placed in ```posts/articles``` must follow this format:

~~~~
<!DOCTYPE html>
<html>
	<head>
		<meta name="timestamp" value="SECONDS SINCE EPOCH"/>
		<meta name="type" value="article"/>
		<title>YOUR TITLE</title>
	</head>
	<body>YOUR STUFF</body>
</html>
~~~~

And those in ```posts/notes```:

~~~~
<!DOCTYPE html>
<html>
	<head>
		<meta name="timestamp" value="SECONDS SINCE EPOCH"/>
		<meta name="type" value="note"/>
	</head>
	<body>YOUR STUFF</body>
</html>
~~~~

```postnote``` will ease posting notes so you need only supply the ```body``` contents. There currently isn't any equivalent for articles.
