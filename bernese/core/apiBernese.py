import sys
# import traceback
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

    # header = {
    #     'COMMENT': None
    #     # TODO acrescentar campos possíveis
    # }

    headers = []

    def __init__(self, bpeName, rheaders, remail, pathTempFiles):

        self.headers = rheaders
        self.email = remail
        self.bpeName = bpeName
        self.pathRnxTempFiles = pathTempFiles

        hDate = self.headers[0]['TIME OF FIRST OBS'].split()
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

            i = 0
            for rnxFile in self.pathRnxTempFiles:
                with open(rnxFile,'r') as tmpFile, open(path.join(DATAPOOL_DIR,'RINEX',setRnxName(self.headers[i])),'w') as destination:
                    aux = tmpFile.read()
                    destination.write(aux)
                i += 1

            return True

        except Exception as e:

            log('Erro ao copiar Rinex para o Datapool')
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))

            return False

    def getEphem(self):

    # TODO Se não achar efemérides do dia procurar pela da semana e/ou IGS

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

                codURL = ('http://ftp.aiub.unibe.ch/CODE/{:04d}/{}'.format(rnxDate.year,sfile))

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
        pCRDfile = path.join(ref52_datapool_dir,campaignName+'.CRD')
        pABBfile = path.join(ref52_datapool_dir,campaignName+'.ABB')
        # pVELfile = path.join(ref52_datapool_dir,campaignName+'.VEL')

        # Gerando arquivo PLD (placa tectonica da estação)
        with open(pPLDfile,'w') as f:

            f.write(PLD_HEADER_TEMPLATE_FILE.format(**{'DATUM': 'IGS14'}))

            for header in self.headers:
                f.write(PLD_BODY_TEMPLATE_FILE.format(**header))


        # Gerando arquivo STA (tipo do receptor e antena)
        with open(pSTAfile,'w') as f:

            f.write(STA_HEADER_T1_TEMPLATE_FILE)

            for header in self.headers:
                f.write(STA_BODY1_TEMPLATE_FILE.format(**header))

            f.write(STA_HEADER_T2_TEMPLATE_FILE)

            for header in self.headers:
                f.write(STA_BODY2_TEMPLATE_FILE.format(**header))

            f.write(STA_FOOTER_TEMPLATE_FILE)


        # Gerando arquivo CRD (coordenadas)
        with open(pCRDfile,'w') as f:

            f.write(CRD_HEADER_TEMPLATE_FILE.format(**{'DATUM': 'IGS14', 'EPOCH': '2010-01-01 00:00:00'}))

            for header in self.headers:
                f.write(CRD_BODY_TEMPLATE_FILE.format(**header))

        # Gerando arquivo ABB (Abreviação do nome da estação)
        with open(pABBfile,'w') as f:

            f.write(ABB_HEADER_TEMPLATE_FILE)

            for header in self.headers:
                f.write(ABB_BODY_TEMPLATE_FILE.format(**header))

        # Gerando arquivo VEL (velocidades da estação)
        # with open(pVELfile,'w') as f:
        #
        #     f.write(VEL_HEADER_TEMPLATE_FILE.format(**{'DATUM': 'IGS14'}))
        #
        #     for header in self.headers:
        #         f.write(VEL_BODY_TEMPLATE_FILE.format(**header))


    def runBPE(self,prcType):

        # Aguarda a vez na fila de processamento do bernese
        self.filaBPE()

        #Salva arquivo rinex em DATAPOOL
        if not self.saveRinex():
            log('Erro ao salvar o arquivo rinex no servidor')

        # Gera os arquivos do bernese com dados da estação
        self.setSTAfiles()

        # Download das efemérides precisas
        if not self.getEphem():
            msg = 'Erro no processamento do(s) arquivo(s): '
            for rnxFile in self.pathRnxTempFiles:
                msg += path.basename(rnxFile) + ' '
            msg += '. \n'
            msg += 'Falha no download das efemérides precisas.'
            send_result_email(self.email,msg)
            self.clearCampaign()
            return False

        try:

            if prcType == 'PPP':
                arg = 'E:\\Sistema\\runasit.exe "C:\\Perl64\\bin\\perl.exe E:\\Sistema\\pppdemo_pcs.pl '
            elif prcType == 'RLT':
                arg = 'E:\\Sistema\\runasit.exe "C:\\Perl64\\bin\\perl.exe E:\\Sistema\\rltufv_pcs.pl '
            else:
                raise Exception('prcType not defined in ApiBernese')

            arg += str(self.dateFile.year) + ' ' + '{:03d}'.format(date2yearDay(self.dateFile)) + '0"'

            logMsg = 'Rodando BPE: ' + self.bpeName + ' - Arquivo(s): '
            for rnxFile in self.pathRnxTempFiles:
                logMsg += path.basename(rnxFile) + ' '
            log(logMsg)

            # descomentar para teste fora do servidor
            runPCFout = 'Ambiente de teste'
            print(arg)
            raise Exception('Ambiente de teste')
            #

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

            # TODO pegar o resultado na campanha ./OUT/PPPxxxx.PRC
            #      e não salvar os resultados em SAVEDISK

            prcFile = prcType + str(self.dateFile.year)[-2:] + '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = str(SAVEDISK_DIR) + '\\' + prcType + '\\' + str(self.dateFile.year) +'\\OUT\\' + prcFile

            if path.isfile(prcPathFile):

                with open(prcPathFile,'r') as pfile, open(path.join(SAVEDISK_DIR,prcType,str(self.dateFile.year),'OUT',prcFile[:-3]+'txt'),'w') as rfile:
                    rfile.write(pfile.read())

                msg = 'Arquivo(s) '
                for rnxFile in self.pathRnxTempFiles:
                    msg += path.basename(rnxFile) + ' '
                msg += 'processado(s) com sucesso.\n'
                msg += 'Em anexo o resultado do processamento.'

                send_result_email(self.email,msg, str(prcPathFile)[:-3]+'txt')
                self.clearCampaign()

                return True
            else:
                log('Arquivo com resultado do processamento não encontrado')


        log('BPE Erro: ' + repr(runPCFout))
        msg = 'Erro no processamento do(s) arquivo(s) '
        for rnxFile in self.pathRnxTempFiles:
            msg += path.basename(rnxFile) + ' '

        bernErrorFile = 'E:\\Sistema\\GPSDATA\\CAMPAIGN52\\SYSTEM\\RAW\\BERN_MSG_ERROR.txt' # RUNBPE.pm alterado na linha 881

        if path.isfile(bernErrorFile):
            msg += '. \nDetalhes sobre o erro no arquivo em anexo.'
            send_result_email(self.email,msg, bernErrorFile)
        else:
            msg += '. \nPara detalhes sobre o erro favor entrar em contato.'
            send_result_email(self.email,msg)

        # self.clearCampaign()

        return False



    def clearCampaign(self):
        CAMPAIGN_DIR = 'E:\\Sistema\\GPSDATA\\CAMPAIGN52\\SYSTEM\\'
        listdir = [
            path.join(DATAPOOL_DIR,'RINEX'),
            path.join(CAMPAIGN_DIR,'RAW'),
            path.join(CAMPAIGN_DIR,'OBS'),
            path.join(CAMPAIGN_DIR,'SOL'),
            # path.join(CAMPAIGN_DIR,'STA'),
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
