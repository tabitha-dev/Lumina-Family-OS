from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
from PIL import Image
source = "https://cdn.openart.ai/openart-ai/production/2026-10/create-image/HOjo8ynMh9nVC5lV2qAW/image_1793307065208_08a10c51_1793307065584_2915d5ca.png"
req=Request(source,headers={"User-Agent":"Lumina-Family-OS/1.0"})
with urlopen(req,timeout=45) as r: data=r.read(22000000)
with Image.open(BytesIO(data)) as im:
    im.load()
    assert im.width > 1600 and im.height > 850
    im = im.convert("RGB")
    im.thumbnail((1800,1100),Image.Resampling.LANCZOS)
    dest=Path("assets/lumina-hero.webp")
    dest.parent.mkdir(exist_ok=True)
    im.save(dest,"WEBP",quality=82,method=6)
    print(str(dest),im.size,dest.stat().st_size)
