import sys
# import traceback
import urllib.request
import requests
from glob import glob
import threading
from datetime import datetime
from os import path, remove, walk
from subprocess import Popen, run, PIPE, DEVNULL
from bernese.core.berneseFilesTemplate import *
from bernese.core.rinex import *
from bernese.settings import (
DATAPOOL_DIR, SAVEDISK_DIR, CAMPAIGN_DIR, RESULTS_DIR,
DEBUG, TEST_SERVER, RINEX_UPLOAD_TEMP_DIR,
)
# from bernese.core.mail import send_result_email
from bernese.core.log import log
from zipfile import ZipFile, ZIP_DEFLATED

#-------------------------------------------------------------------------------
# TODO: transformar logs em raises???
# TODO: definir função a ser execultada pós processamento (send mail, proc.finished_at)
#       fora da Api passa-la por parametro com seus parametros efkwargs
#-------------------------------------------------------------------------------

class ApiBernese:

#-------------------------------------------------------------------------------

    #def __init__(self, bpeName, rheaders, remail, pathTempFiles,pathBlqTempFiles):
    def __init__(self, **kwargs):

        self.setBpeID()
        if 'proc_id' in kwargs:
            self.proc_id = kwargs['proc_id']
        else:
            self.proc_id = self.bpeName
        # self.email = kwargs['email']
        self.linux_server = kwargs['linux_server']
        if self.linux_server and kwargs['blq_file']:
            self.getServerFiles(kwargs['blq_file'])
            self.pathBlqTempFiles = [path.join(RINEX_UPLOAD_TEMP_DIR,'linux_server',kwargs['blq_file'])]
        else:
            self.pathBlqTempFiles = [kwargs['blq_file']]

        self.prcType = kwargs['proc_method']

        if 'datum' in kwargs: self.datum = kwargs['datum']

        # TODO: rever a eficiencia disto
        # if 'endFunction' in kwargs:

        end_f = kwargs['endFunction']

        def newend_f(**kwargs):
            try:
                end_f(**kwargs)
            except Exception as e:
                log('Erro ao rodar endFunction')
                log(str(e))
                erroMsg = sys.exc_info()
                log(str(erroMsg[0]))
                log(str(erroMsg[1]))

        self.endFunction = newend_f

        if kwargs['proc_method'] == 'ppp':

            if self.linux_server:
                self.getServerFiles(kwargs['rinex_file'])
                self.pathRnxTempFiles = [path.join(RINEX_UPLOAD_TEMP_DIR,'linux_server',kwargs['rinex_file'])]
            else:
                self.pathRnxTempFiles = [kwargs['rinex_file']]

            header = self.getHeader(self.pathRnxTempFiles[0])
            header['ID'] = 1
            header['ID2'] = header['MARKER NAME'][:2]
            header['FLAG'] = ''
            header['PLATE'] = kwargs['tectonic_plate']

            self.headers = [header]

        if kwargs['proc_method'] == 'relativo':

            if self.linux_server:
                self.getServerFiles(kwargs['rinex_base_file'])
                self.getServerFiles(kwargs['rinex_rover_file'])
                self.pathRnxTempFiles = [
                path.join(RINEX_UPLOAD_TEMP_DIR,'linux_server',kwargs['rinex_base_file']),
                path.join(RINEX_UPLOAD_TEMP_DIR,'linux_server',kwargs['rinex_rover_file']),
                ]
            else:
                self.pathRnxTempFiles = [
                                    kwargs['rinex_base_file'],
                                    kwargs['rinex_rover_file']
                                    ]

            b_header = self.getHeader(self.pathRnxTempFiles[0])
            b_header['ID'] = 1
            b_header['FLAG'] = 'B'
            b_header['PLATE'] = kwargs['tectonic_plate_base']
            b_header['APPROX POSITION XYZ'] = kwargs['coord_ref']

            r_header = self.getHeader(self.pathRnxTempFiles[1])
            r_header['ID'] = 2
            r_header['FLAG'] = ''
            r_header['PLATE'] = kwargs['tectonic_plate_rover']

            self.headers = [b_header, r_header]


        hDate = self.headers[0]['TIME OF FIRST OBS'].split()
        ano = int(hDate[0])
        mes = int(hDate[1])
        dia = int(hDate[2])
        self.dateFile = datetime(year=ano,month=mes,day=dia)


