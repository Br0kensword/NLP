import nltk
import operator
import re
import sys
from pprint import pprint
from nltk.corpus import wordnet as wn
import ConstParse as cp
import DepParse as dp
from nltk.stem.wordnet import WordNetLemmatizer
stopwords = nltk.corpus.stopwords.words("english")
stopwords.append("?")
stopwords.append("'s")
stopwords.append("'t")
stopwords.append(".")


def file_reader(filename, extension):
    with open('Data/' + filename + '.' + extension, 'r') as file:
        text = file.read()
    return text
def normalize(review):
    lowerText = review.lower()
    lowerText = nltk.word_tokenize(lowerText)

    global stopwords


    normalizedText = (" ").join(word for word in lowerText if word not in stopwords)

    pattern = r"(?<!\w)(\W+)(?!\w)"
    normalizedText = re.sub(pattern, " ", normalizedText)
    normalizedText = re.sub(r"( ){2,}", " ", normalizedText)
    normalizedText = normalizedText.split(sep=' ')

    return normalizedText

def question_parser(filename):
    result = []
    questions = file_reader(filename, 'questions')
    match_question = re.findall(r'Question: (.+)', questions)
    match_id = re.findall(r'QuestionID: (.+)', questions)
    match_difficulty = re.findall(r'Difficulty: (.+)', questions)
    match_type = re.findall(r'Type: (.+)', questions)
    ans = dp.answer_parser(filename)
    for i in range(0, len(match_id)):
        each = {}
        each['filename'] = (match_id[i][:match_id[i].rfind("-")])
        each['question_id'] = match_id[i]
        each['question_number'] = int(match_id[i][match_id[i].rfind("-") + 1:])
        each['question_text'] = (match_question[i])
        each['tokenized_question'] = nltk.word_tokenize(match_question[i])
        each['question_word'] = each['tokenized_question'][0]
        each['pos'] = nltk.pos_tag_sents([each['tokenized_question']])[0]
        each['difficulty'] = (match_difficulty[i])
        each['type'] = (match_type[i].split("|"))
        each['answerkey'] = ans[i][2]
        for i in range(len(each['type'])):
            each['type'][i] = each['type'][i].strip()
        each['root'] = cp.get_root(each['filename'], each['question_number'] - 1)
        if each['root'][1][0] == 'V' or each['root'][1][0] == 'N':
            each['root_lemma'] = cp.lemmatizer(each['root'][0], each['root'][1][0].lower())
        result.append(each)

    return result


def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    # sentences = [nltk.pos_tag(sent) for sent in sentences]

    return sentences


def find_because(sentence):
    result = re.findall(r'(because .*)\.', sentence)
    if result != []:
        return result[0]
    else:
        return None
def find_root_re(answer_sentence, root):
    tokenized_sentence = nltk.word_tokenize(answer_sentence)
    tokenized_sentence = tokenized_sentence[:-1]
    for i in range(len(tokenized_sentence)):
        if root == tokenized_sentence[i]:
            return " ".join(tokenized_sentence[i + 1:])

    for i in range(len(tokenized_sentence)):
        if get_sysnset(root, tokenized_sentence[i]) is not None:
            return " ".join(tokenized_sentence[i+1:])

def sanitize_text(text):
    global stopwords
    return set([t.lower() for t in text if t.lower() not in stopwords])


def lemma_sanitize(text):
    global stopwords
    return set([(t[0].lower(), t[1]) for t in text if t[0].lower() not in stopwords])


def find_best_sent(question, text, type, text2 = None, type2 = None):
    global stopwords
    answers = []
    count = 0
    text = get_sentences(text)
    for sent in text:
        words_in_sent = sanitize_text(sent)
        string_sent = " ".join(t.lower() for t in words_in_sent)
        overlapCount = 0
        for token in question:
            for word in words_in_sent:
                word_check = get_sysnset(word, token)
                if word_check is not None:
                    overlapCount += 1
            result = re.search(token, string_sent)
            if result:
                overlapCount += 1
        overlap = len(question & words_in_sent)
        overlap += overlapCount

        answers.append((overlap, " ".join(sent), count, type))
        count += 1

    if(text2 is not None):
        text2 = get_sentences(text2)
        count = 0
        for sent in text2:
            words_in_sent = sanitize_text(sent)
            string_sent = " ".join(t.lower() for t in words_in_sent)
            overlapCount = 0
            for token in question:
                for word in words_in_sent:
                    word_check = get_sysnset(word, token)
                    if word_check is not None:
                        overlapCount += 1
                result = re.search(token, string_sent)
                if result:
                    overlapCount += 1

            overlap = len(question & words_in_sent)
            overlap += overlapCount

            answers.append((overlap, " ".join(sent), count, type2))
            count += 1

    answers = sorted(answers, key=operator.itemgetter(0), reverse=True)
    best_answer = (answers[0])
    # print(best_answer)
    if best_answer[0] == 0:
        return ("", "", "")
    else:
        return (best_answer[2], best_answer[1], best_answer[3])


