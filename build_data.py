"""花蓮縣健保特約牙醫診所資料整理。
用法：python3 build_data.py <工作資料夾> <輸出資料夾>
工作資料夾需有 dl/nhi_clinic.csv（健保署「健保特約醫事機構-診所」）。
道路位置與門牌查詢結果會快取在 dl/，更新資料時請修改下方 TODAY。
"""
import csv, json, math, re, sys, time, unicodedata, collections, urllib.request, urllib.parse, os
S = sys.argv[1]; OUT = sys.argv[2]; TODAY='20261127'
UA={'User-Agent':'map-data-script/1.0'}
CN='零一二三四五六七八九'
def cn(n):
    n=int(n); return CN[n] if n<10 else ('' if n//10==1 else CN[n//10])+'十'+(CN[n%10] if n%10 else '')
def norm(s):
    s=unicodedata.normalize('NFKC',s).replace('臺','台').replace(' ','')
    s=re.sub(r'(\d+)(?=段|街)', lambda m: cn(m[1]), s)
    s=re.sub(r'[―─‐－–—-]','之',s)
    return re.sub(r'(\d+)號之(\d+)',r'\1之\2號',s)
def fetch(url, data=None, tries=3):
    for i in range(tries):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,data=data,headers=UA),timeout=90))
        except Exception as e:
            err=e; time.sleep(3*(i+1))
    raise err

rows=[]
for r in csv.DictReader(open(S+'/dl/nhi_clinic.csv',encoding='utf-8-sig')):
    end=r['終止合約或歇業日期'].strip()
    if r['地址'].startswith('花蓮縣') and '牙' in r['醫事機構種類'] and (not end or end>TODAY): rows.append(r)
towns=sorted({r['地址'][3:6] for r in rows})

# 各鄉鎮的道路位置（開放街圖）
rf=S+'/dl/hl_roads.json'
if not os.path.exists(rf):
    out={}
    for t in towns:
        q=f'[out:json][timeout:80];area["name"="花蓮縣"]["boundary"="administrative"]->.c;rel(area.c)["boundary"="administrative"]["name"="{t}"];map_to_area->.t;way(area.t)["highway"]["name"];out geom tags;'
        d=fetch('https://overpass-api.de/api/interpreter',urllib.parse.urlencode({'data':q}).encode(),tries=5)
        g=collections.defaultdict(list)
        for w in d['elements']: g[norm(w['tags']['name'])].append([[p['lon'],p['lat']] for p in w['geometry']])
        out[t]=g; print(t,len(g),flush=True); time.sleep(5)
    json.dump(out,open(rf,'w'),ensure_ascii=False)
roads=json.load(open(rf))

def parse(addr):
    s=norm(addr); t=s[3:6]; rest=s[6:]
    c=[r for r in roads.get(t,{}) if r in rest and not r.endswith(('巷','弄'))]
    if c:
        road=max(c,key=len)
    else:
        m=re.search(r'(?:[村里](?:\d+鄰)?)?([^\d村里鄰]{1,6}(?:路|街|大道)(?:[一二三四五]段)?)',rest)
        if not m: return t,None,None
        road=m[1]
    tail=rest[rest.index(road)+len(road):]
    m=re.match(r'((?:\d+巷)?(?:\d+弄)?)(\d+(?:之\d+)?)',tail)
    return (t,road,(m[1],m[2])) if m else (t,road,None)

