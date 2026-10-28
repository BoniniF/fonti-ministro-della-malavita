import re, requests, urllib3, json, sys
urllib3.disable_warnings()
BASE='https://avanti.senato.it'
s = requests.Session(); s.verify=False
s.headers.update({'User-Agent':'Mozilla/5.0'})
TOK=None
def token():
    global TOK
    if TOK is None:
        h=s.get(BASE+'/controller.php?page=ricerca').text
        TOK=re.search(r'name="csrftoken"\s+value="([^"]*)"', h).group(1)
    return TOK
def solr(term, y1, y2, offset=0, d1='01', m1='01', d2='31', m2='12'):
    u=(BASE+f'/controller.php?page=result_solr&csrftoken={token()}&term_search={term}'
       f'&day_start={d1}&month_start={m1}&year_start={y1}&day_end={d2}&month_end={m2}&year_end={y2}&issue=&start_search={offset}&sort=Title_search%20asc')
    return s.get(u, timeout=120).text
def parse_results(html):
    out=[]
    for blk in re.split(r'<div class="result_element">', html)[1:]:
        pd=re.search(r'viewer\.html\?file=([^"]+\.PDF)(?:#search=[^"]*)?', blk)
        ti=re.search(r'n\.\s*(\d+)\s+del\s+(\d\d/\d\d/\d{4})', blk)
        ed=re.search(r'<div style="font-style: italic;">([^<]+)</div>', blk)
        pg=re.search(r'#search=[^"]*&page=(\d+)', blk)
        if pd and ti:
            out.append({'issue':ti.group(1),'date':ti.group(2),'edition':(ed.group(1).strip() if ed else ''),
                        'page':(pg.group(1) if pg else ''),'pdf':pd.group(1)})
    tot=re.search(r'di\s+(\d+)', html)
    return out,(int(tot.group(1)) if tot else None)
def collect(term, y1, y2, d1='01', m1='01', d2='31', m2='12'):
    results=[]; off=0; total=None
    while True:
        h=solr(term,y1,y2,off,d1,m1,d2,m2)
        got,total=parse_results(h)
        if not got: break
        results+=got; off+=10
        if total is not None and off>=int(total): break
    return results,(total or len(results))
