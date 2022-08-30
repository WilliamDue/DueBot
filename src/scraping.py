from urllib.request import urlopen, HTTPError
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
            fp = urlopen(link + f'?page={n}')
        except HTTPError:
            break
        
        soup = BeautifulSoup(fp.read(), 'html.parser')
        fp.close()
        s = soup.find("div", {"class": "panel article aa_eQ"})
        blob += ' '.join([p.get_text() for p in s.find_all("p")]) + ' '
        
        n += 1
        
    return blob