#-------------------------------------------------------------------------------
    # Download dos arquivos do servidor linux
    def getServerFiles(self, file):
        rfile = requests.get('http://gnss.ufv.br/media/' + file)
        # TODO: se erro 404 raise something
        with open(path.join(RINEX_UPLOAD_TEMP_DIR,'linux_server',file),'w',newline='\n') as f:
            f.write(rfile.text)


#-------------------------------------------------------------------------------

    def setBpeID(self):

        instante = datetime.now()

        self.bpeName = 'bern' + '{:03d}'.format(instante.timetuple().tm_yday)
        self.bpeName += '_' +  '{:02d}'.format(instante.hour)
        self.bpeName += '{:02d}'.format(instante.minute)
        self.bpeName += '{:02d}'.format(instante.second)
        self.bpeName += '{}'.format(instante.microsecond)



#-------------------------------------------------------------------------------

    def getHeader(self, rnxFile):
        '''
            rnxFile -> caminho completo do arquivo rinex
            header -> dictionary com os campos do cabeçalho
        '''
        # Verifica se o arquivo rinex existe no servidor
        if not path.isfile(rnxFile):
            raise Exception('Arquivo ' + rnxFile + ' não existe no servidor')

        with open(rnxFile, 'rb') as r_file:
            (r_isOK, msgErro, header) = readRinexObs(r_file)

        if not r_isOK:
            erro = 'Em ApiBernese(): Erro ao ler os dados do arquivo: '
            erro += str(kwargs['rinex_file'])
            erro += msgErro
            raise Exception(erro)

        return header

#-------------------------------------------------------------------------------

    def haveEphem(rnxDate):
        # TODO verificar efemerides
        return True


#-------------------------------------------------------------------------------

    def getRinex(self):
    # Salva o arquivo no servidor (DATAPOOL\RINEX)

        try:

            i = 0
            for rnxFile in self.pathRnxTempFiles:

                verRinex = self.headers[i]['version']
                if verRinex == 2: rinex_dir = 'RINEX'
                elif verRinex == 3: rinex_dir = 'RINEX3'
                else:
                    raise Exception('Rinex version ' + str(verRinex))

                new_rinex_path_name = path.join( DATAPOOL_DIR, rinex_dir, setRnxName(self.headers[i]) )

                with open(rnxFile,'r') as tmpFile, open( new_rinex_path_name, 'w') as destination:
                    aux = tmpFile.read()
                    destination.write(aux)

                if 'CRINEX VERS   / TYPE' in self.headers[i]:
                    cmd = 'crx2rnx -f {}'.format(new_rinex_path_name)
                    status = run(cmd,stdout=PIPE,stderr=PIPE)

                    if status.returncode != 1:
                        remove(new_rinex_path_name)
                    else:
                        log('Erro em ApiBernese -> crx2rnx')
                        if path.isfile(new_rinex_path_name[:-1]+'O'):
                            remove(new_rinex_path_name[:-1]+'O')
                            log(new_rinex_path_name[:-1]+'O removido')
                        raise Exception('Erro ao descompactar hatanaka. ' + str(status.stdout) + str(status.stderr))

                i += 1

            return True

        except Exception as e:

            log('Erro ao copiar Rinex para o Datapool. ' + str(e))
            log(str(e))
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))

            return False


#-------------------------------------------------------------------------------

    def getBlq(self):
    # Salva o arquivo BLQ no servidor (DATAPOOL\REF52)

        try:

            i = 0
            for blqFile in self.pathBlqTempFiles:

                if blqFile:

                    with open(blqFile,'r') as tmpFile, open(path.join(
                         DATAPOOL_DIR,'REF52','SYSTEM.BLQ'),'w') as destination:

                        aux = tmpFile.read()
                        destination.write(aux)

                i += 1

            return True

        except Exception as e:

            log('Erro ao copiar arquivo BLQ para o Datapool')
            log(str(e))
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))

            return False


