"""Pure deterministic binding of an approved template; never authenticates it.

This module has no transport. Required owner values remain null in the proposal.
The caller must separately authenticate the actual decision and exact plan via
the coordinator policy hook. The returned requests are only an artifact until
fresh document/lease/CAS/requiredRevisionId guards permit dispatch.
"""
from __future__ import annotations

import copy
import json
import re

from .native_transforms_v6 import body_text, walk


FIELDS={'OWNER_ID','OWNER_DECISION_ID','OWNER_DECIDED_AT_UTC','OWNER_DECISION_SOURCE_URI','EFFECTIVE_AT_WARSAW','APPROVAL_PAYLOAD_SHA256','APPROVED_TESTED_COMMIT','ACTIVATION_EVENT_ID','RELEASE_MANIFEST_URI','NORMATIVE_AUDIT_ARTIFACT','TECHNICAL_AUDIT_ARTIFACT'}


def u16(text):return len(text.encode('utf-16-le'))//2


def move(index,start,end,delta):
    if start<index<end:raise ValueError('Unexpected reviewed style boundary inside a binding slot')
    return index+delta if index>=end else index


def shift(value,start,end,delta):
    for obj in walk(value):
        for key in ('startIndex','endIndex'):
            if key in obj:
                if type(obj[key]) is not int:raise ValueError('Nonintegral native index')
                obj[key]=move(obj[key],start,end,delta)


def bind(plan,body_template,owner_values,*,owned_tab_id,effective_artifact_commit):
    if set(owner_values)!=FIELDS:raise ValueError('All eleven actual decision bindings are required')
    for value in owner_values.values():
        if not isinstance(value,str) or not value or any(ord(c)<32 for c in value) or '{{' in value or '}}' in value:
            raise ValueError('Unbound, multiline or nested binding')
    if not re.fullmatch(r'[0-9a-f]{64}',owner_values['APPROVAL_PAYLOAD_SHA256']):raise ValueError('Exact approval hash required')
    if not re.fullmatch(r'[0-9a-f]{40}',owner_values['APPROVED_TESTED_COMMIT']):raise ValueError('Exact tested commit required')
    if not re.fullmatch(r'[0-9a-f]{40}',effective_artifact_commit):raise ValueError('Exact effective artifact commit required')
    if not isinstance(owned_tab_id,str) or not re.fullmatch(r't\.[A-Za-z0-9_-]+',owned_tab_id):raise ValueError('Actual acknowledged tab ID required')
    result=copy.deepcopy(plan);body=copy.deepcopy(body_template['body'])
    text=result['full_text_template']
    if body_text(body)!=text+'\n':raise ValueError('Whole body and render text differ')
    for key in sorted(FIELDS):
        token='{{'+key+'}}';replacement=owner_values[key]
        while token in text:
            char=text.index(token);start=1+u16(text[:char]);end=start+u16(token);delta=u16(replacement)-u16(token)
            matches=[x for x in walk(body) if 'textRun' in x and x['startIndex']<=start and x['endIndex']>=end]
            if len(matches)!=1:raise ValueError('Binding crosses an unreviewed native run')
            target=matches[0]['textRun'];raw=target['content'].encode('utf-16-le');offset=(start-matches[0]['startIndex'])*2
            if raw[offset:offset+u16(token)*2].decode('utf-16-le')!=token:raise ValueError('Native token offset differs')
            target['content']=(raw[:offset]+replacement.encode('utf-16-le')+raw[offset+u16(token)*2:]).decode('utf-16-le')
            shift(body,start,end,delta);shift(result['styles'],start,end,delta);shift(result['annex_links'],start,end,delta)
            text=text[:char]+replacement+text[char+len(token):]
    if '{{' in text or body_text(body)!=text+'\n':raise ValueError('Unresolved text binding')
    urls={}
    for link in result['annex_links']:
        link['url']=link['url_template'].replace('{{EFFECTIVE_ARTIFACT_COMMIT}}',effective_artifact_commit)
        urls[link['url_template']]=link['url'];link['range']['tabId']=owned_tab_id
    for obj in walk(body):
        if 'link' in obj:
            url=obj['link']['url']
            if url not in urls:raise ValueError('Unreviewed native link')
            obj['link']['url']=urls[url]
    requests=[{'insertText':{'location':{'tabId':owned_tab_id,'index':1},'text':text}}]
    for item in result['styles']:
        next(iter(item.values()))['range']['tabId']=owned_tab_id
        requests.append(item)
    for link in result['annex_links']:
        requests.append({'updateTextStyle':{'range':link['range'],'textStyle':{'link':{'url':link['url']}},'fields':'link'}})
    if '{{' in json.dumps(requests,ensure_ascii=False):raise ValueError('Unresolved request binding')
    return {'schema':'sf20-v6-bound-render-artifact-v1','not_an_authorization':True,'document_id':plan['canonical_document_id'],'owned_tab_id':owned_tab_id,'effective_artifact_commit':effective_artifact_commit,'full_text':text,'expected_body_template':body,'dynamic_heading_id_json_pointers':copy.deepcopy(body_template['dynamic_heading_id_json_pointers']),'requests':requests}
