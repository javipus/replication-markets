from PyAltmetric.pyaltmetric import Altmetric
import PyAltmetric
import re
import json

# TODO
# Note that you don't need to predict # citations but relative rank among the papers in the db
# this means you don't need to fit a regression for this, just do rank(features) = rank(citations)
# For the publication part, you want to use
# - logistic regression for published / not published
# - categorical-logistic or linear for impac factor?
# /TODO #

doi_regex = r"\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'<>])\S)+)v1\.article-metrics\b"
readers = 'mendeley', 'citeulike', 'connotea'

def write_dois(json_file="data/papers.json", save_file="data/doi.txt"):
    with open(json_file, 'r') as f:
        links = [line['link'] for line in json.load(f)]

    dois = '\n'.join([get_doi_from_url(link) for link in links])

    with open(save_file, 'w') as f:
        f.write(dois)
 
def get_doi_from_url(url):
    finds = re.findall(doi_regex, url)
    assert len(finds) == 1, f"More than one DOI in url: {url}"
    return finds[0]

def get_features_from_doi(doi, feature_names=None):
    article = Altmetric().article_from_doi(doi)
    if article is None:
        return
    features = {fn: get_feature(article, fn) for fn in feature_names}
    return features

def get_feature(article, feature_name):
    if feature_name is None:
        return
    try:
        return getattr(article, feature_name)
    except AttributeError as e:
        if feature_name in readers:
            return getattr(article, 'readers').get(feature_name, None)
        else:
            raise AttributeError(f"{feature_name} not found!")

def build_db_from_dois(dois_path="data/doi.txt", db_path="data/db.json", feature_names=None):
    with open(dois_path, 'r') as f:
        dois = f.read().splitlines()
        
    db = {}
    
    for doi in dois:
        try:
            db[doi] = get_features_from_doi(doi, feature_names)
        except TypeError:
            raise
            # print(f"{doi} not found")

    with open(db_path, 'w') as f:
        json.dump(db, f)

if __name__=='__main__':

    write_dois()
    build_db_from_dois(feature_names=['mendeley'])