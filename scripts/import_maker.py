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

from os.path import expanduser

DIR_HTML = 'html'
DIR_SOUNDS = 'sounds'
DIR_SENTENCES = 'sentences'
DIR_DONE = 'done'

'''
Takes all picture files from a given directory and for each of them then downloads a sound and IPA transcription
from the wiktionary. Prepares a txt file with description and filenames for Anki to import.
'''

userHomeDir = expanduser("~")    #c:\users\majkl
ankiDir = os.path.join(userHomeDir, 'Documents', 'Anki')  #c:\users\majkl\Documents\anki



'''
Projdi adresar
    pro kazdy obrazek (png nebo jpg)
        stahni stranku z wikti (testfile.retrieve("https://en.wiktionary.org/wiki/" + x.lower(), x +".html"))
        stahni zvuk z googlu (testfile.retrieve("https://ssl.gstatic.com/dictionary/static/sounds/de/0/" + x.lower() + ".mp3", x +".mp3")
            pokud neni, najdi zvuk z wiki (vyparsovat z  You can <a href="//upload.wikimedia.org/wikipedia/commons/a/a7/En-us-injury.ogg">download the clip</a>)
                a stahni
        vyparsuj ze stranky IPA (          <span class="IPA" lang="">/xxx/
          </span>
        pridej do vysledku radek obrazek; jmeno ; zvuk ; IPA;<pro bawn-jure>;<pro vase poznamky>
        uloz do archivu
uloz vysledek
uklid

kazdy field se da naplnit posloupnosti
    stahni
    najdi

    obrazek a zvuk se navic musi nakopirovat do anki media folderu


'''
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
    return 'http://www.dict.com/Anglicko-cesky/%s?' %a_word

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


def get_sentence(adr, a_word):
    ''' najde pro dane slovo priklad ve vete '''
    logger.debug('get sentence: %s' %a_word)
    ulozena_veta = os.path.join(adr, DIR_SENTENCES, a_word + '.html')
    logger.debug('ulozena veta:' + ulozena_veta)
    if os.path.exists(ulozena_veta):
        logger.debug('nestahuju, uz byla')
    else:
        logger.debug(ulozena_veta)
        testfile = urllib.URLopener()
        sentence_address = "http://sentence.yourdictionary.com/%s" % a_word.lower()
        logger.debug('sentence_address: %s' % sentence_address)
        try:
            testfile.retrieve(sentence_address, ulozena_veta)
        except IOError:
            logger.warning('nenalezena veta: %s' % sentence_address)
            return ''

    p = re.compile('>[^>]+<b>%s</b>[^>]+<' % a_word)

    with open(ulozena_veta, 'r') as r_sentence:
        for line in r_sentence:
            logger.debug(line)
            vety = p.findall(line)
            if vety:
                logger.debug('nalezeny vety')
                logger.debug(vety)
                #vratim nejkratsi z prvnich 5 - vety jsou serazeny podle jakehosi score a vyse jsou smysluplnejsi
                vety = vety[0:5]
                vety.sort(key=len)
                return vety[0][1:-1] #vrati nejkratsi nalezenou vetu

    r_sentence.close()
    return ""


def check_subdirs(a_dir):
    ''' otestuje, ze existuji pomocne podadresare v danem adresari, pripadne je vytvori '''
    for dir in [DIR_HTML, DIR_SOUNDS, DIR_DONE, DIR_SENTENCES]:
        if not os.path.exists(os.path.join(a_dir, dir)):
            os.mkdir(os.path.join(a_dir, dir))

def to_number(a_word):
    '''
    :param a_word: a number literal  - 4
    :return: a word for number       - four
    '''
    switcher = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "10": "ten",
        "11": "eleven",
        "12": "twelve",
        "13": "thirteen",
        "14": "fourteen",
        "15": "fifteen",
        "16": "sixteen",
        "17": "seventeen",
        "18": "eightteen",
        "19": "nineteen",
        "20": "twenty",
        "30": "thirty",
        "40": "forty",
        "50": "fifty",
        "60": "sixty",
        "70": "seventy",
        "80": "eighty",
        "90": "ninety",
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

        sentence = get_sentence(adr, cword)
        logger.debug('sentence:' + sentence)

        result = word + ';' + img + ';' + sound + ';' + pronunciation + ';' + sentence
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
                    wr.write(zpracuj(adr, s, profile_path) + '\n')
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
