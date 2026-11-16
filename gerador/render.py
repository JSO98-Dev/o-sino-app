"""O Sino — gera o carrossel do Instagram (1080x1350) e o story (1080x1920) a partir de uma edição JSON.
Uso: python3 render.py edicao.json pasta_saida
Edição diária: placar com var_dia. Edição de domingo: placar com var_semana (sem madrugada; agenda com campo "dia").
Cards com "manchete": true também viram posts avulsos manchete-N.png (etiqueta "assunto", "destaque" {valor, rotulo, dir} e "serie" opcional).
Versão 4: identidade visual O Sino (logotipo desenhado, régua de 8 px, margem de 72 px, variação com ícone,
faixa de domingo, slide de fontes, story próprio). Imprime "AVISO:" quando um slide precisou encolher ou ainda não coube."""
import json, sys, html, pathlib, datetime as dt, hashlib, urllib.request
import re as _re
from playwright.sync_api import sync_playwright

# logotipo O SINO. (A1 principal, A2 reduzida), texto em curvas
A1 = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="8.0 50.5 765.8 152.0"><path d="M81.7,54.6C122.9,54.6 155.4,87.1 155.4,128.5C155.4,169.8 122.9,202.4 81.7,202.4C40.4,202.4 8.0,169.8 8.0,128.5C8.0,87.1 40.4,54.6 81.7,54.6ZM81.7,61.2C57.8,61.2 42.0,86.4 42.0,124.3C42.0,162.1 57.8,187.4 81.7,187.4C105.5,187.4 121.4,162.1 121.4,124.3C121.4,86.4 105.5,61.2 81.7,61.2Z" fill="#151413"/><path d="M299.3 63.2 285.5 61.0 298.0 50.5H299.9L307.3 99.1L304.3 99.6L283.0 65.7L291.2 75.6Q283.4 68.1 275.4 64.5Q267.4 61.0 258.9 61.0Q246.5 61.0 241.0 66.6Q235.6 72.3 235.6 81.3Q235.6 87.6 238.5 92.0Q241.5 96.3 246.6 99.2Q251.8 102.1 258.4 104.5Q265.0 106.8 272.2 109.3Q279.5 111.8 286.6 115.0Q293.8 118.3 299.7 123.2Q305.6 128.2 309.2 135.7Q312.8 143.3 312.8 154.4Q312.8 169.0 304.9 179.8Q297.0 190.7 283.8 196.6Q270.6 202.5 254.6 202.5Q243.9 202.5 235.2 201.1Q226.5 199.8 217.1 196.3L208.9 156.0H212.1L239.6 197.8L221.9 186.2Q230.9 191.1 238.1 193.8Q245.3 196.5 253.2 196.5Q265.3 196.5 273.2 193.0Q281.1 189.5 284.9 183.2Q288.8 176.9 288.8 168.5Q288.8 160.3 285.2 155.0Q281.6 149.7 275.7 146.2Q269.8 142.7 262.6 140.1Q255.5 137.5 248.4 134.8Q241.3 132.3 234.9 129.2Q228.5 126.1 223.5 121.7Q218.5 117.3 215.6 111.1Q212.8 104.8 212.8 95.8Q212.8 83.1 219.1 73.8Q225.4 64.6 237.0 59.5Q248.6 54.5 264.2 54.5Q274.2 54.5 282.3 56.5Q290.5 58.6 299.3 63.2Z" fill="#151413"/><path d="M399.2 196.7V200.0H333.0V196.7L349.4 192.3V64.6L333.0 60.2V57.0H399.2V60.2L382.8 64.6V192.3Z" fill="#151413"/><path d="M435.1 192.3V66.9L415.2 59.9V57.0H469.6L546.1 165.9L540.7 178.9V64.6L522.6 60.2V57.0H565.1V60.2L548.3 64.6V201.2H533.1L439.4 67.7L442.0 65.2V192.3L460.1 196.7V200.0H418.3V196.7Z" fill="#151413"/><path d="M656.0,54.6C697.2,54.6 729.7,87.1 729.7,128.5C729.7,169.8 697.2,202.4 656.0,202.4C614.7,202.4 582.3,169.8 582.3,128.5C582.3,87.1 614.7,54.6 656.0,54.6ZM656.0,61.2C632.1,61.2 616.3,86.4 616.3,124.3C616.3,162.1 632.1,187.4 656.0,187.4C679.8,187.4 695.7,162.1 695.7,124.3C695.7,86.4 679.8,61.2 656.0,61.2Z" fill="#151413"/><path d="M756.8,168.4C766.2,168.4 773.8,176.0 773.8,185.4C773.8,194.7 766.2,202.4 756.8,202.4C747.4,202.4 739.8,194.7 739.8,185.4C739.8,176.0 747.4,168.4 756.8,168.4Z" fill="#A3201B"/></svg>'
A2 = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="7.5 58.9 759.2 143.7"><path d="M77.9,63.4C117.4,63.4 148.4,94.0 148.4,133.0C148.4,171.9 117.4,202.6 77.9,202.6C38.5,202.6 7.5,171.9 7.5,133.0C7.5,94.0 38.5,63.4 77.9,63.4ZM77.9,76.0C55.4,76.0 40.5,96.9 40.5,128.3C40.5,159.6 55.4,180.6 77.9,180.6C100.4,180.6 115.4,159.6 115.4,128.3C115.4,96.9 100.4,76.0 77.9,76.0Z" fill="#151413"/><path d="M288.6 71.2 272.7 68.6 285.4 58.9H289.0L296.8 105.8L290.6 107.1L269.1 75.1L276.0 83.0Q270.8 79.1 265.0 77.2Q259.3 75.3 253.3 75.3Q240.9 75.3 235.2 80.1Q229.5 84.8 229.5 92.8Q229.5 98.3 232.4 102.1Q235.3 105.8 240.2 108.5Q245.2 111.1 251.4 113.3Q257.6 115.5 264.3 117.8Q271.0 120.1 277.6 123.2Q284.3 126.3 289.8 130.9Q295.3 135.5 298.6 142.2Q302.0 149.0 302.0 158.8Q302.0 173.2 294.7 182.9Q287.5 192.7 275.2 197.6Q262.9 202.6 247.3 202.6Q236.6 202.6 228.0 201.3Q219.5 200.0 210.2 196.6L201.5 158.0H207.8L237.7 196.5L214.8 182.2Q222.7 186.4 229.0 188.1Q235.3 189.9 242.4 189.9Q253.2 189.9 260.1 187.5Q267.1 185.1 270.5 180.3Q273.9 175.7 273.9 168.9Q273.9 162.3 270.4 157.9Q266.9 153.6 261.2 150.7Q255.6 147.9 248.8 145.7Q242.1 143.6 235.7 141.2Q229.3 138.9 223.5 135.8Q217.7 132.8 213.2 128.4Q208.7 124.1 206.1 117.8Q203.5 111.5 203.5 102.6Q203.5 90.6 209.7 81.8Q215.9 73.1 227.2 68.2Q238.6 63.4 254.0 63.4Q263.6 63.4 271.8 65.2Q280.0 67.0 288.6 71.2Z" fill="#151413"/><path d="M390.0 195.6V200.0H330.2V195.6L344.7 189.8V76.1L330.2 70.4V66.0H390.0V70.4L375.5 76.1V189.8Z" fill="#151413"/><path d="M433.3 189.8V78.1L417.0 69.9V66.0H466.9L539.5 167.9L531.4 172.8V76.1L515.3 70.4V66.0H557.7V70.4L543.2 76.1V200.7H524.3L440.2 80.6L445.2 77.0V189.8L461.2 195.6V200.0H418.8V195.6Z" fill="#151413"/><path d="M653.8,63.4C693.3,63.4 724.3,94.0 724.3,133.0C724.3,171.9 693.3,202.6 653.8,202.6C614.4,202.6 583.4,171.9 583.4,133.0C583.4,94.0 614.4,63.4 653.8,63.4ZM653.8,76.0C631.3,76.0 616.4,96.9 616.4,128.3C616.4,159.6 631.3,180.6 653.8,180.6C676.3,180.6 691.3,159.6 691.3,128.3C691.3,96.9 676.3,76.0 653.8,76.0Z" fill="#151413"/><path d="M750.2,169.4C759.3,169.4 766.7,176.7 766.7,185.9C766.7,195.0 759.3,202.4 750.2,202.4C741.1,202.4 733.7,195.0 733.7,185.9C733.7,176.7 741.1,169.4 750.2,169.4Z" fill="#A3201B"/></svg>'


