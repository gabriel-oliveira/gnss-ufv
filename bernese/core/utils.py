import sys
from os import path
from datetime import datetime
from bernese.settings import RINEX_UPLOAD_TEMP_DIR

#-------------------------------------------------------------------------------

def setBernID():

    instante = datetime.now()

    bpeName = 'bern' + '{:03d}'.format(instante.timetuple().tm_yday)
    bpeName += '_' +  '{:02d}'.format(instante.hour)
    bpeName += '{:02d}'.format(instante.minute)
    bpeName += '{:02d}'.format(instante.second)
    bpeName += '{}'.format(instante.microsecond)

    return bpeName


    #-------------------------------------------------------------------------------

def saveBlq(blqFile,bernID):
    # Salva o arquivo BLQ no servidor (TEMP_DIR)

    if blqFile.name[-3:] not in ['BLQ', 'blq']:
        return False, 'Extensão invalida! Favor inserir um arquivo .BLQ'

    # TODO verificar se é arquivo de texto

    try:

        blqTempName = path.join(RINEX_UPLOAD_TEMP_DIR, (bernID + '.BLQ'))
        with open(blqTempName,'wb') as destination:
            for chunk in blqFile.chunks(): destination.write(chunk)

        return True, '', blqTempName

    except Exception as e:
        msg = 'Erro ao salvar arquivo BLQ.'
        log(msg)
        erroMsg = sys.exc_info()
        log(str(erroMsg[0]))
        log(str(erroMsg[1]))

        return False, msg
