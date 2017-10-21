import sys
import traceback
from datetime import datetime
import urllib.request
from os import path, remove
import glob
from subprocess import Popen, run, PIPE, DEVNULL
from threading import Thread
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


    def __init__(self, rheader, remail):

        self.header = rheader
        self.email = remail

        hDate = self.header['TIME OF FIRST OBS'].split()
        ano = int(hDate[0])
        mes = int(hDate[1])
        dia = int(hDate[2])
        self.dateFile = datetime(year=ano,month=mes,day=dia)


    def haveEphem(rnxDate):
        # TODOafter verificar efemerides
        return True

    def newCampaign():
        # TODOafter Criador de campanha
        pass

    # TODO colocar self onde precisa
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

        self.setSTAfiles()

        if not self.getEphem():
            msg = 'Erro no processamento da estação ' + self.header['MARKER NAME'].strip() + '. \n'
            msg += 'Falha no download das efemérides precisas.'
            send_result_email(self.email,msg)
            self.clearCampaign()
            return False

        arg = 'E:\\Sistema\\runasit.exe "C:\\Perl64\\bin\\perl.exe E:\\Sistema\\pppbas_pcs.pl '
        arg += str(self.dateFile.year) + ' ' + '{:03d}'.format(date2yearDay(self.dateFile)) + '0"'

        log('Rodando BPE...')

        try:
            with Popen(arg,stdout=PIPE,stderr=PIPE,stdin=DEVNULL,cwd='E:\\Sistema') as pRun:
                runPCFout = pRun.communicate()
                erroBPE = runPCFout[1]
            # pRun = run(arg,stderr=PIPE,cwd='E:\\Sistema')
            # erroBPE = pRun.stderr
        except Exception as e:
            log('Erro ao rodar BPE')
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))
            # for tb in traceback.format_exc(erroMsg[2]): log(tb)
            erroBPE = True

        log('BPE Finalizado')

        if not erroBPE:

            prcFile = 'PPP' + str(self.dateFile.year)[-2:] + '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = str(SAVEDISK_DIR) + '\\PPP\\' + str(self.dateFile.year) +'\\OUT\\' + prcFile

            if path.isfile(prcPathFile):

                msg = 'Arquivo processado com sucesso.\n'
                msg += 'Em anexo o resultado do processamento.'

                send_result_email(self.email,msg, prcPathFile)
                self.clearCampaign()

                return True


        log('BPE Erro: ' + repr(runPCFout))
        msg = 'Erro no processamento da estação ' + self.header['MARKER NAME'].strip()
        msg += '\nPara detalhes sobre o erro ocorrido entre em contato.'

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
        log(str(listdir))
        for dir in listdir:
            files = glob.glob(path.join(dir, '*'))
            for f in files:
                remove(f)