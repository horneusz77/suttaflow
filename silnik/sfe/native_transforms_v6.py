"""Strict author-proposed native transform callbacks; no network or authority.

The trusted V6 policy must bind these complete parameters, caller identity,
receipts and source pins. Passing a user-authored expected state to this module
does not authenticate that state. A callback returns exactly True only for its
bounded native effect. Runtime integration/freeze and independent review remain
separate gates. The flat native JSON shape is the observed connector contract;
an unreviewed shape fails closed, without dropping fields.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from functools import wraps


def canonical(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')


def same(a,b):
    return canonical(a)==canonical(b)


def without_revision(value):
    result=copy.deepcopy(value);result.pop('revisionId',None);return result


def digest_native(value):
    return hashlib.sha256(canonical(without_revision(value))).hexdigest()


def require(value):
    if value is not True:
        raise ValueError('Native transform contract differs')


def closed(obj,keys):
    require(isinstance(obj,dict) and set(obj)==set(keys))


def guarded(function):
    @wraps(function)
    def check(*args):
        try:
            return function(*args) is True
        except (ValueError,TypeError,KeyError,IndexError,UnicodeError,RecursionError):
            return False
    return check


def walk(value):
    if isinstance(value,dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value,list):
        for child in value:yield from walk(child)


def heading_ids(value):
    for obj in walk(value):
        if isinstance(obj.get('headingId'),str):yield obj['headingId']


def location(value,pointer):
    require(isinstance(pointer,str) and pointer.startswith('/'))
    keys=pointer[1:].split('/')
    for key in keys[:-1]:
        value=value[int(key)] if isinstance(value,list) else value[key]
    key=int(keys[-1]) if isinstance(value,list) else keys[-1]
    return value,key


def assign(value,pointer,replacement):
    parent,key=location(value,pointer);parent[key]=replacement


def body_text(body):
    return ''.join(e.get('textRun',{}).get('content','') for p in body['content'] for e in p.get('paragraph',{}).get('elements',[]))


def rule_heading_ids(body):
    ids=[]
    for p in body['content']:
        para=p.get('paragraph',{})
        if para.get('paragraphStyle',{}).get('namedStyleType','').startswith('HEADING_'):
            text=''.join(e.get('textRun',{}).get('content','') for e in para.get('elements',[]))
            m=re.match(r'^(SF-RULE-[A-Z]+-\d{3}) — ',text)
            if m:ids.append(m.group(1))
    return ids


def common(params,before,ack,after,count):
    doc=params['document_id']
    require(isinstance(doc,str) and bool(re.fullmatch(r'[A-Za-z0-9_-]{16,160}',doc)))
    require(all(isinstance(x,dict) and x.get('documentId')==doc for x in (before,ack,after)))
    require(params['before_sha256']==digest_native(before))
    for obj in (before,after):
        require(isinstance(obj.get('tabs'),list) and bool(obj['tabs']))
        require(isinstance(obj.get('revisionId'),str) and bool(obj['revisionId']))
        ids=[t['tabId'] for t in obj['tabs']]
        require(len(ids)==len(set(ids)) and all(isinstance(i,str) and i for i in ids))
    require(before['revisionId']!=after['revisionId'])
    control=ack['writeControl']
    require(isinstance(control,dict) and not (set(control)-{'requiredRevisionId','targetRevisionId','writeMode'}))
    require(control['requiredRevisionId']==after['revisionId'] and control.get('targetRevisionId') is None)
    require(control.get('writeMode','EDIT') in {'EDIT','WRITE_MODE_UNSPECIFIED'})
    require(ack.get('revisionId',after['revisionId'])==after['revisionId'])
    require(isinstance(ack.get('replies'),list) and type(count) is int and len(ack['replies'])==count)


@guarded
def verify_append_empty_tab(params,before,ack,after):
    closed(params,{'document_id','before_sha256','new_tab_template'})
    common(params,before,ack,after,1)
    properties=ack['replies'][0]['addDocumentTab']['tabProperties']
    new_id=properties['tabId']
    require(isinstance(new_id,str) and bool(new_id) and new_id not in {t['tabId'] for t in before['tabs']})
    tab=copy.deepcopy(params['new_tab_template'])
    require(tab['tabId'] is None and tab['index']==len(before['tabs']) and type(tab['index']) is int)
    require(tab['parentTabId'] is None and body_text(tab['body'])=='\n' and len(tab['body']['content'])==2)
    require(all(tab.get(k) is None for k in ('headers','footers','footnotes','lists','namedRanges','inlineObjects','positionedObjects','dropdownDefinitions')))
    require(tab['documentId']==params['document_id'])
    require(properties.get('title')==tab['title'] and same(properties.get('index'),tab['index']))
    require(not(set(properties)-{'tabId','title','index','parentTabId','nestingLevel','iconEmoji'}))
    tab['tabId']=new_id
    expected=without_revision(before);expected['tabs'].append(tab)
    require(same(expected,without_revision(after)))
    return True


@guarded
def verify_render_owned_tab(params,before,ack,after):
    closed(params,{'document_id','before_sha256','owned_tab_id','expected_body_template','dynamic_heading_id_json_pointers','request_count','expected_rule_ids'})
    common(params,before,ack,after,params['request_count'])
    require(all(x=={} for x in ack['replies']))
    ids=[t['tabId'] for t in before['tabs']];pos=ids.index(params['owned_tab_id'])
    require(pos>0 and body_text(before['tabs'][pos]['body'])=='\n')
    template=copy.deepcopy(params['expected_body_template'])
    slots=params['dynamic_heading_id_json_pointers']
    require(isinstance(slots,list) and bool(slots) and len(slots)==len(set(slots)))
    expected_slots=['/content/'+str(i)+'/paragraph/paragraphStyle/headingId' for i,p in enumerate(template['content']) if 'headingId' in p.get('paragraph',{}).get('paragraphStyle',{})]
    require(slots==expected_slots)
    fresh=[];old=set(heading_ids(before))
    actual_body=after['tabs'][pos]['body']
    for pointer in slots:
        require(bool(re.fullmatch(r'/content/[0-9]+/paragraph/paragraphStyle/headingId',pointer)))
        parent,key=location(template,pointer);require(parent[key] is None)
        current,k=location(actual_body,pointer);actual=current[k]
        require(isinstance(actual,str) and bool(actual) and actual not in old)
        fresh.append(actual);parent[key]=actual
    require(len(fresh)==len(set(fresh)))
    rules=params['expected_rule_ids']
    require(isinstance(rules,list) and len(rules)==85 and len(set(rules))==85 and rule_heading_ids(template)==rules)
    expected=without_revision(before);expected['tabs'][pos]['body']=template
    require(same(expected,without_revision(after)))
    return True


@guarded
def verify_reorder_tabs(params,before,ack,after):
    closed(params,{'document_id','before_sha256','ordered_tab_ids','changed_titles'})
    common(params,before,ack,after,len(params['changed_titles']))
    require(all(x=={} for x in ack['replies']))
    order=params['ordered_tab_ids'];titles=params['changed_titles'];tabs={t['tabId']:t for t in before['tabs']}
    require(isinstance(order,list) and len(order)==len(tabs) and set(order)==set(tabs))
    require(isinstance(titles,dict) and set(titles)<=set(tabs) and all(isinstance(x,str) and x for x in titles.values()))
    expected=without_revision(before);expected['tabs']=[copy.deepcopy(tabs[i]) for i in order]
    for i,tab in enumerate(expected['tabs']):
        tab['index']=i
        if tab['tabId'] in titles:tab['title']=titles[tab['tabId']]
    require(same(expected,without_revision(after)))
    return True


@guarded
def verify_remove_owned_tab(params,before,ack,after):
    closed(params,{'document_id','before_sha256','owned_tab_id','expected_after_without_revision','request_count'})
    common(params,before,ack,after,params['request_count'])
    require(all(x=={} for x in ack['replies']))
    current={t['tabId']:t for t in before['tabs']};target=params['expected_after_without_revision']
    owned=params['owned_tab_id'];require(owned in current)
    require(set(t['tabId'] for t in target['tabs'])==set(current)-{owned})
    for t in target['tabs']:
        prior=copy.deepcopy(current[t['tabId']]);prior['title']=t['title'];prior['index']=t['index']
        require(same(prior,t))
    top=without_revision(before);top['tabs']=copy.deepcopy(target['tabs'])
    require(same(top,target) and same(target,without_revision(after)))
    return True


def resolve_append_inverse(params,before,ack,after):
    require(verify_append_empty_tab(params,before,ack,after))
    return [{'deleteTab':{'tabId':ack['replies'][0]['addDocumentTab']['tabProperties']['tabId']}}]


@guarded
def verify_owned_creation_group(params,original_actions,native_history,current_before_obj,exact_requests):
    closed(params,{'document_id','ordered_action_ids','append_parameters','render_parameters'})
    ids=params['ordered_action_ids']
    require(isinstance(ids,list) and len(ids)==2 and len(set(ids))==2)
    require(len(original_actions)==len(native_history)==2)
    require([a['action_id'] for a in original_actions]==ids and [h['action_id'] for h in native_history]==ids)
    require(all(a['document_id']==params['document_id'] and a['kind']=='APPLY' for a in original_actions))
    first,second=native_history
    require(same(first['after'],second['before']))
    require(verify_append_empty_tab(params['append_parameters'],first['before'],first['ack'],first['after']))
    require(verify_render_owned_tab(params['render_parameters'],second['before'],second['ack'],second['after']))
    tab=first['ack']['replies'][0]['addDocumentTab']['tabProperties']['tabId']
    require(params['render_parameters']['owned_tab_id']==tab)
    require(same(without_revision(second['after']),without_revision(current_before_obj)))
    require(same(exact_requests,[{'deleteTab':{'tabId':tab}}]))
    return True


POSTCONDITION_VERIFIERS={
    'sf20_v6_append_empty_tab_v1':verify_append_empty_tab,
    'sf20_v6_render_owned_tab_v1':verify_render_owned_tab,
    'sf20_v6_reorder_tabs_v1':verify_reorder_tabs,
    'sf20_v6_remove_owned_tab_v1':verify_remove_owned_tab,
}
INVERSE_RESOLVERS={'sf20_v6_append_inverse_v1':resolve_append_inverse}
GROUP_COMPENSATION_VERIFIERS={'sf20_v6_owned_creation_group_v1':verify_owned_creation_group}
