# Please include datafiles in ./data/


import re, nltk
from pprint import pprint
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn

def file_reader(filename, extension):
    with open('Data/' + filename + '.' + extension, 'r') as file:
        text = file.read()
    file.close()
    return text


def sentence_tokenizer(text):
    token_list = nltk.sent_tokenize(text, "english")
    return token_list


def word_tokenizer(text):
    return nltk.word_tokenize(text)


# accepts a word and either 'n' or 'v' depending on whether the word is a noun or a verb
def lemmatizer(word, n_v):
    lmtzr = WordNetLemmatizer()
    return lmtzr.lemmatize(word, n_v)


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

def question_parser(filename):
    result = []
    questions = file_reader(filename, 'questions')
    match_question = re.findall(r'Question: (.+)', questions)
    match_id = re.findall(r'QuestionID: (.+)', questions)
    match_difficulty = re.findall(r'Difficulty: (.+)', questions)
    match_type = re.findall(r'Type: (.+)', questions)
    for i in range(0, len(match_id)):
        each = []
        each.append(match_id[i])
        each.append(match_question[i])
        each.append(match_difficulty[i])
        each.append(match_type[i])
        result.append(each)

    return result

def create_tree_dict(filename='blogs-01', filetype='story'):
    text = file_reader(filename, filetype + '.par')
    treedict = {}

    if (filetype.lower() == "questions"):
        pattern = r'QuestionId: ([\w-]+)\n(.+)\n'
        questions = re.findall(pattern, text)
        for question in questions:
            treedict[question[0]] = nltk.tree.ParentedTree.fromstring(question[1])
    else:
        lines = text.split("\n")
        i = 0
        lines = lines[:-1]
        for line in lines:
            if line != "":
                treedict[i] = nltk.tree.ParentedTree.fromstring(line)
                i += 1

    return treedict


def dependency_parser(filename, type='story'):
    graphs = []
    items = []
    content = file_reader(filename, type + '.dep')
    content = re.sub(r"\n{3,}",r"\n\n",content)
    lines = content.split('\n\n')
    dependency = [line.split('\n') for line in lines]

    if (type == 'questions'):
        dependency = sorted(dependency, key=lambda tup: (len(tup[0])))
        for i in range(0, len(dependency)):
            dependency[i] = dependency[i][1:]
        dependency = dependency[1:len(dependency)]
    else:
        dependency = dependency[0:len(dependency) - 1]

    # for i in dependency:
    #     print(i)
    #     print('\n')

    for i in dependency:
        dep = []
        if i != []:
            dep = nltk.parse.DependencyGraph(i)
            graphs.append(dep)
    for i in graphs:
        item = []
        item = i.nodes.values()
        items.append(item)
    return items


def get_root(story_name, question_no):
    result = []
    question_dep = dependency_parser(story_name, 'questions')
    question = question_dep[question_no]
    # root = question['deps']
    for i in question:
        deps = i['deps']
        if len(deps['root']) > 0:
            root = (deps['root'][0])
    for i in question:
        if i['address'] == root:
            result.append(i['lemma'])
            result.append(i['tag'])
            result.append(sorted([(k, v) for k, v in i['deps'].items() if k != 'root'], key=lambda tup: (tup[1][0])))
    return result


def find_subtree(tree, string):
    left_wild = ""
    right_wild = ""
    if string[0] == "*":
        left_wild = "\w*"
        string = string[1:]
    if string[-1] == "*":
        right_wild = "\w*"
        string = string[:-1]
    pattern = r"\b" + left_wild + string.lower() + right_wild + r"\b"
    NPs = list(tree.subtrees(
        filter=lambda x: re.match(pattern, x.label().lower())))
    return NPs
    # map(lambda x: list(tree.subtrees(filter=lambda x: x.node == string)), NPs)
    # if(string in tree.leaves()):
    #     leaf_index = tree.leaves().index(string)
    #     tree_location = tree.leaf_treeposition(leaf_index)
    #     return tree_loca tion


def find_supertree(tree, string):
    left_wild = ""
    right_wild = ""
    if string[0] == "*":
        left_wild = "\w*"
        string = string[1:]
    if string[-1] == "*":
        right_wild = "\w*"
        string = string[:-1]
    pattern = r"\b" + left_wild + string.lower() + right_wild + r"\b"
    # if tree.parent() is not None:
    #     tree = tree.parent()
    # print(tree)
    while (tree.parent() is not None):
        tree = tree.parent()
        # print(tree.label())
        if re.match(pattern, tree.label().lower()):
            return tree


