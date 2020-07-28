from bernese.core.models import *


def get_basesRBMC():
    
    query = 'SELECT * FROM rbmc'
    query_set = Proc_Request.objects.raw(query)

    stations =[]
    for field in query_set:
        stations.append((field.name,field.name))

    return tuple(stations)


class Details_Rede(Proc_Request):

    def save(self, *args, **kwargs):
        self.proc_method = 'rede'
        super().save(*args, **kwargs)

    COORD_REF_CHOICES = (
        ('header_rinex', 'Cabeçalho do Rinex'),
        ('user_set','Informado pelo usuário'),
    )

    BASE_DEFINITION = (
        ('auto', 'Automática'),
        ('manual','Manual'),
    )

    base_select_max_distance = models.IntegerField('Distânca Máxima das bases', default='200', null=True, blank=True)
    bases_rbmc_choices = models.CharField('Estações da RBMC', null=True, blank=True, max_length=1000)
    base_select_type = models.CharField('Seleção das bases', choices=BASE_DEFINITION, default='auto', max_length=10)
    rinex_rover_file= models.FileField(max_length=256)
    tectonic_plate_base = models.CharField('Placa Tectonica da Estação Base', choices=TECTONIC_PLATE_CHOICES, default='SOAM', max_length=5)
    tectonic_plate_rover = models.CharField('Placa Tectonica da Estação Rover', choices=TECTONIC_PLATE_CHOICES, default='SOAM', max_length=5)
    blq_file =  models.FileField(max_length=256, null=True, blank=True)
    coord_ref_type = models.CharField('Origem das coordenadas de referência', choices=COORD_REF_CHOICES, default='header_rinex',max_length=20)
    bases_rbmc = models.CharField('Bases da RBMC selecionadas', max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = 'Detalhes do Processamento Relativo em Rede'
        verbose_name_plural = 'Detalhes dos Processamentos Relativo em Rede'
