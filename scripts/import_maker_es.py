# coding=ISO-8859-2

import re
import os
import sys
import logging
import shutil
from argparse import ArgumentParser
import urllib
import zipfile
from datetime import datetime
import htmlentitydefs
from os.path import expanduser

DIR_HTML = 'html'
DIR_SOUNDS = 'sounds'
DIR_DONE = 'done'

'''
Takes all picture files from a given directory and for each of them then downloads a sound and several info from dict.com. Prepares a txt file with description and filenames for Anki to import.
'''

userHomeDir = expanduser("~")    #c:\users\majkl
ankiDir = os.path.join(userHomeDir, 'Documents', 'Anki')  #c:\users\majkl\Documents\anki

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

LOGFILE = 'import.log'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', filename=LOGFILE, datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()


def find_text(a_filename, a_regexp, a_not_found):
    ''' najde v souboru text regexpem, vrati obsah a_not_found, kdyz nenalezne'''
    logger.debug('find_text(%s, %s, %s)' %(a_filename, a_regexp, a_not_found))
    if os.path.exists(a_filename):
        logger.debug('soubor existuje')
        with open(a_filename, 'r') as fd:
            logger.debug('otevren %s' %a_filename)
            p = re.compile(a_regexp)
            for line in fd:
                m = p.search(line)
                if m:
                    try:
                        #logger.debug(str(m))
                        if m.group(1):
                            logger.debug('nalezeno %s' %(m.group(1)))
                            return m.group(1)
                        else:
                            return a_not_found
                    except:
                        logger.warning('Nepodarilo se najit %s v souboru %s - %s' % (a_regexp, a_filename, str(sys.exc_info()[0])))
                        return a_not_found
        fd.close()
    else:
        logger.debug('soubor %s neexistuje' %a_filename)
    return a_not_found


def get_extension(a_filename):
    ''' ze jmena souboru odvodi priponu'''

    logger.debug('get_extension ' + a_filename)
    if not a_filename:
        return None
    ext = a_filename.split('.')[-1].lower()
    logger.debug('returns:' + ext)
    return ext


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

def get_html_file(adr, a_word):
    '''
    :param adr: adresar
    :param a_word: slovo
    :return: filename pro html stranku s popisem slova
    '''
    logger.debug('get_html_file(%s, %s)' %(adr, a_word))
    result = os.path.join (adr, DIR_HTML, a_word + '.html')
    logger.debug('result %s' % result)
    return result

def get_html_address(a_word):
    '''
    Zatim trivialni ale mozna nebude pro non ascii

    :param a_word: slovo
    :return: adresa, na ktere hledat informace o slovu
    '''
    return 'http://www.dict.com/Spanelsko-cesky/%s?' %a_word

def get_real_address(a_address):
    '''
    :param a_address: relativni adresa nalezena ve strance
    :return: full address of a sound
    '''
    return 'http://www.dict.com/data/%s' %a_address


def get_sound(adr, a_word, a_html_file):
    ''' najde pro dane slovo nahravku
        nejdrive jiz existujici nahravku v adresari, jinak zkusi stahnout z dict.com
        vrati tag pro pouziti v anki [sound:word.mp3] a jmeno souboru se zvukem'''
    logger.debug('get_sound:%s %s' %(adr ,a_word))
    ''' na dict com zvuky v dict.com/data/ adresa ve strance - napr. http://www.dict.com/data/audio/en/006/en-006141.mp3 '''
    sound_rel_address = find_text(a_html_file, "<span class='lex_ful_wsnd'>(.*?)</span>", '')
    sound_file =  os.path.join (adr, DIR_SOUNDS, a_word + '.mp3')
    logger.debug ('sound_file: %s' % sound_file)
    if stahni(get_real_address(sound_rel_address), sound_file):
        l_result = '[sound:%s.mp3]' % a_word
        logger.debug(l_result)
        return l_result, sound_file

    return '', ''


def check_subdirs(a_dir):
    ''' otestuje, ze existuji pomocne podadresare v danem adresari, pripadne je vytvori '''
    for dir in [DIR_HTML, DIR_SOUNDS, DIR_DONE]:
        if not os.path.exists(os.path.join(a_dir, dir)):
            os.mkdir(os.path.join(a_dir, dir))

