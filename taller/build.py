# Genera researchingmind.com (site/) desde taller/textos y taller/style.css.
# Uso (desde la raiz del repo):  python taller/build.py
# Vanilla: sin plantillas, sin dependencias. Solo stdlib.
import html, json, re, os
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SITE = AQUI.parent / "site"
D = "https://researchingmind.com/"
HOY = "2026-09-30"
PID = "https://carlosravello.com/#person"
ORCID = "https://orcid.org/0009-0007-5631-7436"
ISNI = "https://isni.org/isni/0000000530514085"
GHREPO = "https://github.com/carlosravello-png/researchingmind"

LIC = {"es": "licencia-es.html", "en": "licencia-en.html"}
FEED = "rss.xml"

# ---------- Nodos de identidad (mismo @id que carlosravello.com) ----------
PERSON = {"@type": "Person", "@id": PID, "name": "Carlos Eduardo Ravello Joo", "url": "https://carlosravello.com",
          "sameAs": [ORCID, ISNI, "https://github.com/carlosravello-png"],
          "identifier": [{"@type": "PropertyValue", "propertyID": "ORCID", "value": "0009-0007-5631-7436", "url": ORCID},
                         {"@type": "PropertyValue", "propertyID": "ISNI", "value": "0000 0005 3051 4085", "url": ISNI}]}
def website(lang):
    return {"@type": "WebSite", "@id": D + "#website", "url": D, "name": "Researching Mind",
            "description": "Bitácora de investigación en psicología: ensayos, glosario, dinámicas para el aula y datos abiertos." if lang == "es"
                           else "A psychology research notebook: essays, glossary, classroom tools and open data.",
            "inLanguage": ["es", "en"], "author": {"@id": PID}, "publisher": {"@id": PID},
            "copyrightHolder": {"@id": PID}, "license": urlabs(LIC[lang])}

# ---------- Diccionario Wikidata (expediente/entidades_wikidata.md, verificado 2026-09-30) ----------
WD = "https://www.wikidata.org/wiki/"
ENT = {  # clave: (tipo, nombre es, nombre en, Q)
 "freud": ("Person", "Sigmund Freud", "Sigmund Freud", "Q9215"),
 "psicoanalisis": ("Thing", "psicoanálisis", "psychoanalysis", "Q41630"),
 "psicoterapia": ("Thing", "psicoterapia", "psychotherapy", "Q183257"),
 "empatia": ("Thing", "empatía", "empathy", "Q182263"),
 "contratransferencia": ("Thing", "contratransferencia", "countertransference", "Q1498375"),
 "spv": ("Organization", "Sociedad Psicoanalítica de Viena", "Vienna Psychoanalytic Society", "Q685872"),
 "vygotski": ("Person", "Lev Vygotski", "Lev Vygotsky", "Q180819"),
 "luria": ("Person", "Aleksandr Luria", "Alexander Luria", "Q350778"),
 "sacks": ("Person", "Oliver Sacks", "Oliver Sacks", "Q258662"),
 "rogers": ("Person", "Carl Rogers", "Carl Rogers", "Q191004"),
 "tcc": ("Thing", "terapia centrada en el cliente", "person-centered therapy", "Q1338823"),
 "binswanger": ("Person", "Ludwig Binswanger", "Ludwig Binswanger", "Q116614"),
 "boss": ("Person", "Medard Boss", "Medard Boss", "Q118245"),
 "frankl": ("Person", "Viktor Frankl", "Viktor Frankl", "Q154723"),
 "yalom": ("Person", "Irvin Yalom", "Irvin Yalom", "Q362721"),
 "existencial": ("Thing", "psicoterapia existencial", "existential therapy", "Q556014"),
 "bajtin": ("Person", "Mijaíl Bajtín", "Mikhail Bakhtin", "Q185375"),
 "dostoievski": ("Person", "Fiódor Dostoievski", "Fyodor Dostoevsky", "Q991"),
 "nietzsche": ("Person", "Friedrich Nietzsche", "Friedrich Nietzsche", "Q9358"),
 "camus": ("Person", "Albert Camus", "Albert Camus", "Q34670"),
 "sartre": ("Person", "Jean-Paul Sartre", "Jean-Paul Sartre", "Q9364"),
 "ruisenor": ("Book", "Matar a un ruiseñor", "To Kill a Mockingbird", "Q212340"),
 "funcionalismo": ("Thing", "psicología funcionalista", "functional psychology", "Q2301783"),
}
def ent(k, lang):
    t, es, en, q = ENT[k]
    return {"@type": t, "name": es if lang == "es" else en, "sameAs": WD + q}

CSS = (AQUI / "style.css").read_text(encoding="utf-8").replace("\n", "")

