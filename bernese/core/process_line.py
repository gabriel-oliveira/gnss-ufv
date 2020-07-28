'''
Processos necessário para gerenciar a fila de processamento do Bernese.
'''

from bernese.settings import MAX_PROCESSING_TIME, RINEX_UPLOAD_TEMP_DIR
from bernese.core.mail import send_result_email
from bernese.core.models import Proc_Request, basesRBMC
from bernese.core.apiBernese import ApiBernese
from bernese.core.log import log
from django.utils import timezone
import threading
import sys
import os
import socket
import requests


def is_connected():
    try:
        with socket.create_connection(("www.google.com", 80)):
            pass
        return True
    except:
        return False


def check_line():
    '''
        Verifica se a fila está liberada e começa o processamento do próximo da
        fila
    '''

    log('check_line: Threadings ' + str(threading.enumerate()))

    # Processos sendo execultados
    procs_running = Proc_Request.objects.filter(proc_status='running')

    if not procs_running:

        # Processos aguardando para serem execultados
        procs_waiting = Proc_Request.objects.filter(proc_status='waiting')

        # Verifica se o servidor está online
        if procs_waiting and is_connected():
            _run_next()

    else:

        if len(procs_running) > 1:
            # WARNING: Situação perigosa. Um processo sendo iniciado antes do
            #          outro ser finalizado.

            log('WARNING!!! check_line(): Mais de um processo sendo execultado')

            # raise something

        t_now = timezone.localtime(timezone.now())

        for proc in procs_running:

            dtime = (t_now - proc.started_at)

            if dtime.total_seconds()/60 > MAX_PROCESSING_TIME:

                msg = 'Tempo máximo de processamento excedido'
                log('ERROR!!! check_line(): ' + msg)
                args = {
                    'status' : 'Erro',
                    'id' : proc.id,
                    'msg' : msg,
                    'result' : None,
                    }
                finishing_process(**args)

                # TODO: matar o processamento atual do bernese


def _run_next():
    '''
        Roda o proximo processo que estiver aguardando na fila
    '''

    log('_run_next: Threadings ' + str(threading.enumerate()))

    proc_waiting = Proc_Request.objects.filter(proc_status='waiting'
                                                    ).order_by('created_at')[0]

    if not proc_waiting:

        log('run_next() execultado sem próximo na fila')

    else:

        context = {
        'proc_id' : proc_waiting.id,
        'email' : proc_waiting.email,
        'proc_method' : proc_waiting.proc_method,
        'endFunction' : finishing_process,
        'hoi_correction' : proc_waiting.hoi_correction,
        }

        proc_details = proc_waiting.get_proc_details()

        file_root = RINEX_UPLOAD_TEMP_DIR

        if proc_details.blq_file:
            context['blq_file'] = os.path.join(
                                                file_root,
                                                proc_details.blq_file.name
                                                )
        else:
            context['blq_file'] = ''

        if proc_waiting.proc_method == 'ppp':

            context['rinex_file'] = os.path.join(
                                        file_root,proc_details.rinex_file.name)

            context['tectonic_plate'] = proc_details.tectonic_plate

            rinex_files_names = proc_details.rinex_file.name

        elif proc_waiting.proc_method == 'relativo':

            context['rinex_base_file'] = os.path.join(
                                            file_root,
                                            proc_details.rinex_base_file.name
                                            )

            context['rinex_rover_file'] = os.path.join(
                                            file_root,
                                            proc_details.rinex_rover_file.name
                                            )
            rinex_files_names = proc_details.rinex_base_file.name + ', ' + proc_details.rinex_rover_file.name

            context['tectonic_plate_base'] = proc_details.tectonic_plate_base
            context['tectonic_plate_rover'] = proc_details.tectonic_plate_rover


            context['coord_ref'] = [
                                    proc_details.coord_ref.X,
                                    proc_details.coord_ref.Y,
                                    proc_details.coord_ref.Z
                                    ]
            context['datum'] = proc_details.coord_ref.datum

        elif proc_waiting.proc_method == 'rede':

            context['rinex_rover_file'] = os.path.join(
                                            file_root,
                                            proc_details.rinex_rover_file.name
                                            )
            rinex_files_names = proc_details.rinex_rover_file.name

            context['tectonic_plate_base'] = proc_details.tectonic_plate_base
            context['tectonic_plate_rover'] = proc_details.tectonic_plate_rover

            context['bases_rbmc'] = proc_details.bases_rbmc

        else:

            log('Em check_line(): proc_method não definido no processo n° ' +
                str(proc_waiting.id)
            )

            raise Exception('Em check_line(): proc_method não definido no '
                            'processo n° ' +  str(proc_waiting.id)
                            )


        try:

            # registra no BD o começo do Processamento
            proc_waiting.start_process()

            # Nova instancia do processamento no bernese
            newBPE = ApiBernese(**context)

            # Abre nova thread para a iniciar o processamento
            threading.Thread(name=newBPE.bpeName,target=newBPE.runBPE).start()

            log(str(proc_waiting) + ' started')

        except Exception as e:

            log('Erro em check_line ao solicitar processamento: ' + str(proc_waiting))
            log(str(e))
            e_Msg = sys.exc_info()
            log(str(e_Msg[0]))
            log(str(e_Msg[1]))

            # finish process
            finishing_process(
                status = False,
                id = proc_waiting.id,
                msg = 'Erro no processamento de ' + rinex_files_names,
                result = None,
            )

def finishing_process(**kwargs):

    log('finishing_process: Threadings ' + str(threading.enumerate()))

    status = kwargs['status']
    id = kwargs['id']
    msg = kwargs['msg']
    result = kwargs['result']
    try:
        filename = kwargs['filename']
    except:
        filename = None

    # Pegar processo pelo id
    proc = Proc_Request.objects.get(id=id)

    # finalizar processo
    proc.finish_process()

    # Enviando email
    send_result_email(proc.email,msg,result,filename)

    # Verifica se tem outro para processar
    check_line()
