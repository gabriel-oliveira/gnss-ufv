from django.db import models
from django.utils import timezone
from bernese.settings import RINEX_UPLOAD_TEMP_DIR


class Proc_Request(models.Model):

    METHOD_CHOICES = (
        ('ppp', 'PPP'),
        ('relativo', 'Relativo'),
    )

    STATUS_CHOICES = (
        ('waiting', 'Aguardando'),
        ('running', 'Processando'),
        ('finished', 'Finalizado'),
    )

    # proc_id = models.CharField(primary_key=True, max_length=100) # not interesting
    proc_method = models.CharField('Método do Processamento',choices = METHOD_CHOICES, max_length=10)
    proc_status = models.CharField('Status do Processamento',choices = STATUS_CHOICES,default='waiting',max_length=10)
    email = models.EmailField('E-mail')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    started_at = models.DateTimeField('Iniciado em', null=True, blank=True)
    finished_at = models.DateTimeField('Finalizado em',null=True, blank=True)
    linux_server = models.BooleanField('Solicitação do servidor linux',default=False)

    def __str__(self):
        return 'Process request id (' + str(self.id) + ')'

    def __rpr__(self):
        return 'Proc_Request id: ' + str(self.id)

    def start_process(self):
        self.proc_status = self.STATUS_CHOICES[1][0]                # 'running'
        self.started_at = timezone.localtime(timezone.now())
        self.save()

    def finish_process(self):
        self.proc_status = self.STATUS_CHOICES[2][0]                # 'finished'
        self.finished_at = timezone.localtime(timezone.now())
        self.save()

    def get_proc_details(self):
        if self.proc_method == 'ppp':
            from bernese.ppp.models import Details_PPP
            return Details_PPP.objects.get(pk=self.id)
        elif self.proc_method == 'relativo':
            from bernese.relativo.models import Details_Relativo
            return Details_Relativo.objects.get(pk=self.id)
        else:
            return None

    class Meta:
        verbose_name = 'Solicitação de Processamento'
        verbose_name_plural = 'Solicitações de Processamentos'
        ordering = ['-created_at']

#-------------------------------------------------------------------------------

TECTONIC_PLATE_CHOICES = (
    ('SOAM', 'SOAM - Sul-Americana',),
    ('AFRC', 'AFRC - Africa'),
    ('ANTA', 'ANTA - Antarctica'),
    ('ARAB', 'ARAB - Arabia'),
    ('AUST', 'AUST - Australia'),
    ('CARB', 'CARB - Caribbean'),
    ('COCO', 'COCO - Cocos (north of NAZC, south of NOAM, east of CARB)'),
    ('EURA', 'EURA - Eurasia'),
    ('INDI', 'INDI - India'),
    ('JUFU', 'JUFU - Juan de Fuca (in between northern NOAM and PCFC)'),
    ('NAZC', 'NAZC - Nazca (west of SOAM, east of PCFC)'),
    ('NOAM', 'NOAM - North America'),
    ('SOAM', 'SOAM - South America'),
    ('PCFC', 'PCFC - Pacific'),
    ('PHIL', 'PHIL - Philippine'),
)


#-------------------------------------------------------------------------------

class Coordinates(models.Model):

    X = models.FloatField()
    Y = models.FloatField()
    Z = models.FloatField()
    devX = models.FloatField()
    devY = models.FloatField()
    devZ = models.FloatField()
    epoch = models.FloatField()
    datum = models.CharField(max_length=100)
    station_name = models.CharField(max_length=100, null=True)

    def latlong(self):
        pass            # TODO: Transformar coordenada para latlong

    def UTM(self):
        pass            # TODO: Transformar coordenada para UTM (plan e alt)

    class Meta:
        verbose_name = 'Coordenada de Referência'
        verbose_name_plural = 'Coordenadas de Referência'