def get_where(question_dict):
    return cp.find_where(question['filename'], question['type'], question['question_number'] - 1,
                                    question['answer_sentence_number'])


def get_who(question_dict):
    return cp.find_who(question['filename'], question['type'], question['question_number'] - 1,
                                  question['answer_sentence_number'])
def get_why(question_dict):
    return find_because(question_dict['answer_sentence'])

def get_what(question_dict):

    possible_result = dp.answer_what(question['filename'], question['type'], question['question_number'] - 1, question['answer_sentence_number'])

    if possible_result is None and question['tokenized_question'][-2] == question['root'][0] and question['root'][2][0][0] == "dobj":
        possible_result = find_root_re(question['answer_sentence'], question['root_lemma'])

    return possible_result

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




def lemmatize_words(text):
    lmtzr = nltk.stem.wordnet.WordNetLemmatizer()
    stemmed_words = []
    for token in text:
        tag = token[1]
        word = token[0]
        if word is not None:
            if tag.startswith("V"):
                stemmed_words.append(lmtzr.lemmatize(word, 'v'))
            else:
                stemmed_words.append(word)
    return stemmed_words

def answer_print(filename, question_num):
        answer = file_reader(filename, 'answers')

        print(re.findall(r"QuestionID: " + filename + "-" + str(question_num) + r"\n.*\n(Answer:.*\n)", answer)[0])
def info_print(question):
    print('QuestionID:', question['question_id'])
    print('QuestionType:', question['type'])
    print('Question:', question['question_text'])
    print('Proposed:', result)
    print('Answer:', question['answerkey'])
    print('Root:', question['root'])
    print()

if __name__ == '__main__':

    # Loop over the files in fables and blogs in order.
    output_file = open("train_my_answers.txt", "w", encoding="utf-8")
    if (len(sys.argv) > 1):
        print(sys.argv[1])
        filenames = file_reader(sys.argv[1])
        filenames = filenames.split("\n")
        print(filenames)
    else:
        filenames = [
            'blogs-01', 'blogs-02', 'blogs-03', 'blogs-04', 'blogs-05', 'blogs-06', 'fables-01', 'fables-02', 'fables-03', 'fables-04', 'fables-05','fables-06']
    count = 0
    total = 0
    whatdict = {}
    for fname in filenames:
        questions = question_parser(fname)
        for question in questions:

            if True:#question['question_word'] == "What":# and question['root'][2][0][0] == "nmod" :#and question['difficulty'] != "Hard":#question['question_word'] == "What" or question['question_word'] == "Where" or question['question_word'] == "Who":

                total = total + 1
                answer = None
                stem = lemma_sanitize(question['pos'])
                normQ = set(lemmatize_words(stem))
                if len(question['type']) > 1:
                    answer = find_best_sent(normQ, file_reader(fname, question['type'][0]), question['type'][0], file_reader(fname, question['type'][1]),question['type'][1])
                else:
                    answer = find_best_sent(normQ, file_reader(fname, question['type'][0]), question['type'][0])
                question['answer_sentence_number'] = answer[0]
                question['answer_sentence'] = answer[1]
                question['type'] = answer[2]
                result = question['answer_sentence']
                possible_result = None

                if question['question_word'] == "Why" and question['answer_sentence'] != "":
                    possible_result = get_why(question)

                elif question['question_word'] == "Where" and question['answer_sentence'] != "":
                    possible_result = get_where(question)

                elif question['question_word'] == "Who" and question['answer_sentence'] != "":
                    possible_result = get_who(question)

                elif question['question_word'] == "What" and question['answer_sentence'] != "":
                    possible_result = get_what(question)


                if possible_result is not None:
                    count = count + 1
                    result = possible_result
                    question['answer_sentence'] = result
                info_print(question)
                # else:
                #     info_print(question)
                output_file.write("QuestionID: {}\n".format(question['filename'] + "-" + str(question['question_number'])))
                output_file.write("Answer: {}\n\n".format(result))
    print(count, "/", total)
    pprint(whatdict)
        # output_file.close()
