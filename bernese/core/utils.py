import sys
from os import path
from django.utils import timezone
from bernese.settings import RINEX_UPLOAD_TEMP_DIR


#-------------------------------------------------------------------------------

# TODO: passar esta função para ApiBernese e acabar com esse arquivo

def is_blq(blqFile):

    if blqFile.name[-3:] not in ['BLQ', 'blq']:
        return False, 'Extensão invalida! Favor inserir um arquivo .BLQ'

    try:
        b = blqFile.read(29).decode()
        if b == '$$ Ocean loading displacement':
            return True, ''
        else:
            return False, 'Erro ao conferir a primeira linha do arquivo: ' + blqFile.name
    except:
        return False, 'Erro ao ler o arquivo: ' + blqFile.name

#-------------------------------------------------------------------------------
## DEPRECTED
def saveBlq(blqFile,bernID):
    # Salva o arquivo BLQ no servidor (TEMP_DIR)

    if blqFile.name[-3:] not in ['BLQ', 'blq']:
        return False, 'Extensão invalida! Favor inserir um arquivo .BLQ', ''


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

        return False, msg, ''
