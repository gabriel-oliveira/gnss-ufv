import sys
import traceback
import urllib.request
import requests
from glob import glob
import threading
from datetime import datetime
from os import path, remove, walk, rename, system, stat, makedirs, name as osname
from subprocess import Popen, run, PIPE, DEVNULL
from bernese.core.berneseFilesTemplate import *
from bernese.core.rinex import *
from bernese.settings import ( MAX_PROCESSING_TIME,
DEBUG, RINEX_UPLOAD_TEMP_DIR, DOWNLOAD_EPHEM, HOST
)
# from bernese.core.mail import send_result_email
from bernese.core.log import log
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copyfile, rmtree

#-------------------------------------------------------------------------------
# TODO: transformar logs em raises???
# TODO: definir função a ser execultada pós processamento (send mail, proc.finished_at)
#       fora da Api passa-la por parametro com seus parametros efkwargs
#-------------------------------------------------------------------------------

class ApiBernese:

#-------------------------------------------------------------------------------

    #def __init__(self, bpeName, rheaders, remail, pathTempFiles,pathBlqTempFiles):
    def __init__(self, **kwargs):
        
        if osname == 'nt':
            self.osname = 'WINDOWS'
        else:
            self.osname = 'LINUX'

        self.setBpeID()

        self.makeGPSDATA_dirs()

        if 'proc_id' in kwargs:
            self.proc_id = kwargs['proc_id']
        else:
            self.proc_id = self.bpeName

        self.hoi_correction = kwargs['hoi_correction']
        
        if kwargs['blq_file']:
            self.pathBlqTempFiles = [kwargs['blq_file']]
        else:
            self.pathBlqTempFiles = []

        self.prcType = kwargs['proc_method']

        if 'datum' in kwargs: self.datum = kwargs['datum']

        # TODO: rever a eficiencia disto
        if 'endFunction' in kwargs:
            end_f = kwargs['endFunction']

        def newend_f(**kwargs):
            try:
                end_f(**kwargs)
                if not DEBUG:
                    rmtree(kwargs['BASE_DIR'], ignore_errors=True)
            except Exception as e:
                log('Erro ao rodar endFunction')
                log(str(e))
                erroMsg = sys.exc_info()
                log(str(erroMsg[0]))
                log(str(erroMsg[1]))

        self.endFunction = newend_f

        if kwargs['proc_method'] == 'ppp':

            self.pathRnxTempFiles = [kwargs['rinex_file']]

            header = self.getHeader(self.pathRnxTempFiles[0])
            header['ID'] = 1
            header['ID2'] = header['MARKER NAME'][:2]
            header['FLAG'] = ''
            header['PLATE'] = kwargs['tectonic_plate']

            self.headers = [header]

        elif kwargs['proc_method'] in ['relativo','rapido']:

            self.pathRnxTempFiles = [
                                    kwargs['rinex_rover_file'],
                                    kwargs['rinex_base_file']
                                    ]

            b_header = self.getHeader(self.pathRnxTempFiles[1])
            b_header['ID'] = 2
            b_header['FLAG'] = 'B'
            b_header['PLATE'] = kwargs['tectonic_plate_base']
            b_header['APPROX POSITION XYZ'] = kwargs['coord_ref']

            r_header = self.getHeader(self.pathRnxTempFiles[0])
            r_header['ID'] = 1
            r_header['FLAG'] = ''
            r_header['PLATE'] = kwargs['tectonic_plate_rover']

            self.headers = [r_header, b_header]

        elif kwargs['proc_method'] == 'rede':

            self.pathRnxTempFiles = [
                                    kwargs['rinex_rover_file']
                                    ]

            r_header = self.getHeader(self.pathRnxTempFiles[0])
            r_header['ID'] = 1
            r_header['FLAG'] = ''
            r_header['PLATE'] = kwargs['tectonic_plate_rover']

            self.tectonic_plate_base = kwargs['tectonic_plate_base']

            self.headers = [r_header]

            self.bases_rbmc = kwargs['bases_rbmc']

        else:
            raise Exception('procType: ' + kwargs['proc_method'])


        hDate = self.headers[0]['TIME OF FIRST OBS'].split()
        ano = int(hDate[0])
        mes = int(hDate[1])
        dia = int(hDate[2])
        self.dateFile = datetime(year=ano,month=mes,day=dia)