def find_verb_phrase(tree, verb, lemmatize=True):
    subtrees = find_subtree(tree, "VB*")
    if lemmatize:
        lemmatized_verb = lemmatizer(verb, 'v')
    else:
        lemmatized_verb = verb
    for subtree in subtrees:

        if get_sysnset(subtree[0], lemmatized_verb) is not None:
            if subtree.parent() is None:
                return subtree
            else:
                return subtree.parent()

def find_phrase(tree,POS, verb, lemmatize=True):
    subtrees = find_subtree(tree, POS + "*")
    if lemmatize:
        lemmatized_verb = lemmatizer(verb, 'v')
    else:
        lemmatized_verb = verb
    for subtree in subtrees:
        if lemmatizer(subtree[0], 'v') == lemmatized_verb:
            if subtree.parent() is None:
                return subtree
            else:
                return subtree.parent()


def find_direct_child(tree, string):
    left_wild = ""
    right_wild = ""
    if string[0] == "*":
        left_wild = "\w*"
        string = string[1:]
    if string[-1] == "*":
        right_wild = "\w*"
        string = string[:-1]
    pattern = r"\b" + left_wild + string.lower() + right_wild + r"\b"
    if tree is not None:
        for subtree in tree:
            if re.match(pattern, subtree.label().lower()):
                return subtree


def find_where(story_name, file_type, question_no, sentence_no):
    treedict = create_tree_dict(story_name, file_type)
    root_verb = get_root(story_name, question_no)[0]
    # print(root_verb)
    # treedict[sentence_no].draw()
    # print(root_verb)

    v_phrase = find_verb_phrase(treedict[sentence_no], root_verb)
    # v_phrase.draw()
    if v_phrase is None:
        v_phrase = find_verb_phrase(treedict[sentence_no], root_verb, False)
    if v_phrase is None:
        v_phrase = treedict[sentence_no]
    direct_child = find_direct_child(v_phrase, "PP")
    # direct_child.pprint()
    if direct_child is not None:
        return (" ".join(direct_child.leaves()))
    else:
        indirect_child = find_subtree(v_phrase, "PP")
        # indirect_child[0].draw()
        if len(indirect_child) > 0 and len(indirect_child[0]) == 1:
            return (" ".join(indirect_child[0].leaves()))
        else:
            return None
            # print(" ".join(subtree[0].leaves()))


#
def find_who(story_name, file_type, question_no, sentence_no):
    treedict = create_tree_dict(story_name, file_type)
    root_verb = get_root(story_name, question_no)
    # print("ROOT_WORD",root_verb)
    # print/(treedict[sentence_no])
    # if root_verb[1][:2] != 'VB':
    #     print ("no")
    v_phrase = find_phrase(treedict[sentence_no],root_verb[1][:2], root_verb[0])
    # print(v_phrase)
    while v_phrase is not None:
        v_phrase = find_supertree(v_phrase, "S")
        # print(v_phrase)
        if v_phrase is not None:
            direct_child = find_direct_child(v_phrase, "NP")
            if direct_child is not None:
                return " ".join(direct_child.leaves())


def get_parent_noun_phrase(tree, string):
    subtree = find_subtree(tree, "NN")
    for tree in subtree:
        if re.match(string, tree[0]):
            subtree = tree
            break

    subtree = find_supertree(subtree, "NP")

def extend_dobj(word, type, filename, answer_sentence_no, POS_Tag):
    tree = create_tree_dict(filename, type)
    answer_tree = find_phrase(tree[answer_sentence_no], POS_Tag, word, False)
    if POS_Tag == 'jj':
        answer_tree = find_supertree(answer_tree, 'S')
    if answer_tree is not None:
        result = answer_tree.leaves()
        if answer_tree.right_sibling() is not None and answer_tree.right_sibling().label() == 'PP':
            result += answer_tree.right_sibling().leaves()
        # print('***************************************************')
        return (" ".join(result))

def print_graph(filename, type, answer_sentence_no):
    tree = create_tree_dict(filename, type)
    tree[answer_sentence_no].draw()

# print(find_who('blogs-02' , 'sch' , 0 , 2))
# 'fables-01', 'sch', 6, 9
# 'fables-01', 'story', 9, 0
# 'fables-01', 'sch', 10, 3
# 'fables-02', 'story', 1, 8

# pprint(find_where('fables-01', 'story', 0, 0))
# 'fables-01', 'story', 0, 0
# 'fables-01', 'sch', 5, 5
# 'fables-01', 'sch', 9, 3
# 'fables-02', 'sch', 3, 2
# 'fables-03', 'story', 6, 4
# 'fables-03', 'story', 10, 5
# 'fables-04', 'sch', 3, 2
# 'blogs-01', 'story', 3, 4
