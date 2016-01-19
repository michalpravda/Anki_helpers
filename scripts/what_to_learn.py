''' Opens a file representing known (or queued to learn) words and a file containing arbitrary words. Produces a file with words to be learned.
    Intended usage is to gen known words by exporting them from Anki, get questioned words from a text (scanned book page, a page from Internet etc.)
    and get as a result list of words which are unknown at the moment a should be queued for learning.

    Output file is by default not sorted.
    Each word found is presented on one line.

    2.0
    If a questioned word is not in its basic state (infinitive for verbs, singular for nouns etc.) then word with its
    basic state in parenthesis is present)
    If can't determine if a word is in a basic state (e.g. books = many exemplars of a book or a financial record), the script chooses that word is not
    in it's basic state ( books => "books (book)")
    If even a word in basic state is not "known" than both forms (found and basic) are presented in the output (books => "book" + "books (book)"
    E.g.
    book
    look
    looks (look)
    looking (look)


'''

import re
import os
import sys
import logging
import shutil
from argparse import ArgumentParser
import urllib
import zipfile
from datetime import datetime

from os.path import expanduser

LOGFILE = 'what_to_learn.log'
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', filename=LOGFILE, datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()



def process_command_line(argv):
    ''' zpracuje cmd parametry do promennych'''

    parser = ArgumentParser()

    parser.add_argument("-k", "--known", help="file (usually exported from Anki) representing known words")
    parser.add_argument("-i", "--input", help="file to be tested - the source of possible new words")
    parser.add_argument("-o", "--output", help="file with results - the words to be learned")
    parser.add_argument("-r", "--ordered", help="Output file is alphabetically sorted", action='store_true')
    parser.add_argument("-g", "--ignoreCase", help="Case insensitive", action='store_true')
    parser.add_argument("--debug", help='show debug messages', action='store_true')
    parser.add_argument("-p", "--profil", help="Anki profile to be used (pictures and sound will be copied to it's media folder")

    args = parser.parse_args()

    logger.debug('vstupni argumenty')
    logger.debug(args)

    #    if not (args.changelistfrom or args.date):
    #     if len(sys.argv)==1:
    #         parser.print_help()
    #         sys.exit(1)    #logger.debug('parsed args')
    return args


def get_words(a_line, a_alllower):
    '''
    :param a_line: A line of text
    :return: list of all words in it.
    '''
    result = re.sub('[,).:(!?]', ' ', a_line).split()
    if a_alllower:
        result = [x.lower() for x in result]
    return result

def get_basic_state(a_word):
    '''
    Gets a basic state of a word (e.g. "books" => "books (book)". It does so by
    :param a_word:
    :return:
    '''

def get_words_from_file(a_file, a_alllower):
    '''
    Reads a file, all it's word puts into a set
    :param a_file:
    :return: a set with all words in a file
    '''
    words = set()
    with open(a_file) as f:
        for line in f:
            words |= set(get_words(line, a_alllower))
    f.close()
    logger.debug('nalezeno %d slov' % len(words))
    return words


def main(argv=None):
    ''' entry point of the script '''
    args = process_command_line(argv)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    words_input = get_words_from_file(args.known, args.ignoreCase)

    words_test = get_words_from_file(args.input, args.ignoreCase)



    word_tmp = words_test.difference(words_input)
    logger.debug('nalezeno %d novych slov' %len(word_tmp))

    if args.ordered:
        words_output = sorted(word_tmp)
    else:
        words_output = word_tmp

    with open (args.output, 'w') as out:
        for word in words_output:
            out.write(word + '\n')
    out.close()
    logger.debug('ulozeno do file')

if __name__ == '__main__':
    status = main()
    sys.exit(status)
