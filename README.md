Trading strategy:

- Find info available in json/spreadsheet + API + easy data augmentation strategies (query gscholar, etc.)
    - download raw data: https://www.replicationmarkets.com/index.php/preprints/
    - already published papers: https://keywscope.sharepoint.com/:x:/g/EfgxFqVD2d5GiG5zBt51OmYBrAWEHD15Yp-hnbu02OHwgA?rtime=qCimEU6G2Eg
- Find data relevant to predict citation counts and publication
    - Relevant reddit thread: https://www.reddit.com/r/ReplicationMarkets/comments/jpkqqy/base_rate_for_publications_by_journal_impact/
    - Relevant paper (maybe): https://www.sciencedirect.com/science/article/pii/S1751157718301767
    - Relevant blogpost: https://followtheargument.org/replication-markets-for-covid-19-preprints
- Use Kelly criterion for multiple simultaneous bets, as explained here: http://www.eecs.harvard.edu/cs286r/courses/fall12/papers/Thorpe_KellyCriterion2007.pdf

In a next iteration you could update base rates with judgmental forecasting based on google searches of the preprints, gauging expert sentiment on twitter, whatever

Tools:
 - [*rxiv api python wrapper](https://github.com/PhosphorylatedRabbits/paperscraper)
 - [biorxiv api primer](https://api.biorxiv.org/) i think medrxiv works the same
 - [altmetrics api python wrapper](https://github.com/CenterForOpenScience/PyAltmetric)
 - [biorxiv api cli](https://pypi.org/project/biorxiv-cli/)
 - [biorxiv retriever](https://pypi.org/project/biorxiv-retriever/) also in python

 Pipeline
    1. query (bio|med)rxiv api with article title or link
    2. get all info in json
    3. from DOI, query altmetric api
    4. augment json <- **YOU'RE HERE**
    5. **TODO**: figure out how to get the DOI info from the RM API; you should use `session.get_questions()` but then what? hard to say without documentation or examples... that's why you may need an API key to test it live; also I'm missing the `client` module where the session class is supposed to be defined hmmm...
    6. include scite? you'd need to request access to their API, which is "researchers only"
    7. include author affiliation, h-index - how do I get this?