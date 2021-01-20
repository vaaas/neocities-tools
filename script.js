const parse_html = x => new DOMParser().parseFromString(x, 'text/html')
const hide = x => x.classList.add('hide')
const show = x => x.classList.remove('hide')
const prop = (x, k) => x.attributes[k].value
const toggle = (type, x) => (type === 'all' || prop(x, 't') === type ? show : hide)(x)

let loaded = false


function filter_clicked(x)
	{ filter_posts(prop(x.target, 'href'))
	return false }

async function filter_posts(type)
	{ const main = document.querySelector('main')
	for (const x of document.querySelectorAll('article'))
		toggle(type, x)
	if (!loaded)
		{ for await (const x of element_loader())
			{ toggle(type, x)
			main.appendChild(x) }
		loaded = true }
	let q = document.querySelector('a.active')
	if (q) q.classList.remove('active')
	q = document.querySelector(`a[href="${type}"]`)
	if (q) q.classList.add('active')
	history.pushState(null, document.title, location.origin+location.pathname+'?'+type) }

async function* element_loader()
	{ dom = document
	while (true)
		{ let a = dom.querySelectorAll('#pagination a')
		if (a) a = a.length === 2 ? a[1] : null
		if (!a) break
		const res = await fetch(prop(a, 'href'))
		const text = await res.text()
		dom = parse_html(text)
		for (const x of dom.querySelectorAll('article'))
			yield x }}

window.onload = function()
	{ if (location.search.length>1)
		filter_posts(location.search.slice(1))
	for (const x of document.querySelectorAll('#cats a'))
		x.onclick = filter_clicked }
