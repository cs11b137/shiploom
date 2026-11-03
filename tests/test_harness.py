import json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
SRC=Path(__file__).resolve().parents[1]/'plugins/shiploom'

class HarnessTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)/'project'; self.root.mkdir()
        self.run_cmd([str(SRC/'init.sh'),str(self.root)])
    def tearDown(self): self.temp.cleanup()
    def run_cmd(self, cmd, ok=True, **kw):
        p=subprocess.run(cmd,cwd=self.root,text=True,capture_output=True,**kw)
        if ok: self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        else: self.assertNotEqual(p.returncode,0,p.stdout+p.stderr)
        return p
    def flow(self,*args,ok=True): return self.run_cmd(['python3','harness/flow.py',*args],ok=ok)
    def test_collision_is_atomic(self):
        before=(self.root/'AGENTS.md').read_text(); self.run_cmd([str(SRC/'init.sh'),str(self.root)],ok=False)
        self.assertEqual(before,(self.root/'AGENTS.md').read_text())
    def test_verify_fail_closed_and_report(self):
        self.run_cmd(['python3','harness/verify.py','full'],ok=False)
        (self.root/'harness/verify.json').write_text(json.dumps({'full':[['python3','-c','print(42)']]}))
        self.run_cmd(['python3','harness/verify.py','full'])
        self.assertTrue(json.loads((self.root/'.harness/verify-full.json').read_text())['passed'])
        (self.root/'harness/verify.json').write_text(json.dumps({'full':[['python3','-c','raise SystemExit(7)']]}))
        self.run_cmd(['python3','harness/verify.py','full'],ok=False)
        self.assertFalse(json.loads((self.root/'.harness/verify-full.json').read_text())['passed'])
    def test_bug_and_review_limits(self):
        self.flow('init','bug'); self.flow('bug-fail','bug'); self.flow('bug-fail','bug')
        self.flow('bug-fail','bug',ok=False)
        (self.root/'evidence.txt').write_text('redacted evidence')
        self.flow('bug-evidence','bug','evidence.txt'); self.flow('bug-fail','bug'); self.flow('bug-fail','bug',ok=False)
        (self.root/'plan.txt').write_text('new plan')
        self.flow('replan','bug','plan.txt'); self.flow('bug-fail','bug')
        for _ in range(3): self.flow('review-start','bug'); self.flow('review-result','bug','fail')
        self.flow('review-start','bug',ok=False)
    def test_hook(self):
        def event(cmd): return json.dumps({'tool_name':'Bash','tool_input':{'command':cmd}})
        self.run_cmd(['python3','harness/guard.py'],input=event('git status'))
        self.run_cmd(['python3','harness/guard.py'],input=event('git commit -m x'),ok=False)
        self.run_cmd(['python3','harness/guard.py'],input='invalid',ok=False)
    def test_worktree(self):
        self.run_cmd(['git','init','-q']); self.run_cmd(['git','config','user.email','test@example.invalid']); self.run_cmd(['git','config','user.name','Test'])
        self.run_cmd(['git','add','.']); self.run_cmd(['git','commit','-qm','initial'])
        self.run_cmd(['python3','harness/worktree.py','start','feature'])
        other=self.root.parent/'project-harness-feature'
        self.assertTrue((other/'harness/flow.py').exists())
        self.run_cmd(['python3','harness/worktree.py','start','feature'],ok=False)
    def test_beta_default_off(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('flag',self.root/'examples/beta_flag.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        self.assertFalse(m.enabled('a')); self.assertTrue(m.enabled('a',beta_enabled=True,percent=100)); self.assertFalse(m.enabled('a',beta_enabled=True,percent=0))

if __name__=='__main__': unittest.main()
