#!/usr/bin/env python3
"""Create/check a complete source manifest and a reproducible companion ZIP.
Only the explicit reader-facing roots are packaged; build products and local
review material are excluded. This performs no remote or publishing action.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
TOP_FILES={'README.md','SOURCE_MAP.md','Makefile','requirements.txt','release.json',
           'CITATION.cff','LICENSE_STATUS.md','.gitignore','.gitattributes'}
DIRS={'src','data','checks','reference','manuscript','docs','.github','LICENSES'}
EXTS={'.py','.cpp','.h','.hpp','.sh','.md','.json','.txt','.csv','.tsv','.log',
      '.tex','.pdf','.bib','.yml','.yaml','.cff'}
BUILD_EXTS={'.aux','.out','.fls','.fdb_latexmk','.synctex.gz','.pyc','.o'}


def payload(root: Path) -> list[Path]:
    result=[]
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if any(part in {'.git','.venv','__pycache__','dist','build'} for part in rel.parts):
            continue
        if p.is_symlink():
            raise ValueError(f'symlinks are not packaged: {rel}')
        if not p.is_file() or rel.as_posix()=='SHA256SUMS':continue
        if len(rel.parts)==1:
            if p.name not in TOP_FILES and not p.name.startswith(('LICENSE','COPYING','NOTICE')):
                continue
        else:
            if rel.parts[0] not in DIRS:continue
            if p.suffix not in EXTS:continue
            if rel.parts[0]=='manuscript' and p.suffix=='.log':continue
        if p.suffix in BUILD_EXTS:continue
        result.append(p)
    return result


def digest(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()


def manifest_text(root: Path) -> str:
    return ''.join(f'{digest(p)}  {p.relative_to(root).as_posix()}\n' for p in payload(root))


def verify_manifest(root: Path) -> int:
    path=root/'SHA256SUMS'
    actual=path.read_text(encoding='utf-8')
    seen=set()
    for line in actual.splitlines():
        if not re.fullmatch(r'[0-9a-f]{64}  [^\r\n]+',line):
            raise ValueError('malformed manifest record')
        name=line[66:]
        if name in seen:raise ValueError(f'duplicate manifest record: {name}')
        seen.add(name)
    if actual!=manifest_text(root):raise ValueError('manifest mismatch: refresh only after reviewing the changed files')
    return len(seen)


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=ROOT)
    g=ap.add_mutually_exclusive_group()
    g.add_argument('--manifest-only',action='store_true')
    g.add_argument('--check-manifest',action='store_true')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args();root=args.root.resolve()
    if not (root/'manuscript/main.tex').is_file():raise ValueError('not a companion repository root')
    if args.check_manifest:
        print(f'Manifest: {verify_manifest(root)} files passed.');return
    (root/'SHA256SUMS').write_text(manifest_text(root),encoding='utf-8')
    n=verify_manifest(root)
    if args.manifest_only:
        print(f'Manifest: {n} file identities written and checked.');return
    version=json.loads((root/'release.json').read_text())['version']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',version):raise ValueError('unsafe version')
    out=(args.output or root/'dist'/f'wilf-s8-{version}.zip').resolve()
    if out.is_relative_to(root) and not out.is_relative_to(root/'dist'):
        raise ValueError('inside the repository, output must be under dist/')
    out.parent.mkdir(parents=True,exist_ok=True)
    entries=payload(root)+[root/'SHA256SUMS']
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(entries):
            info=zipfile.ZipInfo('wilf-s8/'+p.relative_to(root).as_posix(),(2026,9,21,0,0,0))
            info.create_system=3
            info.external_attr=(0o100755 if p.suffix=='.sh' else 0o100644)<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(out) as z:
        if z.testzip() is not None:raise ValueError('ZIP integrity failure')
    checksum=out.with_suffix(out.suffix+'.sha256')
    checksum.write_text(f'{digest(out)}  {out.name}\n')
    print(f'Packaged {n+1} files: {out}\nSHA-256: {digest(out)}')

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError) as e:
        print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
