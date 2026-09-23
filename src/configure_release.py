#!/usr/bin/env python3
"""Configure intended GitHub release/citation locations locally. No network,
publication, license selection, legal interpretation, or public-access check.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
START='% BEGIN RELEASE AVAILABILITY'
END='% END RELEASE AVAILABILITY'


def replace_once(s: str,start: str,end: str,body: str) -> str:
    if s.count(start)!=1 or s.count(end)!=1 or s.index(start)>=s.index(end):
        raise ValueError('missing, repeated, or misordered release markers')
    a=s.index(start)+len(start);b=s.index(end)
    return s[:a]+'\n'+body.rstrip()+'\n'+s[b:]


def valid_repo(value: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9][A-Za-z0-9._-]{0,99}',value)) and '..' not in value


def license_path(root: Path,name: str) -> str:
    p=Path(name)
    if p.is_absolute() or '..' in p.parts:raise ValueError('license paths must be relative and inside the repository')
    target=root/p
    if not target.resolve().is_relative_to(root) or not target.is_file() or not target.read_text().strip():
        raise ValueError(f'missing or empty license file: {name}')
    return p.as_posix()


def citation(config: dict) -> str:
    url=f'https://github.com/{config["repository"]}/releases/tag/{config["tag"]}'
    return f'''cff-version: 1.2.0
message: "Please cite the paper and this exact code/certificate release."
type: software
title: "The Ray–West parameter and the Wilf classification of permutations of length eight: code and certificates"
authors:
  - family-names: Liu
    given-names: Mingchang
version: "{config['version']}"
repository-code: "https://github.com/{config['repository']}"
url: "{url}"
preferred-citation:
  type: unpublished
  title: "The Ray–West parameter and the Wilf classification of permutations of length eight"
  authors:
    - family-names: Liu
      given-names: Mingchang
  year: 2026
  notes: "Manuscript revision {config['manuscript_revision']}; cite the frozen companion release separately for the computation."
'''


def check(root: Path,c: dict) -> None:
    if not c.get('repository') or not valid_repo(c['repository']):raise ValueError('choose the actual OWNER/REPOSITORY first')
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?',c.get('tag') or ''):raise ValueError('choose a release tag such as v1.0.0')
    for key in ('code_license_file','data_license_file'):
        if not c.get(key):raise ValueError(f'author-selected terms not recorded: {key}')
        license_path(root,c[key])
    expected=citation(c)
    if (root/'CITATION.cff').read_text()!=expected:raise ValueError('citation metadata is not synchronized')
    url=f'https://github.com/{c["repository"]}/releases/tag/{c["tag"]}'
    for f in ('README.md','manuscript/main.tex'):
        if url not in (root/f).read_text():raise ValueError(f'release locator missing in {f}')


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--repository')
    p.add_argument('--tag')
    p.add_argument('--code-license')
    p.add_argument('--data-license')
    p.add_argument('--check',action='store_true')
    args=p.parse_args();root=args.root.resolve()
    c=json.loads((root/'release.json').read_text())
    if args.check:
        if any((args.repository,args.tag,args.code_license,args.data_license)):
            raise ValueError('--check cannot be combined with edits')
        check(root,c)
        print('Local release metadata and nonempty license paths: PASS. Public access, publication, and legal sufficiency are not checked.');return
    if not args.repository or not args.tag:raise ValueError('--repository and --tag are required for configuration')
    if not valid_repo(args.repository):raise ValueError('invalid OWNER/REPOSITORY')
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?',args.tag):raise ValueError('use a tag such as v1.0.0 or v1.0.0-rc1')
    c.update(repository=args.repository,tag=args.tag,version=args.tag[1:])
    for key,val in (('code_license_file',args.code_license),('data_license_file',args.data_license)):
        if val is not None:c[key]=license_path(root,val)
    url=f'https://github.com/{args.repository}/releases/tag/{args.tag}'
    readme=(root/'README.md').read_text()
    readme=replace_once(readme,'<!-- BEGIN RELEASE -->','<!-- END RELEASE -->',
        f'Computational companion: [release `{args.tag}`]({url}).\n'
        'The release contains the manuscript, exact certificates, verification\n'
        'code and retained computational records. See below for the scope of\n'
        'the quick checks and full regeneration commands.')
    tex=(root/'manuscript/main.tex').read_text()
    tex=replace_once(tex,START,END,
        'The code, certificates, row-level recounts and buildable source are\n'
        f'provided in the versioned companion at\n'
        f'\\href{{{url}}}{{\\texttt{{github.com/{args.repository}}} (tag \\texttt{{{args.tag}}})}}.\n'
        'The README distinguishes checks of retained evidence from full\n'
        'regeneration. The companion contains the complete $\\Sym_8$ certificate,\n'
        'move provenance, the $9{,}510$ retained direct-placement recounts,\n'
        'and the programs and inputs used for the structural checks.')
    # All validation above precedes writing any file.
    (root/'release.json').write_text(json.dumps(c,indent=2)+'\n')
    (root/'README.md').write_text(readme)
    (root/'manuscript/main.tex').write_text(tex)
    (root/'CITATION.cff').write_text(citation(c))
    if c.get('code_license_file') and c.get('data_license_file'):
        (root/'LICENSE_STATUS.md').write_text(
            '# Reuse terms recorded for this release\n\n'
            f"Code terms: `{c['code_license_file']}`.\n\n"
            f"Data terms: `{c['data_license_file']}`.\n\n"
            'These are the files supplied for this release. This index records\n'
            'their locations; it adds no license grant and does not assess their\n'
            'legal sufficiency. The manuscript may have separate terms. Preserve\n'
            'third-party notices and confirm authority over the earlier-stage\n'
            'material when selecting the applicable terms.\n')
    print('Configured intended release locator locally. Nothing was published. Rebuild the paper, verify, refresh the manifest, then follow docs/GITHUB_SETUP.md.')

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError) as e:
        print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