def metres(a,b): return math.hypot((a[0]-b[0])*101700,(a[1]-b[1])*110900)
def samples(lines, step=130):
    pts=[]
    for ln in lines:
        for a,b in zip(ln,ln[1:]):
            n=max(1,int(metres(a,b)//40))
            for i in range(n+1):
                p=[a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n]
                if all(metres(p,q)>step for q in pts): pts.append(p)
    return pts

cf=S+'/dl/hl_nlsc.json'
cache=json.load(open(cf)) if os.path.exists(cf) else {}
ref={}   # (鄉鎮, 路) -> {(巷弄, 號): (lon,lat)}
def add(items, t, road):
    for x in items:
        a=norm(x.get('addr') or '')
        if t not in a or road not in a: continue
        i=a.index(road)
        if i and a[i-1] not in '鄉鎮市村里鄰]': continue
        m=re.match(r'((?:\d+巷)?(?:\d+弄)?)(\d+(?:之\d+)?)號',a[i+len(road):])
        if m: ref.setdefault((t,road),{}).setdefault((m[1],m[2]),(x['lon'],x['lat']))
def query(p):
    k=f'{p[0]:.4f}/{p[1]:.4f}'
    if k not in cache:
        cache[k]=fetch(f'https://api.nlsc.gov.tw/other/MarkBufferAnlys/bus/{k}/200'); time.sleep(.25)
    return cache[k]

res=[]; stat=collections.Counter()
for r in rows:
    t,road,key=parse(r['地址']); how='none'; xy=None
    lines=roads.get(t,{}).get(road) if road else None
    if lines and key:
        pts=samples(lines)
        for p in pts[:60]:
            add(query(p),t,road)
            if key in ref.get((t,road),{}): break
        got=ref.get((t,road),{})
        la,n=key; base=int(n.split('之')[0])
        if key in got: xy,how=got[key],'exact'
        else:
            same={k:v for k,v in got.items() if k[0]==la}
            main=[v for k,v in same.items() if k[1].split('之')[0]==str(base)]
            if main: xy,how=main[0],'main'
            else:
                c=sorted((abs(int(k[1].split('之')[0])-base),k[1],v) for k,v in same.items() if int(k[1].split('之')[0])%2==base%2)
                if c and c[0][0]<=8: xy,how=c[0][2],'near'
                elif pts:   # 只能放在道路上
                    xy,how=tuple(pts[len(pts)//2]),'road'
    stat[how]+=1
    hours=r['固定看診時段'].split('、')
    bits=''.join('1' if f'星期{d}{s}看診' in hours else '0' for s in ('上午','下午','晚上') for d in '一二三四五六日')
    res.append({'n':r['醫事機構名稱'],'a':r['地址'],'t':r['電話'],'d':t,'h':bits if any(hours) else '','m':r['備註'].strip().strip('-'),
                'p':[round(xy[0],6),round(xy[1],6)] if xy else None,'x':{'exact':0,'main':0,'near':1,'road':2}.get(how,2),'how':how})
    print(how, r['醫事機構名稱'], r['地址'], road, key, xy, flush=True)
    json.dump(cache,open(cf,'w'),ensure_ascii=False)
print(len(res),dict(stat))

# 自動比對不到、人工指定的鄰近門牌點位（地址改變時請一併檢查）
MANUAL = {
    '上九牙醫診所': [121.511258, 23.870643],   # 壽豐路一段 138 號
    '平安牙醫診所': [121.607058, 24.082807],   # 景美村加灣 129 號
}
for c in res:
    if c['how']=='road':
        t,road,key=parse(c['a']); 
        for items in cache.values(): add(items,t,road)
        got=ref.get((t,road),{}); la,n=key; base=int(n.split('之')[0])
        same=sorted((abs(int(k[1].split('之')[0])-base), int(k[1].split('之')[0])%2!=base%2, k[1], v) for k,v in got.items() if k[0]==la)
        print(c['n'],road,key,'candidates:',[(a[2],a[0]) for a in same[:4]])
        if same and same[0][0]<=40:
            c['p']=[round(same[0][3][0],6),round(same[0][3][1],6)]; c['how']='far' ; c['gap']=same[0][0]
    if c['n'] in MANUAL: c['p'] = MANUAL[c['n']]; c['how'] = 'near'
for c in res:
    # 位置精度：0 門牌相符；1 鄰近門牌推估；2 僅能確認在該道路一帶
    c['x']={'exact':0,'main':0,'near':1}.get(c['how'],2)
    if c['how']=='far' and c['gap']<=14: c['x']=1
import collections
print(collections.Counter(c['x'] for c in res), collections.Counter(c['how'] for c in res), sum(1 for c in res if c['p']))
near=[(c['p'],c['n']) for c in res]
d=collections.Counter(tuple(c['p']) for c in res); print('重疊點', {k:v for k,v in d.items() if v>1})
print([(c['n'],c.get('gap')) for c in res if c['x']==2])
res.sort(key=lambda c:(c['d']!='花蓮市',c['d']!='吉安鄉',c['d'],c['n']))
out={'updated':'2026-11-27','clinics':[{k:c[k] for k in ('n','a','t','d','h','m','p','x')} for c in res]}
D=OUT; os.makedirs(D,exist_ok=True)
json.dump(out,open(D+'/clinics.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print([(c['n'],c['a'],c['p'],c['x'],c['h']) for c in out['clinics'] if c['n']=='頂好牙醫診所'])
