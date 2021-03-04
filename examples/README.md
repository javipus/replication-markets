# scicast_bot_example
Example bots for Replication Markets.

We provide two simple bots to show how to use the simplified bot API
developed in January 2020 for Replication Markets. (See for example, 
[the API docs](https://sandbox.replicationmarkets.com/bot/api_docs).)

See also [Bot Rules](BOT_RULES.md) for bot behavior guidelines. 

The two example bots are:
* **NoiseBot** selects a few claims at random, and for each one flips a coin. 
Heads, it raises the probability by a little bit (buys Yes / sells No). 
Tails, it reduces the probability (sells Yes / buys No).

* **PriorBot** has a simple model: it believes the starting price is right.
It sorts claims by most-changed, and randomly selects a few from among the
Top N.  It then nudges them back towards the starting price.

Both bots pick trade size using the smaller of:
* An absolute value like 1% (1 percentage point, .001) at a time, or
* A small fraction of their remaining budget (via `clipped_trade`)

We recommend you use similar guards to keep from spending all your points at once.

These examples explicitly adjust the probability. 
If you're more of a finance type, the API does provide some more 
buy/sell-oriented functions, but they are not demonstrated here. 

## Features:
* Demonstrates how to connect to a SciCastBotSession.
* Defaults to using the 'sandbox' site. 
* Shows how to get your available assets.
* Shows how to get recent trades.
* Shows how to get a particular claim's history.
* Shows how to extract the latest probability from that history.
* Shows how to make a trade with comment.
* Pretty-prints the returned data structures.

## Usage
1. Install the SciCastBotSession client: `pip install -r requirements.txt --upgrade`

2. Get a sandbox account.
  * Visit http://sandbox.replicationmarkets.com
  * Create an account.

3. Get an API key
  * Email the RM helpdesk (support@replicationmarkets.com) to ask.
  * View your profile page to see what it is. (Not your public profile!)

4. Make your API key available to the simple_bot.
  * It assumes you've exported an environment variable BOT_API_KEY. 
    * Unix example: `export BOT_API_KEY=xxxxxxxxxxxx`   (Use a real API key!)
    * Or, set this in your IDE under Runtime settings.
  * Or, put this in a file and replace the `os.getenv` call with
  a file read.
  * Or use an `input` call and paste it when run.
  * Last resort, hard code it, _but not if you share your code!_

5. Run the script, e.g. `python parse.py`


Of course, the point is for you to _modify_ these to do useful things.
PriorBot is likely your best starting place. In the future we may refactor
these to use inheritance.

Also note there may be more functions available than we demonstrate.
Such as `get_recent_trades`.  
		 

## Example Output - probably outdated
### Background info including 3 most recent trades
```
___ASSETS___:
        cash           : 299.9999064211614
___TRADE by 2 on Q. 62 at 2020-01-15T16:53:32+00:00___
        id             : 62
        name           : (Wright-2016-JConflictRes) Unpacking Territorial Disputes
        created_at     : 2020-01-15T16:53:32+00:00
        new_value      : 0.39999995
        old_value_list : ['0.59', '0.41000003']
        new_value_list : ['0.59999996', '0.39999995']
        dimension      : 1
        change         : -0.010000080000000022
        dimension_text : 
        user_id        : 2
        username       : sandbox_crt
___TRADE by 2 on Q. 62 at 2020-01-15T16:53:28+00:00___
        id             : 62
        name           : (Wright-2016-JConflictRes) Unpacking Territorial Disputes
        created_at     : 2020-01-15T16:53:28+00:00
        new_value      : 0.41000003
        old_value_list : ['0.6', '0.4']
        new_value_list : ['0.59', '0.41000003']
        dimension      : 1
        change         : 0.010000029999999993
        dimension_text : 
        user_id        : 2
        username       : sandbox_crt
___TRADE by 2 on Q. 32 at 2020-01-15T16:52:22+00:00___
        id             : 32
        name           : (Gray-2017-CompPolitStu) Leadership Turnover and the Durability of International Trade Commitments
        created_at     : 2020-01-15T16:52:22+00:00
        new_value      : 0.30000004
        old_value_list : ['0.68999994', '0.31']
        new_value_list : ['0.7', '0.30000004']
        dimension      : 1
        change         : -0.009999959999999974
        dimension_text : 
        user_id        : 2
        username       : sandbox_crt
```
### Now the trade:
```
*******************************
** SELECTING Q. 2 for trade. **
*******************************
Trading 0.80 -> 0.81
0.81
___ASSETS___:
        cash           : 292.59984827678375
Undo. Trading 0.81 -> 0.80
0.79999995
___ASSETS___:
        cash           : 299.9999064211614
```
