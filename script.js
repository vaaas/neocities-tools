const B = a => b => c => a(b(c))
const B1 = a => b => c => d => a(b(c)(d))
const C = a => b => c => a(c)(b)
const T = x => f => f(x)
const A = (x, ...fs) => reduce(T)(x)(fs)
const AA = (...fs) => x => A(x, ...fs)
const not = x => !x
const reduce = f => i => xs => { let a = i ; for (const x of xs) a = f(a)(x) ; return a }
const pluck = k => x => x[k]
const pluck_many = C(reduce(C(pluck)))
const tap = f => x => { f(x) ; return x }
const always = v => f => x => { f(x) ; return v }
const falsify = always(false)
const is = a => b => a === b
const isnt = B1(not)(is)
const when = cond => then => x => cond(x) ? then(x) : x
const maybe = when(is(null))
const otherwise = when(isnt(null))
const parse_html = x => new DOMParser().parseFromString(x, 'text/html')
const prop = B(pluck_many)(x=>['attributes',x,'value'])
const toggle = type => x => (type === 'all' || prop('t')(x) === type ? show : hide)(x)
const qs = (q, d=document) => d.querySelector(q)
const qss = (q, d=document) => d.querySelectorAll(q)
const qssc = q => d => qss(q,d)
const each = f => tap(xs => { for (const x of xs) f(x) })
const each_as = f => tap(async xs => { for await (const x of xs) f(x) })
const child = c => x => x.appendChild(c)
const add_class = c => x => x.classList.add(c)
const remove_class = c => x => x.classList.remove(c)
const hide = add_class('hide')
const show = remove_class('hide')
const text = x => x.text()
const then = f => x => x.then(f)
const set = k => v => tap(x => x[k] = v)

let loaded = false

const filter_clicked = falsify(AA(pluck('target'), prop('href'), filter_posts))

async function filter_posts(type)
	{ const main = document.querySelector('main')
	each(toggle(type))(qss('article'))
	if (!loaded)
		{ for await (const x of element_loader())
			A(x, toggle(type), C(child)(main))
		loaded = true }
	maybe(remove_class('active'))(qs('a.active'))
	maybe(add_class('active'))(qs(`a[href="${type}"]`))
	history.pushState(null, document.title, location.origin+location.pathname+'?'+type) }

async function* element_loader()
	{ dom = document
	while (dom)
		yield* await A(dom,
			qssc('#pagination a'),
			maybe(x => x.length === 2 ? x[1] : null),
			maybe(AA(
				prop('href'),
				fetch,
				then(text),
				then(parse_html),
				then(tap(x => dom = x)),
				then(qssc('article')))),
			otherwise(() => { dom = null ; return Promise.resolve([]) })) }

window.onload = function()
	{ if (location.search.length>1)
		filter_posts(location.search.slice(1))
	each(set('onclick')(filter_clicked))(qss('#cats a')) }