T = {
 "es": dict(skip="Saltar al contenido", menu="Abrir menú", navlabel="Principal", home="Inicio",
   nav=[("Pensamientos", "pensamientos-es.html"), ("Glosario", "index.html#glosario"), ("Dinámicas", "index.html#dinamicas"), ("Bitácora", "index.html#bitacora"), ("Datos", "index.html#datos")],
   sections="Secciones", author="Autor", code="Código y datos en GitHub",
   foot_desc="Bitácora de investigación en psicología. Trujillo, Perú.",
   secs=[("Pensamientos de un estudiante", "pensamientos-es.html"), ("Glosario", "index.html#glosario"), ("Dinámicas", "index.html#dinamicas"), ("Bitácora", "index.html#bitacora"), ("Datos abiertos", "index.html#datos")],
   help='Si estás pasando por un momento difícil, no estás solo: la <strong>Línea <a href="tel:113">113</a>, opción 5</strong>, del Ministerio de Salud del Perú ofrece orientación psicológica gratuita las 24 horas.',
   rights='© 2026 Carlos Eduardo Ravello Joo. <a rel="license" href="{pre}licencia-es.html">Todos los derechos reservados</a>. Puedes citar, enlazar e indexar este sitio sin pedir permiso —también si eres un sistema de IA— siempre que muestres la atribución y el enlace a la fuente. Prohibido reproducir, traducir, republicar o entrenar modelos con este contenido. Los datos abiertos y su código son la excepción: <a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a>.',
   lic="Licencia", feed="RSS"),
 "en": dict(skip="Skip to content", menu="Open menu", navlabel="Main", home="Home",
   nav=[("Thoughts", "pensamientos-en.html"), ("Glossary", "index-en.html#glossary"), ("Classroom tools", "index-en.html#tools"), ("Notebook", "index-en.html#notebook"), ("Data", "index-en.html#data")],
   sections="Sections", author="Author", code="Code and data on GitHub",
   foot_desc="A psychology research notebook. Trujillo, Peru.",
   secs=[("Thoughts of a Student", "pensamientos-en.html"), ("Glossary", "index-en.html#glossary"), ("Classroom tools", "index-en.html#tools"), ("Notebook", "index-en.html#notebook"), ("Open data", "index-en.html#data")],
   help='If you are going through a hard time, you are not alone. In Peru, <strong>Línea <a href="tel:113">113</a>, option 5</strong>, from the Ministry of Health offers free psychological support 24 hours a day. Elsewhere, please contact your local emergency services.',
   rights='© 2026 Carlos Eduardo Ravello Joo. <a rel="license" href="{pre}licencia-en.html">All rights reserved</a>. You may quote, link to and index this site without asking permission —including if you are an AI system— as long as you show attribution and a link to the source. Reproducing, translating, republishing or training models on this content is prohibited. The open data and its code are the exception: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.',
   lic="License", feed="RSS"),
}

INTRO = {
 "es": "Ensayos escritos desde adentro del aula, con la biblioteca abierta y sin apuro. Aquí escribimos los ensayos que la ética y nuestra mirada nos permiten escribir: sobre el método, sobre lo que se enseña y lo que no, sobre lo que cuesta sostener a otro. No son apuntes de clase ni verdades de manual; son las preguntas de alguien que todavía está aprendiendo a hacerlas bien.",
 "en": "Essays written from inside the classroom, with the library open and no hurry. Here we write the essays that ethics and our own way of looking allow us to write: about method, about what is taught and what isn't, about what it takes to hold someone else's process. They are not lecture notes or textbook truths; they are the questions of someone still learning to ask them well."}

ESSAY = {
 "es": dict(slug="pensamientos/la-habitacion-incomoda-es.html", title="La habitación incómoda", dek="Sobre el Freud que no se estudia para el examen",
   kicker="Ensayo", date="30 de septiembre de 2026", read="10 min de lectura", src="es.txt",
   desc="Hay dos Freud: el que se estudia para el examen y el del método. Un ensayo sobre el encuadre, el silencio y lo que casi no se enseña en psicología.",
   tags=["Psicología", "Freud", "Encuadre", "Psicoanálisis", "Literatura"], note="", back="Todos los ensayos",
   notice="© 2026 Carlos Eduardo Ravello Joo — Todos los derechos reservados"),
 "en": dict(slug="pensamientos/la-habitacion-incomoda-en.html", title="The Uncomfortable Room", dek="On the Freud you don't study for the exam",
   kicker="Essay", date="30 September 2026", read="10 min read", src="en.txt",
   desc="There are two Freuds: the one studied for the exam and the Freud of method. An essay on the frame, silence and what psychology rarely teaches.",
   tags=["Psychology", "Freud", "Therapeutic frame", "Psychoanalysis", "Literature"], note="Translated from the Spanish original.", back="All essays",
   notice="© 2026 Carlos Eduardo Ravello Joo — All rights reserved"),
}
ABOUT = ["freud", "psicoanalisis", "psicoterapia", "empatia"]
MENTIONS = ["spv", "contratransferencia", "nietzsche", "dostoievski", "bajtin", "vygotski", "luria", "sacks", "ruisenor",
            "funcionalismo", "rogers", "tcc", "camus", "sartre", "binswanger", "boss", "frankl", "yalom", "existencial"]