#-------------------------------------------------------------------------------

    def setBpeID(self):

        instante = datetime.now()

        self.bpeName = 'bern' + '{:03d}'.format(instante.timetuple().tm_yday)
        self.bpeName += '_' +  '{:02d}'.format(instante.hour)
        self.bpeName += '{:02d}'.format(instante.minute)
        self.bpeName += '{:02d}'.format(instante.second)
        self.bpeName += '{}'.format(instante.microsecond)



#-------------------------------------------------------------------------------

    def makeGPSDATA_dirs(self):

        self.GLOBAL_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
        self.BASE_DIR = path.join(self.GLOBAL_DIR,'TEMP',self.bpeName)
        self.GPSDATA_DIR = path.join(self.BASE_DIR, 'GPSDATA')
        self.DATAPOOL_DIR = path.join(self.GPSDATA_DIR, 'DATAPOOL')
        self.SAVEDISK_DIR = path.join(self.GPSDATA_DIR, 'SAVEDISK')
        self.CAMPAIGN_DIR = path.join(self.GPSDATA_DIR, 'CAMPAIGN52', 'SYSTEM')
        self.RESULTS_DIR = path.join(self.GLOBAL_DIR, 'RESULTADOS')

        # SAVEDISK
        makedirs(self.SAVEDISK_DIR)

        # DATAPOOL
        makedirs(path.join(self.DATAPOOL_DIR,'BSW52'))
        makedirs(path.join(self.DATAPOOL_DIR,'COD'))
        makedirs(path.join(self.DATAPOOL_DIR,'COM'))
        makedirs(path.join(self.DATAPOOL_DIR,'HOURLY'))
        makedirs(path.join(self.DATAPOOL_DIR,'IGS'))
        makedirs(path.join(self.DATAPOOL_DIR,'LEO'))
        makedirs(path.join(self.DATAPOOL_DIR,'MSC'))
        makedirs(path.join(self.DATAPOOL_DIR,'REF52'))
        makedirs(path.join(self.DATAPOOL_DIR,'RINEX'))
        makedirs(path.join(self.DATAPOOL_DIR,'RINEX3'))
        makedirs(path.join(self.DATAPOOL_DIR,'SLR_NP'))
        makedirs(path.join(self.DATAPOOL_DIR,'STAT_LOG'))
        makedirs(path.join(self.DATAPOOL_DIR,'VMF1'))

        # CAMPAIGN
        makedirs(path.join(self.CAMPAIGN_DIR,'ATM'))
        makedirs(path.join(self.CAMPAIGN_DIR,'BPE'))
        makedirs(path.join(self.CAMPAIGN_DIR,'GRD'))
        makedirs(path.join(self.CAMPAIGN_DIR,'OBS'))
        makedirs(path.join(self.CAMPAIGN_DIR,'ORB'))
        makedirs(path.join(self.CAMPAIGN_DIR,'ORX'))
        makedirs(path.join(self.CAMPAIGN_DIR,'OUT'))
        makedirs(path.join(self.CAMPAIGN_DIR,'RAW'))
        makedirs(path.join(self.CAMPAIGN_DIR,'SOL'))
        makedirs(path.join(self.CAMPAIGN_DIR,'STA'))
        with open(path.join(self.CAMPAIGN_DIR,'STA','SESSIONS.SES'),'w') as ses_file:
            ses_file.write(SES_TEMPLATE_FILE)


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
            erro += str(rnxFile)
            erro += msgErro
            raise Exception(erro)

        return header


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

                new_rinex_path_name = path.join( self.DATAPOOL_DIR, rinex_dir, setRnxName(self.headers[i]) )

                with open(rnxFile,'r') as tmpFile, open( new_rinex_path_name, 'w') as destination:
                    aux = tmpFile.read()
                    destination.write(aux)

                if 'CRINEX VERS   / TYPE' in self.headers[i]:
                    cmd = 'CRX2RNX -f {}'.format(new_rinex_path_name)
                    status = run(cmd,stdout=PIPE,stderr=PIPE,shell=True)

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
                         self.DATAPOOL_DIR,'REF52','SYSTEM.BLQ'),'w') as destination:

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

    def hasFile(self,pathfile):
        if path.isfile(pathfile):
            if stat(pathfile).st_size > 1:
                return True
            else:
                remove(pathfile)
                return False
        else:
            return False