PERFIL = "@jornal.o_sino"
DOM = False  # definido em build(): edição de domingo
ED = "abertura"  # definido em build(): abertura | meiodia | fechamento
FONTS = pathlib.Path(__file__).parent / "node_modules/@fontsource"
DIAS = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
DIAS_EXT = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
ICON = {"up": '<path d="M6 15l6-6 6 6"/>', "down": '<path d="M6 9l6 6 6-6"/>', "flat": '<path d="M6 12h12"/>',
        "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5.5l3.5 2"/>',
        "ECONOMIA": '<path d="M3 20h18"/><path d="M6 17v-4M10 17v-7M14 17v-5M18 17v-10"/>',
        "POLÍTICA": '<path d="M3 20h18M4 10h16M12 4l8 6H4z"/><path d="M6 10v7M10 10v7M14 10v7M18 10v7"/>',
        "AGRO": '<path d="M12 20v-9"/><path d="M12 11c0-4 3-6 7-6 0 4-3 6-7 6z"/><path d="M12 14c0-3-2.5-5-6-5 0 3 2.5 5 6 5z"/>',
        "INTERNACIONAL": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.5 3.5 5.5 3.5 8.5s-1 6-3.5 8.5c-2.5-2.5-3.5-5.5-3.5-8.5s1-6 3.5-8.5z"/>',
        "ANÁLISE": '<path d="M12 6c-2-1.5-5-2-8-2v14c3 0 6 .5 8 2 2-1.5 5-2 8-2V4c-3 0-6 .5-8 2z"/><path d="M12 6v14"/>',
        "MERCADOS": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>'}
ASSUNTO = {"MERCADOS": "MERCADOS", "BRASIL": "ECONOMIA", "GLOBAL": "INTERNACIONAL", "GEOPOLÍTICA": "INTERNACIONAL",
           "AGRO": "AGRO", "IMOBILIÁRIO": "ECONOMIA"}
GRUPO = {"Ibovespa": 0, "S&P 500": 0, "Nasdaq Composite": 0, "Dólar/Real": 1, "DI Jan/28": 2, "Ouro": 3, "Brent": 3,
         "Boi gordo": 4, "Soja CBOT": 4, "Milho": 4, "IFIX": 5}

def e(s):
    s = _re.sub(r'"([^"]*)"', '“\\1”', str(s))
    s = _re.sub(r'(R\$|US\$|US¢|≈) ', '\\1\u00a0', s)
    s = s.replace(" bps", "\u00a0bps").replace(" pts", "\u00a0pts")
    return html.escape(s, quote=False)
cap1 = lambda s: s[:1].upper() + s[1:]


def font_css():
    faces = [("Newsreader", "newsreader", w, s) for w in (400, 500, 600) for s in ("normal", "italic")]
    faces += [("Plex Cond", "ibm-plex-sans-condensed", w, "normal") for w in (500, 600)]
    faces += [("Plex Mono", "ibm-plex-mono", w, "normal") for w in (400, 500)]
    out = []
    for fam, pkg, w, s in faces:
        f = FONTS / pkg / "files" / f"{pkg}-latin-{w}-{s}.woff2"
        out.append(f"@font-face{{font-family:'{fam}';src:url('file://{f}') format('woff2');font-weight:{w};font-style:{s}}}")
    return "\n".join(out)


CSS = """
:root{--papel:#F2EEE5;--tinta:#151413;--cinza:#6B655B;--linha:#D9D3C6;--vermelho:#A3201B;--alta:#1E6B3E;--queda:#B0281E}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--papel);color:var(--tinta);font-family:'Newsreader',serif;-webkit-font-smoothing:antialiased}
.s{width:1080px;height:1350px;padding:72px;display:flex;flex-direction:column;overflow:hidden}
.s.story{height:1920px;padding:220px 72px 300px}
.body{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}
.regua{height:8px;background:var(--tinta);flex:none}
.fil{height:1px;background:var(--tinta);flex:none}
.mast{display:flex;justify-content:space-between;align-items:flex-end;padding:18px 0 16px;flex:none}
.mast svg{display:block;height:56px;width:auto}.story .mast svg{height:64px}
.mast .dir{display:flex;flex-direction:column;align-items:flex-end;gap:6px}
.mini{display:flex;justify-content:space-between;align-items:center;padding:16px 0 14px;flex:none}
.mini svg{display:block;height:30px;width:auto}
.r{font-family:'Plex Cond';font-weight:600;letter-spacing:.12em;text-transform:uppercase}
.m{font-family:'Plex Mono';font-weight:500;font-variant-numeric:tabular-nums}
.cz{color:var(--cinza)}.vm{color:var(--vermelho)}.up{color:var(--alta)}.down{color:var(--queda)}.flat{color:var(--cinza)}
.linha-ed{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--linha);flex:none}
.faixa{background:var(--vermelho);color:var(--papel);height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 20px;margin-top:10px;flex:none}
.kick{font-size:22px;letter-spacing:.14em;margin-top:40px}
h1{font-weight:600;font-size:76px;line-height:80px;letter-spacing:-.01em;margin-top:16px}
.story h1{font-size:104px;line-height:108px}
.story .foto~div{margin-top:24px !important}.story:has(.foto) h1{font-size:84px;line-height:90px}
.story:has(.foto) .srow .val{font-size:60px}.story:has(.foto) .srow{padding:10px 0}
h2{font-weight:600;font-size:56px;line-height:62px;letter-spacing:-.005em}
h2.f{font-size:60px;line-height:66px;margin-top:14px}
.tit{display:flex;justify-content:space-between;align-items:baseline;gap:24px;padding:32px 0 22px;flex:none}
.tit .ic{display:flex;align-items:center;gap:18px}
.dek{font-size:32px;line-height:42px;margin-top:18px}
.foot{flex:none;margin-top:20px;border-top:1px solid var(--tinta);padding-top:14px;display:flex;justify-content:space-between;align-items:baseline}
.foot i{font-style:italic;font-size:22px;color:var(--cinza)}
.v{display:inline-flex;align-items:center;justify-content:flex-end;gap:5px;white-space:nowrap}
.v svg{flex:none}
/* capa */
.termo{margin-top:34px}
.scale{display:grid;grid-template-columns:repeat(3,1fr);margin-top:12px;border:1px solid var(--tinta)}
.scale div{font-family:'Plex Cond';font-weight:600;font-size:22px;letter-spacing:.1em;text-transform:uppercase;text-align:center;padding:12px 0;color:var(--cinza)}
.scale div+div{border-left:1px solid var(--tinta)}
.scale .on{background:var(--tinta);color:var(--papel)}
.termo p{font-size:26px;line-height:36px;margin-top:14px}
.big3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;border-top:2px solid var(--tinta);margin-top:auto;flex:none}
.big3>div{padding-top:16px;display:flex;flex-direction:column;gap:8px}
.big3 .val{font-size:44px;line-height:52px}
/* tabela */
table{width:100%;border-collapse:collapse}
th{font-family:'Plex Cond';font-weight:600;font-size:18px;letter-spacing:.12em;text-transform:uppercase;color:var(--cinza);text-align:right;padding:0 0 10px;border-bottom:2px solid var(--tinta)}
th:first-child{text-align:left}
td{padding:11px 0 10px;border-top:1px solid var(--linha);text-align:right;font-family:'Plex Mono';font-weight:500;font-size:26px;white-space:nowrap;font-variant-numeric:tabular-nums}
tr.g td{border-top:1px solid var(--tinta)}
tr:nth-child(2) td{border-top:none}
td:first-child{text-align:left;font-family:'Newsreader';font-size:28px;font-weight:500;white-space:normal;line-height:1.1}
td small{display:block;font-family:'Plex Cond';font-size:16px;letter-spacing:.06em;color:var(--cinza);font-weight:500;margin-top:3px}
td .v{font-size:24px}
.note{font-family:'Newsreader';font-style:italic;font-size:21px;color:var(--cinza);margin-top:14px;line-height:1.35}
/* listas */
.it{display:grid;grid-template-columns:72px 1fr;padding:18px 0 20px;border-top:1px solid var(--linha)}
.it:first-child{border-top:1px solid var(--tinta)}
.it .n{font-size:28px;line-height:38px;color:var(--cinza)}
.it p{font-size:28px;line-height:38px}
.it .r{font-size:17px;color:var(--cinza);margin-top:8px}
.rows{border-top:2px solid var(--tinta)}
.row{display:grid;grid-template-columns:150px 1fr auto;gap:22px;align-items:baseline;padding:16px 0;border-bottom:1px solid var(--linha)}
.row.dom{grid-template-columns:250px 1fr auto}
.row .h{font-size:26px;white-space:nowrap}
.row .t{font-size:28px;line-height:36px}
.row .c{font-size:20px;color:var(--cinza);text-align:right;max-width:290px;line-height:1.3}
.row.md{grid-template-columns:1fr 110px 220px 150px;align-items:center}
.row.md .t{font-weight:500}
.row.md .h{font-size:20px;color:var(--cinza)}
.row.md .val{font-size:26px;text-align:right}
.hdr{display:grid;gap:22px;padding-bottom:10px;border-bottom:2px solid var(--tinta)}
/* foco */
.dado{font-size:32px;line-height:44px;border-top:2px solid var(--tinta);border-bottom:1px solid var(--tinta);padding:16px 0;margin-top:26px}
.blk{margin-top:30px}
.blk .r{font-size:22px;letter-spacing:.14em}
.blk p{font-size:32px;line-height:46px;margin-top:10px}
.blk.obs{border-top:2px solid var(--tinta);padding-top:16px}
.imp{display:flex;gap:28px;flex-wrap:wrap;margin-top:22px;align-items:center}
.imp span{font-family:'Plex Cond';font-weight:600;font-size:20px;letter-spacing:.06em;display:inline-flex;align-items:center;gap:6px}
/* fontes */
.src{display:grid;grid-template-columns:190px 1fr;padding:14px 0;border-top:1px solid var(--linha)}
.src .r{font-size:19px;padding-top:5px}
.src p{font-size:26px;line-height:37px;color:var(--cinza)}
.exp{display:grid;grid-template-columns:1fr 300px;gap:40px;align-items:end;margin-top:34px}
.exp p{font-size:28px;line-height:42px}
.aviso{border-top:2px solid var(--tinta);padding-top:18px;margin-top:36px;font-size:26px;line-height:38px}
.selo{display:flex;flex-direction:column;gap:10px}
.selo svg{width:300px;height:auto;display:block}
/* story */
.srow{display:grid;grid-template-columns:1fr auto;align-items:end;padding:16px 0 14px;border-top:1px solid var(--linha)}
.srow .val{font-size:72px;line-height:1}
.srow .v{font-size:36px}
/* manchete avulsa */
.tag{display:inline-block;align-self:flex-start;background:var(--vermelho);color:var(--papel);font-size:24px;letter-spacing:.12em;padding:8px 14px 7px;margin-top:40px}
.painel{margin-top:auto;border-top:2px solid var(--tinta);padding-top:22px;flex:none;display:flex;flex-direction:column;gap:6px}
.painel .num{display:flex;align-items:center;gap:10px;font-family:'Plex Cond';font-weight:600;font-size:184px;line-height:1;letter-spacing:-.01em}
.mch h1{font-size:92px;line-height:98px}
.tcurto{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:center;margin-top:22px;flex:none}
.tcurto .scale div{padding:9px 0;font-size:19px}
.mch .big3{margin-top:22px}
.foto{margin-top:30px;background-size:cover;background-position:center 60%;position:relative;overflow:hidden}
.sob{position:absolute;left:0;bottom:0;background:rgba(21,20,19,.86);padding:16px 26px 14px;display:flex;flex-direction:column;gap:2px}
.sob .num{display:flex;align-items:center;gap:6px;font-family:'Plex Cond';font-weight:600;line-height:1;color:var(--papel)}
.upc{color:#7FD3A1 !important}.downc{color:#FF8A7E !important}.flatc{color:var(--papel)}
.dq{display:flex;align-items:baseline;gap:18px;margin-top:22px}
.dq .num{display:flex;align-items:center;gap:6px;font-family:'Plex Cond';font-weight:600;font-size:84px;line-height:1}
.painel .icone{display:flex;justify-content:center;padding:26px 0 10px}
.cta{display:flex;justify-content:space-between;align-items:baseline;border-top:2px solid var(--tinta);padding-top:20px;margin-top:auto;flex:none}
"""


def sinal(v):
    v = str(v).replace("≈", "").strip()
    if v.startswith("+"):
        return "up"
    if v.startswith("−") or v.startswith("-"):
        return "down"
    return "flat"


def ic(k, size, cls="", sw=2.25):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="square" class="{cls}">{ICON[k]}</svg>')


def var(v, size=24):
    k = sinal(v)
    return f'<span class="v m {k}" style="font-size:{size}px">{ic(k, round(size * .8))}{e(v)}</span>'


def data_ext(iso):
    d = dt.date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d.day} {MESES[d.month-1].upper()} {d.year}", d