#-------------------------------------------------------------------------------

    def getEphem(self):

    # TODO Se não achar efemérides do CODE pegar do IGS

        if TEST_SERVER:
            self.datum = 'IGS14'
            return True

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
            sErpWFile = 'COD{}7.ERP.Z'.format(weekDay[:4])
            sP1C1File = 'P1C1{:02d}{:02d}.DCB.Z'.format(anoRed,rnxDate.month)
            sP1P2File = 'P1P2{:02d}{:02d}.DCB.Z'.format(anoRed,rnxDate.month)


            # Verifica se existe a efemeride do dia, se não pega a efemeride da semana
            try:
                with urllib.request.urlopen(
                'ftp://ftp.aiub.unibe.ch/CODE/{:04d}/{}'.format(
                                                        rnxDate.year,sErpFile)
                                            ) as f: pass
            except Exception as e:
                log(str(e))
                log('EPH do dia não encontrado, utilizando EPH da semana')
                sErpFile = sErpWFile

            sfileList = [sClkFile, sEphFile, sIonFile, sErpFile, sP1C1File,
                        sP1P2File]

            cod_datapool_dir = path.join(DATAPOOL_DIR,'COD')
            bsw52_datapool_dir = path.join(DATAPOOL_DIR,'BSW52')

            for sfile in sfileList:

                codURL = ('ftp://ftp.aiub.unibe.ch/CODE/{:04d}/{}'.format(rnxDate.year,sfile))

                if sfile in [sIonFile, sP1C1File, sP1P2File]: target_dir = bsw52_datapool_dir
                else: target_dir = cod_datapool_dir

                pathFile = path.join(target_dir,sfile)

                if not path.isfile(pathFile): # verifica se os arquivos já estão no servidor
                    with urllib.request.urlopen(codURL) as response, open(pathFile, 'wb') as outFile:
                        data = response.read()
                        if not data: raise('Erro no download de: ' + sFile)
                        outFile.write(data)

                # status = run('7z x {} -o{} -y'.format(pathFile,target_dir),stdout=PIPE,stderr=PIPE)
                # if status.returncode:
                #     print('Erro ao descompactar o arquivo: ' + target_dir)
                #     print(status.stderr)

            # leitura do sistema de referencia das ephemerides
            if not hasattr(self,'datum'):
                command = '7z x {} -o{} -y'.format(str(path.join(cod_datapool_dir,sEphFile)),cod_datapool_dir)
                status = run(command,stdout=PIPE,stderr=PIPE)
                if not status.returncode:
                    with open(path.join(cod_datapool_dir,sEphFile[:-2]),'r') as f:
                        self.datum = f.readline().split()[8]
                        log('Datum lido das efemérides: ' + self.datum)
                else:
                    log('Erro ao ler o datum do arquivo .EPH')
                    self.datum = 'IGS14'

            return True

        except Exception as e:

            log('Erro no download das efemérides precisas')
            log(str(e))
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))
            # for tb in traceback.format_exc(erroMsg[2]): log(tb)

            return False


#-------------------------------------------------------------------------------

    # Define two char ABBreviation
    def setAbb(self):

        abb_list = []


        # Definindo a abreviação do primeiro arquivo
        self.headers[0]['ID2'] = self.headers[0]['MARKER NAME'][:2]
        abb_list.append(self.headers[0]['ID2'])

        # Definindo a abreviação dos demais sem repetição
        for i in range(1,len(self.headers)):

            if self.headers[i]['MARKER NAME'][:2] not in abb_list:
                self.headers[i]['ID2'] = self.headers[i]['MARKER NAME'][:2] # 1° and 2°
            elif self.headers[i]['MARKER NAME'][0::2] not in abb_list:
                self.headers[i]['ID2'] = self.headers[i]['MARKER NAME'][0::2] # 1° and 3°
            elif self.headers[i]['MARKER NAME'][0::3] not in abb_list:
                self.headers[i]['ID2'] = self.headers[i]['MARKER NAME'][0::3] # 1° and 4°
            else:
                for j in range(0,10):
                        if (self.headers[i]['MARKER NAME'][0] + str(j)) not in abb_list:
                            self.headers[i]['ID2'] = (self.headers[i]['MARKER NAME'][0] + str(j))
                            break

            abb_list.append(self.headers[i]['ID2'])

