"""Content-bound source evidence adapter for Standard 2.0 RC.1.

SF-SRCREQ-001..017 / SF-RULE-SRC, LEX, PUB. This module checks supplied
attestations and their actual bytes, never performs philological reading,
establishes authorship by a hash, or authorizes publication. The caller must
obtain the evidence index and trusted human decisions through trusted intake.
Books can have genuine scoped reading attestations without full captures.
Only the Python standard library and release_evidence are required.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
from typing import Any
import unicodedata
from urllib.parse import urlparse
from sfe import release_evidence as RE

CONTRACT_PATH = Path(__file__).resolve().parents[1] / 'docs/standards/2.0-RC.1/source_contract_v2.json'
READY = 'TECHNICAL_SOURCE_EVIDENCE_READY'
FULL = 'PEŁNY_ODCZYT'
PARTIAL = 'CZĘŚCIOWY_ODCZYT'
ABSENT = {'BRAK_PRZEKŁADU_Z_KWERENDĄ', 'BRAK_DOSTĘPU_Z_KWERENDĄ'}
STATES = {FULL, PARTIAL, 'NIEZWERYFIKOWANE'} | ABSENT
KINDS = {'SOURCE_TEXT','CONTROL_PALI','DIRECT_TRANSLATION','COMMENTARY','LEXICON','PARALLEL','ADDITIONAL_VERIFIER'}
META = ('profile_role','evidence_kind','language','title','author_or_editor','edition','actual_carrier')
PARALLELS = {'PALI_CANON','AGAMAS','OTHER_VINAYAS','SANSKRIT_FRAGMENTS','OTHER_EARLY'}
DICTIONARIES = {'DPD','CONE','PED','CPD','DPPN'}
QUERY_RESULTS = {'FOUND_AVAILABLE', 'NO_MATCH_IN_SEARCHED_SCOPE', 'ACCESS_UNAVAILABLE', 'UNREVIEWED'}
PARALLEL_RESULTS = {'MATCH', 'NO_MATCH_IN_SEARCHED_SCOPE', 'NOT_APPLICABLE', 'UNREVIEWED'}
STRUCTURES = {'NARRATIVE','ORIGIN_STORY','RULE','PERMISSION','DEFINITION','EXCEPTION','COMMUNITY_PROCEDURE','COMMENTARY'}
CASE_FIELDS = {'schema_version','case_id','is_synthetic','profile','subject_id','revision_id','content_sha256',
               'scope','basis','sources','queries','lexical_decisions','parallel_queries','public_sources',
               'intended_publication','rights_evidence_refs','no_controls_human_exception_ref',
               'other_kn_owner_contract_ref','evidence_v2_packet_ref','owner_publication_consent_ref'}
SOURCE_FIELDS = set(META)|{'source_id','availability_status','capture_state','read_state','declared_scope',
    'read_scope','read_events','query_evidence_refs','used','usage_loci','limitations','capture_path','capture_sha256'}
BASIS_FIELDS = {'method','language','source_id','indirect','intermediary_source_id','indirect_reason','limitations',
                'r0_evidence_ref','first_comparison_read_ref','prior_exposure_evidence_ref'}
DOCUMENTED = 'PALI_FIRST_UDOKUMENTOWANY'
DECLARED = 'PALI_FIRST_DEKLAROWANY'
METHOD_AXES = {DOCUMENTED, DECLARED, 'EN_PL_HH', 'EN_PL_INNY', 'NIEUSTALONE'}
NEUTRAL_PALI_METHOD = ('polskie opracowanie AI z odwołaniem do tekstu palijskiego; '
                       'pełna niezależność metody nieudokumentowana')


def _need(ok, message):
    if not ok:
        raise RE.EvidenceError(message)


def is_pali(language):
    """The same accepted Pali aliases govern the basis and required DPD checks."""
    return isinstance(language, str) and language.casefold() in {'pli', 'pi', 'pali'}


def _strings(value, *, empty=False):
    _need(isinstance(value,list),'expected a list')
    if empty and not value:
        return []
    return RE.scope(value)


def _auth(record):
    a = record.get('authenticated_source')
    _need(isinstance(a,dict) and all(RE.nonempty(a.get(k)) for k in ('actor_id','uri','record_id')),
          'authenticated source record absent; hash alone is not an attestation')
    return a


def _pali_key(word):
    """Only dictionary alphabetical limits; not morphology or Pali semantics."""
    letters = 'a ā i ī u ū e o k kh g gh ṅ c ch j jh ñ ṭ ṭh ḍ ḍh ṇ t th d dh n p ph b bh m y r l ḷ v s h ṃ'.split()
    word = unicodedata.normalize('NFC', word.lower()).strip()
    result=[];i=0
    while i<len(word):
        token=word[i:i+2] if word[i:i+2] in letters else word[i]
        if token not in letters:
            return None
        result.append(letters.index(token));i+=len(token)
    return tuple(result)


def _in_dictionary_range(role, lemma):
    key=_pali_key(lemma)
    if key is None or not key:
        return True  # The explicit entry/edition scope attestation still applies.
    if role=='CONE':
        return key[0] <= _pali_key('bh')[0]
    if role=='CPD':
        return key <= _pali_key('kāreti')
    return True


class _Validation:
    def __init__(self, case, index, root, evidence, contract, trusted, method_axis):
        self.case=case;self.index=index;self.root=root;self.evidence=evidence
        self.contract=contract;self.trusted=trusted or {};self.reasons=[]
        self.method_axis=method_axis
        self._subject: dict[str, Any] | None = None
        self.sources: dict[str, dict[str, Any]] = {}
        self.reads: dict[str, dict[str, Any]] = {}
        self.proofs: dict[str, list[dict[str, Any]]] = {}
        self.queries: dict[str, dict[str, Any]] = {}

    @property
    def subject(self) -> dict[str, Any]:
        if self._subject is None:
            raise RE.EvidenceError('current subject is not initialized')
        return self._subject

    def bad(self, req, message, locator='', *, blocked=False):
        item={'requirement_id':'SF-SRCREQ-'+req,'code':'SOURCE_EVIDENCE_'+req,
              'message':str(message),'locator':str(locator),'status':'BLOCKED' if blocked else 'HOLD'}
        if item not in self.reasons:self.reasons.append(item)

    def guard(self, req, fn, locator='', *, blocked=False):
        try:
            return fn()
        except (RE.EvidenceError,KeyError,TypeError,ValueError,AttributeError,OSError) as exc:
            self.bad(req,str(exc),locator,blocked=blocked)
            return None

    def artifact(self, key, kind=None, *, partial=False):
        _need(RE.nonempty(key) and key in self.index,'missing evidence reference: '+str(key))
        p=RE.read_artifact(self.root,self.index[key],json_object=True)
        if kind is not None:
            _need(p.get('kind')==kind,'wrong evidence kind, expected '+kind)
            RE.binding(p,self.subject,partial=partial)
            _auth(p)
        return p

    def initialize(self):
        c=self.case
        _need(isinstance(c,dict) and not set(c)-CASE_FIELDS,'unknown case fields or case is not an object')
        _need(c.get('schema_version')=='2.0-RC.1','unknown case version')
        _need(RE.nonempty(c.get('case_id')) and type(c.get('is_synthetic')) is bool,'case identity or synthetic marker absent')
        _need(type(c.get('intended_publication')) is bool,'publication intent must be explicit')
        if self.method_axis is not None:
            _need(isinstance(self.method_axis,dict) and isinstance(self.method_axis.get('value'),str)
                  and self.method_axis['value'] in METHOD_AXES,'method_axis must be an existing axis B record')
        _need(isinstance(self.index,dict),'evidence index absent')
        _need(isinstance(self.contract,dict) and self.contract.get('schema')=='suttaflow-source-contract-v2'
              and self.contract.get('contract_version')=='2.0-RC.1','source contract missing or wrong version')
        _need(c.get('profile') in self.contract['profiles'],'unknown collection profile')
        _need(self.contract.get('no_new_policy')=={'KN_blanket_minimum_two':False,'brahmali_tier':False,
              'new_active_axes':False,'lexical_groups_changed':False},'this adapter cannot activate a new source/axis policy')
        if self.evidence is None:
            self.evidence=self.artifact(c.get('evidence_v2_packet_ref'))
        self._subject=RE.subject_from(self.evidence,self.root,subject_id=c.get('subject_id'),revision_id=c.get('revision_id'))
        RE.binding(c,self.subject)
        for name in ('sources','queries','lexical_decisions','parallel_queries','public_sources','rights_evidence_refs'):
            _need(isinstance(c.get(name),list),name+' must be a list')
        _need(c['sources'],'sources absent')
        for s in c['sources']:
            _need(isinstance(s,dict) and RE.nonempty(s.get('source_id')),'source ID absent')
            _need(not set(s)-SOURCE_FIELDS,'unknown source fields')
            _need(s['source_id'] not in self.sources,'duplicate source ID: '+s['source_id'])
            self.sources[s['source_id']]=s
        self.profile=self.contract['profiles'][c['profile']]
        return True

    def query(self,q):
        _need(isinstance(q,dict),'query must be an object')
        _need(RE.nonempty(q.get('query_id')),'query ID absent')
        _need(q['query_id'] not in self.queries,'duplicate query ID')
        for k in ('source_or_family','query_text','result'):_need(RE.nonempty(q.get(k)),'query '+k+' absent')
        _need(isinstance(q.get('result_status'),str) and q['result_status'] in QUERY_RESULTS,
              'unknown structured source query result')
        _strings(q.get('places_checked'));RE.timestamp(q.get('at'))
        p=self.artifact(q.get('evidence_ref'),'SOURCE_QUERY',partial=True)
        for k in ('query_id','source_or_family','at','places_checked','query_text','result','result_status'):
            _need(p.get(k)==q.get(k),'query proof differs: '+k)
        _need(RE.nonempty(p.get('reason')),'query result reason absent')
        unavailable=_strings(p.get('unavailable_scope'),empty=True)
        _need(set(unavailable)<=set(p['scope']),'unavailable query scope is orphaned')
        _need(not unavailable or q['result_status'] in {'NO_MATCH_IN_SEARCHED_SCOPE','ACCESS_UNAVAILABLE'},
              'positive or unreviewed query cannot prove unavailable scope')
        self.queries[q['query_id']]=p
        self.queries[q['evidence_ref']]=p

    def capture(self,s):
        if s.get('capture_state')=='NOT_CAPTURED':return
        _need(s.get('capture_state')=='CAPTURED','unknown capture state')
        refs=[r for r in self.index.values() if isinstance(r,dict) and r.get('path')==s.get('capture_path')
              and r.get('sha256')==s.get('capture_sha256')]
        _need(refs and RE.nonempty(s.get('capture_path')),'declared capture has no matching indexed file')
        RE.read_artifact(self.root,refs[0])

    def source(self,s):
        sid=s['source_id'];self.reads[sid]={};self.proofs[sid]=[]
        for k in META:_need(RE.nonempty(s.get(k)),'source metadata missing: '+k)
        _need(s['evidence_kind'] in KINDS,'unknown source evidence kind')
        _need(s.get('availability_status') in STATES,'unknown availability status')
        _need(s.get('read_state') in {'READ','NIE_ODCZYTANO','UNKNOWN'},'unknown reading state')
        declared=_strings(s.get('declared_scope'));read=_strings(s.get('read_scope'),empty=True)
        _need(set(read)<=set(declared)<=set(self.subject['scope']),'source scope is outside current task')
        _need(type(s.get('used')) is bool,'used must be boolean')
        _strings(s.get('usage_loci'),empty=not s['used'])
        _strings(s.get('query_evidence_refs'),empty=True)
        _need(isinstance(s.get('read_events'),list),'read events absent')
        self.capture(s)
        if s['read_state']!='READ':
            _need(not read and not s['read_events'] and not s['used'],'unread source claims reading or usage')
            _need(s['availability_status'] not in {FULL,PARTIAL},'unread source has a read availability state')
            return
        _need(s['availability_status'] in {FULL,PARTIAL},'READ conflicts with unavailable/unknown status')
        _need(read and s['read_events'],'read requires actual scope and attestations')
        if s['availability_status']==FULL:_need(set(read)==set(declared),'full read does not match declared scope')
        for e in s['read_events']:
            _need(isinstance(e,dict),'read event must be an object')
            for k in ('actor_id','context_id','locator'):_need(RE.nonempty(e.get(k)),'read event missing '+k)
            when=RE.timestamp(e.get('at'));units=_strings(e.get('scope'))
            _need(set(units)<=set(read),'read event exceeds declared actual read scope')
            p=self.artifact(e.get('evidence_ref'),'SOURCE_READ_ATTESTATION',partial=True)
            for k in ('actor_id','context_id','locator','at','scope'):_need(p.get(k)==e.get(k),'read attestation differs: '+k)
            _need(_auth(p)['actor_id']==e['actor_id'],'reader identity differs from authenticated record')
            _need(p.get('source_id')==sid and p.get('source_metadata')=={k:s[k] for k in META},'read source/edition/role metadata differs')
            _need(self.case['profile'] in _strings(p.get('applicable_profiles')),'edition is not attested for this collection')
            _need(p.get('usage_loci')==s['usage_loci'] and RE.nonempty(p.get('evidence_text')),'read/usage evidence absent')
            _need(p.get('read_mode') in {'CAPTURE_READING','BOOK_READING','DIRECT_SOURCE_READING'},'actual mode of reading absent')
            if p['read_mode']=='CAPTURE_READING':
                _need(s['capture_state']=='CAPTURED','capture reading without captured bytes')
                ref=p.get('capture_ref')
                _need(isinstance(ref,dict) and ref.get('path')==s.get('capture_path')
                      and ref.get('sha256')==s.get('capture_sha256'),
                      'read proof refers to a different captured source version')
                raw=RE.read_artifact(self.root,ref)
                ranges=p.get('read_byte_ranges')
                _need(isinstance(ranges,list) and ranges,'actual read byte ranges absent')
                end=0
                for span in ranges:
                    _need(isinstance(span,list) and len(span)==2 and all(type(n) is int for n in span)
                          and end<=span[0]<span[1]<=len(raw),'read byte range invalid, overlapping or outside capture')
                    end=span[1]
            for u in units:self.reads[sid][u]=min(when,self.reads[sid].get(u,when))
            self.proofs[sid].append(p)
        _need(set(self.reads[sid])==set(read),'reading attestations do not cover claimed read scope')

    def queried_absent(self,s,u):
        for ref in s.get('query_evidence_refs',[]):
            q=self.queries.get(ref)
            if q is None:continue
            expected='ACCESS_UNAVAILABLE' if s.get('availability_status')=='BRAK_DOSTĘPU_Z_KWERENDĄ' else 'NO_MATCH_IN_SEARCHED_SCOPE'
            if q.get('result_status')!=expected:continue
            if q.get('source_or_family') not in {s['source_id'],s['profile_role'],'HH' if s['profile_role'].startswith('HH') else s['profile_role']}:continue
            if u not in q.get('unavailable_scope',[]):continue
            if s['profile_role'].startswith('HH'):
                official=any(urlparse(x).hostname=='suttas.hillsidehermitage.org' for x in q['places_checked'])
                known=q.get('known_publications_checked')
                _need(official and isinstance(known,list) and known and all(RE.nonempty(x) and x in q['places_checked'] for x in known),
                      'HH absence needs official collection and relevant known publications, not one index')
            return True
        return False

    def is_read(self,s,u):
        return s.get('used') is True and s.get('read_state')=='READ' and u in self.reads.get(s['source_id'],{})

    def availability(self,s):
        if s.get('availability_status') in ABSENT or s.get('availability_status')==PARTIAL:
            missing=set(s['declared_scope'])-set(self.reads.get(s['source_id'],{}))
            for u in missing:_need(self.queried_absent(s,u),'missing source scope needs dated query/exception: '+u)

    def role_checks(self):
        profile=self.profile
        allowed={r for stage in profile['sequence'] for r in stage}|set(profile['philological'])
        allowed|=DICTIONARIES|{'SOURCE_TEXT','CONTROL_PALI','PARALLEL','ADDITIONAL_VERIFIER','SUJATO','INTERMEDIARY','SOURCE_CONTROL'}
        for s in self.sources.values():
            if s['profile_role'] not in allowed:
                self.bad('008','source role is not an approved controller for this profile',s['source_id'])
            if 'sujato' in s.get('author_or_editor','').casefold() or s['profile_role']=='SUJATO':
                if s.get('evidence_kind')!='ADDITIONAL_VERIFIER' or s['source_id']==self.case['basis'].get('source_id'):
                    self.bad('015','Sujato cannot be substituted as primary translator/interpretive source',s['source_id'])
            if s['profile_role'] in DICTIONARIES and s.get('evidence_kind')!='LEXICON':
                self.bad('010','dictionary mislabeled as a full translation',s['source_id'])
        for role in {r for st in profile['sequence'] for r in st}|set(profile['philological']):
            if not any(s['profile_role']==role for s in self.sources.values()):self.bad('008','assigned source stage/philological control not accounted for',role)
        for role in profile['philological']:
            records=[s for s in self.sources.values() if s['profile_role']==role]
            for u in self.subject['scope']:
                if not any(self.is_read(s,u) or self.guard('005',lambda s=s:self.queried_absent(s,u),s['source_id']) for s in records):
                    self.bad('008','assigned philological control needs read or actual availability/access exception',role+':'+u)

    def human_exception(self,key,kind):
        p=self.artifact(key,kind)
        _need(isinstance(self.trusted,dict) and self.trusted.get(key)==p,'human decision is not in trusted intake ledger')
        _need(p.get('status')=='APPROVED' and p.get('actor_kind')=='HUMAN','decision is not a current human approval')
        _need(RE.nonempty(p.get('actor_id')) and p['actor_id']==_auth(p)['actor_id'],'human identity differs')
        RE.timestamp(p.get('issued_at'))
        _need(RE.nonempty(p.get('limitations')),'exact scope limitations absent')
        return p

    def other_kn_profile(self):
        if self.case['profile']!='KN_OTHER':return True
        p=self.human_exception(self.case.get('other_kn_owner_contract_ref'),'KN_SOURCE_CONTRACT')
        _need(p.get('actor_role')=='OWNER','new KN source contract needs the project owner')
        profile=p.get('source_profile');catalogue=p.get('source_catalogue')
        _need(isinstance(profile,dict) and isinstance(catalogue,dict),'approved KN source profile/catalogue absent')
        _need(set(profile)=={'sequence','philological'} and isinstance(profile['sequence'],list) and profile['sequence'],
              'approved KN profile must contain a nonempty explicit sequence')
        roles=set(_strings(profile['philological'],empty=True))
        for stage in profile['sequence']:roles.update(_strings(stage))
        _need(roles==set(catalogue),'owner profile catalogue and role sequence differ')
        for role in roles:
            meta=catalogue[role];_need(isinstance(meta,dict) and set(meta)=={'title','author_or_editor','edition'}
                and all(RE.nonempty(v) for v in meta.values()),'owner-approved source edition identity absent')
            records=[s for s in self.sources.values() if s['profile_role']==role]
            _need(records and all(all(s[k]==v for k,v in meta.items()) for s in records),
                  'actual KN controller differs from the precise owner-approved source plan')
        self.profile=profile
        return True

    def priority(self):
        if self.case['profile']=='VINAYA_OTHER':return  # Exact language-specific plan is checked with the basis.
        stages=[[s for s in self.sources.values() if s['profile_role'] in stage] for stage in self.profile['sequence']]
        all_read=set()
        for u in self.subject['scope']:
            stage_times=[];chosen=False
            for records in stages:
                times=[self.reads[s['source_id']][u] for s in records if self.is_read(s,u)]
                if times:all_read.add(u)
                stage_times.append(times)
                if chosen:continue
                if times:chosen=True;continue
                if not records:continue  # Missing assigned record already reported as 008.
                absent=[self.guard('005',lambda s=s:self.queried_absent(s,u),s['source_id']) for s in records]
                if not all(absent):self.bad('004','highest applicable source is neither compared nor justified unavailable',u)
            # Disallow lower-priority reading preceding an actually read higher source.
            for i,times in enumerate(stage_times):
                if times:
                    later=[t for ts in stage_times[i+1:] for t in ts]
                    if later and max(times)>min(later):self.bad('004','comparison reads violate profile priority order',u)
        if not all_read:
            self.guard('006',lambda:self.human_exception(self.case.get('no_controls_human_exception_ref'),'NO_CONTROL_COMPARISON_EXCEPTION'))

    def basis(self):
        b=self.case.get('basis');_need(isinstance(b,dict),'basis absent')
        _need(not set(b)-BASIS_FIELDS,'unknown basis fields')
        _need(b.get('method') in {'PALI_FIRST','EN_PL_HH','EN_PL_OTHER','SOURCE_FIRST_OTHER','INDIRECT_SOURCE_FIRST'},'unknown basis method')
        _need(type(b.get('indirect')) is bool and RE.nonempty(b.get('language')),'basis language/indirect flag absent')
        s=self.sources.get(b.get('source_id'))
        if s is None:raise RE.EvidenceError('basis source absent')
        _need(s['language']==b['language'],'basis language differs from actually read source')
        for u in self.subject['scope']:_need(self.is_read(s,u),'basis source not actually read in full task scope')
        p=self.proofs[s['source_id']][0]
        _need(p.get('method')==b and RE.nonempty(p.get('method_disclosure')) and RE.nonempty(p.get('prior_exposure')),'method/provenance disclosure differs or absent')
        _need((b['method']=='INDIRECT_SOURCE_FIRST') is b['indirect'],
              'indirect method and actual intermediary declaration differ')
        if b['method']=='PALI_FIRST':
            _need(is_pali(b['language']) and s['evidence_kind']=='SOURCE_TEXT',
                  'Pali-first needs the actual Pali source text, not a translation or dictionary')
        elif b['method'] in {'EN_PL_HH','EN_PL_OTHER'}:
            _need(b['language'].casefold() in {'en','eng','english'}
                  and s['evidence_kind']=='DIRECT_TRANSLATION',
                  'English-to-Polish needs the actual English translation basis')
        elif b['method']=='SOURCE_FIRST_OTHER':
            _need(not is_pali(b['language']) and s['evidence_kind']=='SOURCE_TEXT',
                  'other source-first needs an actual non-Pali original-language source')
        if b['indirect']:
            _need(b['method']=='INDIRECT_SOURCE_FIRST' and RE.nonempty(b.get('indirect_reason')) and RE.nonempty(b.get('limitations')),'indirect method needs reason, language and limits')
            intermediary=self.sources.get(b.get('intermediary_source_id'))
            _need(intermediary is not None and intermediary['evidence_kind']=='DIRECT_TRANSLATION','critical intermediary absent')
            _need(all(self.is_read(intermediary,u) for u in self.subject['scope']),'intermediary actual read scope incomplete')

    def declared_work(self, declaration):
        """Verify supplied canonical identity; never infer it from subject_id.

        The actual reader's authenticated record, source edition/carrier and
        unit-to-locus map are the identity evidence. An ID regex is only an
        unambiguous representation check, not evidence that a work was read.
        """
        sid=self.case['basis']['source_id'];profile=self.case['profile']
        work_id=declaration.get('work_id')
        _need(RE.nonempty(work_id) and declaration.get('profile')==profile,
              'declared canonical work/profile absent or differs')
        for proof in self.proofs.get(sid,[]):
            identity=proof.get('work_identity')
            if not isinstance(identity,dict):
                raise RE.EvidenceError('canonical work is not identified in the actual basis reading')
            _need(identity.get('profile')==profile
                  and identity.get('work_id')==work_id and RE.nonempty(identity.get('evidence_text')),
                  'canonical work is not identified in the actual basis reading')
            units=identity.get('units')
            if not isinstance(units,list):
                raise RE.EvidenceError('actual canonical source loci absent')
            _need(all(isinstance(u,dict) and RE.nonempty(u.get('source_locus')) for u in units),
                  'actual canonical source loci absent')
            _need(_strings([u.get('unit_id') for u in units])==proof['scope'],
                  'canonical identity does not cover the actual read scope')
            _need(all(u['source_locus'].startswith(work_id+':') and len(u['source_locus'])>len(work_id)+1 for u in units),
                  'source loci do not identify the same canonical work')
            if profile=='MN':
                _need(re.fullmatch(r'mn[1-9][0-9]*',work_id) is not None,
                      'MN canonical identity is unresolved; declared-method qualification is not evidenced')
            else:
                _need(re.fullmatch(r'mn[0-9]+',work_id,re.IGNORECASE) is None,
                      'canonical MN work conflicts with the actual source profile')
        _need(self.proofs.get(sid),'actual basis reading evidence absent')
        _need(not (profile=='MN' and work_id=='mn53'),
              'MN53/D4 requires section 28.2 documented R0; no declared-method exception is authorized')
        return work_id

    def historical_workflow(self, declaration, work_id):
        """A continuation needs its actual earlier translation and provenance.

        This is an intake/evidence qualification, not an owner policy choice or
        a calendar cutoff. Unknown or new section 28.2 work stays on HOLD.
        """
        workflow=self.artifact(declaration.get('workflow_evidence_ref'),'TRANSLATION_WORKFLOW_ATTESTATION')
        for key,value in (('profile',self.case['profile']),('work_id',work_id)):
            _need(workflow.get(key)==value,'workflow differs from the actual canonical work: '+key)
        _need(workflow.get('workflow')=='CONTINUATION_OF_EXISTING_TRANSLATION',
              'existing-translation qualification absent; new section 28.2 or unresolved workflow has no declared exception')
        _need(RE.nonempty(workflow.get('evidence_text')),'existing workflow evidence absent')
        started=RE.timestamp(workflow.get('started_at'))
        _need(started<=RE.timestamp(declaration.get('at')),'method declaration predates its workflow')
        prior=self.artifact(workflow.get('historical_record_ref'))
        _need(prior.get('kind')=='HISTORICAL_TRANSLATION_RECORD','historical translation record absent')
        _auth(prior)
        _need(RE.nonempty(prior.get('revision_id')) and prior['revision_id']!=self.subject['revision_id'],
              'a current candidate is not evidence of an earlier translation')
        for key,value in (('profile',self.case['profile']),('work_id',work_id)):
            _need(prior.get(key)==value,'historical record differs from the actual canonical work: '+key)
        _need(RE.nonempty(prior.get('evidence_text')),'historical provenance evidence absent')
        raw=RE.read_artifact(self.root,prior.get('translation_ref'))
        _need(raw.strip(),'earlier translation bytes are empty')
        RE.binding(prior,{'subject_id':self.subject['subject_id'],'revision_id':prior['revision_id'],
                          'content':prior['translation_ref'],'scope':self.subject['scope']})
        _need(RE.timestamp(prior.get('recorded_at'))<started,
              'earlier translation existence is not evidenced before the current workflow')

    def declared_method(self):
        b=self.case['basis']
        _need(RE.nonempty(b.get('limitations')),'declared Pali-first requires explicit basis limitations')
        p=self.artifact(b.get('prior_exposure_evidence_ref'),'PALI_FIRST_DECLARATION')
        _need(p.get('method_axis')==DECLARED and p.get('lack_of_order_proof') is True
              and p.get('limitations')==b['limitations'] and p.get('basis_source_id')==b['source_id'],
              'declared method, missing order proof, basis or limitations differ')
        _need(p.get('method_disclosure')==NEUTRAL_PALI_METHOD and RE.nonempty(p.get('prior_exposure')),
              'declared method needs the neutral statement and actual prior exposure disclosure')
        declared_at=RE.timestamp(p.get('at'))
        work_id=self.declared_work(p)
        self.historical_workflow(p,work_id)
        for proof in self.proofs[b['source_id']]:
            _need(proof.get('method')==b and proof.get('method_disclosure')==p['method_disclosure']
                  and proof.get('prior_exposure')==p['prior_exposure'],
                  'actual basis reading and declared method/exposure differ')
            _need(RE.timestamp(proof['at'])<=declared_at,'method declaration predates the actual basis reading')
        # Even an intermediate source check must have a bound prepared public
        # disclosure. Publication itself still depends on FORMAT, reviews and E.
        public=self.artifact(p.get('public_disclosure_evidence_ref'),'PUBLIC_SOURCE_DISCLOSURE')
        _need(self.case['public_sources'] and self.case['public_sources'][-1].get('disclosure_evidence_ref')
              ==p['public_disclosure_evidence_ref'],'declared method does not bind the actual public disclosure')
        for key in ('profile','work_id','basis_source_id','method_axis','limitations','lack_of_order_proof',
                    'prior_exposure','method_disclosure'):
            _need(public.get(key)==p[key],'public method disclosure differs: '+key)
        _need(public.get('lack_of_order_proof') is True and public.get('ai_used') is True,
              'public missing-proof/AI disclosure absent')
        _need(RE.nonempty(public.get('text')) and all(p[k] in public['text']
              for k in ('method_disclosure','limitations','prior_exposure')),
              'public text omits the actual method limitations or prior exposure')
        _need(declared_at<=RE.timestamp(public.get('at')),'public disclosure predates the method declaration')

    def declared_order_integrity(self, axis):
        """Missing order evidence is permitted; damaged supplied evidence is not.

        A retained R0 can exist without its chronology. Partial actual read logs
        remain partial. This checks their bytes/binding/events without inventing
        the missing sequence or treating prior exposure as a digest error.
        """
        b=self.case['basis'];ref=self.evidence.get('r0')
        if 'r0' in self.evidence:
            r0=RE.read_artifact(self.root,ref,json_object=True)
            _need(r0.get('schema')=='suttaflow-r0-v2' and r0.get('subject_id')==self.subject['subject_id'],
                  'retained R0 identity differs')
            units=r0.get('units')
            _need(isinstance(units,list) and all(isinstance(u,dict) and RE.nonempty(u.get('text')) for u in units),
                  'retained R0 unit text absent')
            _need(_strings([u.get('id') for u in units])==self.subject['scope'],
                  'retained R0 does not cover the full scope')
        if 'r0_sha256' in axis:
            _need(isinstance(ref,dict) and axis['r0_sha256']==ref.get('sha256'),
                  'declared axis contains an orphan or inconsistent R0 hash')
        if 'r0_evidence_ref' in b:
            self.artifact(b['r0_evidence_ref'])
            _need(self.index[b['r0_evidence_ref']]==ref,'basis R0 reference differs from the supplied R0 packet')
        if 'first_comparison_read_ref' in b:
            first=self.artifact(b['first_comparison_read_ref'],'SOURCE_READ_ATTESTATION',partial=True)
            comparisons=[p for s in self.sources.values() if s['source_id']!=b['source_id']
                         and s['evidence_kind'] in {'DIRECT_TRANSLATION','COMMENTARY','ADDITIONAL_VERIFIER'}
                         for p in self.proofs.get(s['source_id'],[])]
            _need(first in comparisons and RE.timestamp(first['at'])==min(RE.timestamp(p['at']) for p in comparisons),
                  'claimed first comparison is not the first actually attested comparison')
        if 'read_order' not in self.evidence:return
        log=RE.read_artifact(self.root,self.evidence['read_order'],json_object=True)
        _need(log.get('schema')=='suttaflow-read-order-v2' and log.get('subject_id')==self.subject['subject_id']
              and type(log.get('complete')) is bool,'retained read-order identity or completeness declaration differs')
        events=log.get('events')
        _need(isinstance(events,list) and events and all(isinstance(e,dict) for e in events),
              'retained read-order events absent')
        freezes=[]
        for event in events:
            kind=event.get('type');units=_strings(event.get('scope'));at=RE.timestamp(event.get('at'))
            _need(isinstance(kind,str) and kind in {'PALI_READ','DICTIONARY_READ','COMPARISON_READ','R0_FROZEN'}
                  and set(units)<=set(self.subject['scope']),'unknown retained read event or scope')
            if kind=='R0_FROZEN':
                _need(isinstance(ref,dict) and event.get('sha256')==ref['sha256'] and units==self.subject['scope'],
                      'retained R0 freeze has an absent/different artifact, digest or scope')
                freezes.append(event)
                continue
            source=self.sources.get(event.get('source_id'))
            if source is None:
                raise RE.EvidenceError('retained read-order source absent')
            expected='PALI_READ' if source['source_id']==b['source_id'] else 'DICTIONARY_READ' if source['evidence_kind']=='LEXICON' else 'COMPARISON_READ'
            _need(kind==expected and (kind!='COMPARISON_READ' or source['evidence_kind']
                  in {'DIRECT_TRANSLATION','COMMENTARY','ADDITIONAL_VERIFIER'}),'retained read event mislabels the actual source')
            attested={u for p in self.proofs.get(source['source_id'],[]) if RE.timestamp(p['at'])==at for u in p['scope']}
            _need(set(units)<=attested,'retained read event differs from actual reading attestations')
        _need(len(freezes)<=1,'duplicate retained R0 freeze events')
        if log['complete']:
            _need(len(freezes)==1,'claimed complete read-order lacks its R0 freeze')
            frozen=RE.timestamp(freezes[0]['at'])
            self.match_read_order(log,frozen,check_chronology=False)
            pali={u for e in events if e['type']=='PALI_READ' and RE.timestamp(e['at'])<=frozen for u in e['scope']}
            documented=(pali==set(self.subject['scope']) and all(RE.timestamp(e['at'])>frozen
                        for e in events if e['type']=='COMPARISON_READ'))
            _need(not documented,'complete supplied R0/order evidence contradicts the declaration of missing proof; reconcile B explicitly')

    def r0(self):
        if self.case['basis'].get('method')!='PALI_FIRST':return
        r0=self.evidence.get('r0')
        axis=self.method_axis if self.method_axis is not None else {
            'value':DOCUMENTED,'r0_sha256':r0.get('sha256') if isinstance(r0,dict) else None}
        if axis['value']==DECLARED:
            self.declared_method()
            self.declared_order_integrity(axis)
            return
        _need(axis['value']==DOCUMENTED,'axis B contradicts the actual Pali-first method')
        RE.documented_r0(self.evidence,self.subject,self.root,axis)
        log=RE.read_artifact(self.root,self.evidence['read_order'],json_object=True)
        frozen=RE.timestamp(next(e['at'] for e in log['events'] if e['type']=='R0_FROZEN'))
        self.match_read_order(log,frozen,check_chronology=True)

    def match_read_order(self, log, frozen, *, check_chronology):
        for s in self.sources.values():
            is_basis=s['source_id']==self.case['basis']['source_id']
            kind='PALI_READ' if is_basis else 'DICTIONARY_READ' if s['evidence_kind']=='LEXICON' else 'COMPARISON_READ'
            if not is_basis and s['evidence_kind'] not in {'LEXICON','DIRECT_TRANSLATION','COMMENTARY','ADDITIONAL_VERIFIER'}:continue
            events=[e for e in log['events'] if e['type']==kind]
            for p in self.proofs.get(s['source_id'],[]):
                if check_chronology:
                    if is_basis:_need(RE.timestamp(p['at'])<=frozen,'actual basis reading follows R0')
                    elif kind=='COMPARISON_READ':_need(RE.timestamp(p['at'])>frozen,'actual comparison attestation precedes R0')
                _need(any(RE.timestamp(e['at'])==RE.timestamp(p['at']) and set(p['scope'])<=set(e['scope'])
                          and e.get('source_id')==s['source_id'] for e in events),
                      'actual '+kind+' event absent from complete R0 read-order evidence')

    def lexical(self,d):
        _need(isinstance(d,dict) and RE.nonempty(d.get('decision_id')) and type(d.get('material')) is bool,'lexical decision identity/material flag absent')
        _need(d.get('pali_locus') in self.subject['scope'],'lexical locus outside scope')
        proofs=[self.artifact(k,'LEXICAL_DECISION',partial=True) for k in _strings(d.get('evidence_refs'))]
        p=next((p for p in proofs if p.get('decision_id')==d['decision_id']),None)
        if p is None:raise RE.EvidenceError('matching lexical decision proof absent')
        _need(d['pali_locus'] in p['scope'],'lexical proof does not cover its claimed locus')
        for k in ('pali_locus','material','uncertainty','dictionary_source_ids'):_need(p.get(k)==d.get(k),'lexical decision differs: '+k)
        decision_at=RE.timestamp(p.get('at'))
        if d['material']:
            for k in ('pali_clause','surface_form','lemma','context','canonical_context','chosen','reason','uncertainty'):
                _need(RE.nonempty(p.get(k)),'material lexical protocol missing '+k)
            _strings(p.get('analyses'));_strings(p.get('polish_alternatives'))
        ids=_strings(d.get('dictionary_source_ids'),empty=not d['material'])
        roles=set()
        for sid in ids:
            s=self.sources.get(sid)
            if s is None or s['evidence_kind']!='LEXICON':
                raise RE.EvidenceError('lexical evidence is not an identified dictionary')
            _need(self.is_read(s,d['pali_locus']),'dictionary entry not actually read/used for lexical locus')
            _need(self.reads[sid][d['pali_locus']]<=decision_at,'lexical decision precedes the cited dictionary reading')
            # A different lemma or another unit read earlier cannot backdate this
            # exact lexical control. Later supplementary readings stay separate.
            entries=[e for proof in self.proofs.get(sid,[])
                     if d['pali_locus'] in proof['scope'] and RE.timestamp(proof['at'])<=decision_at
                     for e in proof.get('entries',[])
                     if isinstance(e,dict) and e.get('lemma')==p.get('lemma')]
            _need(entries and all(RE.nonempty(e.get('gloss')) and RE.nonempty(e.get('entry_locator')) for e in entries),'actual dictionary lemma/gloss/entry locus absent')
            inside=all(e.get('within_published_range') is True for e in entries) and _in_dictionary_range(s['profile_role'],p['lemma'])
            if not inside:self.bad('010','dictionary does not cover the cited lemma',sid)
            _need(inside,'out-of-range entry cannot count as dictionary control')
            roles.add(s['profile_role'])
        if d['material'] or d.get('claims_double_lexical_control') is True:
            _need('DPD' in roles and bool(roles & {'CONE','PED','CPD'}),'material/double control needs DPD and a proper philological dictionary; DPPN is not a substitute')
        if p.get('ambiguity') is True:
            for stage in self.profile['sequence']:
                for s in self.sources.values():
                    if s['profile_role'] in stage:
                        for u in p['scope']:
                            if not (self.is_read(s,u) or self.guard('005',lambda s=s,u=u:self.queried_absent(s,u),s['source_id'])):
                                self.bad('007','material ambiguity requires resolution of additional available control',s['source_id']+':'+u)

    def parallels(self):
        families: dict[str, set[str]] = {k:set() for k in PARALLELS}
        ids=set()
        for q in self.case['parallel_queries']:
            _need(isinstance(q,dict),'parallel query must be an object')
            _need(RE.nonempty(q.get('query_id')) and q['query_id'] not in ids,'missing/duplicate parallel query ID');ids.add(q['query_id'])
            p=self.artifact(q.get('evidence_ref'),'PARALLEL_QUERY',partial=True)
            for k in ('query_id','scope','target_family','result','result_status'):_need(p.get(k)==q.get(k),'parallel query proof differs: '+k)
            _need(q['target_family'] in PARALLELS and RE.nonempty(q.get('result')),'unknown target or empty parallel query result')
            result=q.get('result_status')
            _need(isinstance(result,str) and result in PARALLEL_RESULTS and result!='UNREVIEWED',
                  'parallel query has no completed structured result')
            _strings(p.get('places_checked'));_need(RE.nonempty(p.get('query_text')),'actual parallel query absent');query_at=RE.timestamp(p.get('at'))
            _need(set(q['scope'])<=set(self.subject['scope']),'parallel query scope exceeds task')
            if result=='NOT_APPLICABLE':_need(RE.nonempty(p.get('reason')),'not-applicable query lacks reason')
            if result=='MATCH':
                source_ids=_strings(p.get('source_ids'))
                _need(RE.nonempty(p.get('exact_locus')),'parallel match lacks exact locus')
                if 'matches' in p:
                    matches=p['matches']
                    _need(isinstance(matches,list) and matches,'parallel matches must be a nonempty list')
                else:
                    matches=[{'source_id':sid,'scope':q['scope'],'exact_locus':p['exact_locus']} for sid in source_ids]
                matched_sources=set()
                for match in matches:
                    _need(isinstance(match,dict) and set(match)=={'source_id','scope','exact_locus'},'parallel match record malformed')
                    sid=match.get('source_id')
                    _need(RE.nonempty(sid),'parallel match source ID absent')
                    matched_sources.add(sid)
                    units=_strings(match.get('scope'))
                    _need(set(units)<=set(q['scope']),'parallel match scope exceeds query')
                    _need(RE.nonempty(match.get('exact_locus')),'parallel match lacks exact locus')
                    s=self.sources.get(sid)
                    _need(s is not None and s['used'],'parallel match source not read/used')
                    for u in units:
                        _need(self.is_read(s,u),'parallel match unit not actually read/used')
                        _need(self.reads[sid][u]<=query_at,'parallel match precedes source reading')
                _need(matched_sources==set(source_ids),'parallel match source inventory differs')
            families[q['target_family']].update(q['scope'])
        _need(all(s==set(self.subject['scope']) for s in families.values()),'parallel query coverage/applicability declarations incomplete')

    def bibliography(self):
        seen=set();order=[];groups=self.contract['public_source_group_order']
        for item in self.case['public_sources']:
            _need(isinstance(item,dict),'public citation must be an object')
            sid=item.get('source_id');_need(sid in self.sources and sid not in seen,'unknown/duplicate public source ID');seen.add(sid)
            s=self.sources[sid];units=_strings(item.get('represented_scope'))
            _need(s.get('read_state')=='READ' and set(units)<=set(self.reads.get(sid,{})),'public source is unread or exaggerates read scope')
            if s.get('used'):_need(set(units)==set(s['read_scope']),'used source bibliography omits actual represented scope')
            _need(RE.nonempty(item.get('citation')),'source citation absent')
            _need(item.get('group') in groups,'unknown public source group');order.append(groups.index(item['group']))
            self.guard('013',lambda item=item,s=s:self.public_item(item,s),sid)
        _need({s['source_id'] for s in self.sources.values() if s.get('used')}<=seen,'actually used source omitted from bibliography')
        if order!=sorted(order):self.bad('013','public source groups are out of normative order')
        if self.case['intended_publication']:
            _need(self.case['public_sources'],'public bibliography absent')
            self.guard('013',self.disclosure)

    def public_item(self,item,s):
        groups=self.contract['public_source_group_order']
        expected=0 if s['source_id']==self.case['basis'].get('source_id') else 1 if s['evidence_kind']=='CONTROL_PALI' else 4 if s['evidence_kind']=='LEXICON' else 3 if s['evidence_kind']=='ADDITIONAL_VERIFIER' else 5 if s['evidence_kind'] in {'COMMENTARY','PARALLEL'} else 2
        _need(item['group']==groups[expected],'public source group differs from actual source role')
        if s['profile_role']=='DPD':
            _need(RE.nonempty(item.get('attribution')) and s['author_or_editor'] in item['attribution']
                  and 'CC BY-NC-SA 4.0' in item['attribution'],'DPD author/licence attribution absent')
        if not self.case['intended_publication']:return
        if item.get('book_citation_instead_of_unofficial_link') is True:
            _need(not item.get('official_url'),'unofficial/private book citation must not expose a claimed official copy link')
            _need(all(s[k] in item['citation'] for k in ('title','author_or_editor','edition')),'book citation lacks attested title/author/edition')
            return
        url=item.get('official_url');_need(RE.nonempty(url) and urlparse(url).scheme in {'http','https'},'official public URL absent')
        RE.timestamp(item.get('link_checked_at'))
        p=self.artifact(item.get('link_check_evidence_ref'),'PUBLIC_LINK_CHECK',partial=True)
        _need(p.get('source_id')==s['source_id'] and p.get('url')==url and p.get('checked_at')==item['link_checked_at']
              and p.get('is_official') is True and p.get('is_public') is True and p.get('reachable') is True,
              'real checked official link evidence absent or differs')

    def disclosure(self):
        item=self.case['public_sources'][-1]
        p=self.artifact(item.get('disclosure_evidence_ref'),'PUBLIC_SOURCE_DISCLOSURE')
        RE.timestamp(p.get('at'))
        _need(type(p.get('ai_used')) is bool and p.get('human_review_status') in {'NO_HUMAN_REVIEW','PARTIAL_HUMAN_REVIEW','FULL_HUMAN_REVIEW','UNKNOWN'}
              and RE.nonempty(p.get('text')),'truthful AI/human disclosure attestation absent')
        if self.evidence.get('author_report') or self.evidence.get('reviewer_report'):
            _need(p['ai_used'] is True,'AI review evidence contradicts the public AI disclosure')
        if p['human_review_status'] in {'PARTIAL_HUMAN_REVIEW','FULL_HUMAN_REVIEW'}:
            r=RE.human_review(self.evidence,self.subject,self.root,
                              partial=p['human_review_status']=='PARTIAL_HUMAN_REVIEW')
            actual='FULL_HUMAN_REVIEW' if r['scope']==self.subject['scope'] else 'PARTIAL_HUMAN_REVIEW'
            _need(p['human_review_status']==actual,'public human review scope differs from verified report')
            _need(RE.timestamp(r['completed_at'])<=RE.timestamp(p['at']),
                  'public disclosure predates the claimed completed human review')

    def rights(self):
        if not self.case['intended_publication']:return
        covered=set()
        for key in _strings(self.case['rights_evidence_refs'],empty=True):
            p=self.artifact(key,'SOURCE_RIGHTS_CLEARANCE')
            _need(p.get('source_id') in self.sources,'rights clearance for unknown source')
            _need(p.get('permission')=='GRANTED' and p.get('permitted_use')=='PUBLICATION','no applicable rights clearance; non-monetization is not permission')
            for k in ('licensor','source_uri','verified_by','attribution'):_need(RE.nonempty(p.get(k)),'rights evidence missing '+k)
            RE.timestamp(p.get('verified_at'));covered.add(p['source_id'])
        _need({sid for sid,s in self.sources.items() if s.get('used')}<=covered,'actual rights/attribution evidence missing for intended public use')

    def hh_method(self):
        if self.case['basis'].get('method')!='EN_PL_HH':return
        s=self.sources.get(self.case['basis'].get('source_id'))
        if s is None or not s['profile_role'].startswith('HH') or s['language']!='en':
            raise RE.EvidenceError('EN_PL_HH requires actual English HH basis')
        for p in self.proofs.get(s['source_id'],[]):
            notes=p.get('hh_notes')
            if not isinstance(notes,dict):raise RE.EvidenceError('HH notes/method evidence absent')
            _need(_strings(notes.get('original'),empty=True)==_strings(notes.get('retained'),empty=True)
                  and notes.get('attributed_to')=='HH','HH source notes removed or attribution absent')
            _need(notes.get('pali_disputes_checked') is True and notes.get('terminology_checked') is True
                  and notes.get('calque_basis')=='HH','HH dispute/terminology/calque basis evidence absent')

    def vinaya(self):
        if not self.case['profile'].startswith('VINAYA'):return
        b=self.case['basis'];s=self.sources.get(b.get('source_id'))
        if s is None or s['language']!=b.get('language'):
            raise RE.EvidenceError('Vinaya actual witness language differs')
        if self.case['profile']=='VINAYA_OTHER':
            _need(b.get('method') in {'SOURCE_FIRST_OTHER','INDIRECT_SOURCE_FIRST'},'non-Pali Vinaya is not direct Pali-first')
        entries=[]
        for p in self.proofs.get(s['source_id'],[]):
            _need(RE.nonempty(p.get('tradition')),'Vinaya witness/tradition absent')
            _need(isinstance(p.get('vinaya_structure'),list),'Vinaya structural boundaries not recorded')
            entries+=p['vinaya_structure']
        _need(entries and all(isinstance(e,dict) and e.get('kind') in STRUCTURES and RE.nonempty(e.get('reference')) for e in entries),
              'Vinaya narrative/rule/definition/exception/procedure reference absent')
        units=[e.get('unit_id') for e in entries]
        _need(len(set(units))==len(units) and set(units)==set(self.subject['scope']),'Vinaya structure does not cover exact source scope')

    def run(self):
        if not self.guard('001',self.initialize):return self.result()
        for q in self.case['queries']:self.guard('005',lambda q=q:self.query(q),q.get('query_id','') if isinstance(q,dict) else '')
        for s in self.sources.values():self.guard('003',lambda s=s:self.source(s),s['source_id'])
        for s in self.sources.values():self.guard('005',lambda s=s:self.availability(s),s['source_id'])
        self.guard('001',self.basis)
        configured=self.guard('008',self.other_kn_profile,blocked=True)
        self.guard('008',self.role_checks)
        if configured:self.guard('004',self.priority)
        self.guard('002',self.r0)
        lexids=[]
        for d in self.case['lexical_decisions']:
            did=d.get('decision_id') if isinstance(d,dict) else None
            if did in lexids:self.bad('009','duplicate lexical decision ID',did)
            lexids.append(did);self.guard('009',lambda d=d:self.lexical(d),did)
        self.guard('011',self.parallels)
        self.guard('012',self.bibliography)
        self.guard('014',self.rights)
        self.guard('016',self.hh_method)
        self.guard('017',self.vinaya)
        return self.result()

    def result(self):
        c=self.case if isinstance(self.case,dict) else {}
        return {'status':'BLOCKED' if any(x['status']=='BLOCKED' for x in self.reasons) else 'HOLD' if self.reasons else READY,
                'reasons':self.reasons,'subject_id':c.get('subject_id'),'revision_id':c.get('revision_id'),
                'content_sha256':c.get('content_sha256'),'scope':c.get('scope'),
                'evidence_contract':'suttaflow-source-contract-v2/2.0-RC.1','is_synthetic':c.get('is_synthetic'),
                'scope_of_result':'Technical validation of supplied source evidence only; no philological certification or publication authority.'}


def validate(case, evidence_index, *, root, evidence=None, contract=None, trusted_decisions=None, method_axis=None):
    """Return structured source readiness/HOLD/BLOCKED, without mutating inputs.

    ``evidence_index`` maps IDs to {path,sha256,bytes} inside ``root``.
    ``evidence`` is the actual release-evidence-v2 subject/R0 packet; it may
    instead be an indexed ``case.evidence_v2_packet_ref``. Human exceptions
    must also occur unchanged in ``trusted_decisions`` keyed by evidence ID.
    ``method_axis`` is the already checked axis B object, never inferred from
    ``basis.method``. Omission keeps the documented-R0 requirement. An explicit
    declared axis needs bound historical-workflow and public disclosure proof.
    None of these caller-supplied ledgers is independently authenticated here.
    """
    v=_Validation(case,evidence_index,root,evidence,contract,trusted_decisions,method_axis)
    if contract is None:
        try:v.contract=json.loads(CONTRACT_PATH.read_text())
        except (OSError,ValueError) as exc:
            v.bad('001','versioned source contract unavailable: '+str(exc),str(CONTRACT_PATH),blocked=True)
            return v.result()
    return v.run()
