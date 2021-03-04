from time import sleep

from scicast_bot_session.client.scicast_bot_session import SciCastBotSession
from scicast_bot_session.common.utils import scicast_bot_urls
import os
from random import randint
from typing import Sequence

api_key = os.getenv("BOT_API_KEY")
if api_key is None:
    api_key = input('BOT_API_KEY not found - please enter:')
print('Using this BOT_API_KEY:', api_key)

SITE = 'sandbox'
#SITE='dev'
URL = scicast_bot_urls[SITE]

def get_qid():
    '''TODO: make this smarter. Dev span is only R5'''
    if SITE=='sandbox':
        return randint(2,301)
    if SITE=='dev':
        return randint(1103,1403)

    raise ValueError('Simple Bot is not rated for production site!')

def get_nth_prob_from_history(history, n) -> Sequence:
    '''Note: returns a whole list or array.'''
    return [float(x) for x in history[n]['probabilities'].split(',')]

def get_latest_prob_from_history(history) -> float:
    return float(history[-1]['probabilities'].split(',')[1])

def get_latest_prob_from_qid(qid: int, s:SciCastBotSession) -> float:
    history = s.get_question_history(qid)
    return float(history[-1]['probabilities'].split(',')[1])

def get_new_prob(orig_prob):
            new_prob = orig_prob + .01
            if new_prob > .9:
                new_prob -= .02
            return new_prob

# Just some pretty-print routines. 
def print_dict(D, name='<DICT>', KEYLEN=15, prefix=''):
    '''Tabular pretty-print.'''
    if name is not None:
        print(f'{prefix}___{name}___:')
    for key in D:
        print(f'{prefix}\t{key:{KEYLEN}}: {D[key]}')

def print_trade(trade, prefix=''):
    try:
        t, q, u = trade['trade'], trade['question'], trade['user']
    except KeyError:
        tr = trade['trade']
        trq = tr['question']
        t, q, u = \
            {'tid':tr['id'], 'old':tr['old_value_list'], 'new':tr['new_value_list'], 'status':tr['trade_status'], 'assets':tr['assets_per_option']}, \
            {'id': trq['id'], 'cid': trq['claim_id'], 'name':trq['short_name'], 'round':trq['round_id'], 'batch':trq['batch_id']}, \
            {'user_id':tr['user_id']}
    print(f"{prefix}___TRADE by {u['user_id']} on Q. {q['id']}___")
    print_dict(q, None, prefix=prefix)
    print_dict(t, None, prefix=prefix)
    print_dict(u, None, prefix=prefix)

def print_box(s):
    stars = '*' * (6 + len(s))
    print(f"{stars}\n** {s} **\n{stars}")


if __name__ == '__main__':
    with SciCastBotSession(base_url=URL, api_key=api_key) as s:
        ri = s.get_round_info()
        print_dict(ri['R5'], f'ROUND 5 INFO')

    while(True):
        with SciCastBotSession(base_url=URL, api_key=api_key) as s:

            assets = s.get_user_info()
            print_dict(assets, 'PRE-TRADE ASSETS')

            recent_trades = s.get_recent_trades()[:1]
            print_box('MOST RECENT TRADE')
            for item in recent_trades:
                print_trade(item, prefix='\t')

            q_id = get_qid()
            print_box(f'SELECTING Q. {q_id} for trade.')
            orig_prob = get_latest_prob_from_qid(q_id, s)
            new_prob = get_new_prob(orig_prob)
            
            # add a trade
            print(f"Trading {orig_prob:.2f} -> {new_prob:.2f}")
            result = s.trade(q_id, orig_prob+.01, comment='[SimpleBot]: change by 1%.')
            if 'trade' in result.keys():
                print_trade(result, prefix='\t')
            else:
                print(result)

            current_prob = get_latest_prob_from_qid(q_id, s)
            print('Post-trade prob:', current_prob)

            # Check assets
            assets = s.get_user_info()
            print_dict(assets, 'POST-TRADE ASSETS')

            # undo it
            print(f"___UNDO. Trading {new_prob:.2f} -> {orig_prob:.2f}___")
            result = s.trade(q_id, orig_prob, comment='[SimpleBot]: put it back.')
            if 'trade' in result.keys():
                print_trade(result, prefix='\t')
            else:
                print(result)

            current_prob = get_latest_prob_from_qid(q_id, s)
            print('Post-undo prob:', current_prob)

            # Check Assets
            assets = s.get_user_info()
            print_dict(assets, 'POST-UNDO ASSETS')


        sleep(60)
