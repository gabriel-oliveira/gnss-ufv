from bernese.core.models import *
from bernese.settings import LINUX_SERVER


class Details_PPP(Proc_Request):

    def save(self, *args, **kwargs):
        self.proc_method = 'ppp'
        if LINUX_SERVER: self.linux_server = True        
        super().save(*args, **kwargs)

    rinex_file = models.FileField(max_length=256)
    blq_file = models.FileField(max_length=256, null=True,blank=True)
    tectonic_plate = models.CharField(choices=TECTONIC_PLATE_CHOICES,default='SOAM', max_length=5)

    class Meta:
        verbose_name = 'Detalhes do Processamento PPP'
        verbose_name_plural = 'Detalhes dos Processamentos PPP'