def hora_ed():
    return "19:00" if DOM else {"meiodia": "12:00", "fechamento": "19:00"}.get(ED, "07:00")


def mast(ed, story=False):
    txt, _ = data_ext(ed["data"])
    topo = f'<span class="m vm" style="font-size:34px">{hora_ed()}</span>' if story else f'<span class="m cz" style="font-size:22px">Nº {ed["numero"]:03d}</span>'
    out = (f'<div class="regua"></div><div class="mast">{A1}<div class="dir">{topo}'
           f'<span class="r" style="font-size:{22 if story else 20}px;letter-spacing:.1em">{txt}</span></div></div><div class="fil"></div>')
    if DOM:
        out += f'<div class="faixa"><span class="r" style="font-size:20px;letter-spacing:.14em">Edição de domingo · resumo da semana</span><span class="m" style="font-size:22px">19:00</span></div>'
    elif not story:
        out += (f'<div class="linha-ed"><span class="r" style="font-size:18px">Edição das {hora_ed()}</span>'
                f'<span class="r cz" style="font-size:18px;letter-spacing:.1em">Economia · Política · Geopolítica · Agro · Imobiliário</span></div>')
    return out


def mini(ed, secao):
    txt, _ = data_ext(ed["data"])
    return (f'<div class="regua"></div><div class="mini">{A2}<span class="r" style="font-size:18px">{e(secao)} · {txt}</span></div>'
            f'<div class="fil"></div>')


