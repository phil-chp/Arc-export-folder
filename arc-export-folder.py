from sys import argv
import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup

class BookmarkBuilder:
  def __init__(self, fetch_icons):
    self.fetch_icons = fetch_icons
    self.final = BeautifulSoup('<dl></dl>', 'html.parser')
    self.current_folder = None


  def add_folder(self, folder_name):
    """ Add a folder to our HTML object. Keep track of current folder """
    if self.current_folder == folder_name:
      return
    self.current_folder = folder_name
    dt = self.final.new_tag('dt')
    h3 = self.final.new_tag('h3')
    h3.string = folder_name
    dl = self.final.new_tag('dl')
    dt.append(h3)
    self.final.dl.append(dt)
    self.final.dl.append(dl)


  def add_bookmark(self, title, url):
    """ Add a bookmmark to our current folder in our HTML object."""
    dt = self.final.new_tag('dt')
    icon = self._find_favicon(url) if self.fetch_icons else ''
    a = self.final.new_tag('a', href=url, icon_uri=icon)
    a.string = title
    dt.append(a)
    self.final.find_all('dl')[-1].append(dt)


  def print(self):
    return self.final.prettify()


  def _find_favicon(self, url):
    """ Fetches the website to see if it can find a favicon. """
    try:
      site = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
      print(f'Failed to fetch URL: {url} - {e}')
      return urljoin(url, '/favicon.ico')
    if site.status_code != 200:
      return urljoin(url, '/favicon.ico')
    soup = BeautifulSoup(site.text, 'html.parser')
    icon = soup.find('link', rel='icon')
    if icon:
      return urljoin(url, icon['href'])
    return urljoin(url, '/favicon.ico')


def get_links(url):
  """
  Fetch the arc.net/folder page, grab the HTML,
  and return only what we are intersted in (folders and bookmarks)
  """
  response = requests.get(url)

  if response.status_code != 200:
    print(f'Failed to fetch URL: {url} - Status Code: {response.status_code}')
  soup = BeautifulSoup(response.text, 'html.parser')
  return soup.select('.PJLV.PJLV-iieNCbK-css') # ! FIXME: 100% this breaks soon


def parse(builder, links):
  """
  Given a list of elements:
  - `divs` are folders
  - `a` are bookmarks

  This function will iterate over the list and add the folders
  and bookmarks to an HTML object via the `BookmarkBuilder` class.
  """
  for link in links:
    if link.name == 'div':
      folder_name = link.get_text(strip=True)
      print(f"\n[*] Processing folder: {folder_name}\n")
      builder.add_folder(folder_name)
    elif link.name == 'a':
      bookmark_title = link.get_text(strip=True).replace('↗', '')
      print(f"[*] Processing bookmark: \"{bookmark_title}\"")
      bookmark_url = link['href']

      builder.add_bookmark(bookmark_title, bookmark_url)
    else:
      print(f'Unknown element: {link}')


def main():
  if len(argv) < 2 or len(argv) > 3:
    print(f"Usage:\n\tpython3 {argv[0]} <url to arc.net/folder> [--no-icons]")
    exit(1)
  url = argv[1]
  fetch_icons = False if '--no-icons' in argv else True

  links = get_links(url)
  builder = BookmarkBuilder(fetch_icons)

  tot_folders = [l.name == 'div' for l in links].count(True)
  tot_bookmarks = [l.name == 'a' for l in links].count(True)
  print(f"[*] Found {tot_folders} folders and {tot_bookmarks} bookmarks\n")

  parse(builder, links)

  with open('bookmarks.html', 'w', encoding='utf-8') as file:
    file.write(builder.print())
  print('\n\n[*] Finished! Bookmarks saved to bookmarks.html')


if __name__ == "__main__":
  main()