#-------------------------------------------------------------------------------

    def getEphem(self):

    # TODO Se não achar efemérides do CODE pegar do IGS

        if not DOWNLOAD_EPHEM:
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

            cod_datapool_dir_global = path.join(self.GLOBAL_DIR,'GPSDATA','DATAPOOL','COD')
            cod_datapool_dir_local = path.join(self.DATAPOOL_DIR,'COD')
            bsw52_datapool_dir_global = path.join(self.GLOBAL_DIR,'GPSDATA','DATAPOOL','BSW52')
            bsw52_datapool_dir_local = path.join(self.DATAPOOL_DIR,'BSW52')

            # Verifica se existe a efemeride do dia, se não pega a efemeride da semana
            try:
                with urllib.request.urlopen(
                'http://ftp.aiub.unibe.ch/CODE/{:04d}/{}'.format(
                                                        rnxDate.year,sErpFile)
                                            ) as f: pass
            except Exception as e:
                log(str(e))
                log('EPH do dia não encontrado, utilizando EPH da semana')
                sErpFile = sErpWFile

            sfileList = [sClkFile, sEphFile, sIonFile, sErpFile, sP1C1File,
                        sP1P2File]

            for sfile in sfileList:

                codURL = ('http://ftp.aiub.unibe.ch/CODE/{:04d}/{}'.format(rnxDate.year,sfile))

                if sfile in [sIonFile, sP1C1File, sP1P2File]:
                    target_dir_global = bsw52_datapool_dir_global
                    target_dir_local = bsw52_datapool_dir_local
                else:
                    target_dir_global = cod_datapool_dir_global
                    target_dir_local = cod_datapool_dir_local

                pathFile_global = path.join(target_dir_global,sfile)
                pathFile_local = path.join(target_dir_local,sfile)

                if not self.hasFile(pathFile_global): # verifica se os arquivos já estão no servidor
                    with urllib.request.urlopen(codURL) as response, open(pathFile_global, 'wb') as outFile:
                        data = response.read()
                        if not data: raise('Erro no download de: ' + sfile)
                        outFile.write(data)

                copyfile(pathFile_global,pathFile_local)

            # leitura do sistema de referencia das ephemerides
            if not hasattr(self,'datum'):
                command = '7z x {} -o{} -y'.format(str(path.join(cod_datapool_dir_local,sEphFile)),cod_datapool_dir_local)
                status = run(command,stdout=PIPE,stderr=PIPE, shell=True)
                if not status.returncode:
                    with open(path.join(cod_datapool_dir_local,sEphFile[:-2]),'r') as f:
                        self.datum = f.readline().split()[8]
                        log('Datum lido das efemérides: ' + self.datum)
                else:
                    log('Erro ao ler o datum do arquivo .EPH')
                    return False

            ref52_dir_global = path.join(self.GLOBAL_DIR,'GPSDATA','DATAPOOL','REF52')
            ref52_dir_local = path.join(self.DATAPOOL_DIR,'REF52')
            
            copyfile(path.join(ref52_dir_global,'{}_R.CRD'.format(self.datum)),
                        path.join(ref52_dir_local,'{}_R.CRD'.format(self.datum)))
            copyfile(path.join(ref52_dir_global,'{}_R.VEL'.format(self.datum)),
                        path.join(ref52_dir_local,'{}_R.VEL'.format(self.datum)))
            copyfile(path.join(ref52_dir_global,'{}.FIX'.format(self.datum)),
                        path.join(ref52_dir_local,'{}.FIX'.format(self.datum)))

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

        ref52_datapool_dir = path.join(self.DATAPOOL_DIR,'REF52')

        pPLDfile = path.join(ref52_datapool_dir,campaignName+'.PLD')
        pSTAfile = path.join(ref52_datapool_dir,campaignName+'.STA')
        pCRDfile = path.join(ref52_datapool_dir,campaignName+'.CRD')
        pABBfile = path.join(ref52_datapool_dir,campaignName+'.ABB')
        pBSLfile = path.join(ref52_datapool_dir,campaignName+'.BSL')
        # pVELfile = path.join(ref52_datapool_dir,campaignName+'.VEL')

        # Gerando arquivo PLD (placa tectonica da estação)
        with open(pPLDfile,'w') as f:

            f.write(PLD_HEADER_TEMPLATE_FILE.format(**{'DATUM': self.datum,}))

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

        # Gerando arquivo BSL (linhas de base)
        if self.prcType in ['relativo','rede','rapido']:
            with open(pBSLfile,'w') as f:
                for header in self.headers[1:]:
                    context = {
                    'b_name' : header['MARKER NAME'],
                    'b_number' : header['MARKER NUMBER'],
                    'r_name' : self.headers[0]['MARKER NAME'],
                    'r_number' : self.headers[0]['MARKER NUMBER']
                    }
                    f.write('{b_name:<4s} {b_number:<9s}   {r_name:<4s} {r_number:<9s}  \n'.format(**context))

        # Gerando arquivo VEL (velocidades da estação)
        # with open(pVELfile,'w') as f:
        #
        #     f.write(VEL_HEADER_TEMPLATE_FILE.format(**{'DATUM': 'IGS14'}))
        #
        #     for header in self.headers:
        #         f.write(VEL_BODY_TEMPLATE_FILE.format(**header))

