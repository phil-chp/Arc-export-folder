from sys import argv
import requests
from urllib.parse import urljoin, urlsplit
from ctypes import c_uint64
import argparse

from bs4 import BeautifulSoup

# From https://stackoverflow.com/a/50591791/14578266
myhash=lambda word: c_uint64(hash(word)).value.to_bytes(8,"big").hex()

class BookmarkBuilder:
  def __init__(self, no_icons):
    self.no_icons = no_icons
    self.final = BeautifulSoup('<dl></dl>', 'html.parser')
    self.current_folder = None
    self.fqdn_hashmap = {}


  def add_folder(self, folder_name):
    """ Add a folder to our HTML object. Keep track of current folder """
    if self.current_folder == folder_name:
      return
    self.current_folder = folder_name
    dt = self.final.new_tag('dt')
    dt.preserve_whitespace_tags.add('dt')
    h3 = self.final.new_tag('h3')
    h3.preserve_whitespace_tags.add('h3')
    h3.string = folder_name
    dl = self.final.new_tag('dl')
    dt.append(h3)
    self.final.dl.append(dt)
    self.final.dl.append(dl)


  def add_bookmark(self, title, url, favicon):
    """ Add a bookmmark to our current folder in our HTML object."""
    dt = self.final.new_tag('dt')
    dt.preserve_whitespace_tags.add('dt')
    if favicon is not None:
      icon = favicon
    else:
      icon = '' if self.no_icons else self._find_favicon(url)
    a = self.final.new_tag('a', href=url, icon_uri=icon)
    a.preserve_whitespace_tags.add('a')
    a.string = title
    dt.append(a)
    self.final.find_all('dl')[-1].append(dt)


  def print(self):
    return self.final.prettify()


  def _find_favicon(self, url):
    """
    Fetches the website to see if it can find a favicon.
    Ended up too complex and with too many requests, this is not necessary
    WIP
    """
    u = urlsplit(url)
    fqdn = f"{u.scheme}://{u.netloc}/"
    fqdn_hash = myhash(fqdn)
    if fqdn_hash in self.fqdn_hashmap:
      print(f"  [*] Found cached icon for {fqdn}")
      return self.fqdn_hashmap[fqdn_hash]

    try:
      site = requests.get(fqdn, timeout=5)
    except requests.exceptions.RequestException as e:
      print(f'  [!] Failed to fetch URL: {e} ({fqdn})')
      return urljoin(fqdn, '/favicon.ico')

    if site.status_code != 200:
      print(f'  [!] Website returned status code {site.status_code} ({fqdn})')
      return urljoin(fqdn, '/favicon.ico')


    soup = BeautifulSoup(site.text, 'html.parser')
    icon = soup.find('link', rel='icon')
    if icon:
      icon_url = urljoin(fqdn, icon['href'])
      try:
        icon_site = requests.get(icon_url, timeout=5)

        if icon_site.status_code == 200:
          print(f"  [*] Found icon for {fqdn}: {icon_url}")
          self.fqdn_hashmap[myhash(fqdn)] = icon_url
          return icon_url
      except requests.exceptions.RequestException as e:
        pass

    try:
      site_favicon = requests.get(urljoin(fqdn, '/favicon.ico'), timeout=5)

      if site_favicon.status_code == 200:
        icon_url = urljoin(fqdn, '/favicon.ico')
        self.fqdn_hashmap[myhash(fqdn)] = icon_url
        return icon_url
    except requests.exceptions.RequestException as e:
      pass

    print(f'  [!] No icon found for {fqdn}, using default ({fqdn})')
    return urljoin(fqdn, '/favicon.ico')


def get_links(url):
  """
  Fetch the arc.net/folder page, grab the HTML,
  and return only what we are intersted in (folders and bookmarks)
  """
  response = requests.get(url)

  if response.status_code != 200:
    print(f'Failed to fetch URL: {url} - Status Code: {response.status_code}')
  soup = BeautifulSoup(response.text, 'html.parser')
  try:
    # TODO: This select query might break in the future.
    container = soup.select('body > div#__next > div > div > div > div:nth-child(2)')[0]
  except IndexError:
    print(f'Failed to find container in URL: {url}')
    return []

  # className = "." + ".".join(container['class'])
  base = container['class'][0]
  className = f'.{base}[class*="{base}-"][href="#"], a.{base}[class*="{base}-"]'
  return container.select(className)


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
      favicon = link.select('img')[0].get('src') if link.select('img') else None
      print(f"[*] Processing bookmark: \"{bookmark_title}\"")
      try:
        bookmark_url = link['href']
      except KeyError:
        print(f"   [!] Bookmark {bookmark_title} doesn't have a URL, skipping...")
        continue

      builder.add_bookmark(bookmark_title, bookmark_url, favicon)
    else:
      print(f'Unknown element: {link}')

def parse_args():
  parser = argparse.ArgumentParser(description='Export Arc bookmarks to HTML format')
  parser.add_argument('url', type=str, help='URL to the Arc.net folder')
  parser.add_argument('-n', '--no-icons', action='store_true', help='Skip fetching favicon icons')
  # parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
  args = parser.parse_args()

  url = args.url
  return url, args

def main():
  # if len(argv) < 2 or len(argv) > 3:
  #   print(f"Usage:\n\tpython3 {argv[0]} <url to arc.net/folder> [--no-icons]")
  #   exit(1)
  # url = argv[1]
  # fetch_icons = False if '--no-icons' in argv else True
  url, options = parse_args()

  links = get_links(url)
  builder = BookmarkBuilder(options.no_icons)

  tot_folders = [l.name == 'div' for l in links].count(True)
  tot_bookmarks = [l.name == 'a' for l in links].count(True)
  print(f"[*] Found {tot_folders} folders and {tot_bookmarks} bookmarks\n")

  parse(builder, links)

  with open('bookmarks.html', 'w', encoding='utf-8') as file:
    file.write(builder.print())
  print('\n\n[*] Finished! Bookmarks saved to bookmarks.html')


if __name__ == "__main__":
  main()