#-------------------------------------------------------------------------------

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

            f.write(CRD_HEADER_TEMPLATE_FILE.format(**{'DATUM': self.datum, 'EPOCH': '2010-01-01 00:00:00'}))

            for header in self.headers:
                f.write(CRD_BODY_TEMPLATE_FILE.format(**header))

        # Gerando arquivo ABB (Abreviação do nome da estação)
        self.setAbb()
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


#-------------------------------------------------------------------------------

    def runBPE(self):

        # TODO: Rever esse método. utilizar o finaly para mandar email deve melhar.

        result = None
        erroBPE = True
        runPCFout = []

        try:

            # confere se a fila de bpe threadings está liberada
            self.filaBPE()

            # limpa a pasta da campanha antes de iniciar o processamento
            self.clearCampaign()

            #Salva arquivo rinex em DATAPOOL
            if not self.getRinex():
                msg = 'Erro ao salvar o arquivo RINEX no servidor'
                log(msg)
                raise Exception(msg)

            #Salva arquivo BLQ em DATAPOOL
            if not self.getBlq():
                msg = 'Erro ao salvar o arquivo BLQ no servidor'
                log(msg)
                raise Exception(msg)

            # Download das efemérides precisas
            if not self.getEphem():

                if len(self.headers) > 1:
                    msg = 'Erro no processamento dos arquivos: '
                else:
                    msg = 'Erro no processamento do arquivo: '

                for rnxHeader in self.headers:
                    msg += path.basename(rnxHeader['RAW_NAME']) + ' '

                msg += '. \n'
                msg += 'Falha no download das efemérides precisas do CODE.'

                log(msg)

                # send_result_email(self.email,msg)
                # self.clearCampaign()
                self.endFunction(status = False, id = self.proc_id,
                                msg = msg, result = None)

                return False

            # Gera os arquivos do bernese com dados da estação
            self.setSTAfiles()


            arg = 'E:\\Sistema\\runasit.exe "C:\\Perl64\\bin\\perl.exe '

            if self.prcType == 'ppp':
                arg += 'E:\\Sistema\\pppdemo_pcs.pl '
            elif self.prcType == 'relativo':
                arg += 'E:\\Sistema\\rltufv_pcs.pl '
            else:
                raise Exception('prcType not defined in ApiBernese')

            arg += str(self.dateFile.year) + ' '
            arg += '{:03d}'.format(date2yearDay(self.dateFile)) + '0'

            if not hasattr(self,'datum'):
                log('Datum não definido')
                self.datum = 'IGS14'

            arg += ' V_REFINF ' + self.datum

            arg += ' V_PCV I' + self.datum[-2:]

            # TODO: adicionar outros argumentos aqui

            arg += '"'


            logMsg = 'Rodando BPE: ' + self.bpeName
            if len(self.headers) > 1: logMsg += ' - Arquivos: '
            else:  logMsg += ' - Arquivo: '
            for rnxHeader in self.headers:
                logMsg += path.basename(rnxHeader['RAW_NAME']) + ' '
            log(logMsg)

            if TEST_SERVER:
                print(arg)
                runPCFout = 'Ambiente de teste'
                result = None
                raise Exception(runPCFout)

            runPCFout = ['None']
            result = None
            with Popen(arg,stdout=PIPE,stderr=PIPE,stdin=DEVNULL,cwd='E:\\Sistema') as pRun:
                runPCFout = pRun.communicate()
                erroBPE = runPCFout[1]
            ## Another way
            # pRun = run(arg,stderr=PIPE,cwd='E:\\Sistema')
            # erroBPE = pRun.stderr

        except Exception as e:
            log('Erro ao rodar BPE: ' + self.bpeName)
            log(str(e))
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))
            # for tb in traceback.format_exc(erroMsg[2]): log(tb)
            erroBPE = True
            result = None

        # log('BPE: ' + self.bpeName + ' finalizado')


        if not erroBPE:

            log('BPE: ' + self.bpeName + ' finalizado com sucesso')

            try:
                result = self.getResult()
            except Exception as e:
                result = None
                log('Erro pegar o resultado da BPE: ' + self.bpeName)
                log(str(e))
                erroMsg = sys.exc_info()
                log(str(erroMsg[0]))
                log(str(erroMsg[1]))

        if result:

            if len(self.headers) > 1: msg = 'Arquivos '
            else:  msg = 'Arquivo '
            for rnxHeader in self.headers:
                msg += path.basename(rnxHeader['RAW_NAME']) + ' '
            if len(self.headers) > 1: msg += 'processado com sucesso.\n'
            else:  msg += 'processados com sucesso.\n'
            msg += 'Em anexo o resultado do processamento.'

            # send_result_email(self.email,msg, result)
            self.endFunction(status = True, id = self.proc_id,
                            msg = msg, result = result)

            self.clearCampaign()

            return True

        else:
            log('Arquivo com resultado do processamento não encontrado. Pegando pasta completa como resultado. ')
            try:
                result = self.get_full_result()
            except Exception as e:
                result = None
                log('Erro pegar a pasta como resultado da BPE: ' + self.bpeName)
                log(str(e))
                erroMsg = sys.exc_info()
                log(str(erroMsg[0]))
                log(str(erroMsg[1]))


        log('BPE Erro: ' + repr(runPCFout))

        if len(self.headers) > 1: msg = 'Erro no processamento dos arquivos '
        else:  msg = 'Erro no processamento do arquivo '
        for rnxHeader in self.headers:
            msg += path.basename(rnxHeader['RAW_NAME']) + ' '

        # RUNBPE.pm alterado na linha 881
        bernErrorFile = path.join(CAMPAIGN_DIR,'RAW','BERN_MSG_ERROR.txt')

        if path.isfile(bernErrorFile):
            msg += '. \nDetalhes sobre o erro no arquivo em anexo.'
            # send_result_email(self.email,msg, bernErrorFile)
            self.endFunction(status = False, id = self.proc_id,
                            msg = msg, result = bernErrorFile)
        else:
            msg += '. \nErro desconhecido.'
            # send_result_email(self.email,msg)
            self.endFunction(status = False, id = self.proc_id,
                            msg = msg, result = result)

        # self.clearCampaign()

        return False


