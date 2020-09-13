from bernese.core.models import *

class Details_Rapido(Proc_Request):

    def save(self, *args, **kwargs):
        self.proc_method = 'rapido'
        super().save(*args, **kwargs)

    COORD_REF_CHOICES = (
        ('header_rinex', 'Cabeçalho do Rinex'),
        ('user_set','Informado pelo usuário'),
    )

    rinex_base_file = models.FileField(max_length=256)
    rinex_rover_file= models.FileField(max_length=256)
    tectonic_plate_base = models.CharField('Placa Tectonica da Estação Base', choices=TECTONIC_PLATE_CHOICES, default='SOAM', max_length=5)
    tectonic_plate_rover = models.CharField('Placa Tectonica da Estação Rover', choices=TECTONIC_PLATE_CHOICES, default='SOAM', max_length=5)
    blq_file =  models.FileField(max_length=256, null=True, blank=True)
    coord_ref_type = models.CharField('Origem das coordenadas de referência', choices=COORD_REF_CHOICES, max_length=20)
    coord_ref = models.ForeignKey('core.Coordinates', on_delete=models.PROTECT, null=True)


    class Meta:
        verbose_name = 'Detalhes do Processamento Relativo Estatico Rapido'
        verbose_name_plural = 'Detalhes dos Processamentos Relativo Estatico Rapido'
