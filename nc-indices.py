#!/usr/bin/env python3

import sys
import os
import re
import urllib.parse
from bs4 import BeautifulSoup

class Dependency():
	template_html = """<article><div class="date">{DATE}</div><h1><a href="{URL}">{TITLE}</a></h1></article>"""
	template_rss = """<item><title>{TITLE}</title><link>{URL}</link><guid>{URL}</guid><description>{DESCRIPTION}</description><pubDate>{DATE}</pubDate></item>"""
	def __init__ (self, pathname):
		self.pathname = pathname
		self.set_url()
		self.mtime = os.stat(self.pathname).st_mtime
	
	def set_url (hostname="localhost"):
		self.url = os.path.join(hostname, urllib.parse.quote(self.pathname)
	
	def parse (self):
		with open(self.pathname, "r") as f:
			contents = f.read()
		soup = BeautifulSoup(contents, "html.parser")
		tmp = soup.find(attrs={"name":"keywords"})
		self.keywords = set(tmp["content"].split(", ")) if tmp else set()
		tmp = soup.find(attrs={"name":"date"})
		self.date = tmp["content"] if tmp else "0000-00-00"
		self.title = str(soup.select_one("main > h1").renderContents(), encoding="utf8")
		self.contents = str(soup.main.renderContents(), encoding="utf8")
	
	def render_html (self):
		return self.template_html.format(
			URL=self.url,
			TITLE=self.title,
			DATE=self.date
		)
	def render_rss (self):
		return self.template_rss.format(
			TITLE=self.title,
			URL=self.url,
			DATE=self.date,
			DESCRIPTION="<![CDATA["+self.contents+"]]>"
		)

class Target():
	def __init__ (self, pathname, deps=[]):
		self.pathname = pathname
		if os.path.exists(self.pathname):
			self.mtime = os.stat(self.pathname).st_mtime
		self.dependencies = deps
		self.init_template()
	
	def needs_remake (self):
		if not os.path.exists(self.pathname): return True
		for dep in self.dependencies:
			if dep.mtime > self.mtime: return True
		return False
	
	def init_template(): pass

class Index(Target):
	def init_template (self):
		if not os.path.isfile("template.html"): quit()
		with open("template.html", "r") as f:
			contents = f.read()
		self.template = contents.replace("<main>", "<main class=\"index\">\n{ITEMS}")

	def render(self):
		for dep in self.dependencies: dep.parse()
		self.dependencies.sort(reverse=True, key=lambda dep: dep.date)
		items = list()
		keywords = set()
		for dep in self.dependencies:
			items.append(dep.render_html())
			keywords.union(dep.keywords)
		final = self.template.format(
			ITEMS="".join(items),
			DATE=self.dependencies[0].date,
			KEYWORDS=", ".join(keywords)
		)
		with open(self.pathname, "w") as f:
			f.write(final)
			print("Wrote", self.pathname)

class Feed(Target):
	def init_template(self):
		self.template = """<?xml version='1.0' encoding='UTF-8' ?><rss version="2.0"><channel><title>{TITLE}</title><link>{URL}</link><description>{DESCRIPTION}</description>{ITEMS}</channel></rss>"""
		if not os.path.isfile("template.html"): quit()
		with open("template.html", "r") as f:
			contents = f.read()
		soup = BeautifulSoup(contents, "html.parser")
		self.title = str(soup.title.renderContents(), "utf8")
		tmp = soup.find(attrs={"name":"url"})
		self.url = tmp["content"] if tmp else "localhost"
		tmp = soup.find(attrs={"name":"description"})
		self.description = tmp["content"] if tmp else "localhost"
		for dep in self.dependencies: dep.set_url(self.url)

	def render(self):
		for dep in self.dependencies: dep.parse()
		self.dependencies.sort(reverse=True, key=lambda dep: dep.date)
		items = list()
		for dep in self.dependencies[:10]: items.append(dep.render_rss())
		self.dependencies.sort(reverse=True, key=lambda dep: dep.date)
		final = self.template.format(
			ITEMS="".join(items),
			URL=self.url,
			TITLE=self.title,
			DESCRIPTION=self.description
		)
		with open(self.pathname, "w") as f:
			f.write(final)
			print("Wrote", self.pathname)

def valid_page (page):
	if page in ["index.html", "template.html"]: return False
	elif not os.path.isfile(page): return False
	elif page[0] == ".": return False
	elif not page.endswith(".html"): return False
	else: return True

def main ():
	deps = [Dependency(f) for f in os.listdir(".") if valid_page(f)]
	if len(deps) == 0: sys.exit()
	index = Index("index.html", deps)
	feed = Feed("rss.xml", deps)
	if index.needs_remake(): index.render()
	if feed.needs_remake(): feed.render()

if __name__ == "__main__": main()
