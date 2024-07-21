# 일기 감정별로 분류해주기
# 자연어 처리하기
# 처리 한 거 기반으로 음악 추천해서 렌더링해주기.!!!
from project.models import db, Diary, User
import regex as re
from konlpy.tag import Kkma




def preprocess_text(text):
    text = re.sub(r"[^\s\w]","",text) #정규표현식으로, 단어,공백(\s,\w)를 제외한(^) 것들을 ""로 대체(없애는 거지)
    text = re.sub(r"\d+","",text)  #숫자 제거, 대괄호가 쓰이지 않는 이유는 \d+가 이미 하나의 문자 클래스이기 때문.
    text = text.strip() #공백 제거
    return text

def tokenize(text):

    kkma = Kkma()
    tokens = kkma.morphs(text)
    return tokens

def remove_stopwords(tokens):
    stopwords=['은','는','이','가']
    tokens=[token for token in tokens if token not in stopwords]
    return tokens


import os
from konlpy import utils


javadir = '%s%sjava' % (utils.installpath, os.sep)
args = [javadir, os.sep]
folder_suffix = ['{0}{1}open-korean-text-2.1.0.jar']
classpath = [f.format(*args) for f in folder_suffix]

text = input()
tokens = tokenize(text)
print(tokens)


