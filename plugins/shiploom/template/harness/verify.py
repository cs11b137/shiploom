#!/usr/bin/env python3
import datetime, json, os, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if len(sys.argv) != 2 or sys.argv[1] not in ('fast', 'feature', 'full'):
    sys.exit('用法：python3 harness/verify.py fast|feature|full')
level=sys.argv[1]
try:
    cfg=json.loads((root/'harness/verify.json').read_text())
    cmds=cfg[level]
    if not isinstance(cmds,list) or not cmds or not all(isinstance(c,list) and c and all(isinstance(x,str) and x for x in c) for c in cmds):
        raise ValueError('每个等级必须配置至少一个非空 argv 数组')
except (OSError, ValueError, KeyError) as e:
    sys.exit(f'验证未配置或配置错误：{e}')
report=root/'.harness'; report.mkdir(exist_ok=True)
head=subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,capture_output=True)
rows=[]
for cmd in cmds:
    try:
        proc=subprocess.run(cmd,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        rows.append({'argv':cmd,'exit':proc.returncode,'output':proc.stdout})
    except OSError as e:
        rows.append({'argv':cmd,'exit':127,'output':str(e)})
result={'level':level,'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':head.stdout.strip() or None,'worktree_dirty':bool(subprocess.run(['git','status','--porcelain'],cwd=root,text=True,capture_output=True).stdout.strip()),'commands':rows,'passed':all(r['exit']==0 for r in rows)}
path=report/f'verify-{level}.json'; path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for row in rows:
    print(f"{row['argv']}: exit {row['exit']}\n{row['output']}")
print(f'报告：{path}；日志可能含敏感信息，请先脱敏再分享。')
sys.exit(0 if result['passed'] else 1)
