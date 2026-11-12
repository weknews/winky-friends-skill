"""PubMed E-utilities 검색(키 없이 초당 3회 → 0.4초 간격). 사용: python3 pubmed.py 이름 "검색식" [개수] → 이름.json(제목·초록). NCBI E-utilities, 키 없음. 대본 근거(R-15) 찾기용"""
import json, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def get(u):
    time.sleep(0.4)
    with urllib.request.urlopen(u + "&tool=winky-friends", timeout=30) as r: return r.read()
name, term, n = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12
ids = json.loads(get(f"{E}/esearch.fcgi?db=pubmed&retmode=json&sort=relevance&retmax={n}&term={urllib.parse.quote(term)}"))["esearchresult"]["idlist"]
root = ET.fromstring(get(f"{E}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids)}")) if ids else None
out = []
for a in (root.findall(".//PubmedArticle") if root is not None else []):
    g = lambda p: (a.findtext(p) or "").strip()
    out.append({"pmid": g(".//PMID"), "title": "".join(a.find(".//ArticleTitle").itertext()), "journal": g(".//Journal/ISOAbbreviation"),
                "year": g(".//PubDate/Year") or g(".//PubDate/MedlineDate")[:4], "types": [t.text for t in a.findall(".//PublicationType")],
                "abstract": " ".join("".join(x.itertext()) for x in a.findall(".//AbstractText"))})
json.dump({"term": term, "results": out}, open(f"{name}.json", "w"), ensure_ascii=False, indent=1)
for r in out: print(f"- {r['pmid']} {r['year']} {r['journal']} | {r['title'][:150]} | {','.join(t for t in r['types'] if t in ('Meta-Analysis','Systematic Review','Randomized Controlled Trial','Review'))}")
