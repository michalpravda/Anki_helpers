''' Opens a file representing known (or queued to learn) words and a file containing arbitrary words. Produces a file with words to be learned.
    Intended usage is to gen known words by exporting them from Anki, get questioned words from a text (scanned book page, a page from Internet etc.)
    and get as a result list of words which are unknown at the moment a should be queued for learning.

    Output file is by default intentionally in random order.
    Each word found is presented on one line.
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
    parser.add_argument("--debug", help='show debug messages', action='store_true')
    parser.add_argument("-p", "--profil", help="Anki profile to be used (pictures and sound will be copied to it's media folder")
    parser.add_argument("--zip", help='zip logfile and copy it to anki media folder', action='store_true')

    args = parser.parse_args()

    logger.debug('vstupni argumenty')
    logger.debug(args)

    #    if not (args.changelistfrom or args.date):
    #     if len(sys.argv)==1:
    #         parser.print_help()
    #         sys.exit(1)    #logger.debug('parsed args')
    return args


def get_words(a_line):
    '''
    :param a_line: A line of text
    :return: list of all words in it.
    '''
    result = re.sub('[,.!?]', ' ', a_line).split()
    return result

def main(argv=None):
    ''' entry point of the script '''
    args = process_command_line(argv)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    words_input = set()

    with open(args.input) as f:
        for line in f:
            words_input |= set(get_words(line))
    f.close()

    logger.debug('nalezeno %d slov' % len(words_input))

    with open (args.output, 'w') as out:
        for word in words_input:
            out.write(word + '\n')
    out.close()
    logger.debug('ulozeno do file')

if __name__ == '__main__':
    status = main()
    sys.exit(status)
