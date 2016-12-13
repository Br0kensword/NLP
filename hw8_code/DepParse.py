import nltk
import re
import os
import sys
from pprint import pprint
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import warnings
warnings.filterwarnings("ignore")
from nltk.corpus import wordnet as wn
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
lancaster_stemmer = LancasterStemmer()
from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer('english')
import ConstParse as cp

# def get_sysnset(word, word2):
#
#     word_synsets = wn.synsets(word)
#     word2_synsets = wn.synsets(word2)
#
#     for synset in word_synsets:
#         if(synset.name().split('.')[0] == word2):
#             return synset.name().split('.')[0]
#
#     for synset in word2_synsets:
#         if (synset.name().split('.')[0] == word):
#             return synset.name().split('.')[0]
#     return None

# get
def get_sysnset(word, word2):

    word_synsets = wn.synsets(word)
    word2_synsets = wn.synsets(word2)

    for synset in word_synsets:
        if(synset.name().split('.')[0] == word2):
            return synset.name().split('.')[0]

    for synset in word2_synsets:
        if (synset.name().split('.')[0] == word):
            return synset.name().split('.')[0]
    return None

def dependency_parser(filename, type='story'):
    graphs = []
    items = []
    content = file_reader(filename, type + '.dep')
    content = re.sub(r"\n{3,}",r"\n\n",content)
    lines = content.split('\n\n')
    
    dependency = [line.split('\n') for line in lines]
    dependency = [dep for dep in dependency if dep != ['']]
    if (type == 'questions'):
        #pprint(dependency)
        #sortsorted(dependency, key=lambda tup: (int(tup[0].split("-")[2]) if tup != [''] else 10000))
        
        sortD = sorted(dependency, key=lambda tup: (abs(int(tup[0][-2:])) if tup != [''] else 10000))
        
        dependency = sortD
       # pprint(sortD)
        for i in range(0, len(dependency)):
            dependency[i] = dependency[i][1:]
#        dependency = dependency[1:len(dependency)]
#    else:
#        dependency = dependency[0:len(dependency)-1]
    
    for i in dependency:
        dep = []
        dep = nltk.parse.DependencyGraph(i)
        graphs.append(dep)
    for i in graphs:
        item = []
        item = i.nodes.values()
        items.append(item)
    return items

def file_reader( filename, extension ):
    with open('Data/'+filename+'.'+extension,'r') as file:
        text = file.read()
    file.close()
    return text

def answer_parser( filename ):
    result = []
    answers = file_reader( filename, 'answers')
    match_question = re.findall(r'Question: (.+)', answers)
    match_answers = re.findall(r'Answer: (.+)',answers)
    match_id = re.findall(r'QuestionID: (.+)', answers)
    match_difficulty = re.findall(r'Difficulty: (.+)', answers)
    match_type = re.findall(r'Type: (.+)', answers)
    match_ans = re.findall(r'Answer: (.+)', answers)
    for i in range(0,len(match_id)):
        each = []
        each.append( match_question[i] )
        each.append( match_id[i] )
        each.append( match_answers[i] )
        each.append( match_difficulty[i] )
        each.append( match_type[i] )
        result.append(each)
    return result

def answer_finder( file_name ):
    question_no = 0
    test = [{1: 0, 3:0, 6:0}]
    ans_sent_no = 0
    ans = answer_parser( file_name )
    for each in ans:
        if re.findall(r'(What).+',each[0]):
            type = each[4]
            if(len(type) > 5):
                type = 'Story' # sometimes type is story | sch
            answer_what(file_name , type , question_no, ans_sent_no)
        question_no+=1

def test_answer_finder( file_name ):
    question_no = 0
    # test = {1: 0, 3:6, 6:6, 8:5, 9:5, 10:7, 11:7, 12:7, 16:5, 22:6} #blog 1
    # test = {5: 0, 10:7, 11:4, 16:0, 19:0} #blog 2
    # test = {0: 0, 1: 7, 2: 9, 6: 8, 11: 10, 13: 15, 15: 0,16: 0} #blog 3
    # test = {1:0, 3:3, 5:9, 7:0, 11:6} #fables 1
    # test = {5:6, 8:2, 10:3, 11:5, 14:8, 16:4, 20:0, 21:0} #Fables - 02
    # test = {2:0, 4:0, 6:5, 8:6, 10:4, 11:3, 16:2, 18:3, 19:3 , 23:0}# Fables - 03
    test = {1:0, 4:0, 6:7, 8:1, 10:7, 11:0, 12:1, 15:0} #Fables - 04
    # test = {1:0, 3:6, 6:6, 8:6, 9:5, 10:7, 11:7, 12:7, 16:5} #blogs - 01
    # test = {0:0, 1:7, 2:9, 6:8, 11:10, 13:12} #blogs - 03
    # test = {2:11, 3:3, 6:0, 13:1} #blogs - 04

    ans = answer_parser( file_name )

    for each in ans:
        if re.findall(r'(What).+',each[0]):
            type = each[4]
            if(len(type) > 5):
                type = 'story' # sometimes type is story | sch
            answer_what(file_name , type , question_no, test[question_no], each)
        question_no += 1


def get_root_any(question_dep):
    result = [0]
    question = list(question_dep)  
    
    if (question[0]['deps']['root']):
        return question[0]['deps']['root'][0]
    return( result )


def get_lemma( question_dep, number ):
    for i in question_dep:
        if i['address'] == number:
            return i['lemma']

def get_deps( question_dep, number ):
    for i in question_dep:
        if i['address'] == number:
            return dict(i['deps'])


