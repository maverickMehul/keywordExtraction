#/usr/bin/env python
#author@Mehul
# -*- coding: utf-8 -*-


import base64, random, web, re, json, requests, time
from datetime import datetime, timedelta
from dateutil.parser import parse
from bson import json_util
from collections import deque

class keywordApp(web.application):
    def run(self, port=5050, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer("english")

from nltk.corpus import stopwords
import os
import string
from random import randint
from operator import add
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


def posTag(line):
    parseDoc = parser(line)
    token_text = [token.orth_ for token in parseDoc]
    token_pos = [token.pos_ for token in parseDoc]
    token_lemma = [token.lemma_ for token in parseDoc]
    idxPROPN = getIndexList(token_pos,u'PROPN') 
    idxNOUN = getIndexList(token_pos,u'NOUN')
    idxADJ = getIndexList(token_pos,u'ADJ')
    idxCONJ = getIndexList(token_pos,u'CONJ')
    adNoun = map(add, map(add, idxNOUN, idxPROPN), idxADJ)
    posKeywords = []
    noise = ["my", "his", "her", "its", "your", "our",\
             "their", "this", "that", "these", "those",\
             "which", "what", "when", "whose"]
    keyword = u''
    for i,token in enumerate(token_text):
        if adNoun[i] == 1:
            if not token.lower() in noise:
                keyword += token + ' '
        else:
            if len(keyword) > 0:
                posKeywords.append(keyword.strip().lower())
            keyword = u''
    posKeywords = list(set(posKeywords))
    '''for ent in parseDoc.ents:
        if ent.label_ == 'GPE' or ent.label_ == 'LOC' or \
           ent.label_ == 'ORG' or ent.label_ == 'PRODUCT':
            for keyword in posKeywords:    
                if ent.text.lower() in keyword:
                    flag = 1
            if not flag:
                posKeywords.append(ent.text.lower())'''
    return posKeywords


import rake
import operator

# Path to Stoplist, Min Character length, Max number of words in phrase, Number of occurences
rake_object = rake.Rake("SmartStoplist.txt", 2, 5, 1)

def repl_char(text):
   try:
       text = text.replace(u"\u2019","'")
       text = text.replace("'s","")
       text = text.replace("s'","s")
       text = text.replace("-"," ")
       chars_to_remove = [')' ,'(', "'", '"', '/']
       remove_punctuation_map = dict((ord(char), None) for char in chars_to_remove)
       text = text.translate(remove_punctuation_map)
       text = " ".join(text.split())
   except:
        return
   return text


def get_keywords(text):
    try:
        keywords = rake_object.run(text)
    except:
        return []
    return keywords


def keywords(text):
    text = repl_char(text)
    posTags = posTag(text)
    print posTags
    Words = []
    for keyword in get_keywords(text):
        #Relevant keyword with score greater than 1
        if float(keyword[1]) >= 1:
            Words.append(keyword[0].lower())
            #print keyword
    Words = list(set(Words))
    keywords = []
    for word in posTags:
        if word in Words:
            keywords.append(word)
    return keywords



urls = (
    '/keywords', 'Keywords',
    '/login', 'Login'
)

allowed = (
    ('maverickMehul', '__ARDF5ojo')
)

class Keywords:
    def POST(self):
        if web.ctx.env.get('HTTP_AUTHORIZATION') is not None:
            data = web.data()
            data = json.loads(data)
            return json.dumps(keywords(data['text']), default=json_util.default)
        else:
            raise web.seeother('/login')


class Login:
    def GET(self):
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ', '', auth)
            username, password = base64.decodestring(auth).split(':')
            if (username, password) in allowed:
                raise web.seeother('/')
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate', 'Basic realm="Auth example"')
            web.ctx.status = '401 Unauthorized'
            return

    def POST(self):
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ', '', auth)
            username, password = base64.decodestring(auth).split(':')
            if (username, password) in allowed:
                raise web.seeother('/')
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate', 'Basic realm="Auth example"')
            web.ctx.status = '401 Unauthorized'
            return

if __name__ == "__main__":
    app = keywordApp(urls, globals())
    app.run(port=5050)