def foot(i, n, nota=""):
    return (f'<div class="foot"><span class="r" style="font-size:20px;letter-spacing:.08em">{e(PERFIL)}</span>'
            f'<i>{e(nota)}</i><span class="m cz" style="font-size:22px">{i:02d}/{n:02d}</span></div>')


def termo(ed):
    t = ed["termometro"]
    cells = "".join(f'<div class="{"on" if x == t["leitura"] else ""}">{x}</div>' for x in ("Risk-off", "Neutro", "Risk-on"))
    return (f'<div class="termo"><div class="r cz" style="font-size:20px">{"Termômetro da semana" if DOM else "Termômetro para amanhã" if ED == "fechamento" else "Termômetro do dia"}</div>'
            f'<div class="scale">{cells}</div><p>{e(t["justificativa"])}</p></div>')


SEM = '<span class="r cz" style="font-size:16px;margin-left:10px">na semana</span>'
TRES = (("Ibovespa", "Ibovespa"), ("Dólar/Real", "Dólar · R$"), ("DI Jan/28", "DI jan/28 · %"))
def limpa(f):
    for t in (" pts", "/bbl", "/oz", "/@", "/sc", "/bu", "R$ ", "US$ ", "US¢ "):
        f = f.replace(t, "")
    return f


def big3(ed):
    p = {x["ativo"]: x for x in ed["placar"]}
    out = ""
    for n, rot in TRES:
        if n not in p:
            continue
        x = p[n]
        out += (f'<div><span class="r cz" style="font-size:20px">{e(rot)}</span><span class="m val">{e(limpa(x["fechamento"]).replace("%", ""))}</span>'
                f'<div>{var(x[VK()], 26)}{SEM if DOM else ""}</div></div>')
    return f'<div class="big3">{out}</div>'


