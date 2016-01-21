
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
DIR_HTML = 'html'


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', filename=LOGFILE, datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()


def stahni (a_co, a_kam):
    ''' Pokud soubor jeste neexistuje, tak stahne soubor z internetu a ulozi ho pod danym jmenem'''
    logger.debug('stahni: z %s, do %s' % (a_co, a_kam))
    if (os.path.exists(a_kam)):
        logger.debug('jiz stazeno drive')
    else:
        testfile = urllib.URLopener()
        logger.debug('stahnu soubor')
        try:
            testfile.retrieve(a_co, a_kam)
        except:
            logger.warning('nenalezen soubor na adrese %s' % a_co)
            return False
    return True


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


def check_subdirs(a_dir):
    ''' otestuje, ze existuji pomocne podadresare v danem adresari, pripadne je vytvori '''
    for dir in [DIR_HTML]:
        if not os.path.exists(os.path.join(a_dir, dir)):
            os.mkdir(os.path.join(a_dir, dir))


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

def find_text(a_filename, a_regexp, a_not_found=''):
    ''' najde v souboru text regexpem, vrati obsah a_not_found, kdyz nenalezne'''
    if os.path.exists(a_filename):
        with open(a_filename, 'r') as fd:
            logger.debug('otevren %s' %a_filename)
            p = re.compile(a_regexp, re.IGNORECASE)
            file_content = fd.read()
            m = p.search(file_content)
            if m:
                try:
                    #logger.debug(str(m))
                    if m.group(1):
                        return m.group(1)
                    else:
                        return a_not_found
                except:
                    logger.warning('Nepodarilo se najit %s v souboru %s - %s' % (a_regexp, a_filename, str(sys.exc_info()[0])))
                    return a_not_found
            else:
                logger.warning('Nepodarilo se najit %s v souboru %s' % (a_regexp, a_filename))

        fd.close()
    return a_not_found

def getCanonical(aWord):
    '''
    Gets a canonical form of a word (books -> book, ate -> eat)
    :param aWord: A word to be tested
    :return: a canonical form of a word
    '''

    '''
    download meriam webster page
    find title
    '''
    logger.debug('getCanonical:%s' %aWord)
    MW = 'http://www.merriam-webster.com/dictionary/'
    original_address = MW + aWord
    logger.debug ('original address: %s' %original_address)
    filename = '%s/%s.html' %(DIR_HTML ,aWord)
    logger.debug('filename:%s' % filename)
    if stahni(original_address, filename):
        real_address = find_text(filename, '"canonical" href="(.*?)"')
        logger.debug('real_address:%s' %real_address)
        if real_address!=original_address:
            logger.debug('probehlo presmerovani na zakladni tvar')
            canon = find_text(filename, 'definition of (.*?) by merriam-webster')
            logger.debug('returns:%s' %canon)
            return canon.lower()
        else:
            logger.debug('neprobehlo presmerovani, musim najit link a odvodit z nej nebo se jiz jedna o zakladni tvar')

            definition = find_text(filename, '(simple definition of)')
            if definition:
                logger.debug ('obsahuje "simple definition of", tak to je zakladni tvar')
                canon = aWord
            else:
                canon = find_text(filename, '  <div class="card-primary-content"><ol class="definition-list"><li><p class="definition-inner-item"><span> <em>[^\n]*? of[^\n]*?<a[^\n]*?>([^\n]*?)</a>')
                if (canon):
                    logger.debug('nasel jsem canonicky tvar')
                else:
                    logger.debug('nenasel jsem kanonicky tvar, tak to je zakladni tvar')
                    canon = aWord
            logger.debug('returns:%s' %canon)
            return canon.lower()
    else:
        logger.debug('nepodarilo se stahnout stranku, prohlasim vstup za canonical')
        return aWord




def main(argv=None):
    ''' entry point of the script '''
    args = process_command_line(argv)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    words_input = get_words_from_file(args.known, args.ignoreCase)

    words_test = get_words_from_file(args.input, args.ignoreCase)

    check_subdirs('.')


    word_tmp = words_test.difference(words_input)
    logger.debug('nalezeno %d novych slov' %len(word_tmp))

    if args.ordered:
        words_output = sorted(word_tmp)
    else:
        words_output = word_tmp

    with open (args.output, 'w') as out:
        for word in words_output:
            canon = getCanonical(word)
            if canon.lower() == word.lower():
                out.write(word + '\n')
            else:
                out.write('%s (%s)\n'%(word, canon))
    out.close()
    logger.debug('ulozeno do file')

if __name__ == '__main__':
    status = main()
    sys.exit(status)
