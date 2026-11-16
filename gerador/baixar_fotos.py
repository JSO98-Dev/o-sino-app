"""Baixa as fotos do Pexels (licença livre) listadas em fotos_fontes.json para gerador/fotos/ (1080 px de largura)."""
import io, json, pathlib, urllib.request
from PIL import Image

base = pathlib.Path(__file__).parent
fontes = json.load(open(base / "fotos_fontes.json"))
saida = base / "fotos"; saida.mkdir(exist_ok=True)
cat = {}
for chave, ids in fontes.items():
    for pid in ids:
        nome = f"{chave}-{pid}.jpg"
        url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1600"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=60).read())).convert("RGB")
            if im.width > 1080:
                im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
            im.save(saida / nome, quality=82, optimize=True)
            cat.setdefault(chave, []).append(nome)
            print("ok", nome, im.size)
        except Exception as e:
            print("falhou", nome, e)
json.dump(cat, open(saida / "catalogo.json", "w"), indent=1)
