# Import external library dependencies
import requests
from bs4 import BeautifulSoup
import re
# Required if sitemap_is_gzip == True
import os
import gzip
import glob

# Main script functions
def get_urls(url):
    # Extract URLs from XML by looking for <loc> tag contents.
    page = requests.get(url, timeout=15)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = [element.text for element in soup.findAll('loc')]
    return links

def get_all_urls(sitemap_url):
    # Loop over get_urls function for all XML pages.
    # Get list of .xml files
    urls = get_urls(sitemap_url)
    urls_not_gz = [u for u in urls if u[-3:] != '.gz']
    for i, url in enumerate((set(urls) - set(urls_not_gz))):
        if i == 0:
            print('Warning - ignoring the following gzip files:')
        print(url)
    urls = urls_not_gz
    sitemap_urls = []
    for i, url in enumerate(urls):
        links = get_urls(url)
        print('Searched through %s XML file(s)' % (i+1), end='\r')
        sitemap_urls += links
    return sitemap_urls

def get_gzip_urls(f_):
    # Extract URLs from gzip XML by looking for <loc> tag contents.
    f = gzip.open(f_)
    soup = BeautifulSoup(f.read(), 'html.parser')
    links = [item.text for item in soup.findAll('loc')]
    return links

def get_all_gzip_urls(sitemap_url):
    # Loop over get_gzip_urls function for all XML pages. Index XML page is assumed to be unzipped.
    # Get list of .xml.gz files
    urls = get_urls(sitemap_url)
    urls_gz = [u for u in urls if u[-3:] == '.gz']
    for i, url in enumerate((set(urls) - set(urls_gz))):
        if i == 0:
            print('Warning - ignoring the following non-gzip files:')
        print(url)
    urls = urls_gz
    # Download the sitemap files
    for i, url in enumerate(urls):
        filename = url.split('/')[-1]
        page = requests.get(url, timeout=15)
        with open('gzip-sitemaps/' + filename, 'wb') as f:
            f.write(page.content)
    # Extract urls from sitemap files
    sitemap_urls = []
    all_sitemaps = glob.glob('gzip-sitemaps/*.gz')
    for i, f_ in enumerate(all_sitemaps):
        links = get_gzip_urls(f_)
        print('Searched through %s XML file(s)' % (i+1), end='\r')
        sitemap_urls += links
    return sitemap_urls

def main():
    # Asking for global variables
    sitemap_url = input("Enter sitemap URL: ")
    sitemap_is_index_tmp = input("Does the URL point to other XML pages? (y/n) ")
    if "y" in sitemap_is_index_tmp.lower() or "1" in sitemap_is_index_tmp.lower():
        sitemap_is_index = True
    else:
        sitemap_is_index = False
    sitemap_is_gzip_tmp = input("Is the XML page in compressed format (gzip)? (y/n) ")
    if "y" in sitemap_is_gzip_tmp.lower() or "1" in sitemap_is_gzip_tmp.lower():
        sitemap_is_gzip = True
    else:
        sitemap_is_gzip = False
    should_get_titles_tmp = input("Do you want titles of the URLs (takes longer)? (y/n) ")
    if "y" in should_get_titles_tmp.lower() or "1" in should_get_titles_tmp.lower():
        should_get_titles = True
    else:
        should_get_titles = False
    print("===============")
    # If the XML files are not compressed
    if not sitemap_is_gzip:
        # If the XML sitemap is an index to other XML files
        if sitemap_is_index:
            sitemap_urls = get_all_urls(sitemap_url)
        # If the XML sitemap contains the page links directly
        if not sitemap_is_index:
            sitemap_urls = get_urls(sitemap_url)
    # If the XML files are compressed
    else:
        # Make a folder to hold gzip files
        if not os.path.exists('gzip-sitemaps'):
            os.makedirs('gzip-sitemaps')
        # If the XML sitemap is an index to other XML files
        if sitemap_is_index:
            sitemap_urls = get_all_gzip_urls(sitemap_url)
        # If the XML sitemap contains the page links directly
        if not sitemap_is_index:
            filename = sitemap_url.split('/')[-1]
            page = requests.get(sitemap_url, timeout=15)
            with open('gzip-sitemaps/' + filename, 'wb') as f:
                f.write(page.content)
            sitemap_urls = get_gzip_urls('gzip-sitemaps/' + filename)
    # Print the URLs to a file
    forbidden_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    print("\n===============")
    with open(f'{sitemap_url.replace("http://", "").replace("https://", "").translate({ord(x): "=" for x in forbidden_characters})}.txt', 'w', encoding='utf8') as f:
        for url in sitemap_urls:
            if should_get_titles == True:
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        match = re.compile(r'<title>(.*?)</title>', re.UNICODE).search(r.text)
                        if match:
                            f.write(match.group(1) + '\n' + url + '\n===============\n')
                            print(match.group(1) + '\n' + url + '\n===============')
                        else:
                            f.write('{No_Title}\n' + url + '\n===============\n')
                            print('{No_Title}\n' + url + '\n===============')
                    else:
                        f.write('Code ' + str(r.status_code) + '\n' + url + '\n===============\n')
                        print('Code ' + str(r.status_code) + '\n' + url + '\n===============')
                except:
                    f.write(url + '\n===============\n')
                    print(url + '\n===============')
            else:
                f.write(url + '\n')
                print(url)
    # Print the number of URLs found
    forbidden_characters = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    print(f'Found {len(sitemap_urls)} URLs in the sitemap and saved them to {sitemap_url.replace("http://", "").replace("https://", "").translate({ord(x): "=" for x in forbidden_characters})}.txt')


if __name__ == '__main__':
    main()
