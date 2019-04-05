import pickle
import time
import datetime

from bs4 import BeautifulSoup
from lxml import html
from urllib import request

# shim to resolve unicode problems in ebooklib imports
# taken from https://stackoverflow.com/questions/33433223/reading-images-into-ebooklib-epub-in-python-3-4
from ebooklib import epub
original_get_template = epub.EpubBook.get_template
def new_get_template(*args, **kwargs):
    return original_get_template(*args, **kwargs).encode(encoding='utf8')
epub.EpubBook.get_template = new_get_template



def get_fname(url):
    return "posts/" + url.split("/")[-1] + ".html"


def write_html(url, html_page):
    fname = get_fname(url)
    try:
        with open(fname, 'wb+') as file:
            pickle.dump(html_page, file)   
    except:
        print("Error opening or writing file.")
        return -1
    return 0


def read_html(fname):
    try:
        with open(fname, 'rb') as file:
            doc = pickle.load(file)
    except:
        print("error opening or reading file")
        return -1
    return doc


def parse_entry(html_doc):
    
    soup = BeautifulSoup(html_doc)
    post = soup.find("div", class_="post")
    title_str = str(post.find("h1"))
    body = post.find("div", class_="entry")
    

   

def process_entry(entry_url):
    try:
        f = get_fname(entry_url)
        doc = read_html(fname)
    except:
        doc = request.urlopen(entry_url).read()
        write_html(entry_url, doc)

    chapter = parse_entry(doc)
    

def get_links(toc_url):