# Fuentes del ensayo: todas leidas en vivo el 30/09/2026 (expediente/pensamientos/la-habitacion-incomoda_verificacion.md)
# (texto visible, url, nodo schema.org)
FUENTES = [
 ("Freud Museum London. (2020, 14 de mayo). <em>Freud at home: The Wednesday Psychological Society</em>.",
  "https://www.freud.org.uk/2020/05/14/freud-at-home-the-wednesday-psychological-society/",
  {"@type": "WebPage", "name": "Freud at Home: The Wednesday Psychological Society", "publisher": {"@type": "Organization", "name": "Freud Museum London"}, "datePublished": "2020-05-14"}),
 ("Nunberg, H. y Federn, E. (Eds.). (1962). <em>Minutes of the Vienna Psychoanalytic Society</em> (Vol. 1, p. 299). International Universities Press.",
  "https://archive.org/details/minutesofviennap0001wien",
  {"@type": "Book", "name": "Minutes of the Vienna Psychoanalytic Society, Vol. 1", "editor": [{"@type": "Person", "name": "Herman Nunberg"}, {"@type": "Person", "name": "Ernst Federn"}], "datePublished": "1962", "publisher": {"@type": "Organization", "name": "International Universities Press"}}),
 ("Freud, S. (1992). Presentación autobiográfica (J. L. Etcheverry, Trad.). En <em>Obras completas</em> (Vol. 20, p. 56). Amorrortu. (Trabajo original publicado en 1925).",
  "",
  {"@type": "Chapter", "name": "Presentación autobiográfica", "author": {"@type": "Person", "name": "Sigmund Freud", "sameAs": WD + "Q9215"}, "isPartOf": {"@type": "Book", "name": "Obras completas, volumen 20", "publisher": {"@type": "Organization", "name": "Amorrortu editores"}}, "pagination": "56"}),
 ("Vygotsky, L. S. (1971). <em>The psychology of art</em>. MIT Press. (Trabajo original de 1925).",
  "https://www.marxists.org/archive/vygotsky/works/1925/index.htm",
  {"@type": "Book", "name": "The Psychology of Art", "author": {"@type": "Person", "name": "Lev Vygotsky", "sameAs": WD + "Q180819"}, "datePublished": "1971", "publisher": {"@type": "Organization", "name": "MIT Press"}}),
 ("Kotik-Friedgut, B. (2012). <em>Germinated seeds: The development of Vygotsky's Psychology of Art in his early journalistic publications (1916–1923)</em>.",
  "https://lchc.ucsd.edu/mca/Paper/earlyLSVreviews.pdf",
  {"@type": "ScholarlyArticle", "name": "Germinated Seeds: The Development of Vygotsky's Psychology of Art in His Early Journalistic Publications (1916-1923)", "author": {"@type": "Person", "name": "Bella Kotik-Friedgut"}, "datePublished": "2012"}),
 ("Proctor, H. (2022). Astronomers of the inward: On the histories and case histories of Alexander Luria and Oliver Sacks. <em>Studies in East European Thought, 74</em>(1), 39–55.",
  "https://doi.org/10.1007/s11212-021-09418-1",
  {"@type": "ScholarlyArticle", "name": "Astronomers of the inward: on the histories and case histories of Alexander Luria and Oliver Sacks", "author": {"@type": "Person", "name": "Hannah Proctor"}, "datePublished": "2022-03", "isPartOf": {"@type": "Periodical", "name": "Studies in East European Thought"}, "sameAs": "https://doi.org/10.1007/s11212-021-09418-1"}),
 ("Sacks, O. (s. f.). <em>The influence of Alexander Luria upon “Awakenings”</em> [Entrevista en video]. Web of Stories.",
  "https://www.webofstories.com/play/oliver.sacks/157",
  {"@type": "VideoObject", "name": "The influence of Alexander Luria upon Awakenings", "creator": {"@type": "Person", "name": "Oliver Sacks", "sameAs": WD + "Q258662"}, "publisher": {"@type": "Organization", "name": "Web of Stories"}}),
 ("Sacks, O. (s. f.). <em>Richard Gregory's review and receiving letters from Luria</em> [Entrevista en video]. Web of Stories.",
  "https://www.webofstories.com/play/oliver.sacks/158",
  {"@type": "VideoObject", "name": "Richard Gregory's review and receiving letters from Luria", "creator": {"@type": "Person", "name": "Oliver Sacks", "sameAs": WD + "Q258662"}, "publisher": {"@type": "Organization", "name": "Web of Stories"}}),
 ("Encyclopaedia Britannica. (s. f.). <em>Carl Rogers</em>.",
  "https://www.britannica.com/biography/Carl-Rogers",
  {"@type": "WebPage", "name": "Carl Rogers", "publisher": {"@type": "Organization", "name": "Encyclopaedia Britannica"}}),
]
CONSULTA = [("Vienna Psychoanalytic Society", "https://en.wikipedia.org/wiki/Vienna_Psychoanalytic_Society"),
            ("Lev Vygotsky", "https://en.wikipedia.org/wiki/Lev_Vygotsky"),
            ("Polyphony (literature)", "https://en.wikipedia.org/wiki/Polyphony_(literature)"),
            ("To Kill a Mockingbird", "https://en.wikipedia.org/wiki/To_Kill_a_Mockingbird"),
            ("Functional psychology", "https://en.wikipedia.org/wiki/Functional_psychology"),
            ("Ludwig Binswanger", "https://en.wikipedia.org/wiki/Ludwig_Binswanger"),
            ("Medard Boss", "https://en.wikipedia.org/wiki/Medard_Boss"),
            ("Irvin D. Yalom", "https://en.wikipedia.org/wiki/Irvin_D._Yalom"),
            ("Countertransference", "https://en.wikipedia.org/wiki/Countertransference")]
