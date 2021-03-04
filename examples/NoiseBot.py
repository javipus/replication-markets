import random
from scicast_bot_session.client.scicast_bot_session import SciCastBotSession
from scicast_bot_session.common.utils import scicast_bot_urls
import botutils
from time import sleep
import datetime

noisebot_comment="[NoiseBot] I flip a coin to buy/sell shares. "\
                    "If I made a mistake, correct me to earn points!"
claim_count = 5

def trade(site,bot='',roundid:str='', percent=0.005):
    print (f'\nNoise Bot {datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}')
    try:
        # login
        api_key = botutils.lookup_key(site+bot)
        URL = scicast_bot_urls[site]
        s = SciCastBotSession(base_url=URL, api_key=api_key)
        
        # determine bet size
        assets = s.get_user_info()
        currentCash=assets["cash"]
        budget = botutils.get_trade_cost(cash=currentCash,fraction=percent)
        print(f'Trading on {URL}')
        print(f'cash = {currentCash}, budget = {budget}')
        #print('Getting random QID')
        #q_id = botutils.get_qid(s,roundid)
        
        # Find market to trade on
        qids = botutils.get_qid(s,roundid,flag=True)
        hist = botutils.get_ques_trade_counts(s,qids)
        print(f'Selecting {claim_count} least traded claims: ',end='')
        print(f'{hist[-claim_count:]}')
        claims =  [qid[0] for qid in hist[-claim_count:]]
        for q_id in claims: 
            try:
                botutils.print_box(f'SELECTING Q. {q_id} for trade.')
                sleep(20)
                if(q_id==-1):
                    quit()
                print('Getting original prob.')
                orig_prob = botutils.get_latest_prob(s,qid=q_id)
                print(f'orig prob = {orig_prob}')
                #trade
                #Delta from noisebot trade function in botbase
                new_p = orig_prob - 0.03
                if random.choice([True, False]):
                    new_p = orig_prob + 0.03   
                print(f'new prob = {new_p}')
                botutils.capped_trade(s,q_id, old_prob=orig_prob,new_prob=new_p, 
                                    max_cost=budget,comment=noisebot_comment)
                print(f"NoiseBot/trade(): q_id={q_id}, p={orig_prob:.2f}, ",
                end='')
                print(f"q={new_p:.2f}, limit=${budget:.2f}")
            except Exception as e:
                print(f'Error trading qid {q_id} : {e}')
                continue 
    except Exception as e:
            print(f'Noise Bot Error: {e}')

    
    
