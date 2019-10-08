# Imports
import nltk
import nltk.data
import re
import os
import nltk.tokenize
import nltk.tokenize.punkt
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tokenize import TreebankWordTokenizer
from os import listdir
from os.path import isfile, join
from nltk.tag import brill, brill_trainer
from nltk.tag import UnigramTagger
from nltk.tag import BigramTagger
from nltk.tag import TrigramTagger
from nltk.tag import DefaultTagger
from nltk.corpus import treebank
import nltk.tag.stanford
from nltk.tokenize import WhitespaceTokenizer
from nltk.tag.stanford import StanfordNERTagger

st = StanfordNERTagger('stanford-ner/english.all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

# Placeholder variable which is used to store the edited header and allow it to be used across different functions.
edit = ''

# Function that uses a regex pattern to extract the header portion of the email, by splitting on the portion directly after the last header tag.
def read_tags(file):
    tagSection = re.split("(^\n[A-Za-z\s]*[^:]+\s)", file, flags=re.MULTILINE)[0]

    return tagSection

# Function that is used to preserve the word that is matched against the regex pattern in the body.
def keep_splitter(file):
    splitter = re.split("(^\n[A-Za-z\s]*[^:]+\s)", file, flags=re.MULTILINE)[1]

    return splitter

# Function that uses a regex pattern to extract the body portion of the email, by splitting on the portion directly after the last header tag.
def read_email(file):
    bodySection = re.split("(^\n[A-Za-z\s]*[^:]+\s)", file, flags=re.MULTILINE)[2:]
    bodySection = ''.join(bodySection)

    return bodySection

# Tags start times and end times(if applicable) in the header portion of the email.
def tag_time(header):
    global edit

    # Regex that matches if AM/PM is present in the time in the email.
    #AMorPM = '[\s*]([AaPp][\.]?[Mm])?'
    AMorPM = '([\s*][AaPp][\.]?[Mm])?'

    # Searches the header portion of the email for any String matching the format HH:MM AM/PM - HH:MM AM/PM.
    doubletime_tagged = re.search(r'(([0-9]+)(:)([0-5])([0-9])' + AMorPM + ')\s?([-])\s(([0-9]+)(:)([0-5])([0-9])' + AMorPM + ')', header)
    # Searches the header portion of the email for any String matching the format HH:MM AM/PM.
    singletime_tagged = re.search(r'(([0-9]+)(:)([0-5])([0-9])' + AMorPM + ')', header)

    # If the format HH:MM AM/PM - HH:MM AM/PM is matched then the start and end times are tagged with <stime> and <endtime>.
    if doubletime_tagged:
        doubletime_tagged = re.compile(r'(([0-9]+)(:)([0-5])([0-9])' + AMorPM + ')\s?([-])\s(([0-9]+)(:)([0-5])([0-9])' + AMorPM + ')', re.I)
        edit = doubletime_tagged.sub(r'<s-time>\1</s-time> - <e-time>\8</e-time>', header, count=1) # Using count=1 to capture ONLY first occurence to avoid the 'EMAIL SENT' time.
        return edit

    # If the format HH:MM AM/PM is matched then the start time is tagged with <stime> .
    if singletime_tagged:
        singletime_tagged = re.compile(r'(([0-9]+)(:)([0-5])([0-9])' + AMorPM + ')', re.I)
        edit = singletime_tagged.sub(r'<s-time>\1</s-time>', header, count=1) # Using count=1 to capture ONLY first occurence to avoid the 'EMAIL SENT' time.
        return edit

    return edit

def tag_location(header):
    global edit
    location_tagged = re.search(r'(Place:\s+)([^\n]*)(\n)', header)

    if location_tagged:
        location_tagged = re.compile(r'(Place:\s+)([^\n]*)(\n)', re.I)
        edit = location_tagged.sub(r'\1<location>\2</location>\n', header, count=1)
        return edit

    return edit

# Function that tags the topic in the header of the email.
def tag_topic(header):
    global edit
    topic_tagged = re.search(r'(Topic:\s+)([^\n]*)(\n)', header)
    topic_tagged2 = re.search(r'(Topic:\s+)(\D+)(\n)', header)

    # For multiline topic
    if topic_tagged2:
        topic_tagged = re.compile(r'(Topic:\s+)(\D+)(\n)', re.I)
        edit = topic_tagged.sub(r'\1<topic>\2</topic>\n', header, count=1)
        return edit

    # For single line topic
    if topic_tagged:
        topic_tagged = re.compile(r'(Topic:\s+)([^\n]*)(\n)', re.I)
        edit = topic_tagged.sub(r'\1<topic>\2</topic>\n', header, count=1)
        return edit

    return edit

# Function that tags the speaker in the body portion of the email.
def tag_speaker(sentence):
        for sent in nltk.sent_tokenize(sentence):
            tokens = WhitespaceTokenizer().tokenize(sent)
            tags = st.tag(tokens)
            ret_val = ''
            for tag in tags:
                if tag[1]=='PERSON':
                    ret_val +=  '<speaker>' + tag[0] + '</speaker> '
                else:
                    ret_val += tag[0] + " "
            # For instances with more than 1 matched 'PERSON' value.
            ret_val = ret_val.replace('</speaker> <speaker>', ' ')
            # In order to get rid of final ' ' which messes with format.
            ret_val = ret_val[:-1]

        return (ret_val) 

# Function that tags sentences and paragraphs in the body section of the email.
def tag_sentences_and_paragraphs(body):
    
    untagged_portion = re.split("(^\s+[A-Z][a-z]+\s)", body, flags=re.MULTILINE)[0]
    tagged_portion = re.split("(^\s+[A-Z][a-z]+\s)", body, flags=re.MULTILINE)[1:]

    tagged_portion = ''.join(tagged_portion)

    tagged_portion = tagged_portion.split('\n\n')

    paragraphs_tagged = untagged_portion

    for paragraph in tagged_portion:
        tokenized_text_list = sent_tokenize(paragraph)
        sentences_tagged = ''

        for l in tokenized_text_list:
            l = '<sentence>' + tag_speaker(l) + '</sentence>'
            sentences_tagged += l

        if sentences_tagged != '':
            sentences_tagged = '<paragraph>' + sentences_tagged + '</paragraph>\n\n'
        else: 
            sentences_tagged = ''

        paragraphs_tagged += sentences_tagged

    return paragraphs_tagged


count = 0
dir = os.getcwd()
os.mkdir('TAGGED')
for file in os.listdir(dir):
    filename = os.fsdecode(file)
    if filename.endswith(".txt"):
        filetxt = nltk.data.load(filename, format='text')
        write_file = open('TAGGED/' + filename, 'w') 
        headers = read_tags(filetxt)
        body = keep_splitter(filetxt) + read_email(filetxt)
        headers = tag_time(headers)
        headers = tag_topic(headers)
        headers = tag_location(headers)
        body = tag_sentences_and_paragraphs(body)
        print(headers)
        write_file.write(headers)
        print(body)
        write_file.write(body)
        write_file.close()
        count += 1
    else:
        continue

print(count)