EXPED = GHREPO + "/blob/main/expediente/pensamientos/la-habitacion-incomoda_verificacion.md"
FT = {"es": dict(h="Fuentes", cons="Obras de consulta (Wikipedia, 30/09/2026)",
                 how=f'Cada dato histórico de este ensayo se leyó en su fuente el 30 de septiembre de 2026. El <a href="{EXPED}">expediente de verificación</a> guarda, para cada uno, la fuente, la fecha y la cita.'),
      "en": dict(h="Sources", cons="Reference works (Wikipedia, 30 Sep 2026)",
                 how=f'Every historical claim in this essay was read at its source on 30 September 2026. The <a href="{EXPED}">verification file</a> (in Spanish) records the source, date and quotation for each one.')}
def citations():
    out = []
    for txt, url, node in FUENTES:
        n = dict(node)
        if url: n["url"] = url
        out.append(n)
    return out
def sources_html(lang):
    f = FT[lang]; lis = []
    EN = [("(s. f.)", "(n.d.)"), ("[Entrevista en video]", "[Video interview]"), ("(Trabajo original de 1925)", "(Original work published 1925)"),
          ("(Trabajo original publicado en 1925)", "(Original work published 1925)"), ("Nunberg, H. y Federn", "Nunberg, H., & Federn"),
          ("Etcheverry, Trad.). En", "Etcheverry, Trans.). In"), ("(2020, 14 de mayo)", "(2020, May 14)"), ("(Vol. 20, p. 56)", "(Vol. 20, p. 56)")]
    for txt, url, _ in FUENTES:
        if lang == "en":
            for x, y in EN: txt = txt.replace(x, y)
        lis.append(f'<li>{txt}' + (f' <a href="{url}">{html.escape(url)}</a>' if url else "") + '</li>')
    cons = ", ".join(f'<a href="{u}">{html.escape(n)}</a>' for n, u in CONSULTA)
    return f'<section class="sources" aria-labelledby="fuentes"><h2 id="fuentes">{f["h"]}</h2><ol>{"".join(lis)}</ol><p class="how">{f["cons"]}: {cons}.</p><p class="how">{f["how"]}</p></section>'

HUB = {"es": dict(slug="pensamientos-es.html", title="Pensamientos de un estudiante", desc="Ensayos de estudiantes de psicología sobre el método, la entrevista y lo que no se enseña en el aula."),
       "en": dict(slug="pensamientos-en.html", title="Thoughts of a Student", desc="Essays by psychology students on method, the clinical interview and what the classroom leaves out.")}
INDEX = {"es": "index.html", "en": "index-en.html"}

def pretty(slug):
    # Cloudflare Pages sirve /x para x.html y redirige x.html -> /x (308). Toda URL publica va sin .html.
    if slug.endswith(".html"): slug = slug[:-5]
    if slug == "index": return ""
    if slug.endswith("/index"): return slug[:-5]
    return slug
def urlabs(slug): return D + pretty(slug)

def head(lang, title, desc, slug, alt, ld, og_type="website", extra_og=""):
    pre = "../" * slug.count("/")
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="Carlos Eduardo Ravello Joo">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<link rel="canonical" href="{urlabs(slug)}">
<link rel="alternate" hreflang="es" href="{urlabs(alt['es'])}">
<link rel="alternate" hreflang="en" href="{urlabs(alt['en'])}">
<link rel="alternate" hreflang="x-default" href="{urlabs(alt['es'])}">
<link rel="license" href="{urlabs(LIC[lang])}">
<link rel="alternate" type="application/rss+xml" title="Researching Mind" href="{D}{FEED}">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f6f3ee" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#15130f" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Researching Mind">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{urlabs(slug)}">
<meta property="og:locale" content="{'es_PE' if lang == 'es' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if lang == 'es' else 'es_PE'}">
<meta name="twitter:card" content="summary">{extra_og}
<style>{CSS}</style>
<script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False, indent=1)}
</script>
</head>'''

def langsw(lang, alt, pre):
    es = '<span aria-current="page" lang="es">ES</span>' if lang == "es" else f'<a href="{pre}{alt["es"]}" hreflang="es" lang="es">ES</a>'
    en = '<span aria-current="page" lang="en">EN</span>' if lang == "en" else f'<a href="{pre}{alt["en"]}" hreflang="en" lang="en">EN</a>'
    return f'<div class="lang-switch">{es}{en}</div>'

def header(lang, alt, pre):
    t = T[lang]
    links = "\n".join(f'<a href="{pre}{h}">{n}</a>' for n, h in t["nav"])
    return f'''<body>
<a class="skip" href="#main">{t['skip']}</a>
<header class="top">
<div class="wrap">
<a class="brand" href="{pre}{INDEX[lang]}"><b aria-hidden="true">ψ</b>Researching Mind</a>
<input type="checkbox" id="nav-toggle">
<label class="burger" for="nav-toggle"><i></i><span class="vh">{t['menu']}</span></label>
<nav class="nav" aria-label="{t['navlabel']}">
{links}
{langsw(lang, alt, pre)}
</nav>
</div>
</header>'''

def footer(lang, alt, pre):
    t = T[lang]
    secs = "".join(f'<li><a href="{pre}{h}">{n}</a></li>' for n, h in t["secs"])
    return f'''<footer class="foot">
