import requests,bs4,json,re,time,pathlib
p=pathlib.Path("emoji_audit");p.mkdir(exist_ok=True)
s=requests.Session();s.headers["User-Agent"]="Mozilla/5.0 Chrome/125 Safari/537.36"
rows={}; b=None; stats=[]
for n in range(60):
 u="https://t.me/s/nonsenses368"+(f"?before={b}" if b is not None else "")
 try:
  r=s.get(u,timeout=30);r.raise_for_status()
 except Exception as e: print("ERROR",e);break
 soup=bs4.BeautifulSoup(r.text,"html.parser"); nodes=soup.select(".tgme_widget_message[data-post]")
 if not nodes:break
 ids=[]
 for node in nodes:
  try: pid=int(node["data-post"].split("/")[-1])
  except:continue
  ids.append(pid)
  if pid in rows:continue
  elem=node.select_one(".tgme_widget_message_text")
  custom=[]
  for e in node.select("tg-emoji, [emoji-id], [data-document-id], [data-emoji-id]"):
   custom.append({"attrs":dict(e.attrs),"text":e.get_text(" ",strip=True),"html":str(e)[:5000]})
  rows[pid]={"id":pid,"source":f"https://t.me/nonsenses368/{pid}","date":(node.select_one("time").get("datetime","") if node.select_one("time") else ""),"text":elem.get_text(" ",strip=True) if elem else "","text_html":str(elem) if elem else "","custom_emoji":custom}
 old=min(ids);stats.append({"before":b,"oldest":old,"posts":len(nodes)})
 print("PAGE",n,"total",len(rows),"emoji tags",sum(len(v["custom_emoji"]) for v in rows.values()),flush=True)
 if old<=1 or b is not None and old>=b:break
 b=old;time.sleep(.3)
(p/"emoji_metadata.json").write_text(json.dumps([rows[k] for k in sorted(rows)],ensure_ascii=False,indent=2))
(p/"summary.json").write_text(json.dumps({"posts":len(rows),"pages":len(stats),"custom_emoji_posts":sum(bool(v["custom_emoji"]) for v in rows.values()),"custom_emoji_occurrences":sum(len(v["custom_emoji"]) for v in rows.values()),"pages_audited":stats},ensure_ascii=False,indent=2))
print("SUMMARY",json.dumps({"posts":len(rows),"emoji_occurrences":sum(len(v["custom_emoji"]) for v in rows.values())}))
