"""Package the installable mod and a native, editable FNFC chart archive."""
from pathlib import Path
import json
import zipfile

root=Path(__file__).resolve().parents[1]
mod=root/'mods/energize'
dist=root/'dist';dist.mkdir(exist_ok=True)
with zipfile.ZipFile(dist/'energize-mod.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(mod.rglob('*')):
        if path.is_file():z.write(path,Path('energize')/path.relative_to(mod))
with zipfile.ZipFile(dist/'energize.fnfc','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('manifest.json',json.dumps({'version':'1.0.0','songId':'energize'}))
    for path in sorted((mod/'data/songs/energize').glob('*.json')):
        z.write(path,path.name)
    z.write(mod/'songs/energize/Inst.ogg','Inst.ogg')
print('Packaged dist/energize-mod.zip and dist/energize.fnfc')
