#author@Mehul
# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer("english")

from nltk.corpus import stopwords
from datetime import datetime
import os
os.chdir('/root/maroon-transform/AI/RAKE')

import string
from random import randint
from operator import add
from datetime import datetime
from spacy.en import English
parser = English()


def getIndexList(List,indexof):
    IndexList = []
    for obj in List:
        if obj == indexof:
            IndexList.append(1)
        else:
            IndexList.append(0)
    return(IndexList)


##Connect to MongoDB
from pymongo import MongoClient
from bson import ObjectId
conn = MongoClient("mongodb://mehul:jeep@52.170.90.238:27003")
db = conn.Linkedin
CompanyED = db.CompanyED

query = {'$or' : [{'specialties' : {'$exists' : True}, 'description' : {'$exists' : True}}], 'NLP.posKeywords' : {'$exists':False}}
#count = CompanyED.find(query).count()


def posTag(doc):
    print('Starting {}'.format(doc['_id']))
    line = u''
    try:
      line += unicode(doc['description']).replace(u"\u2019","'")
    except:
      pass
    try:
      line += unicode(doc['specialties']).replace(u"\u2019","'")
    except:
      pass
    line = line.replace("-","")
    parseDoc = parser(line)
    token_text = [token.orth_ for token in parseDoc]
    token_pos = [token.pos_ for token in parseDoc]
    token_lemma = [token.lemma_ for token in parseDoc]
    idxPROPN = getIndexList(token_pos,u'PROPN') 
    idxNOUN = getIndexList(token_pos,u'NOUN')
    idxADJ = getIndexList(token_pos,u'ADJ')
    idxPROPN = getIndexList(token_pos,u'PROPN')
    idxCONJ = getIndexList(token_pos,u'CONJ')
    adNoun = map(add, map(add, idxNOUN, idxPROPN), idxADJ)
    posKeywords = []
    keyword = u''
    for i,token in enumerate(token_text):
        if adNoun[i] == 1:
            keyword += token + ' '
        else:
            if len(keyword) > 0:
                posKeywords.append(keyword.strip().lower())
            keyword = u''
    posKeywords = list(set(posKeywords))
    #print CompanyED.update({'_id':doc['_id']},{'$set' : {'NLP.posKeywords' : posKeywords, 'status.posUpdate':datetime.utcnow()}})
    return posKeywords


import rake
import operator

# Path to Stoplist, Min Character length, Max number of words in phrase, Number of occurences
rake_object = rake.Rake("SmartStoplist.txt", 3, 3, 1)

def repl_char(text):
   try:
       text = text.replace('-','')
       chars_to_remove = [')' ,'(', "'", '"', '/']
       remove_punctuation_map = dict((ord(char), None) for char in chars_to_remove)
       text = text.translate(remove_punctuation_map)
       text = " ".join(text.split())
   except:
        return
   return text


def get_keywords(text):
    text = repl_char(text)
    try:
        keywords = rake_object.run(text)
    except:
        return []
    return keywords


def update(doc):
    posTags = posTag(doc)
    print('Starting {}'.format(doc['_id']))
    text = ''
    try:
        text += doc['description']
    except:
        pass
    Words = []
    try:
        specs = doc['specialties']
        specs = ' '.join([word for word in specs.split() if word not in stopwords.words('english')])
        Words += [t.strip().lower() for t in specs.split(',') if len(t.split()) < 4]
    except:
        pass
    for keyword in get_keywords(text):
        #Relevant keyword with score greater than 3
        if float(keyword[1]) >= 2.0:
            Words.append(keyword[0].lower())
            #print keyword
    Words = list(set(Words))
    keywords = []
    for word in posTags:
        if word in Words:
            keywords.append(word)
    print keywords
    print CompanyED.update({'_id' : doc['_id']}, {'$set' : {'NLP.RAKE' : Words, 'NLP.posKeywords' : posTags, 'status.posUpdate':datetime.utcnow(), 'NLP.tags' : keywords, 'status.RAKEupdate':datetime.utcnow(), 'status.nlp.status':2}})


def main():
    while(True):
        docs = []
        for doc in CompanyED.find({'status.nlp.status' : 0},{'description':1,'specialties':1}, no_cursor_timeout = True).limit(200):
            docs.append(doc)
        jobs = [gevent.spawn(update,doc) for doc in docs]
        gevent.wait(jobs)


if __name__ == '__main__':
  main()
