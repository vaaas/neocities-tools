const L = location
const D = document
const qs = q => D.querySelector(q)
const qss = q => D.querySelectorAll(q)
const add_class = c => x => x.classList.add(c)
const remove_class = c => x => x.classList.remove(c)

const filter_clicked = x => filter_posts(x.target.attributes.href.value)

const filter_posts = type =>
	{ for (x of qss('article'))
		(type === 'all' || x.attributes.t.value === type ? remove_class('hide') : add_class('hide'))(x)
	x = qs('a.active') ? remove_class('active')(x) : 0
	x = qs(`a[href="${type}"]`) ? add_class('active')(x) : 0
	history.pushState(null, D.title, L.origin+L.pathname+'?'+type) }

if (L.search.length>1)
	filter_posts(L.search.slice(1))
for (x of qss('#cats a'))
	x.onclick = filter_clicked
