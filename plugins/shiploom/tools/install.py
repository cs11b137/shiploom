import os, shutil, sys
from pathlib import Path
src, target = map(Path, sys.argv[1:])
items = [p for p in src.rglob('*') if p.is_file()]
collisions = [str(p.relative_to(src)) for p in items if (target / p.relative_to(src)).exists() or (target / p.relative_to(src)).is_symlink()]
if collisions:
    sys.exit('已停止：目标文件已存在，未写入任何文件：\n' + '\n'.join(collisions))
for p in items:
    dst = target / p.relative_to(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)
print('已安装。请先配置 harness/verify.json，并按 README 完成安全配置。')
