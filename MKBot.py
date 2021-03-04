from scicast_bot_session.client.scicast_bot_session import SciCastBotSession
from scicast_bot_session.common.utils import scicast_bot_urls
import botutils
import lmsrutils as lmsr
from api_key import API_KEY, API_KEY_TEST

from pyaltmetric import Altmetric

import random
import os
import logging
import json
from time import sleep
import datetime

from scipy.stats import percentileofscore

# TODO too late to solve this exactly
# - divide your bankroll in 3 - one for each type of market
# - for citations
# -- divide bankroll further by # papers
# -- apply kelly separately to each market (start from largest)

ROUND_ID = 'R400'
SITE = 'dev'
DB_PATH = os.path.abspath('data/db.json')
PDB_PATH = os.path.abspath('data/pdb.json')

class LoginError(Exception):
    pass

#class Question:
is_tradeable = lambda q: q['question']['is_tradeable']
is_citations = lambda q: q['question_categories'][-1]['name'] == 'Citations'
is_nopub = lambda q: q['question_categories'][-1]['name'] == 'No Publication'
get_qid = lambda q: str(q['question']['id'])
get_prob = lambda q: q['prob'][1]
get_doi = lambda q: q['question']['claim_id']

class Bot:
    bot_comment = "[Bot] generic bot"

    def __init__(self, api_key, site=SITE, round_id=ROUND_ID, **kwds):
        # constants
        self.api_key = api_key
        self.site = site
        self.round_id = round_id

        # login
        self.session = self.login()
        
        # pull data
        self.user_info = self.session.get_user_info()
        self.bankroll = self.user_info['cash']

    def trade(self, qid, shares):
        raise NotImplementedError

    def get_citation_questions(self, round_id=ROUND_ID):
        return [q for q in self.session.get_questions(round_id) if \
            is_tradeable(q) and is_citations(q)]

    def get_nopub_questions(self, round_id=ROUND_ID):
        return [q for q in self.session.get_questions(round_id) if \
            is_tradeable(q) and is_nopub(q)]

    def get_q(self, question):
        return question['prob'][1]
    
    def get_qs(self):
        return {get_qid(question): self.get_q(question) for question in self.questions}
    
    def get_doi(self, question):
        return question['question']['claim_id']

    def login(self):
        try:
            URL = scicast_bot_urls[self.site]
            s = SciCastBotSession(base_url=URL, api_key=self.api_key)
        except Exception as e:
            raise LoginError(f"{e.msg}")

        return s

class PublishedBot(Bot):

    def __init__(self, api_key, site='dev', round_id=ROUND_ID, db=PDB_PATH):
        super().__init__(api_key=api_key, site=site, round_id=round_id)
        self.db = JSONDB(db, update=False)
        self.questions = self.get_nopub_questions()
        self.ps = {get_qid(question): 1. / 100 for question in self.questions if get_doi(question) in [paper['doi'] for paper in self.db._data.values()]}
        self.qs = {qid: q for qid, q in self.get_qs().items() if str(qid) in self.ps.keys()}

    def calculate_bet_sizes(self):
        assert self.ps.keys() == self.qs.keys(), "Key mismatch between ps and qs!"
        fs = {qid: kelly(self.ps[qid], self.qs[qid]) / len(self.ps) for qid in self.ps}
        assert sum(fs.values()) < 1 / len(self.ps), "Betting more than your bankroll"
        return fs

    def trade(self, dry_run=False, sleep_secs=2):
        print(f'Published Bot {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}')
        fs = self.calculate_bet_sizes()

        for k, f in fs.items():
            
            budget = f*self.bankroll
            sgn = 'yes' if budget > 0 else 'no'
            p, q = self.ps[k], self.qs[k]

            print(f"Trading up to ${abs(budget):.3} towards {sgn} on question {k} -- Proability {100*q:.3} -> {100*p:.3}")
            
            try:
                if not dry_run:
                    capped_trade(
                        s=self.session,
                        qid=int(k),
                        towards=sgn,
                        old_prob=self.qs[k],
                        new_prob=self.ps[k], 
                        max_cost=abs(budget),
                        comment=self.bot_comment
                        )
                    sleep(sleep_secs)
            except Exception as e:
                print(f'Error trading qid {k} : {e}')
                continue