#-------------------------------------------------------------------------------

    def getRBMC(self):

        rnxDate = self.dateFile

        ano = str(self.dateFile.year)
        dia = '{:03d}'.format(date2yearDay(self.dateFile))
        if rnxDate.year > 1999:
            anoRed = rnxDate.year - 2000
        else:
            anoRed = rnxDate.year - 1900

        ftp_link = 'ftp://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados/{}/{}/'.format(ano,dia)

        bases = self.bases_rbmc.split()

        if self.headers[0]['MARKER NAME'] in bases: bases.remove(self.headers[0]['MARKER NAME'])

        rinex_datapool_dir = path.join(self.DATAPOOL_DIR,'RINEX')

        bases_ok = [i for i in bases]
        i = 1
        for base in bases:

            erro = False

            file_name = base.lower() + dia + '1.zip'
            file_link = (ftp_link + file_name)
            zfile_target = path.join(rinex_datapool_dir, file_name)

            try:
                with urllib.request.urlopen(file_link) as response, open(zfile_target, 'wb') as outFile:
                    data = response.read()
                    if data: outFile.write(data)
                    else: erro = True
            except:
                erro = True

            if not erro:

                rnxO_file_name = file_name[:-3] + '{:02d}o'.format(anoRed)
                rnxD_file_name = file_name[:-3] + '{:02d}d'.format(anoRed)

                with ZipFile(zfile_target) as zfile:
                    if rnxO_file_name in zfile.namelist():
                        extract_file = zfile.extract(rnxO_file_name,path=rinex_datapool_dir)
                        target_file = path.join(rinex_datapool_dir, file_name[:-5].upper() + '0.{:02d}O'.format(anoRed))
                        rename(extract_file, target_file)
                    elif rnxD_file_name in zfile.namelist():
                        extract_file = zfile.extract(rnxD_file_name,path=rinex_datapool_dir)
                        target_file = path.join(rinex_datapool_dir, file_name[:-5].upper() + '0.{:02d}D'.format(anoRed))
                        rename(extract_file, target_file)
                        status = system('CRX2RNX {}'.format(target_file))
                        if not status:
                            remove(target_file)
                        else:
                            erro = True
                    else:
                        erro = True
                remove(zfile_target)

                header = self.getHeader(target_file[:-1] + 'O')
                i += 1
                header['ID'] = i
                header['FLAG'] = 'B'
                header['PLATE'] = self.tectonic_plate_base
                self.headers.append(header)
            else:
                bases_ok.remove(base)

        if not bases_ok: raise Exception('Nenhum arquivo de base encontrado')

        return True

