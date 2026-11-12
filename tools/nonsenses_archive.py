import requests, bs4, re, json, time, pathlib, hashlib, html, zipfile, mimetypes
from urllib.parse import urlsplit
BASE="https://t.me/s/nonsenses368"
root=pathlib.Path("NONSenses");media=root/"media";media.mkdir(parents=True,exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
def fetch(u):
 for a in range(3):
  try:
   r=s.get(u,timeout=35);r.raise_for_status();return r
  except Exception as ex:
   print("FETCH ERROR",str(ex)[:140],flush=True);time.sleep(2+a*3)
 return None
posts={};before=None;visited=set();errors=[]
for n in range(110):
 url=BASE+(f"?before={before}" if before is not None else "")
 r=fetch(url)
 if r is None:errors.append("page "+url);break
 soup=bs4.BeautifulSoup(r.text,"html.parser")
 nodes=soup.select(".tgme_widget_message[data-post]")
 ids=[]
 for node in nodes:
  try:pid=int(node["data-post"].split("/")[-1])
  except:continue
  ids.append(pid)
  if pid in posts:continue
  text=node.select_one(".tgme_widget_message_text")
  tm=node.select_one("time")
  urls=[]
  for el in [node]+node.find_all(True):
   style=el.get("style","")
   urls += re.findall(r"url\\(['\\\"]?(https?[^)\\'\\\"]+)",style)
   for attr in ["src","poster","data-src"]:
    v=el.get(attr,"")
    if v.startswith("//"):v="https:"+v
    if v.startswith("http"):urls.append(v)
  urls=list(dict.fromkeys(html.unescape(x) for x in urls if "telesco.pe" in x or "t.me/i/" in x or "telegram.org/file/" in x))
  posts[pid]={"id":pid,"url":f"https://t.me/nonsenses368/{pid}","date":tm.get("datetime","") if tm else "","text":text.get_text(" ",strip=True) if text else "","media_urls":urls,"media":[]}
 if not ids:errors.append("No posts at "+url);break
 nxt=min(ids)
 print("PAGE",n+1,"POSTS",len(nodes),"TOTAL",len(posts),"OLDEST",nxt,flush=True)
 if nxt<=1 or nxt in visited or before is not None and nxt>=before:break
 before=nxt;visited.add(nxt);time.sleep(0.7)
for i,p in sorted(posts.items()):
 for j,u in enumerate(p["media_urls"]):
  r=fetch(u)
  if r is None or "text/html" in r.headers.get("content-type",""):errors.append("media "+str(i)+" "+u);continue
  ext=pathlib.Path(urlsplit(u).path).suffix.lower()
  if ext not in (".jpg",".jpeg",".png",".webp",".gif",".mp4",".mov",".webm",".ogg"):ext=mimetypes.guess_extension(r.headers.get("content-type","").split(";")[0]) or ".bin"
  name=f"{i:04}_{j:02}_{hashlib.sha256(u.encode()).hexdigest()[:8]}{ext}"
  (media/name).write_bytes(r.content)
  p["media"].append({"file":"media/"+name,"bytes":len(r.content),"mime":r.headers.get("content-type","")})
 print("POST",i,"MEDIA",len(p["media"]),"EXPECTED",len(p["media_urls"]),flush=True)
 time.sleep(.15)
(root/"posts.json").write_text(json.dumps(list(dict(sorted(posts.items())).values()),ensure_ascii=False,indent=2))
(root/"errors.json").write_text(json.dumps(errors,ensure_ascii=False,indent=2))
parts=['<!doctype html><html lang="uk"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{background:#111;color:#eee;max-width:780px;margin:auto;font:16px system-ui;padding:22px}article{padding:22px 0;border-bottom:1px solid #444}img,video{max-width:100%;display:block;margin:15px 0}a{color:#bcaeff}</style><h1>NONSenses reader archive</h1><p>Public preview only; original media may be missing.</p>']
for i,p in sorted(posts.items()):
 parts.append('<article><small>#'+str(i)+' | '+html.escape(p["date"])+' | <a href="'+p["url"]+'">Original</a></small><p>'+html.escape(p["text"])+'</p>')
 for m in p["media"]:
  path=html.escape(m["file"],quote=True)
  parts.append('<video controls src="'+path+'"></video>' if "video" in m["mime"] or path.endswith((".mp4",".webm")) else '<img loading="lazy" src="'+path+'">')
 if len(p["media"])<len(p["media_urls"]):parts.append('<p>Some media unavailable</p>')
 parts.append('</article>')
parts.append('</html>')
(root/"reader.html").write_text("\n".join(parts))
(root/"README.txt").write_text("Best-effort public Telegram preview archive. NOT a full native Telegram export. Open reader.html to browse.")
with zipfile.ZipFile("NONSenses_public_archive.zip","w",zipfile.ZIP_DEFLATED) as z:
 for f in root.rglob("*"):
  if f.is_file():z.write(f,f.as_posix())
print("SUMMARY",json.dumps({"posts":len(posts),"media_downloaded":sum(len(p["media"]) for p in posts.values()),"media_references":sum(len(p["media_urls"]) for p in posts.values()),"errors":len(errors)}))
