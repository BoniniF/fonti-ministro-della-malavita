import re, json, hashlib, requests, urllib.parse, sys
UA='curl/8.23.0'
s=requests.Session(); s.verify=False; s.headers.update({'User-Agent':UA})
def solve(html, redir):
    ch=json.loads(re.search(r'id="anubis_challenge"[^>]*>(.*?)</script>', html, re.S).group(1))
    ver=json.loads(re.search(r'id="anubis_version"[^>]*>(.*?)</script>', html, re.S).group(1))
    base=json.loads(re.search(r'id="anubis_base_prefix"[^>]*>(.*?)</script>', html, re.S).group(1))
    if not base:
        from urllib.parse import urlparse
        p=urlparse(redir)
        base=f'{p.scheme}://{p.netloc}'
    data=ch['challenge']['randomData']; diff=ch['rules']['difficulty']; cid=ch['challenge']['id']
    nonce=0
    while True:
        h=hashlib.sha256((data+str(nonce)).encode()).hexdigest()
        if h.startswith('0'*diff): break
        nonce+=1
    u=(base.rstrip('/')+'/.within.website/x/cmd/anubis/api/pass-challenge?'+urllib.parse.urlencode(
        {'id':cid,'response':h,'nonce':nonce,'redir':redir,'elapsedTime':'4200'}))
    r=s.get(u, allow_redirects=False)
    print("pass-challenge:", r.status_code, dict(s.cookies), file=sys.stderr)
    return s
def get(url, depth=0):
    r=s.get(url, allow_redirects=True)
    if 'anubis_challenge' in r.text and depth<5:
        solve(r.text, url)
        r=s.get(url, allow_redirects=True)
    return r