def stemmer(word):
    porter_stemmer = PorterStemmer()
    stem = porter_stemmer.stem( word )
    return(stem)


def LancasterStemmer(word):
    stem = lancaster_stemmer.stem( word )
    return stem

def snowball_stemmers( word ):
    return snowball_stemmer.stem( word )

def get_tag( question_dep, word ):
    for i in question_dep:
        if i['lemma'] == word:
            return i['tag'].lower()


def get_address( answer_dep , word , word_pos ):
    for i in answer_dep:
        if i['lemma'] == word:
            if i['address'] is not None:
                return i['address']
    for i in answer_dep:
        if i['lemma'] is not None:
            lemma = i['lemma']
            pos = i['tag'].lower()
            # print( lemmatizer(lemma, pos[0]) ,'==', lemmatizer(word, word_pos[0]) )
            if lemmatizer(lemma, pos[0]) == lemmatizer(word, word_pos[0]):
                return(i['address'])
    # for i in answer_dep:
    #     if i['lemma'] is not None:
    #         lemma = i['lemma']
    #         new_word = get_sysnset(lemma, word)
    #         if new_word is not None:
    #             print('-------------------------------------')
    #             return i['address']
    return None

def lemmatizer(word, n_v):
    if(n_v == 'n' or n_v == 'v'):
        lmtzr = WordNetLemmatizer()
        return lmtzr.lemmatize(word, n_v)

def answer_what_nmod(question_dep, answer_dep, type, file_name, answer_sent_no):
    print(question_dep)
    root = get_root_any( question_dep )
    root_word = get_lemma( question_dep, root )
    root_tag = get_tag( question_dep, root_word )
    ans_address = get_address( answer_dep , root_word , root_tag )
    if ans_address is not None:
        ans_deps = get_deps( answer_dep, ans_address )
        if 'nmod' in ans_deps:
            ans_word = get_lemma(answer_dep, ans_deps['nmod'][0])
            ans_tag = get_tag(answer_dep, ans_word)
            ans_word = cp.extend_dobj(ans_word, type, file_name, answer_sent_no, ans_tag)
            return( ans_word )
            # extend_dobj( ans_word, type, file_name, answer_sent_no , ans_tag )
        if 'nsubj' in ans_deps:
            ans_word = get_lemma(answer_dep, ans_deps['nsubj'][0])
            ans_tag = get_tag(answer_dep, ans_word)
            ans_word = cp.extend_dobj(ans_word, type, file_name, answer_sent_no, ans_tag)
            return (ans_word)
            # extend_dobj( ans_word, type, file_name, answer_sent_no , ans_tag )
    else:
        for i in answer_dep:
            if i['rel'] == 'nmod':
                ans_word = i['lemma']
                ans_tag = i['tag']
                break
        ans_word = cp.extend_dobj(ans_word, type, file_name, answer_sent_no, ans_tag)
        return (ans_word)
    return None


def answer_what(file_name , type , question_no, answer_sent_no):
    result = []
    question_dep = dependency_parser(file_name, 'questions')
    answer_dep = dependency_parser(file_name, type)
    question_dep = question_dep[question_no]
    answer_dep = answer_dep[answer_sent_no]
    q_deps =  get_deps(question_dep, get_root_any(question_dep))
    
    if 'dobj' in q_deps and q_deps['dobj'][0] == 1:
        return answer_what_dobj( question_dep , answer_dep , type, file_name, answer_sent_no)
    if 'nmod' in q_deps and q_deps['nmod'][0] == 1:
        return answer_what_nmod(question_dep, answer_dep, type, file_name, answer_sent_no)
    # elif 'nsubjpass' in q_deps and q_deps['nsubjpass'][0] == 1:
    #     print('njubjpass')


    # print("Question =============================")
    # for i in question_dep:`
    #     print(i)
    #     print('\n')
    # print("Answer =============================")
    # for i in answer_dep:
    #     print(i)
    #     print('\n')

def answer_what_dobj(question_dep , answer_dep , type, file_name, answer_sent_no):
    # print(answer_sent_no, answer_dep, question_dep)
    ans_list = []
    rootany = get_root_any(question_dep)
    # print(rootany)
    word = get_lemma(question_dep, rootany)
    # print(word)
    word_pos = get_tag( question_dep, word )
    address = get_address( answer_dep , word , word_pos )
    if address == None:
        # print("hiya")
        return None
    ans_word = get_lemma( answer_dep, address)
    ans_deps = get_deps( answer_dep , address )
    if 'dobj' in ans_deps:
        ans_word =  get_lemma( answer_dep,ans_deps['dobj'][0])
        ans_tag =  get_tag(answer_dep, ans_word)
        ans_word = cp.extend_dobj( ans_word, type, file_name, answer_sent_no , ans_tag )
        return ans_word

    elif 'ccomp' in ans_deps:
        ans_word = get_lemma( answer_dep, ans_deps['ccomp'][0] )
        ans_tag = get_tag(answer_dep, ans_word)
        ans_word = cp.extend_dobj(ans_word, type, file_name, answer_sent_no, ans_tag)
        return ans_word
    elif 'xcomp' in ans_deps:
        ans_word = get_lemma(answer_dep, ans_deps['xcomp'][0])
        ans_tag = get_tag(answer_dep, ans_word)
        ans_word = cp.extend_dobj(ans_word, type, file_name, answer_sent_no, ans_tag)
        return ans_word



# if __name__ == '__main__':
#     files =  os.listdir('./Data')
#     files = sorted( set([re.sub(r'(\..+)','',f) for f in files]) )
#     answers = []
#     for file_name in files:
#         test_answer_finder( file_name )