#-------------------------------------------------------------------------------

    def getResult(self):

        if self.prcType == 'relativo':

            prcFile = 'RLT' + str(self.dateFile.year)[-2:]
            prcFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = path.join(CAMPAIGN_DIR,'OUT',prcFile)

            snxFile = 'F1_' + str(self.dateFile.year)[-2:]
            snxFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.SNX'
            snxFilePath = path.join(CAMPAIGN_DIR,'SOL',snxFile)

            outFile = 'F1_' + str(self.dateFile.year)[-2:]
            outFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.OUT'
            outFilePath = path.join(CAMPAIGN_DIR,'OUT',outFile)

            resultListFiles = [prcPathFile, snxFilePath, outFilePath]

        elif self.prcType == 'ppp':

            prcFile = 'PPP' + str(self.dateFile.year)[-2:]
            prcFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = path.join(CAMPAIGN_DIR,'OUT',prcFile)

            snxFile = 'RED' + str(self.dateFile.year)[-2:]
            snxFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.SNX'
            snxFilePath = path.join(CAMPAIGN_DIR,'SOL',snxFile)

            outFile = 'RED' + str(self.dateFile.year)[-2:]
            outFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.OUT'
            outFilePath = path.join(CAMPAIGN_DIR,'OUT',outFile)

            kinFile = 'KIN' + '{:03d}'.format(date2yearDay(self.dateFile)) + '0'
            kinFile += self.headers[0]['MARKER NAME'][:4] + '.SUM'
            kinFilePath = path.join(CAMPAIGN_DIR,'OUT',kinFile)

            resultListFiles = [prcPathFile, snxFilePath, outFilePath, kinFilePath]

        else:
            return False

        resultZipFile = path.join(RESULTS_DIR,self.bpeName + '.zip')

        with ZipFile(resultZipFile, 'x', ZIP_DEFLATED) as rZipFile:
            for file in resultListFiles:
                if path.isfile(file):
                    rZipFile.write(file, path.basename(file))
                else:
                    log('Arquivo ' + path.basename(file) + ' não encontrado.')

        # Verifica se arquivo está vazio
        if rZipFile.namelist():
            return resultZipFile
        else:
            return False


