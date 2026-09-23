#!/usr/bin/env python3
"""Local fixture tests of release configuration and archive integrity.
No external service is contacted and fixture reuse text is never distributed.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def run(*args: str,success: bool=True) -> subprocess.CompletedProcess:
    p=subprocess.run([sys.executable,*args],capture_output=True,text=True,timeout=30)
    if (p.returncode==0)!=success:
        raise RuntimeError(f'Unexpected result for {args}: {p.returncode}\n{p.stdout}\n{p.stderr}')
    return p


def main() -> None:
    n=0
    with tempfile.TemporaryDirectory() as td:
        r=Path(td)/'repo';r.mkdir();(r/'manuscript').mkdir();(r/'src').mkdir()
        for f in ('README.md','release.json','CITATION.cff'):
            shutil.copy2(ROOT/f,r/f)
        shutil.copy2(ROOT/'manuscript/main.tex',r/'manuscript/main.tex')
        # Reset fixture metadata even when the real package has been configured.
        c=json.loads((r/'release.json').read_text())
        c.update(repository=None,tag=None,code_license_file=None,data_license_file=None)
        (r/'release.json').write_text(json.dumps(c))
        cfg=str(ROOT/'src/configure_release.py');pkg=str(ROOT/'src/package_repository.py')
        run(cfg,'--root',str(r),'--check',success=False);n+=1
        for owner in ('bad owner/repo','a/../../b','https://github.com/a/b'):
            run(cfg,'--root',str(r),'--repository',owner,'--tag','v1.0.0',success=False);n+=1
        run(cfg,'--root',str(r),'--repository','example-owner/wilf-s8','--tag','../v1',success=False);n+=1
        run(cfg,'--root',str(r),'--repository','example-owner/wilf-s8','--tag','v1.0.0','--code-license','../outside',success=False);n+=1
        (r/'LICENSE.txt').write_text('NONPUBLIC TEST FIXTURE, not a license grant.')
        run(cfg,'--root',str(r),'--repository','example-owner/wilf-s8','--tag','v1.0.0','--code-license','LICENSE.txt','--data-license','LICENSE.txt');n+=1
        run(cfg,'--root',str(r),'--check');n+=1
        run(pkg,'--root',str(r),'--manifest-only');n+=1
        run(pkg,'--root',str(r),'--check-manifest');n+=1
        out=Path(td)/'one.zip';run(pkg,'--root',str(r),'--output',str(out));data=out.read_bytes();n+=1
        run(pkg,'--root',str(r),'--output',str(out))
        if data!=out.read_bytes():raise RuntimeError('ZIP is not deterministic')
        n+=1
        with zipfile.ZipFile(out) as z:
            if any('..' in Path(x).parts or x.startswith('/') for x in z.namelist()):raise RuntimeError('unsafe ZIP name')
        n+=1
        (r/'README.md').write_text('corrupted')
        run(pkg,'--root',str(r),'--check-manifest',success=False);n+=1
        run(cfg,'--root',str(r),'--check',success=False);n+=1
        run(pkg,'--root',str(r),'--manifest-only')
        m=r/'SHA256SUMS';m.write_text(m.read_text()+m.read_text().splitlines()[0]+'\n')
        run(pkg,'--root',str(r),'--check-manifest',success=False);n+=1
    print(f'Release/package fixture checks: {n} passed; no remote actions.')

if __name__=='__main__':main()