#-------------------------------------------------------------------------------

    def runBPE(self):

        # TODO: Rever esse método. utilizar o finaly para mandar email deve melhar.

        run_stdout, run_stderr = [False, False]

        try:

            # confere se a fila de bpe threadings está liberada
            self.filaBPE()

            # Download dos arquivos de base da RBMC
            if self.prcType == 'rede':
                self.getRBMC()

            # Salva arquivo rinex em DATAPOOL
            if not self.getRinex():
                msg = 'Erro ao salvar o arquivo RINEX no servidor'
                log(msg)
                raise Exception(msg)

            # Salva arquivo BLQ em DATAPOOL
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

                self.endFunction(status = False, id = self.proc_id,
                                msg = msg, result = None, BASE_DIR = self.BASE_DIR)

                return [False, '{} Falha no download das efemérides precisas'.format(self.bpeName)]

            # Gera os arquivos do bernese com dados da estação
            self.setSTAfiles()

            if self.osname == 'LINUX':
                host = HOST
            else:
                host = 'host.docker.internal'

            arg = 'docker --host={} run --network=internal --rm --name {} '.format(host,self.bpeName)
            arg += '-v gnssufv_temp:/home/TEMP -v gnssufv_log:/home/LOG '
            arg += '-e BPENAME={} '.format(self.bpeName)
            arg += 'gnssufv/bernese:latest bash -c '

            if self.osname == 'LINUX':
                arg += "'source /home/BERN52/GPS/EXE/LOADGPS.setvar "
            else:
                arg += '"source /home/BERN52/GPS/EXE/LOADGPS.setvar '

            if self.prcType == 'ppp':
                arg += '&& perl ${U}/SCRIPT/pppdemo_pcs.pl '
            elif self.prcType in ['relativo','rede']:
                arg += '&& perl ${U}/SCRIPT/rltufv_pcs.pl '
            elif self.prcType == 'rapido':
                arg += '&& perl ${U}/SCRIPT/rapsta_pcs.pl '
            else:
                raise Exception('prcType not defined in ApiBernese')

            arg += str(self.dateFile.year) + ' '
            arg += '{:03d}'.format(date2yearDay(self.dateFile)) + '0'

            if not hasattr(self,'datum'):
                log('Datum não definido')
                self.datum = 'IGS14'

            arg += ' V_REFINF ' + self.datum

            # arg += ' V_PCV I' + self.datum[-2:]

            if self.hoi_correction:
                arg += ' V_HOIFIL HOI\$YSS+0'

            # TODO: adicionar outros argumentos aqui

            if self.osname == 'LINUX':
                arg += "'"
            else:
                arg += '"'

            logMsg = 'Rodando BPE: ' + self.bpeName
            if len(self.headers) > 1: logMsg += ' - Arquivos: '
            else:  logMsg += ' - Arquivo: '
            for rnxHeader in self.headers:
                logMsg += path.basename(rnxHeader['RAW_NAME']) + ' '
            log(logMsg)

            with Popen(arg,stdout=PIPE,stderr=PIPE,stdin=DEVNULL,cwd=self.BASE_DIR,shell=True) as pRun:
                run_stdout, run_stderr = pRun.communicate()

        except Exception as e:
            log('Erro ao rodar BPE: ' + self.bpeName)
            log(str(e))
            erroMsg = sys.exc_info()
            log(str(erroMsg[0]))
            log(str(erroMsg[1]))
            for tb in traceback.format_exc(erroMsg[2]): log(tb)

        log('BPE: ' + self.bpeName + ' finalizado')
        
        if run_stderr:

            result = False

        else:

            try:
                result = self.getResult()
            except Exception as e:
                result = False
                log('Erro ao pegar o resultado da BPE: ' + self.bpeName)
                log(str(e))
                erroMsg = sys.exc_info()
                log(str(erroMsg[0]))
                log(str(erroMsg[1]))

        if result:

            if len(self.headers) > 1: msg = 'Arquivos '
            else:  msg = 'Arquivo '
            resultFileName = ''
            for rnxHeader in self.headers:
                msg += path.basename(rnxHeader['RAW_NAME']) + ' '
                resultFileName += path.basename(rnxHeader['RAW_NAME'])[:-4] + '_'
            resultFileName += '.zip'
            if len(self.headers) > 1: msg += 'processados com sucesso.\n'
            else:  msg += 'processado com sucesso.\n'
            msg += 'Em anexo o resultado do processamento.\n\n'

            if self.coord_result:
                msg += 'Estação: ' + self.coord_result[0] + '\n'
                msg += 'Coordenadas Estimadas (X Y Z) (m):'
                msg += '\t{:.4f}\t{:.4f}\t{:.4f}\n'.format(*self.coord_result[1:4]).replace('.',',')
                msg += 'Desvios (X Y Z) (m): '
                msg += '\t{:.4f}\t{:.4f}\t{:.4f}\n\n'.format(*self.coord_result[4:7]).replace('.',',')
                msg += 'Sistema de Referência e Época: '
                if self.prcType == 'ppp':
                    msg += self.datum + ' '
                    msg += '{:d}'.format(self.dateFile.year) + ','
                    msg += '{:4.2f}'.format(date2yearDay(self.dateFile)/365.0)[2:]
                elif self.prcType in ['relativo','rapido']:
                    msg += 'O mesmo da coordenada de referência definida na submissão'
                elif self.prcType == 'rede':
                    msg += 'SIRGAS2000, 2000.4'


            self.endFunction(status = True, id = self.proc_id,
                            msg = msg, result = result, filename = resultFileName, BASE_DIR = self.BASE_DIR)
            
            # Sucessful end runBPE
            return [True, 'Finalizado com sucesso']

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


        log('RUNBPE STDOUT: {}\n STDERR: {}'.format(run_stdout.decode(errors='replace'),run_stderr.decode(errors='replace')))

        if len(self.headers) > 1: msg = 'Erro no processamento dos arquivos '
        else:  msg = 'Erro no processamento do arquivo '
        for rnxHeader in self.headers:
            msg += path.basename(rnxHeader['RAW_NAME']) + ' '

        # RUNBPE.pm alterado na linha 881
        bernErrorFile = path.join(self.CAMPAIGN_DIR,'RAW','BERN_MSG_ERROR.txt')

        if path.isfile(bernErrorFile):
            msg += '. \nDetalhes sobre o erro no arquivo em anexo.'
            # send_result_email(self.email,msg, bernErrorFile)
            self.endFunction(status = False, id = self.proc_id,
                            msg = msg, result = bernErrorFile, filename='ERRO_BERN.txt', BASE_DIR = self.BASE_DIR)
        else:
            msg += '. \nErro desconhecido.'
            # send_result_email(self.email,msg)
            self.endFunction(status = False, id = self.proc_id,
                            msg = msg, result = result, filename='campaign.zip', BASE_DIR = self.BASE_DIR)

        return [False, 'Erro no processamento do {}. Resultado: {}'.format(self.bpeName, str(result))]