#-------------------------------------------------------------------------------

    def get_full_result(self):

        if TEST_SERVER:
            return False

        resultZipFile = path.join(RESULTS_DIR,self.bpeName + 'campaign.zip')

        with ZipFile(resultZipFile, 'x', ZIP_DEFLATED) as rZipFile:
            for dirname, subdirs, files in walk(CAMPAIGN_DIR):
                rZipFile.write(dirname)
                for filename in files:
                    rZipFile.write(path.join(dirname, filename))

        # Verifica se arquivo está vazio
        if rZipFile.namelist():
            return resultZipFile
        else:
            return False

#-------------------------------------------------------------------------------

    def clearCampaign(self):

        # Não roda a função. Evita de limpar os dados para depuração.
        # if TEST_SERVER:
        #     return True

        log('Clear Campaign Starting')

        listdir = [

            path.join(DATAPOOL_DIR,'RINEX'),
            path.join(DATAPOOL_DIR,'RINEX3'),
            # path.join(DATAPOOL_DIR,'BSW52'),
            # path.join(DATAPOOL_DIR,'COD'),

            path.join(CAMPAIGN_DIR,'ATM'),
            path.join(CAMPAIGN_DIR,'BPE'),
            path.join(CAMPAIGN_DIR,'GRD'),
            path.join(CAMPAIGN_DIR,'OBS'),
            path.join(CAMPAIGN_DIR,'ORB'),
            path.join(CAMPAIGN_DIR,'ORX'),
            path.join(CAMPAIGN_DIR,'OUT'),
            path.join(CAMPAIGN_DIR,'RAW'),
            path.join(CAMPAIGN_DIR,'SOL'),
            path.join(CAMPAIGN_DIR,'STA'),

        ]

        for dir in listdir:
            files = glob(path.join(dir, '*'))
            for f in files:
                remove(f)

        with open(path.join(CAMPAIGN_DIR,'STA','SESSIONS.SES'),'w') as ses_file:
            ses_file.write(SES_TEMPLATE_FILE)

        for f in glob(path.join(DATAPOOL_DIR,'REF52','SYSTEM.*')):
            remove(f)

        log('Campaign Cleaned')

#-------------------------------------------------------------------------------

    def filaBPE(self):

        # Verifica todas as threadings ativas
        threads = threading.enumerate()

        # Coloca as threadings que tem o inicio do nome com 'bern' em uma lista
        threadsNames = []
        position = 0
        for th in threads:
            if (th.name[:4] == 'bern') and (th.name != self.bpeName):
                threadsNames_aux = {'id':position, 'name':th.name}
                threadsNames.append(threadsNames_aux)
            position += 1

        # ordena pelo nome, que esta ligado ao datetime que foi criado
        threadsNames.sort(key=lambda k:k['name'])

        # um de cada vez, como a tia gorda ensinou
        for tname in threadsNames:
            threads[tname['id']].join()