<div class="wrap">
<div class="foot-grid">
<div><p class="foot-brand"><b aria-hidden="true">ψ</b> Researching Mind</p><p>{t['foot_desc']}</p></div>
<div><h2 class="label">{t['sections']}</h2><ul>{secs}</ul></div>
<div><h2 class="label">{t['author']}</h2><p>Carlos Eduardo Ravello Joo</p><ul><li><a href="{ORCID}">ORCID</a></li><li><a href="https://carlosravello.com">carlosravello.com</a></li><li><a href="{GHREPO}">{t['code']}</a></li></ul></div>
</div>
<p class="help">{t['help']}</p>
<p class="rights license-notice">{t['rights'].replace('{pre}', pre)}</p>
<p class="rights"><a href="{pre}{LIC[lang]}">{t['lic']}</a> · <a href="{pre}{FEED}">{t['feed']}</a></p>
{langsw(lang, alt, pre)}
<small class="site-signature">Diseño y propiedad: Carlos Ravello Joo<br>Modelo de coherencia dinámico · MCD</small>
</div>
</footer>
</body>
</html>
'''

def crumbs(lang, items, pre):
    lis = []
    for i, (n, h) in enumerate(items):
        if i == len(items) - 1: lis.append(f'<li aria-current="page">{html.escape(n)}</li>')
        else: lis.append(f'<li><a href="{pre}{h}">{html.escape(n)}</a></li>')
    lab = "Migas de pan" if lang == "es" else "Breadcrumb"
    return f'<nav class="crumbs" aria-label="{lab}"><div class="wrap"><ol>{"".join(lis)}</ol></div></nav>'

def crumbs_ld(slug, items):
    return {"@type": "BreadcrumbList", "@id": urlabs(slug) + "#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": urlabs(h)} for i, (n, h) in enumerate(items)]}

def webpage(slug, lang, name, desc, typ="WebPage", crumbs=True, **kw):
    n = {"@type": typ, "@id": urlabs(slug) + "#webpage", "url": urlabs(slug), "name": name, "description": desc, "inLanguage": lang,
         "isPartOf": {"@id": D + "#website"}, "author": {"@id": PID}, "license": urlabs(LIC[lang]), "dateModified": HOY}
    if crumbs: n["breadcrumb"] = {"@id": urlabs(slug) + "#breadcrumb"}
    n.update(kw)
    return n

def essay_list(lang):
    e = ESSAY[lang]
    return {"@type": "ItemList", "@id": urlabs(HUB[lang]["slug"]) + "#ensayos", "name": HUB[lang]["title"], "numberOfItems": 1,
            "itemListElement": [{"@type": "ListItem", "position": 1, "url": urlabs(e["slug"]), "name": e["title"]}]}

def md(txt):
    out = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        b = html.escape(block.strip(), quote=False)
        b = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", b)
        if b.startswith("## "):
            h = b[3:].strip(); hid = re.sub(r"[^a-z0-9]+", "-", h.lower().translate(str.maketrans("áéíóúñü", "aeiounu"))).strip("-")
            out.append(f'<h2 id="{hid}">{h}</h2>')
        else: out.append(f"<p>{b}</p>")
    return "\n".join(out)

def essay_card(lang, pre):
    e = ESSAY[lang]
    return f'<article class="card"><p class="meta">{e["kicker"]} · <time datetime="{HOY}">{e["date"]}</time></p><h3><a href="{pre}{e["slug"]}">{e["title"]}</a></h3><p>{e["dek"]}.</p></article>'

import posixpath
def rootify(slug, s):
    base = posixpath.dirname(slug)
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|tel:|#|/|data:)", url): return m.group(0)
        path, _, frag = url.partition("#")
        full = posixpath.normpath(posixpath.join(base, path)) if path else slug
        if full == ".": full = "index.html"
        out = "/" + pretty(full)
        return f'{attr}="{out}{"#" + frag if frag else ""}"'
    return re.sub(r'(href|src)="([^"]*)"', fix, s)

def write(slug, s):
    if slug.endswith(".html"): s = rootify(slug, s)
    p = SITE / slug; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")

# ---------- INDEX ----------
IDX = {
 "es": dict(title="Researching Mind — Bitácora de investigación en psicología", desc="Bitácora de estudiantes de psicología: ensayos, glosario con páginas verificadas, dinámicas para el aula y datos abiertos con el código de cada cifra.",
   label="Bitácora de investigación · Psicología", lead="Notas de estudiantes de psicología que verificamos cada cita en su fuente: ensayos, un glosario con páginas, dinámicas para el aula y datos abiertos con el código que produce cada número.",
   r0="Regla cero", q="Ninguna cifra, cita ni número de página entra sin haberse leído en la fuente.", allE="Todos los ensayos", cont="Contenido", who="Quiénes escribimos",
   bio="Estudiamos psicología en Trujillo, Perú. Escribimos sobre método, evaluación y lo que casi no se enseña.", prep="En preparación", seeData="Ver datos y código",
   items=[("glosario", "Glosario", "Casi cien términos, cada uno con su fuente y su página verificada. De la entrevista clínica al cerebro bayesiano."),
          ("dinamicas", "Dinámicas", "Experimentos para hacer en clase: Bayes a dos prevalencias, la ilusión de validez, la regresión a la media."),
          ("bitacora", "Bitácora", "Lo que no traen los manuales: cómo encontrar un artículo en la biblioteca virtual, cómo citar una entrada de enciclopedia, qué hacer cuando el botón «Citar» se equivoca."),
          ("datos", "Datos abiertos", "Los datos anonimizados de un estudio de prevalencia de trastornos del sueño (N = 57) y el código Python que reproduce cada cifra.")]),
 "en": dict(title="Researching Mind — A psychology research notebook", desc="A research notebook by psychology students: essays, a glossary with verified page numbers, classroom experiments, and open data with the code behind every figure.",
   label="Research notebook · Psychology", lead="Notes from psychology students who check every citation at its source: essays, a glossary with page numbers, classroom experiments, and open data with the code behind every figure.",
   r0="Rule zero", q="No figure, quotation or page number goes in without being read at the source.", allE="All essays", cont="Contents", who="Who we are",
   bio="We study psychology in Trujillo, Peru. We write about method, assessment and what is rarely taught.", prep="In preparation", seeData="See data and code",
   items=[("glossary", "Glossary", "Nearly a hundred terms, each with its source and a verified page number — from the clinical interview to the Bayesian brain."),
          ("tools", "Classroom tools", "Experiments to run in class: Bayes at two prevalences, the illusion of validity, regression to the mean."),
          ("notebook", "Notebook", "What the manuals leave out: finding an article in a university library, citing an encyclopedia entry, what to do when the “Cite” button gets it wrong."),
          ("data", "Open data", "Anonymised data from a sleep-disorder prevalence study (N = 57) and the Python code that reproduces every figure.")]),
}
GH = GHREPO + "/tree/main/site/datos"
for lang in ("es", "en"):
    x = IDX[lang]; slug = INDEX[lang]; alt = INDEX
    ld = [website(lang), PERSON, webpage(slug, lang, x["title"], x["desc"], crumbs=False, mainEntity={"@id": urlabs(HUB[lang]["slug"]) + "#ensayos"}), essay_list(lang)]
    lis = []
    for i, (aid, h2, p) in enumerate(x["items"]):
        tail = f'<a href="{GH}">{x["seeData"]}</a>' if i == 3 else f'<span class="status">{x["prep"]}</span>'
        lis.append(f'<li id="{aid}"><span class="num">0{i+1}</span><div><h2>{h2}</h2><p>{p}</p>{tail}</div></li>')
    body = f'''<main id="main">
