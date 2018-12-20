# -*- coding: utf-8 -*-
import os
import shutil
from zipfile import ZipFile
from subprocess import Popen, PIPE
from hashlib import sha1

from bs4 import BeautifulSoup as BS

from .html import HTML


class EPUB:
    
    def __init__(self, filename):
        self.filename = filename
        self._file = ZipFile(filename, "r")
        self.sha1 = None
        self.nav = []
        self.nav_point = {}
        self.items = {}
        self.metadata = {}
        self.check_mimetype()
        self._sha1()
        self.read_ncx()
        self.read_opf()
    
    def __getitem__(self, name):
        assert (name in self.metadata), KeyError(
            "'%s' has no metadata named '%s'" % (self.filename,
                                                 name))
        return self.metadata[name]
    
    def _sha1(self):
        if self.sha1:
            return self.sha1
        with open(self.filename, "rb") as file:
            self.sha1 = sha1(file.read()).hexdigest()
        return self.sha1
    
    def check_mimetype(self):
        try:
            mimetype = self._file.read("mimetype")
            assert mimetype == b"application/epub+zip", \
                   TypeError("'%s' is not a ePub file" % self.filename)
        except KeyError:
            raise TypeError("'%s' is not a ePub file" % self.filename)
    
    def read_xml(self, filename, decoder="lxml"):
        try:
            xml = self._file.read(filename)
            return BS(xml, decoder)
        except KeyError:
            raise FileNotFoundError(
                "'%s' has no file named '%s'" % (self.filename, filename))
    
    def read_ncx(self):
        ncx = self.read_xml("OEBPS/toc.ncx")
        for nav in ncx.find_all("navpoint"):
            self.nav_point[nav["id"]] = {
                "id": nav["id"],
                "title": nav.navlabel.text.strip(),
                "content": os.path.join("OEBPS", nav.content["src"]),
                "play_order": nav.PlayOrder or len(self.nav) + 1}
            self.nav.append(self.nav_point[nav["id"]])
    
    def read_opf(self):
        opf = self.read_xml("OEBPS/content.opf")
        for data in opf.metadata.contents:
            if data.name is None:
                continue
            elif data.name == "meta":
                self.metadata[data["name"]] = data["content"]
            elif data.name[:3] == "dc:":
                self.metadata[data.name[3:]] = data.text
            else:
                self.metadata[data.name] = data.text
        for item in opf.find_all("item"):
            self.items[item["id"]] = {
                "id": item["id"],
                "href": os.path.join("OEBPS", item["href"]),
                "media-type": item["media-type"]}
    
    def get_file(self, name):
        assert (name in self.items), FileNotFoundError(
            "'%s' has no file named '%s'" % (self.filename, name))
        return self._file.read(self.items[name]["href"])
    
    def tmp(self):
        _path = os.path.join("/tmp", self.sha1)
        if not os.path.exists(_path):
            os.mkdir(_path)
        return _path
    
    def fix_opf(self):
        opf = self.read_xml("OEBPS/content.opf")
        _list = set()
        for item in opf.find_all("item"):
            if item["id"] in _list:
                item.extract()
            else:
                _list.add(item["id"])
        return str(opf)
    
    def convert_to_mobi(self, kindlegen=None):
        if not kindlegen:
            kindlegen = os.path.join(os.getcwd(), "kindlegen")
        if not os.path.exists(kindlegen):
            raise FileNotFoundError("Kindlegen not found")
        _tmp = self.tmp()
        self._file.extractall(_tmp)
        with open(os.path.join(_tmp, "OEBPS/content.opf"), "wb") as file:
            file.write(self.fix_opf().encode("utf-8"))
        ps = Popen("%s -dont_append_source OEBPS/content.opf" % kindlegen,
                   shell=True,
                   cwd=_tmp,
                   stdout=PIPE)
        ps.wait()
        with open(os.path.join(_tmp, "OEBPS/content.mobi"), "rb") as file:
            mobi = file.read()
        shutil.rmtree(_tmp)
        return mobi
    
    def convert_to_txt(self):
        txt = self["title"]
        for nav in self.nav:
            _title = nav["title"]
            _file = nav["content"]
            _text = HTML(self._file.read(_file)).purify().strip()
            if not _text:
                continue
            txt += "\n\n\n>>> %s <<<\n\n\n" % _title
            txt += _text
            txt += "\n\n\n>>> 本章结束 <<<\n\n\n"
        txt += ">>>>> The End <<<<<"
        return txt
        