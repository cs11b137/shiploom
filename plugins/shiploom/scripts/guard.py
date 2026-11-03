#!/usr/bin/env python3
"""Conservative tripwire, not a shell parser or security sandbox."""
import json, re, sys
try:
    event = json.load(sys.stdin)
    tool = event['tool_name']; inp = event['tool_input']
    if tool == 'Bash':
        cmd = inp['command']
        patterns = [r'\bgit\s+(?:-[^\s]+\s+\S+\s+)*(?:commit|merge|push|reset|clean|branch\s+-[dD]|worktree\s+(?:remove|prune))\b', r'\b(?:rm|rmdir|unlink|shred)\b', r'\b(?:deploy|release|publish)\b']
        if any(re.search(p, cmd, re.I) for p in patterns):
            raise ValueError('受控操作：停止并交由人确认和执行')
    elif tool in ('Write','Edit'):
        path = inp['file_path'].replace('\\', '/')
        if re.search(r'(^|/)\.env(?:\.|$)', path):
            raise ValueError('禁止修改凭据文件')
except Exception as e:
    print('Harness 拒绝工具调用：' + str(e), file=sys.stderr)
    sys.exit(2)