def termo_curto(ed):
    t = ed["termometro"]
    cells = "".join(f'<div class="{"on" if x == t["leitura"] else ""}">{x}</div>' for x in ("Risk-off", "Neutro", "Risk-on"))
    rot = "Termômetro da semana" if DOM else "Termômetro para amanhã" if ED == "fechamento" else "Termômetro do dia"
    return (f'<div class="tcurto"><span class="r cz" style="font-size:18px">{rot}</span>'
            f'<div class="scale" style="margin-top:0">{cells}</div></div>')


def capa(ed, foco, n):
    q = quadro(ed, foco, num=104)
    vis = q or f'<div class="painel" style="margin-top:auto">{visual(foco, num=150, sh=110, ico=190)}</div>'
    return (f'<section class="s mch">{mast(ed)}<div class="body"><span class="r tag" style="margin-top:30px">{e(assunto(foco))}</span><h1>{e(foco["titulo"])}</h1>'
            f'<p class="dek">{e(foco["dado"])}</p>{vis}{termo_curto(ed)}{big3(ed)}</div>{foot(1, n)}</section>')


def story(ed, foco):
    p = {x["ativo"]: x for x in ed["placar"]}
    rows = "".join(f'<div class="srow"><div style="display:flex;flex-direction:column;gap:10px"><span class="r cz" style="font-size:26px">{e(rot)}</span>'
                   f'<div>{var(p[n][VK()], 36)}</div></div><span class="m val">{e(limpa(p[n]["fechamento"]).replace("%", ""))}</span></div>'
                   for n, rot in TRES if n in p)
    ag = "".join(f'<div class="row{" dom" if DOM else ""}" style="grid-template-columns:{250 if DOM else 150}px 1fr"><span class="m h" style="font-size:30px">{e((a.get("dia", "") + " " + a["hora"]).strip())}</span>'
                 f'<span class="t" style="font-size:32px;line-height:42px">{e(a["evento"])}</span></div>' for a in ed["agenda"][:3])
    kick = '<div class="r kick" style="font-size:26px">A semana em dois minutos</div>' if DOM else f'<div class="r kick vm" style="font-size:26px">{ {"meiodia": "No meio do pregão", "fechamento": "Depois do sino"}.get(ED, "Antes do sino")}</div>'
    q = quadro(ed, foco, num=80, minh=330) or ""
    return (f'<section class="s story">{mast(ed, story=True)}<div class="body">{kick}<h1>{e(foco["titulo"])}</h1>{q}'
            f'<div style="margin-top:36px;border-bottom:1px solid var(--linha)">{rows}</div>'
            f'<div style="margin-top:36px"><div style="display:flex;align-items:center;gap:14px;padding-bottom:12px">{ic("relogio", 30)}'
            f'<span class="r" style="font-size:26px">{"Semana que vem" if DOM else "Amanhã" if ED == "fechamento" else "Agenda"}</span></div><div class="rows">{ag}</div></div>'
            f'<div class="cta"><span style="font-style:italic;font-size:36px">{"Fechamento às 19:00" if ED == "meiodia" else "Próxima edição às 07:00" if ED == "fechamento" else "Edição completa no feed"}</span><span class="m cz" style="font-size:26px">{e(PERFIL)}</span></div>'
            f'</div></section>')


def spark(serie, cor, h=170):
    v = [float(x) for x in serie]
    lo, hi = min(v), max(v)
    w, pad = 936, 10
    pts = [(pad + i * (w - 2 * pad) / (len(v) - 1), pad + (h - 2 * pad) * (1 - ((x - lo) / (hi - lo) if hi > lo else .5))) for i, x in enumerate(v)]
    lin = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    x, y = pts[-1]
    return (f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="display:block;margin-top:14px"><polyline points="{lin}" fill="none" '
            f'stroke="var(--{cor})" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="var(--{cor})"/></svg>')


