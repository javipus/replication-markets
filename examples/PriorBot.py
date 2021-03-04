from scicast_bot_session.client.scicast_bot_session import SciCastBotSession
from scicast_bot_session.common.utils import scicast_bot_urls
import botutils
from time import process_time
import datetime
import random



prior_comment="[PriorBot] I try to enforce the starting prices. I think I’ll "\
"be right ~70% of the time. Use your superior human situation awareness to "\
"correct me and earn points!"

claim_count = 5

def trade(site='',bot='',roundid='',percent=0.005):
    try:
        print (f'\nPrior Bot {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}')
        api_key = botutils.lookup_key(site+bot)
        URL = scicast_bot_urls[site]
        s = SciCastBotSession(base_url=URL, api_key=api_key)
        qids = botutils.get_qid(s,roundid,flag=True)
        print(f'Trading on {URL}')
        start = process_time()
        print(f'Getting deltas: ',end='')
        deltas = botutils.get_deltas(s,qids)
        print(f' Completed in {process_time()-start} seconds')
        
        print(f'Randomly selecting {claim_count} claims from {[(qid[0],qid[1][1]) for qid in deltas[:50]]}')
        claims = random.sample(k=claim_count, population= deltas[:50])
        for claim in claims:
            try:
                #
                #if claim[1][0] <0.005: quit()  
                q_id = claim[0]
                botutils.print_box(f'SELECTING Q. {q_id} for trade.')
                assets = s.get_user_info()
                currentCash=assets["cash"]
                budget = botutils.get_trade_cost(cash=currentCash,fraction=percent)
                print(f'cash = {currentCash}, budget = {budget}')
                orig_prob = claim[1][2]
                print(f'Delta: {claim[1][1]}')
                #trade
                new_p =  claim[1][3] 
                print(f'current prob. = {orig_prob}\norginial prob. = {new_p}')
                if new_p != botutils.clip(orig_prob,claim[1][3]):
                    new_p = botutils.clip(orig_prob,claim[1][3])
                    print(f'Capped prob.: {new_p}')
                botutils.capped_trade(s,q_id, old_prob=orig_prob, new_prob=new_p, 
                                    max_cost=budget,comment=prior_comment)
                print(f"Piorbot/trade(): q_id={q_id}, p={orig_prob:.2f}, ",end='')
                print(f"q={new_p:.2f}, limit=${budget:.2f}",end='\n\n')
            except Exception as e:
                print(f'Error trading: {e}')
                continue 
    except Exception as e:
        print(f'Prior Bot Error: {e}')


    
