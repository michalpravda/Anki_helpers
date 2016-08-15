# coding=windows-1250
import logging
'''
Vezme seznam slov se stitky
Doplni obrazek a zvuk a anglicky vyznam a slovni druh a poradi
'''

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(lineno)d: %(message)s', datefmt='%d.%m.%Y %H:%M:%S%p)')
logger = logging.getLogger()


def getSlovo(radek):
    '''
    vytahne z radku to spravne slovo, ktere me zajima>
    la mujer => mujer
    bueno, -a => bueno
    café m => café
    '''
    logger.debug('getSlovo:_%s_'  %radek)
    result = None
    if not ' ' in radek:
        result = radek
    else:
        slova = radek.split(' ')
        #zrus cleny
        if slova[0] in ['la', 'el']:
            del (slova[0])
        if len(slova) == 1:
            result = slova[0]

        #zrus sklonovani pridavnych jmen, rody
        else:
            if slova[1] in ['-a', 'm', 'ž'.decode('windows-1250'), 'm.']:
                del (slova[1])
            if len(slova) == 1:
                result = slova[0].strip(',')
    if result == None:
        result = 'error'
    logger.debug( ' %s -> %s' %(radek, result))
    return result

deb = False
if deb:
    zdroj1 = 'd:\\majkl\\fluent forever\\spanelstina\\Essential Spanish Vocabulary Top 5000_10.txt'
    zdroj2 = 'd:\\majkl\\fluent forever\\spanelstina\\CZ - Španělština pro samouky4_10.txt'
else:
    zdroj1 = 'd:\\majkl\\fluent forever\\spanelstina\\Essential Spanish Vocabulary Top 5000_pozn.txt'
    zdroj2 = 'd:\\majkl\\fluent forever\\spanelstina\\CZ - Španělština pro samouky4.txt'


pole = {}
with open (zdroj1, 'r') as top5000:
    for f in top5000:
   #    absoluto (adj)	"<img src=""paste-4562608183050241.jpg"" />"	absolute	[sound:yandex-ed786d1b-be3786b7-8c793710-a9852788-0ac15d82.mp3] 	574 	1000   adj
        funi = f.decode('utf-8')
        polozky = funi.split('\t')

        logger.debug(polozky[0])
        index = polozky[0].split(' ')[0].strip(',')
        logger.debug(index)

        pole[index] = polozky
    top5000.close()



with open (zdroj2, 'r') as infile:
# sbohem	adiós		L01 stitek
    with open ('d:\\majkl\\fluent forever\\spanelstina\\CZ - Španělština pro samouky_obr.txt', 'w') as outfile:
        for f in infile:
            polozky_radku = f.decode('utf-8').split('\t')
            slovo = getSlovo(polozky_radku[1])
            if slovo in pole:
                logger.debug('nasel jsem %s' % polozky_radku[1])
                r = pole[slovo]
                out = '%s;%s;%s;%s;%s;%s;%s;%s;\n' %(polozky_radku[0], polozky_radku[1], r[1], r[2], r[3], r[0].split(' ')[1], r[4], polozky_radku[3].strip())
                outfile.write(out.encode('utf-8'))
            else:
                logger.debug('nenasel jsem %s' % polozky_radku[1])
                out = '%s;%s;%s;%s;%s;%s;%s;%s;\n' %(polozky_radku[0], polozky_radku[1], '', '', '', '', '', polozky_radku[3].strip())
                outfile.write(out.encode('utf-8'))


    infile.close()