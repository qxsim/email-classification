# Imports
import nltk
import os
import shutil
import nltk.data
import re
from os import listdir
from os.path import isfile, join
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import wordnet as wn
from nltk.corpus import reader
from nltk.corpus.reader.wordnet import WordNetError

categories = ['artificial intelligence', 'ai', 'hci', 'robotics', 'graphics', 'software engineering', 'semantics', 'logic', 'theoretical', 'computer science', 'programming']

dir_dict = {}

dir_dict['computer_science_dir'] = 'computer science'
dir_dict['artificial_intelligence_dir'] = 'computer science/artificial intelligence'
dir_dict['robotics_dir'] = 'computer science/artificial intelligence/robotics'
dir_dict['software_engineering_dir'] = 'computer science/software engineering'
dir_dict['programming_dir'] = 'computer science/software engineering/programming'
dir_dict['hci_dir'] = 'computer science/hci'
dir_dict['graphics_dir'] = 'computer science/graphics'
dir_dict['theoretical_dir'] = 'computer science/theoretical'
dir_dict['logic_dir'] = 'computer science/theoretical/logic'
dir_dict['semantics_dir'] = 'computer science/theoretical/semantics'

computer_science_dir = 'computer science'
artificial_intelligence_dir = 'computer science/artificial intelligence'
robotics_dir = 'computer science/artificial intelligence/robotics'
software_engineering_dir = 'computer science/software engineering'
programming_dir = 'computer science/software engineering/programming'
hci_dir = 'computer science/hci'
graphics_dir = 'computer science/graphics'
theoretical_dir = 'computer science/theoretical'
logic_dir = 'computer science/theoretical/logic'
semantics_dir = 'computer science/theoretical/semantics'

matches = []
    
def find_match(file, tokens):
    global categories
    global matches
    
    matches = []

    for cat in categories:
        if cat in tokens:
            if cat == 'ai':
                cat = 'artificial intelligence'
            matches.append(cat)
        else:
            continue

    return matches

def make_directories():
    dir_list = [robotics_dir, programming_dir, hci_dir, graphics_dir, logic_dir, semantics_dir]
    
    for directory in dir_list:
        if not os.path.exists(directory):
            os.makedirs(directory)

    return


def match_all_words(file, tokens):
    global categories
    global matches

    try:
        for cat in categories:
            if cat == 'ai':
                cat = 'artificial intelligence'
               
            for token in tokens:
                if token.isalpha():
                    try:
                        if ((parse_from_wn((wn.synset(parse_to_wn(token)).lowest_common_hypernyms(wn.synset(parse_to_wn(cat))))))) in cat:
                            matches.append(cat)
                        else:
                            continue
                    except WordNetError:
                        continue
                else:
                    continue
    except WordNetError: 
        return matches
        
    return matches


def calc_semantic_difference(matches):
    match_set = set(matches)

    if not match_set:
        final_tag = 'computer science'

        return final_tag

    sem_dict = {}

    for match in match_set:
        try:
            sem_diff = wn.synset(parse_to_wn(match)).path_similarity(wn.synset('computer_science.n.01'))
            sem_dict[match] = sem_diff
        except:
            final_tag = match
            return final_tag
    
    final_tag = min(sem_dict, key=sem_dict.get)

    return final_tag


def parse_to_wn(text):
    text = text.replace(' ', '_')
    text += '.n.01'

    return text


def parse_from_wn(text):
    text = text[0]
    text = text.name().split(".")[0].replace('_',' ')

    return text

def ontology_run(file):
    tokens = WordPunctTokenizer().tokenize(file)
    make_directories()
    find_match(file, tokens)
    match_all_words(file, tokens)
    calc_semantic_difference(matches)


count = 0
dir = os.getcwd()
tagged_dir = dir + '/TAGGED'
for file in os.listdir(tagged_dir):
    filename = os.fsdecode(file)
    if filename.endswith(".txt"):
        filetxt = nltk.data.load(filename, format='text')
        filetxt = filetxt.lower()
        ontology_run(filetxt)
        print(filename + ': ' + calc_semantic_difference(matches))
        dir_to_copy = dir_dict[calc_semantic_difference(matches).replace(' ', '_')+'_dir']
        shutil.copy('TAGGED/' + filename, dir_to_copy)
        count += 1
    else:
        continue

print(count)