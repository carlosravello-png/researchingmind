# Verificador aparte: SOLO LEE. Audita todo site/. Veredicto binario.
# Uso: python taller/verifica.py
import json, re, os, sys
from pathlib import Path
SITE = Path(__file__).resolve().parent.parent / "site"
DIC = (Path(__file__).resolve().parent.parent / "expediente" / "entidades_wikidata.md").read_text(encoding="utf-8")
Q_OK = set(re.findall(r"\| (Q\d+) \|[^\n]*\| verificado \|", DIC))
D = "https://researchingmind.com/"
RE_LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

def sin_duplicadas(pairs):
    d = {}
    for k, v in pairs:
        if k in d: raise ValueError("clave duplicada: " + k)
        d[k] = v
    return d

malos = {k: [] for k in ["no_cierra_html", "bytes_nul", "ld_roto", "claves_duplicadas", "canonical", "hreflang_no_reciproco",
                         "enlace_roto", "q_sin_diccionario", "licencia_capas", "itemlist_vs_grid", "sin_breadcrumb", "fecha"]}
paginas = sorted(p for p in SITE.rglob("*.html"))
info = {}
for p in paginas:
    rel = p.relative_to(SITE).as_posix(); b = p.read_bytes(); s = b.decode("utf-8")
    if not s.rstrip().endswith("</html>"): malos["no_cierra_html"].append(rel)
    if b"\x00" in b: malos["bytes_nul"].append(rel)
    blocks = RE_LD.findall(s); graph = []
    for blk in blocks:
        try:
            obj = json.loads(blk, object_pairs_hook=sin_duplicadas); graph += obj.get("@graph", [obj])
        except ValueError as e:
            (malos["claves_duplicadas"] if "duplicada" in str(e) else malos["ld_roto"]).append(f"{rel}: {e}")
    if rel == "404.html":
        if 'content="noindex"' not in s: malos["canonical"].append("404 sin noindex")
        continue
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
    limpio = rel[:-5] if rel.endswith(".html") else rel
    esperado = D + ("" if limpio == "index" else limpio)
    if canon != esperado: malos["canonical"].append(f"{rel}: {canon}")
    hl = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', s))
    info[rel] = (canon, hl)
    # enlaces internos
    # Cloudflare Pages: /x sirve x.html; un enlace interno con .html provoca un 308 y cuenta como fallo
    for h in re.findall(r'(?:href|src)="([^"#:]*)(?:#[^"]*)?"', s):
        if h == "": continue
        if not h.startswith("/"): malos["enlace_roto"].append(f"{rel} -> {h} (relativo)"); continue
        if h.endswith(".html"): malos["enlace_roto"].append(f"{rel} -> {h} (con .html: redirige)"); continue
        base = SITE / h.lstrip("/")
        cands = [base / "index.html"] if h.endswith("/") else [base, base.with_name(base.name + ".html")]
        if not any(c.is_file() for c in cands): malos["enlace_roto"].append(f"{rel} -> {h}")
    for u in re.findall(r'https://researchingmind\.com/[^"\s<]*', s):
        if u.split("#")[0].endswith(".html"): malos["enlace_roto"].append(f"{rel}: URL absoluta con .html {u}")
    # Q-IDs solo del diccionario
    for q in set(re.findall(r"wikidata\.org/wiki/(Q\d+)", s)):
        if q not in Q_OK: malos["q_sin_diccionario"].append(f"{rel}: {q}")
    # licencia en tres capas: head + pie con rel=license + JSON-LD
    head_ok = re.search(r'<link rel="license" href="https://researchingmind\.com/licencia-(es|en)">', s)
    pie_ok = re.search(r'<p class="rights license-notice">.*?<a rel="license" href="/licencia-(es|en)"', s, re.S)
    ld_ok = any(n.get("license", "").startswith(D + "licencia-") for n in graph if n.get("@type") in ("WebSite",))
    if not (head_ok and pie_ok and ld_ok): malos["licencia_capas"].append(f"{rel}: head={bool(head_ok)} pie={bool(pie_ok)} ld={ld_ok}")
    # grid visible == ItemList
    cards = len(re.findall(r'<article class="card">', s))
    il = [n for n in graph if n.get("@type") == "ItemList"]
    if cards and (not il or len(il[0]["itemListElement"]) != cards): malos["itemlist_vs_grid"].append(f"{rel}: grid={cards} itemlist={[len(x['itemListElement']) for x in il]}")
    if rel not in ("index.html", "index-en.html") and not any(n.get("@type") == "BreadcrumbList" for n in graph): malos["sin_breadcrumb"].append(rel)
    for n in graph:
        if n.get("@type") == "BlogPosting":
            visible = re.search(r'<p class="byline">.*?<time datetime="([^"]+)"', s, re.S)
            og = re.search(r'article:published_time" content="([^"]+)"', s)
            if not visible or n.get("datePublished") != visible.group(1) or not og or og.group(1) != visible.group(1):
                malos["fecha"].append(rel)
    info[rel] += ([n.get("@type") for n in graph],)

# Barrido del repo entero: ningun rastro de la universidad del autor (terminos en hex para no escribirlos)
PROHIBIDO = [bytes.fromhex(h).decode() for h in ("756376", "76616c6c656a6f", "636c656d656e74696e61", "7472696c6365", "726762713535")]
RAIZ = SITE.parent
malos["institucion_prohibida"] = []
for f in RAIZ.rglob("*"):
    if ".git" in f.parts or not f.is_file(): continue
    nombre = f.relative_to(RAIZ).as_posix()
    if any(t in nombre.lower() for t in PROHIBIDO): malos["institucion_prohibida"].append("nombre: " + nombre)
    try: txt = f.read_text(encoding="utf-8").lower()
    except (UnicodeDecodeError, OSError): continue
    for t in PROHIBIDO:
        if re.search(r"(?<![a-z])" + t + r"(?![a-z])", txt): malos["institucion_prohibida"].append(nombre)

urls = {v[0]: k for k, v in info.items()}
for rel, (canon, hl, _) in info.items():
    if set(hl) != {"es", "en", "x-default"}: malos["hreflang_no_reciproco"].append(f"{rel}: {sorted(hl)}")
    for lang, u in hl.items():
        if u not in urls or canon not in info[urls[u]][1].values(): malos["hreflang_no_reciproco"].append(f"{rel} <-> {u}")

print("LO QUE HAY")
for rel, (_, _, tipos) in info.items(): print(f"  {rel:48s} {', '.join(map(str, tipos))}")
print("LO QUE NO PODIA ROMPERSE (todo = 0)")
total = 0
for k, v in malos.items():
    print(f"  {k:24s}: {len(v)}"); total += len(v)
    for x in v[:5]: print("      ", x)
print("LO PROMETIDO")
s_all = "".join(p.read_text(encoding="utf-8") for p in paginas)
print(f"  Q en el diccionario verificados : {len(Q_OK)}")
print(f"  enlaces a orcid.org             : {s_all.count('orcid.org/0009-0007-5631-7436')}")
print(f"  @id de persona canonico         : {s_all.count('https://carlosravello.com/#person')}")
print(f"  Q139714842 (borrado) en el sitio: {s_all.count('Q139714842')}")
print("\nTODO OK — se puede publicar" if total == 0 and "Q139714842" not in s_all else "\nHAY QUE REVISAR — NO PUBLICAR")
