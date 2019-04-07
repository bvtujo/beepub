import pickle
import time
import requests
import uuid
import os

from bs4 import BeautifulSoup
from lxml import html


# shim to resolve unicode problems in ebooklib imports
# taken from https://stackoverflow.com/questions/33433223/reading-images-into-ebooklib-epub-in-python-3-4
from ebooklib import epub
# original_get_template = epub.EpubBook.get_template
# def new_get_template(*args, **kwargs):
#     return original_get_template(*args, **kwargs).encode(encoding='utf8')
# epub.EpubBook.get_template = new_get_template


HTTP_HEADER_ = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
UUID = str(uuid.uuid4())

def pickle_file(filename, object):
    with open(filename, 'wb+') as f:
        pickle.dump(object, f);

def unpickle(filename):
    with open(filename, 'rb') as f:
        object = pickle.load(f)
        return object

def get_fname(url):
    return "posts/" + url.split("/")[-2] + ".html"


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
    with open(fname, 'rb') as file:
        doc = pickle.load(file)
    return doc


def parse_entry(html_doc, url):
    
    soup = BeautifulSoup(html_doc)
    post = soup.find("div", class_="post")
    title = post.find("h1")
    title_str = str(title.text)
    body = post.find("div", class_="entry")
    meta = post.find("div", class_="meta")
    author = meta.get_text().strip().split(" ")[-1]
    date = meta.find("div", class_="date")
    print(title_str, str(meta.get_text()), date)

    ch = epub.EpubHtml(title=title_str,
        file_name=url.split("/")[-2]+str(".xhtml"),
        lang='en')
    ch.set_content(str(title).encode() + str(meta).encode() + str(body).encode())
    return ch

def process_entry(entry_url):
    try:
        f = get_fname(entry_url)
        doc = read_html(f)
    except:
        print("sending GET request to {}".format(entry_url))
        r = requests.get(entry_url, headers=HTTP_HEADER_)
        doc = r.content
        BeautifulSoup(doc)
        write_html(entry_url, doc)

    chapter = parse_entry(doc, entry_url)
    return chapter


def get_links(toc_url, ids, links):
    print("Down one level!")
    print("Sending GET request to {}".format(toc_url))
    r = requests.get(toc_url, headers=HTTP_HEADER_)
    doc = r.content
    soup = BeautifulSoup(doc)
    b = soup.find_all(id='leftcontent')[0]
    posts = b.find_all('div', class_='posts')
    ids.extend([p.h2['id'] for p in posts])
    links.extend([p.a['href'] for p in posts])
    print("Found {} links here.".format(len(links)))
    older = b.find_all('div',class_='alignleft')[0]
    if "Older Entries" in older.text:
        print("Found an older page.")
        ids, links = get_links(older.a['href'], ids, links)
    else:
        print("recursion finished!")
    return ids, links


def make_book(BookName, author, chapters, uuid, filename):
    book = epub.EpubBook()
    book.set_identifier(uuid)
    book.set_title(BookName)
    book.set_language("en")
    book.add_author(author)

    for a in chapters:
        book.add_item(a)

    style = 'body { font-family: Times, Times New Roman, serif; } h1 {font-size: 16; font-style: bold;}'
    nav_css = epub.EpubItem(uid="style_nav",
                            file_name="style/nav.css",
                            media_type="text/css",
                            content=style)
    book.add_item(nav_css)
    book.toc = tuple(chapters)
    book.spine = ['nav'] + chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(filename, book)



if __name__ == "__main__":

    TAG = 'rationality'
    TAG_URL_ = r"https://blog.beeminder.com/tag/{}/".format(TAG)
    AUTHOR_ = "Daniel Reeves, Bethany Soule, et al."
    TITLE_ = "Rationality: From Akrasia to Beeminder"
    FNAME_ = "BeeminderRationality.epub"
    if not os.path.exists("toc_{}.dat".format(TAG)):
        ids, links = get_links(TAG_URL_, [],[])
        pickle_file("toc_{}.dat".format(TAG), {"ids": ids, "links": links})

    toc = unpickle("toc_{}.dat".format(TAG))


    toc['links'].reverse()
    for i in toc['links'][-6:]:
        print(i)
    chapters = [process_entry(ch) for ch in toc['links']]

    make_book(TITLE_, 
        AUTHOR_, 
        chapters, 
        UUID, 
        FNAME_)


