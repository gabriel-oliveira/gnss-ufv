import sys
import traceback
import urllib.request
import glob
import threading
from datetime import datetime
from os import path, remove
from subprocess import Popen, run, PIPE, DEVNULL
from bernese.core.berneseFilesTemplate import *
from bernese.core.rinex import *
from bernese.settings import DATAPOOL_DIR, SAVEDISK_DIR
from bernese.core.mail import send_result_email
from bernese.core.log import log

class ApiBernese:

    header = {
        'COMMENT': None
        # TODO acrescentar campos possíveis
    }


    def __init__(self, bpeName, rheader, remail, pathTempFile):

        self.header = rheader
        self.email = remail
        self.bpeName = bpeName
        self.pathRnxTempFile = pathTempFile

        hDate = self.header['TIME OF FIRST OBS'].split()
        ano = int(hDate[0])
        mes = int(hDate[1])
        dia = int(hDate[2])
        self.dateFile = datetime(year=ano,month=mes,day=dia)


    def haveEphem(rnxDate):
        # TODO verificar efemerides
        return True

    def newCampaign():
        # TODO Criador de campanha
        pass


    def saveRinex(self):
    # Salva o arquivo no servidor (DATAPOOL\RINEX)

        try:

            with open(self.pathRnxTempFile,'r') as tmpFile, open(path.join(DATAPOOL_DIR,'RINEX',setRnxName(self.header)),'w') as destination:
                aux = tmpFile.read()
                destination.write(aux)

            return True

        except Exception as e:

            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))

            return False


    def getEphem(self):

        rnxDate = self.dateFile

        try:
            weekDay = date2gpsWeek(rnxDate)

            if rnxDate.year > 1999:
                anoRed = rnxDate.year - 2000
            else:
                anoRed = rnxDate.year - 1900

            sClkFile = 'COD{}.CLK.Z'.format(weekDay)
            sEphFile = 'COD{}.EPH.Z'.format(weekDay)
            sIonFile = 'COD{}.ION.Z'.format(weekDay)
            sErpFile = 'COD{}.ERP.Z'.format(weekDay)
            sP1C1File = 'P1C1{:02d}{:02d}.DCB.Z'.format(anoRed,rnxDate.month)
            sP1P2File = 'P1P2{:02d}{:02d}.DCB.Z'.format(anoRed,rnxDate.month)

            sfileList = [sClkFile, sEphFile, sIonFile, sErpFile, sP1C1File, sP1P2File]

            cod_datapool_dir = path.join(DATAPOOL_DIR,'COD')
            bsw52_datapool_dir = path.join(DATAPOOL_DIR,'BSW52')

            for sfile in sfileList:

                codURL = ('http://www.aiub.unibe.ch/download/CODE/{:04d}/{}'.format(rnxDate.year,sfile))

                if sfile in [sIonFile, sP1C1File, sP1P2File]: target_dir = bsw52_datapool_dir
                else: target_dir = cod_datapool_dir

                pathFile = path.join(target_dir,sfile)

                with urllib.request.urlopen(codURL) as response, open(pathFile, 'wb') as outFile:
                    data = response.read()
                    if not data: raise('Erro no download de: ' + sFile)
                    outFile.write(data)

                # status = run('7z x {} -o{} -y'.format(pathFile,target_dir),stdout=PIPE,stderr=PIPE)
                # if status.returncode:
                #     print('Erro ao descompactar o arquivo: ' + target_dir)
                #     print(status.stderr)

            return True

        except Exception as e:

            log('Erro no download das efemérides precisas')
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))
            # for tb in traceback.format_exc(erroMsg[2]): log(tb)

            return False

    def setSTAfiles(self):

        campaignName = 'SYSTEM'

        ref52_datapool_dir = path.join(DATAPOOL_DIR,'REF52')

        pPLDfile = path.join(ref52_datapool_dir,campaignName+'.PLD')
        pSTAfile = path.join(ref52_datapool_dir,campaignName+'.STA')
        # pCRDfile = path.join(ref52_datapool_dir,campaignName+'.CRD')

        with open(pPLDfile,'w') as f:
            f.write(PLD_TEMPLATE_FILE.format(**self.header))

        with open(pSTAfile,'w') as f:
            f.write(STA_TEMPLATE_FILE.format(**self.header))

        # with open(pCRDfile,'w') as f:
        #     f.write(CRD_TEMPLATE_FILE.format(**self.header))


    def runBPE(self):

        # Aguarda a vez na fila de processamento do bernese
        self.filaBPE()

        #Salva arquivo rinex em DATAPOOL
        if not self.saveRinex():
            log('Erro ao salvar o arquivo rinex no servidor')

        # Gera os arquivos do bernese com dados da estação
        self.setSTAfiles()

        # Download das efemérides precisas
        if not self.getEphem():
            msg = 'Erro no processamento do arquivo ' + str(self.pathRnxTempFile).rsplit(sep='\\',maxsplit=1)[1] + '. \n'
            msg += 'Falha no download das efemérides precisas.'
            send_result_email(self.email,msg)
            self.clearCampaign()
            return False

        arg = 'E:\\Sistema\\runasit.exe "C:\\Perl64\\bin\\perl.exe E:\\Sistema\\pppbas_pcs.pl '
        arg += str(self.dateFile.year) + ' ' + '{:03d}'.format(date2yearDay(self.dateFile)) + '0"'

        log('Rodando BPE: ' + self.bpeName + ' - Arquivo: ' + str(self.pathRnxTempFile).rsplit(sep='\\',maxsplit=1)[1])

        try:
            raise Exception('Ambiente de teste')
            with Popen(arg,stdout=PIPE,stderr=PIPE,stdin=DEVNULL,cwd='E:\\Sistema') as pRun:
                runPCFout = pRun.communicate()
                erroBPE = runPCFout[1]
            # pRun = run(arg,stderr=PIPE,cwd='E:\\Sistema')
            # erroBPE = pRun.stderr
        except Exception as e:
            log('Erro ao rodar BPE: ' + self.bpeName)
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))
            # for tb in traceback.format_exc(erroMsg[2]): log(tb)
            erroBPE = True

        log('BPE: ' + self.bpeName + ' finalizado')

        if not erroBPE:

            prcFile = 'PPP' + str(self.dateFile.year)[-2:] + '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = str(SAVEDISK_DIR) + '\\PPP\\' + str(self.dateFile.year) +'\\OUT\\' + prcFile

            if path.isfile(prcPathFile):

                msg = 'Arquivo ' + str(self.pathRnxTempFile).rsplit(sep='\\',maxsplit=1)[1] + ' processado com sucesso.\n'
                msg += 'Em anexo o resultado do processamento.'

                send_result_email(self.email,msg, prcPathFile)
                self.clearCampaign()

                return True
            else:
                log('Arquivo com resultado do processamento não encontrado')


        # log('BPE Erro: ' + repr(runPCFout))
        msg = 'Erro no processamento do arquivo ' + str(self.pathRnxTempFile).rsplit(sep='\\',maxsplit=1)[1]
        msg += '. \nPara detalhes sobre o erro ocorrido entre em contato.'

        send_result_email(self.email,msg)
        self.clearCampaign()

        return False



    def clearCampaign(self):
        CAMPAIGN_DIR = 'E:\\Sistema\\GPSDATA\\CAMPAIGN52\\SYSTEM\\'
        listdir = [
            path.join(DATAPOOL_DIR,'RINEX'),
            path.join(CAMPAIGN_DIR,'RAW'),
            path.join(CAMPAIGN_DIR,'OBS'),
            path.join(SAVEDISK_DIR,'PPP',str(self.dateFile.year),'OUT'),
        ]
        log('Cleaning Campaign')
        for dir in listdir:
            files = glob.glob(path.join(dir, '*'))
            for f in files:
                remove(f)



    def filaBPE(self):

        threads = threading.enumerate()

        threadsNames = []
        position = 0
        for th in threads:
            if (th.name[:4] == 'bern') and (th.name != self.bpeName):
                threadsNames_aux = {'id':position, 'name':th.name}
                threadsNames.append(threadsNames_aux)
            position += 1

        threadsNames.sort(key=lambda k:k['name'])

        # um de cada vez, como a tia gorda ensinou
        for tname in threadsNames:
            threads[tname['id']].join()
