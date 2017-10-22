import sys
import traceback
from os import path
from math import floor
from datetime import datetime
import re
from bernese.settings import DATAPOOL_DIR, RINEX_UPLOAD_TEMP_DIR
from bernese.core.log import log

START_DAY_GPS = datetime(year=1980,month=1,day=6)


def isRinex(rnxFile):

    erroMsg =''

    rExt = re.compile('\d{2}O')

    if rExt.match(rnxFile.name[-3:].upper()) or rnxFile.name.upper().endswith('.OBS'):
        return True, erroMsg
    else:
        erroMsg = ('Extensão invalida!!! Favor inserir um arquivo Rinex de Observação' +
                    '(.OBS ou .yyO, onde yy = Ano)')
        return False, erroMsg


def setRnxName(header):

    hDate = header['TIME OF FIRST OBS'].split()
    ano = int(hDate[0])
    mes = int(hDate[1])
    dia = int(hDate[2])

    diaDoAno = date2yearDay(datetime(year=ano,month=mes,day=dia))
    anoRed = (ano - 2000)

    rnxName = header['MARKER NAME'][:4].upper() + '{:03d}'.format(diaDoAno) + '0.' + str(anoRed) + 'O'

    return rnxName



def readRinexObs(rnxFile):

    try:
        header={}
        erroMsg=''
        rnxTempName=''
        # Capture header info
        for i,bl in enumerate(rnxFile):
            l = bl.decode()
            if "END OF HEADER" in l:
                i+=1 # skip to data
                break
            if l[60:80].strip() not in header: #Header label
                header[l[60:80].strip()] = l[:60]  # don't strip for fixed-width parsers
                # string with info
            else:
                header[l[60:80].strip()] += " "+l[:60]
                #concatenate to the existing string

        verRinex = float(header['RINEX VERSION / TYPE'][:9])  # %9.2f
        # list with x,y,z cartesian
        header['APPROX POSITION XYZ'] = [float(i) for i in header['APPROX POSITION XYZ'].split()]
        header['ANTENNA DELTA H/E/N'] = [float(i) for i in header['ANTENNA: DELTA H/E/N'].split()]
        header['REC # / TYPE / VERS'] = [header['REC # / TYPE / VERS'][:19],
                                        header['REC # / TYPE / VERS'][20:39],
                                        header['REC # / TYPE / VERS'][40:]]
        header['ANT # / TYPE'] = [header['ANT # / TYPE'][:19],
                                header['ANT # / TYPE'][20:40]]
        header['MARKER NAME'] = header['MARKER NAME'].strip()
        header['MARKER NUMBER'] = header['MARKER NUMBER'].strip()
        #observation types
        # v2.xx
        # header['# / TYPES OF OBSERV'] = header['# / TYPES OF OBSERV'].split()
        # header['# / TYPES OF OBSERV'][0] = int(header['# / TYPES OF OBSERV'][0])
        # v3.xx
        # header['SYS / # / OBS TYPES'] =
        #turn into int number of observations
        header['INTERVAL'] = float(header['INTERVAL'][:10])

        # TODO ler intervalo de observação
        # primeira observação é facil mas e a ultima???
        if floor(verRinex) == 2:
            rinex_dir = 'RINEX'
        # elif floor(verRinex) == 3:
        #     rinex_dir = 'RINEX3'
        else:
            erroMsg = 'Sem suporte para a versão Rinex ' + str(verRinex)
            return False, erroMsg, header

        # Salva arquivo em pasta de arquivos temporários
        rnxTempName = path.join(RINEX_UPLOAD_TEMP_DIR, rnxFile.name)
        with open(rnxTempName,'wb') as destination:
        	for chunk in rnxFile.chunks(): destination.write(chunk)


        return True, erroMsg, header, rnxTempName
    # fim com sucesso de readRinexObs()

    except Exception as e:

        log('Erro ao ler arquivo Rinex')
        erroMsg = sys.exc_info()
        log(str(erroMsg[0]))
        log(str(erroMsg[1]))
        # traceback.print_tb(erroMsg[2])

        erroMsg = 'Erro ao ler arquivo Rinex.'

        return False, erroMsg, header, rnxTempName
# fim com erro de readRinexObs()


def date2yearDay(epoch):

    dia_mes = [31,28,31,30,31,30,31,31,30,31,30,31]
    yDay = 0

    dia = epoch.day
    mes = epoch.month
    ano = epoch.year

    if (ano%4) == 0: dia_mes[1] = 29
    if mes == 1: dia_mes[0] = 0

    b = 0
    while b < (mes-1):
        yDay += dia_mes[b]
        b += 1

    yDay += dia

    return yDay


def date2gpsWeek(epoch):

    delta = epoch - START_DAY_GPS
    delta_weeks = delta.days/7
    weeks = floor(delta_weeks)
    dayOfWeek = floor((delta_weeks % 1 + 0.001) * 7) # Gambiarra -> timetuple resolve

    return '{:04d}{:01d}'.format(weeks,dayOfWeek)