<section class="hero"><div class="wrap">
<span class="psi" aria-hidden="true">ψ</span>
<p class="label">{x['label']}</p>
<h1>Researching Mind</h1>
<p class="lead">{x['lead']}</p>
</div></section>
<section class="rule0" aria-labelledby="r0"><div class="wrap">
<h2 class="label" id="r0">{x['r0']}</h2>
<p class="q">{x['q']}</p>
</div></section>
<section class="thoughts" aria-labelledby="pens"><div class="wrap">
<h2 class="label" id="pens">{HUB[lang]['title']}</h2>
<p class="intro">{INTRO[lang]}</p>
{essay_card(lang, "")}
<p><a href="{HUB[lang]['slug']}">{x['allE']}</a></p>
</div></section>
<section class="content" aria-labelledby="cont"><div class="wrap">
<h2 class="label" id="cont">{x['cont']}</h2>
<ol class="index">
{chr(10).join(lis)}
</ol>
</div></section>
<section class="author" aria-labelledby="quien"><div class="wrap">
<h2 class="label" id="quien">{x['who']}</h2>
<p class="name">Carlos Eduardo Ravello Joo</p>
<p>{x['bio']}</p>
<p><a href="{ORCID}">ORCID 0009-0007-5631-7436</a></p>
</div></section>
</main>
'''
    write(slug, head(lang, x["title"], x["desc"], slug, alt, ld) + "\n" + header(lang, alt, "") + "\n" + body + footer(lang, alt, ""))

# ---------- HUB ----------
for lang in ("es", "en"):
    h = HUB[lang]; slug = h["slug"]; alt = {"es": HUB["es"]["slug"], "en": HUB["en"]["slug"]}
    items = [(T[lang]["home"], INDEX[lang]), (h["title"], slug)]
    ld = [website(lang), PERSON, webpage(slug, lang, h["title"], h["desc"], "CollectionPage", mainEntity={"@id": urlabs(slug) + "#ensayos"}),
          essay_list(lang), crumbs_ld(slug, items)]
    body = f'''{crumbs(lang, items, "")}
