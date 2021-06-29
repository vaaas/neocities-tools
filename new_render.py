import string, time, json, os
from typing import Iterable, Union, Tuple, List, Optional
import xml.dom.minidom as dom

Attrib = Tuple[str, str]

CONF = json.loads(open('config').read())
DIGITS: str = string.digits + string.ascii_letters + '-_'

def has_file(x: dom.Element) -> bool:
	return x.hasAttribute('file')

def element(tag: str, attrib: Iterable[Attrib], children=Union[Iterable[dom.Element], str]) -> dom.Element:
	doc = dom.Document()
	elem = doc.createElement(tag)
	for x in attrib:
		elem.setAttribute(x[0], x[1])
	for x in list(children):
		elem.appendChild(doc.createTextNode(x) if isinstance(x, str) else x)
	return elem

def ymd(x: int) -> str: return time.strftime('%Y-%m-%d', time.gmtime(x))
def rfctime(x: int) -> str: return time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime(x))
def emptyjoin(x: Iterable) -> str: return ''.join(x)

def int_to_base(x: int, base: int) -> str:
	if x == 0: return DIGITS[0]
	xs: List[str] = []
	while x:
		x, mod = divmod(x, base)
		xs.append(DIGITS[mod])
	return emptyjoin(reversed(xs))

def guid(x: int) -> str:
	return int_to_base((x-1483228800)//60, len(DIGITS))

def article_template(x: dom.Element) -> dom.Element:
	return html(
		CONF['lang'],
		head(x.getElementsByTagName('h1')[0].firstChild.nodeValue),
		element('body', [], [
			element('header', [], [
				element('a', [('href', '/')], ['Home']),
				' — ',
				element('time', [], ymd(int(x.getAttribute('timestamp')))),
			]),
			element('main', [], [x.cloneNode(True) for x in x.childNodes]),
		])
	)

def html(lang: str, head: dom.Element, body: dom.Element) -> dom.Element:
	return element('html', [ ('lang', lang ) ], [ head, body ])

def head(title: str) -> dom.Element:
	return element('head', [], [
		element('meta', [ ('charset', 'utf-8') ], []),
		element('meta', [ ('name', 'viewport'), ('content', 'width=device-width, initial-scale=1.0') ], []),
		element('meta', [ ('name', 'url'), ('content', 'https://%s.neocities.org' % (CONF['sitename'],)) ], []),
		element('meta', [ ('name', 'author'), ('content', CONF['author']) ], []),
		element('meta', [ ('name', 'description'), ('content', CONF['title']) ], []),
		element('link', [ ('rel', 'stylesheet'), ('href', '/style.css') ], []),
		element('link', [ ('rel', 'icon'), ('href', '/favicon.ico?v=2') ], []),
		element('link', [ ('rel', 'alternate'), ('href', '/rss.xml'), ('type', 'application/rss+xml') ], []),
		element('title', [], [ title ]),
	])

def imglink(href: str, src: str, alt: Optional[str]) -> dom.Element:
	imgprops = [ ('src', src) ]
	if alt is not None: imgprops.append(('alt', alt))
	return element('a', [('href', href)], [ element('img', imgprops, []) ])

def handle(x: dom.Element) -> dom.Element:
	return handle_article(x) if has_file(x) else handle_note(x)

def handle_note(x: dom.Element) -> dom.Element:
	return element('article',
		[
			('id', guid(int(x.getAttribute('timestamp')))),
			('t', x.getAttribute('t'))
		],
		[
			element('time', [], [
				ymd(int(x.getAttribute('timestamp')))
			]),
			*iter(x.childNodes),
		])

def handle_article(x: dom.Element) -> dom.Element:
	return element('article',
		[
			('id', guid(int(x.getAttribute('timestamp')))),
			('t', x.getAttribute('t'))
		],
		[
			element('time', [], ymd(int(x.getAttribute('timestamp')))),
			element('h1', [], [
				element('a',
					[ ('href', x.getAttribute('file')) ],
					list(x.getElementsByTagName('h1')[0].childNodes)),
			]),
			x.getElementsByTagName('p')[0],
		]
	)

def render_index(posts: List[dom.Element]) -> dom.Element:
	CATS = set()
	for x in posts: CATS.add(x.getAttribute('t'))
	return html(CONF['lang'], head(CONF['title']),
		element('body', [], [
			element('header', [], [
				imglink(href='/', src='/pics/ruri_thinking_icon.jpg', alt='icon'),
				element('h1', [], [
					CONF['title'],
					' ',
					imglink(href='/rss.xml', src='/pics/feed-icon.svg', alt='rss')
				]),
				element('nav', [('id', 'links')], (element('a', [('href', CONF['links'][x])], [x]) for x in CONF['links'])),
				element('p', [], [ CONF['about'] ]),
			]),
			element('main', [], [
				element('nav', [('id', 'cats')], [
					element('a', [('href', 'all'), ('class', 'active')], 'all'),
					*(element('a', [('href', x)], x) for x in CATS),
				]),
				*(handle(x.cloneNode(True)) for x in posts),
			]),
			element('script', [('src', '/script.js')], [' ']),
		]))

def render_rss(xs: List[dom.Element]) -> dom.Element:
	def render_item_rss(item: dom.Element) -> dom.Element:
		g = guid(int(item.getAttribute('timestamp')))
		pubdate = rfctime(int(item.getAttribute('timestamp')))
		return element('item', [],
			[
				element('title', [], [ 'New post on %s (%s)' % (CONF['sitename'], g) ]),
				element('guid', [ ('isPermaLink', 'false') ], [ 'https://%s.neocities.org/#%s' % (CONF['sitename'], g) ]),
				element('pubDate', [], [ pubdate ]),
				element('description', [], [ handle(item) ]),
				element('link', [], [ 'https://%s.neocities.org/#%s' % (CONF['sitename'], g) ]),
			]
		)

	return element(
		'rss',
		[
			('version', '2.0'),
			('xmlns:atom', 'http://www.w3.org/2005/Atom')
		],
		[
			element('channel', [], [
				element('title', [], [CONF['title']]),
				element('link', [], ['https://%s.neocities.org' % (CONF['sitename'],)]),
				element('atom:link',
					[
						('href', 'https://%s.neocities.org/rss.xml' % (CONF['sitename'],)),
						('rel', 'self'),
						('type', 'application/rss+xml')
					], []),
				element('description', [], [CONF['title']]),
				element('pubDate', [], [xs[0].getAttribute('timestamp')]),
				element('language', [], [CONF['lang']]),
				element('ttl', [], ['1440']),
				*(render_item_rss(x.cloneNode(True)) for x in xs)
			]),
		]
	)

def write(pathname: str, data: str) -> None:
	fp = open(pathname, 'w')
	fp.write(data)
	fp.close()

def main() -> None:
	tree = dom.parse('posts.xml')

	for x in tree.getElementsByTagName('post'):
		if not has_file(x): continue
		write(
			os.path.join('render', x.getAttribute('file')),
			'<!DOCTYPE html>' + article_template(x).toxml())

	write(
		os.path.join('render', 'index.html'),
		'<!DOCTYPE html>' +
		render_index(list(tree.getElementsByTagName('post'))).toxml())
	write(
		os.path.join('render', 'rss.xml'),
		'<?xml version="1.0" encoding="UTF-8"?>' +
		render_rss(list(tree.getElementsByTagName('post'))).toxml())

main()
