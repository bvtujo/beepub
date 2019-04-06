# beepub

A simple quick-and-dirty scrape of the bee-all tag at https://blog.beeminder.com/bee-all

Usage: 
* Change desired user-specified parameters. 
* Make sure requirements are satisfied (`pip install -r requirements.txt`)
* Run `py beepub.py`
* The software will scrape the tags pages until there are none left, generate a table of contents, then grab the blog post from each url in the table to make an ebook. 

User-specified parameters:
```
TAG_URL_
TITLE_
AUTHOR_
FNAME_
```