#-------------------------------------------------------------------------------

    def getResult(self):

        if self.prcType in ['relativo','rede']:

            prcFile = 'RLT' + str(self.dateFile.year)[-2:]
            prcFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = path.join(self.CAMPAIGN_DIR,'OUT',prcFile)

            snxFile = 'F1_' + str(self.dateFile.year)[-2:]
            snxFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.SNX'
            snxFilePath = path.join(self.CAMPAIGN_DIR,'SOL',snxFile)

            outFile = 'F1_' + str(self.dateFile.year)[-2:]
            outFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.OUT'
            outFilePath = path.join(self.CAMPAIGN_DIR,'OUT',outFile)

            resultListFiles = [prcPathFile, snxFilePath, outFilePath]

        elif self.prcType == 'rapido':

            prcFile = 'RLT' + str(self.dateFile.year)[-2:]
            prcFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = path.join(self.CAMPAIGN_DIR,'OUT',prcFile)

            snxFile = 'F1_' + str(self.dateFile.year)[-2:]
            snxFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.SNX'
            snxFilePath = path.join(self.CAMPAIGN_DIR,'SOL',snxFile)

            snxFile2 = 'P1_' + str(self.dateFile.year)[-2:]
            snxFile2 += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.SNX'
            snxFilePath2 = path.join(self.CAMPAIGN_DIR,'SOL',snxFile2)

            outFile = 'F1_' + str(self.dateFile.year)[-2:]
            outFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.OUT'
            outFilePath = path.join(self.CAMPAIGN_DIR,'OUT',outFile)

            outFile2 = 'P1_' + str(self.dateFile.year)[-2:]
            outFile2 += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.OUT'
            outFilePath2 = path.join(self.CAMPAIGN_DIR,'OUT',outFile2)

            resultListFiles = [snxFilePath, snxFilePath2, outFilePath, outFilePath2]

        elif self.prcType == 'ppp':

            prcFile = 'PPP' + str(self.dateFile.year)[-2:]
            prcFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.PRC'
            prcPathFile = path.join(self.CAMPAIGN_DIR,'OUT',prcFile)

            snxFile = 'RED' + str(self.dateFile.year)[-2:]
            snxFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.SNX'
            snxFilePath = path.join(self.CAMPAIGN_DIR,'SOL',snxFile)

            outFile = 'RED' + str(self.dateFile.year)[-2:]
            outFile += '{:03d}'.format(date2yearDay(self.dateFile)) + '0.OUT'
            outFilePath = path.join(self.CAMPAIGN_DIR,'OUT',outFile)

            kinFile = 'KIN' + '{:03d}'.format(date2yearDay(self.dateFile)) + '0'
            kinFile += self.headers[0]['MARKER NAME'][:4] + '.SUM'
            kinFilePath = path.join(self.CAMPAIGN_DIR,'OUT',kinFile)

            resultListFiles = [prcPathFile, snxFilePath, outFilePath, kinFilePath]

        else:
            return False

        resultZipFile = path.join(self.RESULTS_DIR,self.bpeName + '.zip')

        with ZipFile(resultZipFile, 'x', ZIP_DEFLATED) as rZipFile:
            for file in resultListFiles:
                if path.isfile(file):
                    rZipFile.write(file, path.basename(file))
                else:
                    log('Arquivo ' + path.basename(file) + ' não encontrado.')

        # Verifica se arquivo está vazio
        if rZipFile.namelist():
            if path.isfile(snxFilePath):
                self.coord_result = self.get_coord_result(snxFilePath)
            else:
                self.coord_result = self.get_coord_result(snxFilePath2)
            return resultZipFile
        else:
            return False


