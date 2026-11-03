#!/usr/bin/env python3
import re, subprocess, sys
from pathlib import Path
if len(sys.argv)!=3 or sys.argv[1]!='start' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',sys.argv[2]):
    sys.exit('用法：python3 harness/worktree.py start <task-id>')
task=sys.argv[2]; root=Path(__file__).resolve().parent.parent
p=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=root,text=True,capture_output=True)
if p.returncode: sys.exit('需要 Git 仓库和至少一个提交')
repo=Path(p.stdout.strip()); target=repo.parent/(repo.name+'-harness-'+task)
if target.exists() or target.is_symlink(): sys.exit('目标已存在，拒绝覆盖')
cmd=['git','worktree','add','-b','harness/'+task,str(target),'HEAD']
r=subprocess.run(cmd,cwd=repo)
if r.returncode: sys.exit(r.returncode)
print('已创建：',target,'；在此目录启动 Builder。不会自动合并或删除。')
