#!/usr/bin/env python3
"""Regression tests: malformed inputs and corrupted evidence must not pass."""
from __future__ import annotations
import csv, math, subprocess, tempfile, sys
from pathlib import Path
from check_known_sequences import check_cluster_output
from check_recount_records import check_csv
from recount_containment import parse_counter
ROOT=Path(__file__).resolve().parents[1]
passed=0

def require(ok: bool, why: str) -> None:
    if not ok:raise ValueError(why)

def rejected(call, name: str) -> None:
    global passed
    try:call()
    except (ValueError,KeyError):passed+=1;print(f'PASS rejected: {name}')
    else:raise ValueError(f'FALSE ACCEPTANCE: {name}')

def main() -> None:
    global passed
    valid='r=3 c_r=1 clusters=1 Av_3=5\nr=4 c_r=-6 clusters=6 Av_4=14\n'
    expected={3:(1,5),4:(-6,14)}
    check_cluster_output(valid,expected);passed+=1
    for text,name in [(valid.replace('Av_4=14','Av_4=15'),'wrong known value'),(valid.splitlines()[0],'missing known row'),(valid+valid.splitlines()[0]+'\n','duplicate known row'),('','empty known output')]:
        rejected(lambda t=text:check_cluster_output(t,expected),name)
    for text in ('','tau=12 n=5 g_3=119 Av_4=1','tau=12 n=5 g_3=118 Av_5=1','tau=21 n=5 g_3=119 Av_5=1'):
        rejected(lambda t=text:parse_counter(t,'12',5),'malformed or wrong-scope counter output')
    with (ROOT/'checks/bruteforce_all_n12.csv').open(newline='') as f:
        reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
    cert=ROOT/'data/S8_classes.csv'
    with tempfile.TemporaryDirectory() as td:
        target=Path(td)/'bad.csv'
        def write_and_check(data):
            with target.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(data)
            return check_csv(target,cert)
        rejected(lambda:write_and_check(rows[:-1]),'missing recount row')
        rejected(lambda:write_and_check(rows+[rows[-1]]),'duplicate recount row')
        bad=[dict(r) for r in rows];bad[-1]['stdout']='truncated output'
        rejected(lambda:write_and_check(bad),'malformed retained stdout')
        bad=[dict(r) for r in rows];r=bad[-1];r['g']=str(int(r['g'])+1);r['avoidance']=str(int(r['avoidance'])-1)
        r['stdout']=f"tau={r['representative']} n={r['n']} g_{int(r['n'])-8}={r['g']} Av_{r['n']}={r['avoidance']}"
        rejected(lambda:write_and_check(bad),'consistent complement but incorrect count')
    counter=ROOT/'src/bruteforce_contain'
    for args in ([],['0','12'],['15','12'],['5','11'],['5','13'],['5','1x'],['5',''],['5x','12'],['1','12'],['5','12','extra']):
        proc=subprocess.run([str(counter),*args],capture_output=True,text=True)
        require(proc.returncode!=0 and not proc.stdout,'malformed counter input was accepted: '+repr(args));passed+=1
    print('PASS: ten invalid counter invocations rejected')
    for n,tau in ((1,'1'),(2,'12'),(5,'12'),(5,'21'),(8,'12345678')):
        out=subprocess.run([str(counter),str(n),tau],capture_output=True,text=True,check=True).stdout
        g,av=parse_counter(out,tau,n)
        target=0 if tau=='1' else (math.factorial(n)-1 if len(tau)==n else 1)
        require(av==target,'boundary counter value failed');passed+=1
    print('PASS: five valid boundary/known counter invocations')
    print(f'PASS: {passed} verification regression checks')
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError) as e:
        print(f'ERROR: {e}',file=sys.stderr);sys.exit(1)