#-------------------------------------------------------------------------------

    def get_coord_result(self,snxfile):

        with open(snxfile,'r') as sfile:
            snx = sfile.readlines()

        snxFile = iter(snx)
        while True:
            line = next(snxFile)
            if line:
                if line.split()[0] == '+SOLUTION/ESTIMATE':
                    header = next(snxFile)
                    line = next(snxFile).split()
                    coord_X = float(line[8])
                    sigm_X = float(line[9])
                    line = next(snxFile).split()
                    coord_Y = float(line[8])
                    sigm_Y = float(line[9])
                    line = next(snxFile).split()
                    coord_Z = float(line[8])
                    sigm_Z = float(line[9])
                    station = line[2]
                    return [station, coord_X, coord_Y, coord_Z, sigm_X, sigm_Y, sigm_Z]
            else:
                return False


#-------------------------------------------------------------------------------

    def get_full_result(self):

        resultZipFile = path.join(self.RESULTS_DIR,self.bpeName + 'campaign.zip')

        with ZipFile(resultZipFile, 'x', ZIP_DEFLATED) as rZipFile:
            for dirname, subdirs, files in walk(self.CAMPAIGN_DIR):
                if dirname[-3:] not in ['RAW','OBS']:
                    rZipFile.write(dirname)
                    for filename in files:
                        rZipFile.write(path.join(dirname, filename))

        # Verifica se arquivo está vazio
        if rZipFile.namelist():
            return resultZipFile
        else:
            return False

#-------------------------------------------------------------------------------
# DEPRECATED
    # def clearCampaign(self):

    #     log('Clear Campaign Starting')

    #     listdir = [

    #         path.join(self.DATAPOOL_DIR,'RINEX'),
    #         path.join(self.DATAPOOL_DIR,'RINEX3'),
    #         # path.join(DATAPOOL_DIR,'BSW52'),
    #         # path.join(DATAPOOL_DIR,'COD'),

    #         path.join(self.CAMPAIGN_DIR,'ATM'),
    #         path.join(self.CAMPAIGN_DIR,'BPE'),
    #         path.join(self.CAMPAIGN_DIR,'GRD'),
    #         path.join(self.CAMPAIGN_DIR,'OBS'),
    #         path.join(self.CAMPAIGN_DIR,'ORB'),
    #         path.join(self.CAMPAIGN_DIR,'ORX'),
    #         path.join(self.CAMPAIGN_DIR,'OUT'),
    #         path.join(self.CAMPAIGN_DIR,'RAW'),
    #         path.join(self.CAMPAIGN_DIR,'SOL'),
    #         path.join(self.CAMPAIGN_DIR,'STA'),

    #     ]

    #     for dir in listdir:
    #         files = glob(path.join(dir, '*'))
    #         for f in files:
    #             remove(f)

    #     with open(path.join(self.CAMPAIGN_DIR,'STA','SESSIONS.SES'),'w') as ses_file:
    #         ses_file.write(SES_TEMPLATE_FILE)

    #     for f in glob(path.join(DATAPOOL_DIR,'REF52','SYSTEM.*')):
    #         remove(f)

    #     log('Campaign Cleaned')

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

        if len(threadsNames) != 0: # Um processamento por vez

            log('Waiting free threads')
            
            for tname in threadsNames:

                threads[tname['id']].join(MAX_PROCESSING_TIME*60) # TODO: float seconds arg time out

                if threads[tname['id']].is_alive():
                    # TODO: kill docker and remove dir
                    log('Thread time out')
