import urllib.request
from bs4 import BeautifulSoup


def get_literotica_text(link: str) -> str:
    
    begin0 = 'https://www.literotica.com/s/'
    begin1 = 'www.literotica.com/s/'
    link_begin0 = link[:len(begin0)]
    link_begin1 = link[:len(begin1)]
    
    if link_begin0 != begin0 and link_begin1 != begin1:
        return ''
    
    blob = ''
    n = 1
    
    while True:
        
        try:
            fp = urllib.request.urlopen(link + f'?page={n}')
        except urllib.error.HTTPError:
            break
        
        page_bytes = fp.read()
        fp.close()
        
        soup = BeautifulSoup(page_bytes, 'html.parser')
        s = soup.find("div", {"class": "panel article aa_eQ"})
        blob += ' '.join([p.get_text() for p in s.find_all("p")]) + ' '
        
        n += 1
        
    return blob