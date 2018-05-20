'''
Processos necessário para gerenciar a fila de processamento do Bernese.
'''

from bernese.settings import MAX_PROCESSING_TIME, MEDIA_ROOT, DEBUG
from bernese.core.mail import send_result_email
from bernese.core.models import Proc_Request
from bernese.core.apiBernese import ApiBernese
from bernese.core.log import log
from django.utils import timezone
import threading
import sys
import os

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

        if procs_waiting:
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
                log('ERROR!!! check_line(): Tempo máximo de processamento excedido')
                proc.finish_process() ## TODO: chamar finishing_process

                # _run_next()

            # TODO: matar o processamento atual do bernese
            #       finalizar processo atual com erro
            #       chamar um novo processo


def _run_next():
    '''
        Roda o proximo processo que estiver aguardando na fila
    '''

    log('_run_next: Threadings ' + str(threading.enumerate()))

    proc_waiting = Proc_Request.objects.filter(proc_status='waiting'
                                                    ).order_by('created_at')[0]

    if DEBUG: print('_run_next(): ' + str(proc_waiting))

    if not proc_waiting:

        log('run_next() execultado sem próximo na fila')

    else:

        context = {
        'proc_id' : proc_waiting.id,
        'email' : proc_waiting.email,
        'proc_method' : proc_waiting.proc_method,
        'endFunction' : finishing_process,
        }

        proc_details = proc_waiting.get_proc_details()

        if proc_details.blq_file:
            context['blq_file'] = os.path.join(
                                                MEDIA_ROOT,
                                                proc_details.blq_file.name
                                                )
        else:
            context['blq_file'] = ''

        if proc_waiting.proc_method == 'ppp':

            context['rinex_file'] = os.path.join(
                                        MEDIA_ROOT,proc_details.rinex_file.name)

            context['tectonic_plate'] = proc_details.tectonic_plate


        elif proc_waiting.proc_method == 'relativo':

            context['rinex_base_file'] = os.path.join(
                                            MEDIA_ROOT,
                                            proc_details.rinex_base_file.name
                                            )

            context['rinex_rover_file'] = os.path.join(
                                            MEDIA_ROOT,
                                            proc_details.rinex_rover_file.name
                                            )

            context['tectonic_plate_base'] = proc_details.tectonic_plate_base
            context['tectonic_plate_rover'] = proc_details.tectonic_plate_rover


            context['coord_ref'] = [
                                    proc_details.coord_ref.X,
                                    proc_details.coord_ref.Y,
                                    proc_details.coord_ref.Z
                                    ]

        else:

            log('Em check_line(): proc_method não definido no processo n° ' +
                str(proc_waiting.id)
            )

            raise Exception('Em check_line(): proc_method não definido no '
                            'processo n° ' +  str(proc_waiting.id)
                            )


        try:

            # Nova instancia do processamento no bernese
            newBPE = ApiBernese(**context)

            # Abre nova thread para a iniciar o processamento
            threading.Thread(name=newBPE.bpeName,target=newBPE.runBPE).start()

            # registra no BD o começo do Processamento
            proc_waiting.start_process()

            if DEBUG: print(str(proc_waiting) + ' started')

        except Exception as e:

            log('Erro ao solicitar processamento: ' + str(proc_waiting))
            e_Msg = sys.exc_info()
            log(str(e_Msg[0]))
            log(str(e_Msg[1]))

def finishing_process(**kwargs):

    log('finishing_process: Threadings ' + str(threading.enumerate()))

    status = kwargs['status']
    id = kwargs['id']
    msg = kwargs['msg']
    result = kwargs['result']

    # Pegar processo pelo id
    proc = Proc_Request.objects.get(id=id)

    # finalizar processo
    proc.finish_process()

    # Enviando email
    send_result_email(proc.email,msg,result)

    # Verifica se tem outro para processar
    check_line()

    # TODO: Se o BPE der erro copiar os arquivos para uma pasta temp


#  PPP
# headers = [header]
# pathTempFiles = [pathTempFile]
# pathBlqTempFiles = []
# if b: pathBlqTempFiles = [pathBlqTempFile]

#  Relativo
# headers = [b_header,r_header]
# pathTempFiles = [b_pathTempFile,r_pathTempFile]
# pathBlqTempFiles = []
# if b: pathBlqTempFiles = [pathBlqTempFile]
