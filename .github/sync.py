import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone

PASTA = '1N6jEp24YigCB55VWuPpBemDe7NKscYVJ'
TOPICO = os.environ.get('NTFY_TOPIC') or 'osino-0162925b313e872b'
APP = 'https://jso98-dev.github.io/o-sino-app/'
ARQ = 'editions.json'
TIPO = {'domingo': 'Domingo', 'meiodia': 'Meio-dia', 'fechamento': 'Fechamento'}
ORDEM = {'meiodia': 2, 'fechamento': 3}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            erro = e
            time.sleep(3)
    raise erro


def chave(e):
    if e.get('t') == 'manchete':
        return e['d'] + '-' + str(e.get('k', ''))
    return e['d'] + ('-' + e['t'] if e.get('t') in ORDEM else '')


def recente(e, horas=12):
    try:
        c = datetime.fromisoformat(e['criado'].replace('Z', '+00:00'))
        if c.tzinfo is None:
            c = c.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - c).total_seconds() < horas * 3600
    except Exception:
        return False


def avisar(grupo):
    base = next((x for x in grupo if x.get('t') != 'manchete'), grupo[0])
    ext = sum(1 for x in grupo if x.get('t') == 'manchete' and x is not base)
    tipo = base.get('o') if base.get('t') == 'manchete' else base.get('t')
    d = base['d'].split('-')
    corpo = {
        'topic': TOPICO,
        'title': f"O Sino · {TIPO.get(tipo, 'Abertura')} {d[2]}/{d[1]}",
        'message': (base.get('m') or 'Pronta para aprovar') + (f" · +{ext} manchete{'s' if ext > 1 else ''}" if ext else ''),
        'click': APP + '#ed=' + chave(base),
        'tags': ['bell'],
        'priority': 4,
    }
    req = urllib.request.Request('https://ntfy.sh', data=json.dumps(corpo).encode(),
                                 headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req, timeout=30).read()


try:
    base = json.load(open(ARQ, encoding='utf-8'))
except Exception:
    base = {'edicoes': [], 'vistos': []}
edicoes = {chave(e): e for e in base.get('edicoes', [])}
vistos = set(base.get('vistos', []))

pagina = get(f'https://drive.google.com/embeddedfolderview?id={PASTA}').decode('utf-8', 'replace')
arquivos = re.findall(r'id="entry-([\w-]+)".*?class="flip-entry-title">([^<]+)<', pagina, re.S)
print(len(arquivos), 'arquivos na pasta')

novos = []
for fid, nome in arquivos:
    if fid in vistos or not nome.strip().endswith('.json'):
        continue
    try:
        e = json.loads(get(f'https://drive.google.com/uc?export=download&id={fid}').decode('utf-8'))
        assert e.get('d') and isinstance(e.get('s'), list)
    except Exception as err:
        print('ignorado', nome, err)
        continue
    k = chave(e)
    atual = edicoes.get(k)
    if not atual or (e.get('criado') or '') >= (atual.get('criado') or ''):
        edicoes[k] = e
        novos.append(e)
    vistos.add(fid)
    print('novo', nome)

lista = sorted(edicoes.values(), key=lambda e: (e['d'], ORDEM.get(e.get('o') if e.get('t') == 'manchete' else e.get('t'), 1), e.get('t') != 'manchete', -int(re.sub(r'\D', '', str(e.get('k', ''))) or 0)), reverse=True)[:150]
saida = {'edicoes': lista, 'vistos': sorted(vistos)}
if saida != base:
    json.dump(saida, open(ARQ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

grupos = {}
for e in novos:
    if recente(e):
        grupos.setdefault((e['d'], e.get('o') if e.get('t') == 'manchete' else e.get('t')), []).append(e)
for g in grupos.values():
    try:
        avisar(g)
        print('aviso', chave(g[0]), len(g))
    except Exception as err:
        print('aviso falhou', err, file=sys.stderr)
