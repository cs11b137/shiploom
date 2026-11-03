#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
args=sys.argv[1:]
def die(msg): sys.exit(msg)
if len(args)<2 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args[1]): die('用法：flow.py init|bug-fail|bug-evidence|replan|review-start|review-result <task-id> [参数]')
action,task=args[:2]; state=root/'.harness'/f'{task}.json'
if action=='init':
    if state.exists(): die('状态已存在，拒绝覆盖')
    state.parent.mkdir(exist_ok=True); data={'bug_failures':0,'bug_evidence':None,'stopped':False,'reviews':0,'review_open':False,'review_result':None,'history':[]}
else:
    if not state.exists(): die('请先 init')
    data=json.loads(state.read_text())
if action=='bug-fail':
    if data['stopped']: die('已停止，先完成重新规划')
    if data['bug_failures']==2 and not data['bug_evidence']: die('必须先记录第二次失败的证据')
    data['bug_failures']+=1
    if data['bug_failures']>=3: data['stopped']=True
    print('失败次数：',data['bug_failures'], '；第三次失败已停止，重新规划' if data['stopped'] else '；第二次后须收集证据' if data['bug_failures']==2 else '')
elif action in ('bug-evidence','replan'):
    if len(args)!=3: die('请提供非空证据或方案文件路径')
    path=Path(args[2]).resolve()
    if not path.is_file() or not path.read_text().strip(): die('文件不存在或为空')
    if action=='bug-evidence':
        if data['bug_failures']!=2 or data['stopped']: die('仅在第二次失败后记录证据')
        data['bug_evidence']=str(path)
    else:
        if not data['stopped']: die('仅在第三次失败停止后重新规划')
        data['bug_failures']=0; data['bug_evidence']=None; data['stopped']=False
elif action=='review-start':
    if data['stopped'] or data['review_open'] or data['reviews']>=3: die('已停止、已有审查进行中或已达三轮上限')
    data['reviews']+=1; data['review_open']=True; data['review_result']=None
elif action=='review-result':
    if len(args)!=3 or args[2] not in ('pass','fail') or not data['review_open']: die('需要进行中的审查和 pass|fail')
    data['review_open']=False; data['review_result']=args[2]
elif action!='init': die('未知操作')
data['history'].append({'action':action,'args':args[2:]})
state.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(data,ensure_ascii=False))