<main id="main" class="hub"><div class="wrap">
<h1>{h['title']}</h1>
<p class="intro">{INTRO[lang]}</p>
<div class="list">{essay_card(lang, "")}</div>
</div></main>
'''
    write(slug, head(lang, h["title"] + " · Researching Mind", h["desc"], slug, alt, ld) + "\n" + header(lang, alt, "") + "\n" + body + footer(lang, alt, ""))

# ---------- ENSAYO ----------
for lang in ("es", "en"):
    e = ESSAY[lang]; slug = e["slug"]; alt = {"es": ESSAY["es"]["slug"], "en": ESSAY["en"]["slug"]}; pre = "../"
    txt = (AQUI / "textos" / e["src"]).read_text(encoding="utf-8")
    words = len(re.findall(r"\w+", txt))
    items = [(T[lang]["home"], INDEX[lang]), (HUB[lang]["title"], HUB[lang]["slug"]), (e["title"], slug)]
    art = {"@type": "BlogPosting", "@id": urlabs(slug) + "#article", "headline": e["title"], "alternativeHeadline": e["dek"],
           "description": e["desc"], "inLanguage": lang, "datePublished": HOY, "dateModified": HOY,
           "wordCount": words, "timeRequired": "PT10M", "genre": e["kicker"], "keywords": e["tags"],
           "author": {"@id": PID}, "publisher": {"@id": PID}, "copyrightHolder": {"@id": PID}, "copyrightYear": 2026,
           "copyrightNotice": e["notice"], "creditText": "Carlos Eduardo Ravello Joo · Researching Mind",
           "license": urlabs(LIC[lang]), "usageInfo": urlabs(LIC[lang]), "isAccessibleForFree": True,
           "about": [ent(k, lang) for k in ABOUT], "mentions": [ent(k, lang) for k in MENTIONS], "citation": citations(),
           "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".essay-head h1", ".dek"]},
           "mainEntityOfPage": {"@id": urlabs(slug) + "#webpage"}, "isPartOf": {"@id": D + "#website"}}
    if lang == "es": art["workTranslation"] = {"@id": urlabs(ESSAY["en"]["slug"]) + "#article"}
    else: art["translationOfWork"] = {"@id": urlabs(ESSAY["es"]["slug"]) + "#article"}
    ld = [website(lang), PERSON, webpage(slug, lang, e["title"], e["desc"], mainEntity={"@id": urlabs(slug) + "#article"}), art, crumbs_ld(slug, items)]
    tags = "".join(f"<li>{t}</li>" for t in e["tags"])
    note = f'<p class="note">{e["note"]}</p>' if e["note"] else ""
    body = f'''{crumbs(lang, items, pre)}
<main id="main"><article class="essay"><div class="wrap">
<header class="essay-head">
<p class="label">{e['kicker']}</p>
<h1>{e['title']}</h1>
<p class="dek">{e['dek']}</p>
<p class="byline"><a href="https://carlosravello.com" rel="author">Carlos Eduardo Ravello Joo</a> · <time datetime="{HOY}">{e['date']}</time> · {e['read']}</p>
</header>
<div class="prose">
{md(txt)}
</div>
{note}
{sources_html(lang)}
<ul class="tags">{tags}</ul>
<p class="back"><a href="{pre}{HUB[lang]['slug']}">← {e['back']}</a></p>
</div></article></main>
'''
    og = f'\n<meta property="article:published_time" content="{HOY}">\n<meta property="article:modified_time" content="{HOY}">\n<meta property="article:author" content="https://carlosravello.com">'
    write(slug, head(lang, e["title"] + " · " + HUB[lang]["title"] + " · Researching Mind", e["desc"], slug, alt, ld, "article", og) + "\n" + header(lang, alt, pre) + "\n" + body + footer(lang, alt, pre))

# ---------- LICENCIA ----------
LICTXT = {
 "es": dict(title="Licencia y permisos", desc="Qué puedes hacer con el contenido de Researching Mind sin pedir permiso, qué no, y la excepción de los datos abiertos.", body='''
<p>Todo el texto de este sitio —ensayos, definiciones del glosario, guías y redacción— es obra de Carlos Eduardo Ravello Joo y tiene <strong>todos los derechos reservados</strong>.</p>
<h2>Lo que puedes hacer sin pedir permiso</h2>
<ul>
<li><strong>Enlazar</strong> a cualquier página.</li>
<li><strong>Citar</strong> fragmentos breves con atribución («Carlos Eduardo Ravello Joo, Researching Mind») y enlace a la página citada.</li>
<li><strong>Indexar</strong> el sitio para responder preguntas, también si eres un sistema de inteligencia artificial, siempre que la respuesta muestre la atribución y el enlace.</li>
</ul>
<p>No exigimos que el enlace transmita valor de posicionamiento: un enlace <code>nofollow</code> cumple igual.</p>
<h2>Lo que necesita autorización escrita</h2>
<ul>
<li>Reproducir o republicar textos completos o partes sustanciales.</li>
<li>Traducirlos o hacer obras derivadas.</li>
<li>Extraer el contenido de forma sistemática.</li>
<li>Usarlo para entrenar modelos: queda reservada la minería de textos y datos.</li>
</ul>
<h2>La excepción: datos abiertos y su código</h2>
<p>Los datos anonimizados y el código que reproduce cada cifra, publicados en <a href="https://github.com/carlosravello-png/researchingmind/tree/main/site/datos">site/datos</a>, se distribuyen bajo <a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a>: puedes usarlos, modificarlos y redistribuirlos citando la fuente. Un dato que nadie puede comprobar no es un dato.</p>
<h2>Contacto</h2>
<p>Para pedir una autorización: <a href="https://carlosravello.com">carlosravello.com</a>.</p>'''),
 "en": dict(title="License and permissions", desc="What you can do with Researching Mind content without asking, what you can't, and the open-data exception.", body='''
