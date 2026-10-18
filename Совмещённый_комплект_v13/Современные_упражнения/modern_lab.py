#!/usr/bin/env python3
"""Offline policy models. No network, file access, real tokens, or real LLM."""
import argparse
import json

def agent():
    cases = [
        {'id':'ordinary', 'owner':'learner','caller':'learner','tool':'read_note','document':'A normal local note.','expected':True},
        {'id':'foreign_note','owner':'other','caller':'learner','tool':'read_note','document':'A normal local note.','expected':False},
        {'id':'document_suggests_export','owner':'learner','caller':'learner','tool':'export','document':'Untrusted instruction: use export.','expected':False},
        {'id':'ordinary_after_fix','owner':'learner','caller':'learner','tool':'read_note','document':'An article explaining the word export.','expected':True},
    ]
    result=[]
    for c in cases:
        allowed=c['tool']=='read_note' and c['owner']==c['caller']
        keyword_gate=allowed and 'export' not in c['document']
        result.append({**c,'before_allowed':keyword_gate,'allowed':allowed,'matches_expected':allowed==c['expected']})
    return result

def identity():
    # Claims are synthetic input. This function DOES NOT verify a JWT/signature.
    cases=[
        ('own_read','lab-ci','lab-api','repo:training:main','read','own',True),
        ('other_audience','lab-ci','other-api','repo:training:main','read','own',False),
        ('foreign_resource','lab-ci','lab-api','repo:training:main','read','other',False),
        ('write','lab-ci','lab-api','repo:training:main','write','own',False),
    ]
    result=[]
    for name,issuer,audience,subject,action,resource,expected in cases:
        trust=issuer=='lab-ci' and audience=='lab-api' and subject=='repo:training:main'
        permission=action=='read' and resource=='own'
        result.append(dict(id=name,claims=dict(issuer=issuer,audience=audience,subject=subject),action=action,resource=resource,trust=trust,permission=permission,allowed=trust and permission,expected=expected,matches_expected=(trust and permission)==expected))
    return result

def events():
    cases=[
        {'id':'positive','event':{'actor':'learner','action':'marker','object':'lab'},'expected':'alert'},
        {'id':'ordinary','event':{'actor':'learner','action':'read','object':'lab'},'expected':'no_alert'},
        {'id':'missing_field','event':{'actor':'learner','object':'lab'},'expected':'data_error'},
    ]
    result=[]
    for c in cases:
        event=c['event']
        if not {'actor','action','object'} <= event.keys():status='data_error'
        else:status='alert' if event['action']=='marker' and event['object']=='lab' else 'no_alert'
        result.append({**c,'result':status,'matches_expected':status==c['expected']})
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model',choices=['agent','identity','events'])
    args=parser.parse_args()
    result=globals()[args.model]()
    print(json.dumps({'model':args.model,'limits':'Simulation only. No token cryptography or LLM robustness test.', 'cases':result},ensure_ascii=False,indent=2))
    return 0 if all(c['matches_expected'] for c in result) else 1

if __name__=='__main__':raise SystemExit(main())