class MKBot(Bot):
    bot_comment = """[MKBot] is short for Mendeley-Kelly bot. It predicts citation rank for a paper from number of Mendeley downloads and bets on the associated market using a fraction determined by the Kelly criterion."""

    def __init__(self, api_key, site='dev', round_id=ROUND_ID, db=DB_PATH, update_db=False):
        super().__init__(api_key=api_key, site=site, round_id=round_id)
        self.db = JSONDB(db, update=update_db)
        self.questions = self.get_citation_questions()
        self.ps = self.calculate_ps()
        self.qs = self.get_qs()

    def calculate_ps(self):
        ps = {qid: paper['mendeley'] for qid, paper in self.db._data.items()}
        ps = {qid: percentileofscore(list(ps.values()), p) / 100. for qid, p in ps.items()}
        return ps

    def calculate_bet_sizes(self):
        assert self.ps.keys() == self.qs.keys(), "Key mismatch between ps and qs!"
        fs = {qid: kelly(self.ps[qid], self.qs[qid]) / len(self.ps) for qid in self.ps}
        assert sum(fs.values()) < 1 / len(self.ps), "Betting more than your bankroll"
        return fs

    def trade(self, dry_run=False, sleep_secs=2):
        print(f'MK Bot {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}')
        fs = self.calculate_bet_sizes()

        for k, f in fs.items():
            
            budget = f*self.bankroll
            sgn = 'yes' if budget > 0 else 'no'
            p, q = self.ps[k], self.qs[k]

            print(f"Trading up to ${abs(budget):.3} towards {sgn} on question {k} -- Proability {100*q:.3} -> {100*p:.3}")
            
            try:
                if not dry_run:
                    capped_trade(
                        s=self.session,
                        qid=int(k),
                        towards=sgn,
                        old_prob=self.qs[k],
                        new_prob=self.ps[k], 
                        max_cost=abs(budget),
                        comment=self.bot_comment
                        )
                    sleep(sleep_secs)
            except Exception as e:
                print(f'Error trading qid {k} : {e}')
                continue

def kelly(p, q, correction = .99):
    b = (1-q) / q
    f = p - (1-p) / b
    return f * correction

def capped_trade(s,qid: int, towards, new_prob: float, 
                 old_prob: float, max_cost: float, comment:str='',
                 epsilon=0.001):
        """Trade P(Yes) from oldValue *towards* newValue, 
        spending no more than max_cost."""
        
        if towards=='yes':
            pass
        elif towards=='no':
            old_prob, new_prob = 1 - old_prob, 1 - new_prob
        else:
            raise ValueError("yes or no")

        P = [1 - old_prob, old_prob]

        q_min, q_max = lmsr.trade_limits(P, max_cost, 1)
        params = {'question_id': qid, 'comment': comment,
                  'old_value': str(P), 'max_cost': max_cost}
        if q_min < new_prob < q_max:
            params['new_value'] = new_prob
        elif new_prob > old_prob:
            params['new_value'] = q_max - epsilon
        else:
            params['new_value'] = q_min + epsilon
        return s.trade(**params)

class JSONDB:

    def __init__(self, db_path, update=False, services=['rm', 'alt']):
        self.path = db_path
        self.services = services

        if update:
            self.update()
        else:
            self.load()

    def load(self):
        with open(self.path, 'r') as f:
            self._data = json.load(f)

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self._data, f)

    def update(self):
        print("Pulling questions from RM site...")
        data = {get_qid(q): {'doi': get_doi(q)} for q in Bot(api_key=API_KEY).get_citation_questions()}
        print("Done!\n")

        if 'alt' in self.services:
            print("Pulling data from altmetrics...")
            
            for i, (qid, paper) in enumerate(data.items()):
                print(f"Paper {i+1} of {len(data)}...")
                data[qid]['mendeley'] = int(Altmetric().article_from_doi(paper["doi"]).readers['mendeley'])
            
            print("Done!\n")

        if 'scite' in self.services:
            pass
        
        self._data = data
        self.save()

def main(test=True, dry_run=False, update_db=False, sleep_secs=2):
    if not test:
        _key = API_KEY
        _site = 'covid19'
    else:
        _key = API_KEY_TEST
        _site = SITE
    
    bot = MKBot(api_key=_key, site=_site, db=DB_PATH, update_db=update_db)
    bot.trade(dry_run=dry_run, sleep_secs=sleep_secs)

# # RECALL THAT
# # > (Citation markets resolve as mixtures: a paper in the 75th %ile will count each Yes share as 0.75 and each No share as 0.25.)
# def get_optimal_fractions(ps, qs, bs, cov=None, mode='simple'):
#     if mode=='simple':
#         odds = [q / (1-q) for q in qs]
#         ms = []
#     # TODO
#     # - work out the general formula for N bets w/o correlation
#     # Covariance matrix for rank statistics X_i = Y_i - Y_j
#     # In these coordinates, my bet is that X_i > 0 for all i=1,...,n-1
#     sigma = [
#         [
#             (i==j) + (i==j+1) + (i+1==j) + (i+1==j+1)
#         for i in range(len(ps))
#         ]
#         for j in range(len(ps))
#     ]
#     raise NotImplementedError