def to_number(a_word):
    '''
    :param a_word: a number literal  - 4
    :return: a word for number       - four
    '''
    switcher = {
        "0": "cero",
        "1": "uno",
        "2": "dos",
        "3": "tres",
        "4": "cuatro",
        "5": "cinco",
        "6": "seis",
        "7": "siete",
        "8": "ocho",
        "9": "nueve",
        "10": "diez",
        "11": "once",
        "12": "doce",
        "13": "trece",
        "14": "catorce",
        "15": "quince",
        "16": "dieciséis",
        "17": "diecisiete",
        "18": "dieciocho",
        "19": "diecinueve",
        "20": "veinte",
        "21": "veintiuno",
        "22": "veintidós",
        "30": "treinta",
        "40": "cuarenta",
        "50": "cincuenta",
        "60": "sesenta",
        "70": "setenta",
        "80": "ochenta",
        "90": "noventa",
        "100": "hundred",
    }
    return switcher.get(a_word, a_word)


def zpracuj(adr, a_picture, a_profile_path):
    ''' stahne k danemu obrazku co nejvice doplnujicich informaci (zvuk, vyslovnost),
    zkopiruje media do anki folderu
    vrati radek k importu do anki.
        Predpoklada, ze obrazek ma jmeno slovicko.jpg/png/gif
    '''
    # word; picture; sound; pronunciation; example sentence
    # hello; <img src="hello.jpg">; [sound:hello.mp3]; /h??l??/; Hello world!
    logger.debug('function zpracuj: ' + a_picture)

    word = "".join(a_picture.split('.')[0:-1])
    word = to_number(word)

    logger.debug('word ' + str(word))
    if word.startswith('to '):
        logger.debug('infinitive - cut "to "')
        cword=word[3:]
        word = '(to) ' + word[3:]
    else:
        logger.debug('not infinitive - word remains unaltered')
        cword = word
    img = '<img src="' + a_picture + '">'
    logger.debug('img' + img)

    html_file =   get_html_file(adr, cword)
    if stahni(get_html_address(cword), html_file):
        logger.debug('nasel jsem stranku pro dane slovo')
        sound, sound_filename = get_sound(adr, cword, html_file)
        logger.debug('sound:' + sound)
        pronunciation = find_text(html_file, "<span class='lex_ful_pron'>(.*?)</span>", '//')
        logger.debug('pronunciation:' + pronunciation)
        pronunciation = unescape(pronunciation)
        logger.debug('pronunciation unescaped:' + pronunciation)

        result = word + ';' + img + ';' + sound + ';' + pronunciation + ';'
        logger.debug('result' + result)

        shutil.copy(os.path.join(adr, a_picture), a_profile_path)
        logger.debug('zkopirovan obrazek do profilu')

        logger.debug('zkopiruju ' + sound_filename)
        if os.path.exists(sound_filename):
            shutil.copy(sound_filename, a_profile_path)
        else:
            logger.debug('nepodarilo se stahnout sound file neni jej odkud kopirovat')
        done_path = os.path.join(adr, DIR_DONE, a_picture)
        logger.debug('done:' + done_path)
        shutil.move(os.path.join(adr, a_picture), done_path)

        return result
    logger.debug('nepodarilo se najit ve slovniku')
    return None

def zip_log(args, profile_path):
    '''zazipuje log a nahraje jej do adresare anki, odtamtud se synchronizaci dostane ke mne pě při každém pokusu'''
    if args.zip:
        logger.debug('zipuju logfile - %s' %LOGFILE)

        zipfl = 'log_%s.zip' %datetime.now().strftime('%Y%m%d_%H%M%S')
        with zipfile.ZipFile(zipfl, 'w', zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(LOGFILE)
        myzip.close()

        shutil.copy(zipfl, profile_path)
        return None

def process_command_line(argv):
    ''' zpracuje cmd parametry do promennych'''

    parser = ArgumentParser()

    parser.add_argument("-d", "--directory", help="directory with pictures to make an import script upon")
    parser.add_argument("--debug", help='show debug messages', action='store_true')
    parser.add_argument("-p", "--profil", help="Anki profile to be used (pictures and sound will be copied to it's media folder")
    parser.add_argument("--zip", help='zip logfile and copy it to anki media folder', action='store_true')

    args = parser.parse_args()

    logger.debug('vstupni argumenty')
    logger.debug(args)
    return args


def main(argv=None):
    ''' entry point of the script '''
    args = process_command_line(argv)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    adr = args.directory
    check_subdirs(adr)

    profile_path = os.path.join(ankiDir, args.profil, 'collection.media')
    logger.debug('profile_path:' + profile_path)
    with open(adr + '/import.txt', 'w') as wr:
        for s in os.listdir(adr):
            logger.debug('filename:' + s)
            if get_extension(s) in ['jpg', 'gif', 'png']:
                try:
                    wr.write((zpracuj(adr, s, profile_path) + '\n').encode('utf-8'))
                    logger.debug('zapsano do import filu')
                    logger.info('zpracovano: %s' %s)
                except:
                    logger.warn(s + ' ' + str(sys.exc_info()))
                    raise
    wr.close()
    zip_log(args, profile_path)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