FOTOS = pathlib.Path(__file__).parent / "fotos"
RAW_FOTOS = "https://raw.githubusercontent.com/JSO98-Dev/o-sino-app/main/gerador/fotos/"
PALAVRAS = [
    ("petroleo", r"petr[óo]leo|brent|\bwti\b|opep|ormuz|petrobras"),
    ("ouro", r"\bouro\b"),
    ("boi", r"\bboi\b|pecu[áa]ria|arroba|carne bovina"),
    ("graos", r"\bsoja\b|\bmilho\b|safra|gr[ãa]os|\btrigo\b|\bcaf[ée]\b"),
    ("china", r"\bchina\b|chin[êe]s|pequim|xangai"),
    ("capitolio", r"\bfed\b|treasury|\beua\b|trump|washington|casa branca|powell"),
    ("porto", r"tarifa|exporta|importa|com[ée]rcio exterior|\bfrete\b|navio"),
    ("congresso", r"senado|c[âa]mara|congresso|\bstf\b|governo|\blula\b|minist|planalto|fiscal|reforma|\bplp\b|\bpec\b"),
    ("dinheiro", r"d[óo]lar|c[âa]mbio|\breal\b|infla[çc][ãa]o|\bipca\b|juros|selic|copom|banco central"),
    ("bolsa", r"ibovespa|\bbolsa\b|a[çc][õo]es|\bb3\b|nasdaq|s&p|balan[çc]o|lucro"),
    ("saopaulo", r"varejo|emprego|\bpib\b|ind[úu]stria|imobili"),
]
PADRAO = {"ECONOMIA": "dinheiro", "POLÍTICA": "congresso", "AGRO": "graos", "INTERNACIONAL": "porto",
          "ANÁLISE": "jornal", "MERCADOS": "bolsa"}
_CAT = None


def catalogo():
    global _CAT
    if _CAT is None:
        try:
            _CAT = json.load(open(FOTOS / "catalogo.json"))
        except Exception:
            try:
                _CAT = json.loads(urllib.request.urlopen(RAW_FOTOS + "catalogo.json", timeout=20).read())
            except Exception:
                _CAT = {}
    return _CAT


def foto(ed, c):
    """Caminho local de uma foto do banco para o card (campo "foto" ou palavras-chave ou assunto); None se não houver."""
    cat = catalogo()
    if not cat:
        return None
    k = c.get("foto") if c.get("foto") in cat else None
    if not k:
        for txt in (c.get("titulo", ""), c.get("dado", "")):
            k = next((k for k, rx in PALAVRAS if k in cat and _re.search(rx, txt.lower())), None)
            if k:
                break
    k = k or PADRAO.get(assunto(c), "bolsa")
    lst = cat.get(k) or cat.get("bolsa") or []
    if not lst:
        return None
    nome = lst[int(hashlib.md5((ed["data"] + c.get("titulo", "")).encode()).hexdigest(), 16) % len(lst)]
    f = FOTOS / nome
    if not f.exists():
        try:
            FOTOS.mkdir(exist_ok=True)
            f.write_bytes(urllib.request.urlopen(RAW_FOTOS + nome, timeout=30).read())
        except Exception:
            return None
    return f


def quadro(ed, c, h=None, num=118, minh=240):
    """Foto do assunto com o número em destaque sobreposto; cai para visual() sem foto."""
    f = foto(ed, c)
    if not f:
        return None
    d = c.get("destaque") or {}
    sob = ""
    if d.get("valor"):
        k = {"↑": "up", "↓": "down", "→": "flat"}.get(d.get("dir"), sinal(d["valor"]))
        sob = (f'<div class="sob"><span class="r" style="font-size:22px;color:var(--papel)">{e(d.get("rotulo", ""))}</span>'
               f'<div class="num {k}c" style="font-size:{num}px">{ic(k, round(num * .78), sw=2.8)}{e(d["valor"])}</div></div>')
    alt = f"height:{h}px;flex:none" if h else f"flex:1 1 0;min-height:{minh}px"
    return f'<div class="foto" style="{alt};background-image:url(\'file://{f}\')">{sob}</div>'


def assunto(c):
    return c.get("assunto") or ASSUNTO.get(c["tag"], "ECONOMIA")


def visual(c, num=184, sh=170, ico=260):
    d = c.get("destaque") or {}
    if d.get("valor"):
        k = {"↑": "up", "↓": "down", "→": "flat"}.get(d.get("dir"), sinal(d["valor"]))
        cor = {"up": "alta", "down": "queda"}.get(k, "cinza")
        serie = c.get("serie") or []
        return (f'<span class="r cz" style="font-size:24px">{e(d.get("rotulo", ""))}</span>'
                f'<div class="num {k}" style="font-size:{num}px">{ic(k, round(num * .82), sw=2.6)}{e(d["valor"])}</div>'
                + (spark(serie, cor, sh) + f'<span class="r cz" style="font-size:18px;margin-top:6px">{"Últimas" if DOM else "Últimos"} {len(serie)} {"semanas" if DOM else "pregões"}</span>' if len(serie) >= 3 else ""))
    return f'<div class="icone">{ic(assunto(c), ico, sw=1.1)}</div>'


def manchete(ed, c):
    a = assunto(c)
    q = quadro(ed, c, num=150)
    vis = q or f'<div class="painel">{visual(c)}</div>'
    txt, _ = data_ext(ed["data"])
    nota = "Edição completa disponível no feed"
    return (f'<section class="s mch"><div class="regua"></div><div class="mini">{A2}<span class="r" style="font-size:18px">{hora_ed()} · {txt}</span></div><div class="fil"></div>'
            f'<div class="body"><span class="r tag">{e(a)}</span><h1>{e(c["titulo"])}</h1><p class="dek">{e(c["dado"])}</p>'
            f'{vis}</div>'
            f'<div class="foot"><span class="r" style="font-size:20px;letter-spacing:.08em">{e(PERFIL)}</span><i>{e(nota)}</i></div></section>')


