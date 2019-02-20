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
    rExt2 = re.compile('\d{2}D')

    if not ( rExt.match(rnxFile.name[-3:].upper())
            or rExt2.match(rnxFile.name[-3:].upper())
            or rnxFile.name.upper().endswith('.OBS')
            or rnxFile.name.upper().endswith('.RNX')
            or rnxFile.name.upper().endswith('.CRX')  ):
        erroMsg = ('Extensão invalida! Favor inserir um arquivo Rinex de Observação' +
                    ' (.yyO, yyD, .OBS, .RNX, .CRX)')
        return False, erroMsg
    else:
        try:
            f = rnxFile.read(80).decode()
            if f[60:80] in ['RINEX VERSION / TYPE', 'CRINEX VERS   / TYPE']:
                return True, erroMsg
            else:
                return False, 'Erro ao conferir a primeira linha do arquivo: ' + rnxFile.name
        except:
            return False, 'Erro ao ler o arquivo: ' + rnxFile.name



#-------------------------------------------------------------------------------

def setRnxName(header):

    hDate = header['TIME OF FIRST OBS'].split()
    ano = int(hDate[0])
    mes = int(hDate[1])
    dia = int(hDate[2])

    diaDoAno = date2yearDay(datetime(year=ano,month=mes,day=dia))

    if ano > 1999:
        anoRed = ano - 2000
    else:
        anoRed = ano - 1900

    # verifica se o arquivo é do tipo hatanaka
    if 'CRINEX VERS   / TYPE' in header:
        tipo = 'D'
    else:
        tipo = 'O'

    rnxName = header['MARKER NAME'][:4].upper() + '{:03d}'.format(diaDoAno) + '0.' + '{:02d}'.format(anoRed) + tipo

    return rnxName


#-------------------------------------------------------------------------------

# TODO: enviar msg pro log no lugar de retornar na função

def readRinexObs(rnxFile):
    '''
        rnxFile > deve ser do tipo file binary, ou seja, o arquivo de ser aberto
                  no modo binário antes da função ser chamada. PS: arquivo do form
                  ja vem aberto.

        return > boolean, string, dictionary

                 bolean - sucesso na Leitura
                 string - mensagem de erroMsg
                 dictionary - cabeçalho do arquivo rinex
    '''

    try:
        header={}
        erroMsg=''
        # rnxTempName=''

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
        header['version'] = floor(verRinex)

        # list with x,y,z cartesian
        if 'APPROX POSITION XYZ' in header and len(header['APPROX POSITION XYZ'].split()) == 3:
            header['APPROX POSITION XYZ'] = [
                float(i) for i in header['APPROX POSITION XYZ'].split()
                ]
        else:
            raise Exception('Erro em APPROX POSITION XYZ')

        if 'ANTENNA: DELTA H/E/N' in header and len(header['ANTENNA: DELTA H/E/N'].split()) == 3:
            header['ANTENNA DELTA H/E/N'] = [
                float(i) for i in header['ANTENNA: DELTA H/E/N'].split()
                ]
        else:
            raise Exception('Erro em ANTENNA: DELTA H/E/N')

        header['REC # / TYPE / VERS'] = [header['REC # / TYPE / VERS'][:19],
                                        header['REC # / TYPE / VERS'][20:39],
                                        header['REC # / TYPE / VERS'][40:]]
        header['ANT # / TYPE'] = [header['ANT # / TYPE'][:19],
                                header['ANT # / TYPE'][20:40]]
        header['MARKER NAME'] = header['MARKER NAME'][:4].strip().upper()
        header['MARKER NUMBER'] = header['MARKER NUMBER'][:9].strip().upper()
        header['RAW_NAME'] = rnxFile.name

        if floor(verRinex) not in [2,3]:
            erroMsg = 'Sem suporte para a versão Rinex ' + str(verRinex)
            return False, erroMsg, header
            # fim com erro de readRinexObs()

        #observation types
        # v2.xx
        # header['# / TYPES OF OBSERV'] = header['# / TYPES OF OBSERV'].split()
        # header['# / TYPES OF OBSERV'][0] = int(header['# / TYPES OF OBSERV'][0])
        # v3.xx
        # header['SYS / # / OBS TYPES'] =
        #turn into int number of observations

        # TODO deu erro no processamento do William
        # header['INTERVAL'] = float(header['INTERVAL'][:10])

        # TODO ler intervalo de observação
        # primeira observação é facil mas e a ultima???


        return True, erroMsg, header
        # fim com sucesso de readRinexObs()

    except Exception as e:

        erroMsg = 'Erro ao ler o cabeçalho do arquivo Rinex: ' + rnxFile.name + '. '
        erroMsg += str(e)

        log(erroMsg)
        sysErroMsg = sys.exc_info()
        log(str(sysErroMsg[0]))
        log(str(sysErroMsg[1]))
        # traceback.print_tb(erroMsg[2])


        return False, erroMsg, header
        # fim com erro de readRinexObs()


#-------------------------------------------------------------------------------

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


#-------------------------------------------------------------------------------

def date2gpsWeek(epoch):

    delta = epoch - START_DAY_GPS
    delta_weeks = delta.days/7
    weeks = floor(delta_weeks)
    dayOfWeek = floor((delta_weeks % 1 + 0.001) * 7) # TODO Gambiarra -> timetuple resolve

    return '{:04d}{:01d}'.format(weeks,dayOfWeek)
