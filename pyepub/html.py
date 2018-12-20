# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS


class HTML:

    def __init__(self, html):
        self.bs = BS(html, "lxml")
        self.txt = ""
        self.inline = ["a", "b", "em", "i", "span", "strong"]
        self.block = ["div", "p", "h1", "h2", "h3", "h4", "h5", "h6"]
        self.ignore = ["img"]
    
    def plain(self, element):
        c = element
        if len(list(element.contents)) == 1:
            if c.name == "br":
                return "\n"
            elif c.name in self.ignore:
                return ""
            elif c.name in self.inline:
                return element.text
            elif c.name in self.block:
                return element.text + "\n"
        txt = ""
        for c in element.children:
            if c.name == "br":
                return "\n"
            elif c.name in self.ignore:
                continue
            elif c.name in self.inline:
                txt += self.plain(c)
            elif c.name in self.block:
                txt += self.plain(c) + "\n"
        return txt    
    
    def purify(self):
        return self.plain(self.bs.body)
                