def placar(ed, n):
    rot = {"Dólar/Real": "Dólar", "Nasdaq Composite": "Nasdaq", "DI Jan/28": "DI jan/28", "Soja CBOT": "Soja Chicago"}
    un = {"Ibovespa": "pts", "S&P 500": "pts", "Nasdaq Composite": "pts", "Dólar/Real": "R$", "DI Jan/28": "% a.a. · var. em bps",
          "Ouro": "US$/oz", "Brent": "US$/barril", "Boi gordo": "R$/@ · Cepea", "Soja CBOT": "US¢/bu", "Milho": "R$/saca · Cepea", "IFIX": "pts"}
    rows, ant = "", None
    for x in ed["placar"]:
        g = GRUPO.get(x["ativo"])
        u = un.get(x["ativo"], "")
        if x["ativo"] == "Soja CBOT" and x.get("codigo"):
            u += f' · {x["codigo"]}'
        rows += (f'<tr class="{"g" if ant is not None and g != ant else ""}"><td>{e(rot.get(x["ativo"], x["ativo"]))}<small>{e(u)}</small></td>'
                 f'<td>{e(limpa(x["fechamento"]))}</td>'
                 + "".join(f'<td>{var(x[k].replace(" bps", ""), 24)}</td>' for k in (VK(), "var_mes", "var_ano")) + "</tr>")
        ant = g
    ref = ed["placar"][0]["data_ref"]
    return (f'<section class="s">{mini(ed, "Mercados")}<div class="body"><div class="tit"><h2>{"A semana em números" if DOM else "Fechamento de " + e(ref)}</h2>'
            f'<span class="r cz" style="font-size:18px">{"Variação na semana, no mês e no ano" if DOM else "Variação no dia, no mês e no ano"}</span></div>'
            f'<table><tr><th>Ativo</th><th>Fech.</th><th>{"Semana" if DOM else "Dia"}</th><th>Mês</th><th>Ano</th></tr>{rows}</table>'
            f'<p class="note">DI em pontos-base. ≈ indica base aproximada.</p></div>{foot(2, n, "Valores de fechamento. Fontes no último slide.")}</section>')


def fatos(ed, n, titulo):
    li = "".join(f'<div class="it"><span class="m n">{i:02d}</span><div><p>{e(f["texto"])}</p><div class="r">Afeta: {e(f["afeta"])}</div></div></div>'
                 for i, f in enumerate(ed["fatos"], 1))
    return (f'<section class="s">{mini(ed, "Manchetes")}<div class="body"><div class="tit"><h2>{e(titulo)}</h2></div>'
            f'<div>{li}</div></div>{foot(3, n)}</section>')


def foco(ed, c, n, idx):
    p = c["porque"]
    k = p.rfind("Observe")
    mec, obs = (p[:k].strip(), p[k:].strip()) if k > 0 else (p, "")
    dirk = {"↑": "up", "↓": "down", "→": "flat"}
    imp = "".join(f'<span class="{dirk.get(i["dir"], "flat")}">{ic(dirk.get(i["dir"], "flat"), 22)}<span style="color:var(--tinta)">{e(i["ativo"])}</span></span>'
                  for i in c["impacto"])
    d = c.get("destaque") or {}
    dq = ""
    if d.get("valor"):
        k = {"↑": "up", "↓": "down", "→": "flat"}.get(d.get("dir"), sinal(d["valor"]))
        dq = (f'<div class="dq"><div class="num {k}">{ic(k, 64, sw=2.6)}{e(d["valor"])}</div>'
              f'<span class="r cz" style="font-size:22px">{e(d.get("rotulo", ""))}</span></div>')
    return (f'<section class="s">{mini(ed, "Análise")}<div class="body"><span class="r tag" style="margin-top:28px;font-size:20px">{e(assunto(c))}</span>'
            f'<h2 class="f" style="margin-top:14px">{e(c["titulo"])}</h2>{dq}'
            f'<p class="dado">{e(c["dado"])}</p>'
            f'<div class="blk"><div class="r vm">Por que importa</div><p>{e(mec)}</p></div>'
            + (f'<div class="blk obs"><div class="r">{"O que observar na semana" if DOM else "O que observar amanhã" if ED == "fechamento" else "O que observar hoje"}</div><p>{e(cap1(obs.removeprefix("Observe ")))}</p></div>' if obs else "")
            + f'<div class="imp"><span class="r cz" style="font-size:18px">Impacto</span>{imp}</div>'
            f'<p class="note" style="margin-top:auto">Fontes: {e(", ".join(x["nome"] for x in c["fontes"]))}</p></div>{foot(idx, n)}</section>')


def madrugada(ed, n, idx):
    hdr = ('<div class="hdr" style="grid-template-columns:1fr 110px 220px 150px"><span class="r cz" style="font-size:18px">Ativo</span>'
           '<span class="r cz" style="font-size:18px">Hora</span><span class="r cz" style="font-size:18px;text-align:right">Valor</span>'
           '<span class="r cz" style="font-size:18px;text-align:right">Var.</span></div>')
    rows = "".join(f'<div class="row md"><div class="t">{e(m["ativo"])}</div><div class="m h">{e(m.get("hora", ""))}</div>'
                   f'<div class="m val">{e(m["valor"])}</div><div style="text-align:right">{var(m["var"], 24)}</div></div>' for m in ed["madrugada"])
    return (f'<section class="s">{mini(ed, "Mundo")}<div class="body"><div class="tit"><h2>Como o mundo amanheceu</h2>'
            f'<span class="r cz" style="font-size:18px">Horário de Brasília</span></div>{hdr}{rows}</div>{foot(idx, n)}</section>')