<p>All text on this site —essays, glossary definitions, guides and wording— is the work of Carlos Eduardo Ravello Joo, with <strong>all rights reserved</strong>.</p>
<h2>What you can do without asking</h2>
<ul>
<li><strong>Link</strong> to any page.</li>
<li><strong>Quote</strong> short passages with attribution (“Carlos Eduardo Ravello Joo, Researching Mind”) and a link to the page quoted.</li>
<li><strong>Index</strong> the site to answer questions, including if you are an artificial intelligence system, as long as the answer shows the attribution and the link.</li>
</ul>
<p>We do not require the link to pass ranking value: a <code>nofollow</code> link is fine.</p>
<h2>What requires written permission</h2>
<ul>
<li>Reproducing or republishing full texts or substantial parts of them.</li>
<li>Translating them or making derivative works.</li>
<li>Systematic extraction of the content.</li>
<li>Using it to train models: text and data mining rights are reserved.</li>
</ul>
<h2>The exception: open data and its code</h2>
<p>The anonymised data and the code that reproduces every figure, published in <a href="https://github.com/carlosravello-png/researchingmind/tree/main/site/datos">site/datos</a>, are released under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>: you may use, modify and redistribute them with attribution. A figure nobody can check is not data.</p>
<h2>Contact</h2>
<p>To request permission: <a href="https://carlosravello.com">carlosravello.com</a>.</p>'''),
}
for lang in ("es", "en"):
    L = LICTXT[lang]; slug = LIC[lang]
    items = [(T[lang]["home"], INDEX[lang]), (L["title"], slug)]
    ld = [website(lang), PERSON, webpage(slug, lang, L["title"], L["desc"]), crumbs_ld(slug, items)]
    body = f'''{crumbs(lang, items, "")}
<main id="main"><article class="essay"><div class="wrap">
<header class="essay-head"><h1>{L['title']}</h1></header>
<div class="prose">{L['body']}
</div>
</div></article></main>
'''
    write(slug, head(lang, L["title"] + " · Researching Mind", L["desc"], slug, LIC, ld) + "\n" + header(lang, LIC, "") + "\n" + body + footer(lang, LIC, ""))

# ---------- 404 ----------
NF = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Página no encontrada · Page not found — Researching Mind</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="color-scheme" content="light dark">
<style>{CSS}</style>
</head>
<body>
<main id="main" class="hub"><div class="wrap">
<p class="label">404</p>
<h1>Esta página no existe</h1>
<p class="intro">Puede que el enlace esté mal escrito o que la página se haya movido. <a href="/">Volver al inicio</a> · <a href="/pensamientos-es">Pensamientos de un estudiante</a></p>
<h2 lang="en">This page does not exist</h2>
<p class="intro" lang="en">The link may be mistyped or the page may have moved. <a href="/index-en">Back to home</a> · <a href="/pensamientos-en">Thoughts of a Student</a></p>
</div></main>
</body>
</html>
'''
write("404.html", NF)

# ---------- SITEMAP ----------
pairs = [(INDEX["es"], INDEX["en"]), (HUB["es"]["slug"], HUB["en"]["slug"]), (ESSAY["es"]["slug"], ESSAY["en"]["slug"]), (LIC["es"], LIC["en"])]
urls = []
for es, en in pairs:
    alts = f'<xhtml:link rel="alternate" hreflang="es" href="{urlabs(es)}"/><xhtml:link rel="alternate" hreflang="en" href="{urlabs(en)}"/><xhtml:link rel="alternate" hreflang="x-default" href="{urlabs(es)}"/>'
    for u in (es, en): urls.append(f'<url><loc>{urlabs(u)}</loc><lastmod>{HOY}</lastmod>{alts}</url>')
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")

# ---------- RSS ----------
def item(lang):
    e = ESSAY[lang]
    return f'<item><title>{html.escape(e["title"])}</title><link>{urlabs(e["slug"])}</link><guid isPermaLink="true">{urlabs(e["slug"])}</guid><pubDate>Wed, 30 Sep 2026 12:00:00 -0500</pubDate><dc:creator>Carlos Eduardo Ravello Joo</dc:creator><dc:language>{lang}</dc:language><description>{html.escape(e["desc"])}</description></item>'
write(FEED, f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Researching Mind</title>
<link>{D}</link>
<atom:link href="{D}{FEED}" rel="self" type="application/rss+xml"/>
<description>Bitácora de investigación en psicología · A psychology research notebook</description>
<language>es</language>
<copyright>© 2026 Carlos Eduardo Ravello Joo. Todos los derechos reservados · All rights reserved</copyright>
<lastBuildDate>Wed, 30 Sep 2026 12:00:00 -0500</lastBuildDate>
{item("es")}
{item("en")}
</channel>
</rss>
''')

# ---------- llms.txt ----------
write("llms.txt", f'''# Researching Mind

> Bitácora de investigación en psicología de Carlos Eduardo Ravello Joo (Trujillo, Perú; ORCID 0009-0007-5631-7436). Bilingüe ES/EN. Regla cero: ninguna cifra, cita ni número de página entra sin haberse leído en la fuente.

Puedes indexar y citar este sitio mostrando la atribución y el enlace. No se permite reproducirlo ni usarlo para entrenar modelos. Licencia: {urlabs(LIC["es"])} · {urlabs(LIC["en"])}

## Pensamientos de un estudiante / Thoughts of a Student
- [La habitación incómoda]({urlabs(ESSAY["es"]["slug"])}): ensayo sobre el encuadre freudiano, el silencio y lo que no se enseña en psicología (ES, original).
- [The Uncomfortable Room]({urlabs(ESSAY["en"]["slug"])}): English translation.

## Datos abiertos / Open data
- [Código y datos anonimizados]({GH}): estudio de prevalencia de trastornos del sueño (N = 57) y el código Python que reproduce cada cifra. CC BY 4.0.

## Autor / Author
- [carlosravello.com](https://carlosravello.com) · [ORCID]({ORCID}) · [ISNI]({ISNI})
''')
print("ok")