def agenda(ed, n, idx):
    w = 250 if DOM else 150
    hdr = (f'<div class="hdr" style="grid-template-columns:{w}px 1fr auto"><span class="r cz" style="font-size:18px">{"Dia e hora" if DOM else "Hora"}</span>'
           '<span class="r cz" style="font-size:18px">Evento</span><span class="r cz" style="font-size:18px;text-align:right">Consenso</span></div>')
    rows = "".join(f'<div class="row{" dom" if DOM else ""}"><div class="m h">{e((a.get("dia", "") + " " + a["hora"]).strip())}</div><div class="t">{e(a["evento"])}</div>'
                   f'<div class="m c">{"" if a["consenso"].startswith("n/d") else e(a["consenso"])}</div></div>' for a in ed["agenda"])
    return (f'<section class="s">{mini(ed, "Agenda")}<div class="body"><div class="tit"><div class="ic">{ic("relogio", 44)}'
            f'<h2>{"A semana que vem" if DOM else "O que acompanhar amanhã" if ED == "fechamento" else "O que acompanhar hoje"}</h2></div><span class="r cz" style="font-size:18px">Horário de Brasília</span></div>'
            f'{hdr}<div style="border-top:none">{rows}</div></div>{foot(idx, n, "Projeções: consenso do mercado.")}</section>')


def nomes(lst):
    vistos = []
    for y in lst:
        for x in str(y).split(" / "):
            x = _re.split(r" \(| — | via ", x)[0].strip()
            if x and x not in vistos:
                vistos.append(x)
    return ", ".join(vistos)


def fontes(ed, focos, n, idx):
    sec = [("Mercados", nomes(x.get("fonte", "") for x in ed["placar"])),
           ("Análise", nomes(f["nome"] for c in focos for f in c.get("fontes", []))),
           ("Mundo", nomes(m.get("fonte", "") for m in ed.get("madrugada", []))),
           ("Agenda", nomes(f["nome"] for f in ed.get("agenda_fontes", [])))]
    src = "".join(f'<div class="src"><span class="r">{k}</span><p>{e(v)}</p></div>' for k, v in sec if v)
    _, d = data_ext(ed["data"])
    hora = str(ed.get("publicado_em", ""))[11:16]
    if DOM:
        prox = "segunda, às 07:00"
    elif d.weekday() == 5:
        prox = "domingo, resumo às 19:00"
    else:
        prox = "amanhã, às 07:00"
    selo = A1.replace('fill="#A3201B"', 'fill="none"')
    selo_html = (f'<div class="selo"><div class="regua" style="height:10px"></div>{selo}<div class="fil"></div>'
                 f'<div style="display:flex;justify-content:space-between;align-items:baseline"><span class="r" style="font-size:15px">{"Edição de domingo" if DOM else "Edição diária"}</span>'
                 f'<span class="m vm" style="font-size:20px">{hora_ed()}</span></div></div>')
    return (f'<section class="s">{mini(ed, "Fontes")}<div class="body"><div class="tit"><h2>Fontes</h2></div>'
            f'<div style="border-bottom:1px solid var(--linha)">{src}</div>'
            f'<div class="exp"><div><div class="r" style="font-size:20px;margin-bottom:8px">Expediente</div>'
            f'<p>O Sino · jornal financeiro diário<br>Edição Nº {ed["numero"]:03d}{" · fechada às " + hora if hora else ""}, horário de Brasília<br>Próxima edição: {prox}</p></div>{selo_html}</div>'
            f'</div>{foot(idx, n, "Os fatos antes do sino.")}</section>')


def VK():
    return "var_semana" if DOM else "var_dia"


def build(ed):
    global DOM, ED
    DOM = "var_semana" in ed["placar"][0]
    ED = ed.get("edicao", "abertura")
    cards = sorted(ed["cards"], key=lambda c: -c["relevancia"])
    principal = cards[0]
    wd = data_ext(ed["data"])[1].weekday()
    titulo_fatos = "O que marcou a semana" if DOM else "O que marcou o dia" if ED == "fechamento" else "O que mudou no fim de semana" if wd in (0, 6) else "O que mudou nas últimas 24 horas"
    sem_md = DOM or not ed.get("madrugada")
    N = 7 if sem_md else 8
    slides = [capa(ed, principal, N), placar(ed, N), fatos(ed, N, titulo_fatos), foco(ed, cards[0], N, 4), foco(ed, cards[1], N, 5)]
    slides += [agenda(ed, N, 6)] if sem_md else [madrugada(ed, N, 6), agenda(ed, N, 7)]
    slides += [fontes(ed, cards[:2], N, N)]
    extras = [manchete(ed, c) for c in cards if c.get("manchete")]
    return slides, story(ed, principal), extras


FIT = """
<script>
window.__fit = () => {
  const b = document.querySelector('.body');
  if (!b) return 1;
  let z = 1;
  while (b.scrollHeight > b.clientHeight + 1 && z > 0.84) { z -= 0.02; b.style.zoom = z; }
  return b.scrollHeight > b.clientHeight + 1 ? -z : z;
};
</script>"""


def page(body):
    return f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>{font_css()}{CSS}</style>{FIT}</head><body>{body}</body></html>"


if __name__ == "__main__":
    ed = json.load(open(sys.argv[1]))
    out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    slides, st, extras = build(ed)
    with sync_playwright() as p:
        b = p.chromium.launch()
        nomes_png = [f"slide-{i}.png" for i in range(1, len(slides) + 1)] + ["story.png"] + [f"manchete-{i}.png" for i in range(1, len(extras) + 1)]
        for name, s in zip(nomes_png, slides + [st] + extras):
            is_story = name == "story.png"
            h = 1920 if is_story else 1350
            pg = b.new_page(viewport={"width": 1080, "height": h})
            f = out / "tmp.html"; f.write_text(page(s)); pg.goto(f"file://{f}")
            pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            z = pg.evaluate("window.__fit()")
            if z < 0:
                print(f"AVISO: {name} não coube mesmo reduzido a {-z:.0%}; encurte o texto.")
            elif z < 1:
                print(f"AVISO: {name} reduzido a {z:.0%} para caber.")
            pg.screenshot(path=str(out / name)); pg.close()
        (out / "tmp.html").unlink()
        b.close()
    print("ok", out)
