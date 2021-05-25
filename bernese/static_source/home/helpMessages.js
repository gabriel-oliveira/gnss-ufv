var helpMessages = {

    rinex_file: "<p>Arquivo com observações GNSS no formato RINEX (<i>Receiver INdependent Exchange</i>)</p>\
    <p>É esperado arquivos com mais de duas horas de rastreio. </p> \
    <p>São aceitos arquivos no formato RINEX 3.x, 2.x e Hatanaka. Nas seguintes extensões: yyO, yyD, \
OBS, RNX, CRX. (yy = dois últimos dígitos do ano). </p> \
    <p>Vários arquivos podem ser enviados em uma pasta compactada no formato ZIP. Para cada arquivo será \
aberta uma nova solicitação de processamento. </p>",
    
    rinex_base_file_rlt_sgl: "<p>Arquivo com observações GNSS no formato RINEX (<i>Receiver INdependent \
Exchange</i>) da estação de referência (BASE) com coordenadas conhecidas. Estas coordenadas servirão de \
referência para determinar as coordenadas da estação ROVER.</p>\
    <p>São aceitos arquivos no formato RINEX 3.x, 2.x e Hatanaka. Nas seguintes extensões: yyO, yyD, \
OBS, RNX, CRX. (yy = dois últimos dígitos do ano)</p>\
    <p>Para este modo é esperado arquivos com mais de duas horas de rastreio.</p>\
    <p> Arquivos com menos de duas horas que retornarem com erro do processamento, é aconselhado que \
sejam processados no modo estático rápido.</p>",
    
    rinex_base_file_rlt_rap: "<p>Arquivo com observações GNSS no formato RINEX (<i>Receiver INdependent \
Exchange</i>) da estação de referência (BASE) com coordenadas conhecidas. Estas coordenadas servirão de \
referência para determinar as coordenadas da estação ROVER.</p><p>São aceitos arquivos no formato \
RINEX 3.x, 2.x e Hatanaka. Nas seguintes extensões: yyO, yyD, OBS, RNX, CRX. (yy = dois últimos dígitos \
do ano)</p>\
    <p>Para este modo é esperado arquivos de curta duração que não tiveram sucesso no processamento do \
modo Linha de Base Única.</p>",
    
    rinex_rover_file_rlt_sgl: "<p>Arquivo com observações GNSS no formato RINEX (<i>Receiver INdependent \
Exchange</i>) da estação com coordenadas a serem determinadas.</p>\
    <p>São aceitos arquivos no formato RINEX 3.x, 2.x e Hatanaka. Nas seguintes extensões: yyO, yyD, \
OBS, RNX, CRX. (yy = dois últimos dígitos do ano)</p>\
    <p>Para este modo é esperado arquivos com mais de duas horas de rastreio.</p>\
    <p> Arquivos com menos de duas horas que retornarem com erro do processamento, é aconselhado que \
sejam processados no modo estático rápido.</p>",
    
    rinex_rover_file_rlt_rede: "<p>Arquivo com observações GNSS no formato RINEX (<i>Receiver INdependent \
Exchange</i>) da estação com coordenadas a serem determinadas.</p>\
    <p>São aceitos arquivos no formato RINEX 3.x, 2.x e Hatanaka. Nas seguintes extensões: yyO, yyD, \
OBS, RNX, CRX. (yy = dois últimos dígitos do ano)</p>\
    <p>Vários arquivos podem ser enviados em uma pasta compactada no formato ZIP. Para cada arquivo será \
aberta uma nova solicitação de processamento. </p>",
    
    rinex_rover_file_rlt_rap: "<p>Arquivo com observações GNSS no formato RINEX (<i>Receiver INdependent \
Exchange</i>) da estação com coordenadas a serem determinadas.</p>\
    <p>São aceitos arquivos no formato RINEX 3.x, 2.x e Hatanaka. Nas seguintes extensões: yyO, yyD, \
OBS, RNX, CRX. (yy = dois últimos dígitos do ano)</p>\
    <p>Para este modo é esperado arquivos de curta duração que não tiveram sucesso no processamento do \
modo Linha de Base Única.</p>",

    hoi_correction: "<p>Selecione este campo para indicar se quer que seja feita a correção do efeito ionosférico de ordem superior (2ª e 3ª ordens). As correções são feitas utilizando o modelo global da ionosfera fornecido pelo CODE.</p>",

    blq_file: '<p>O efeito da carga oceânica (<i>Ocean Tide Loading</i>) é causado pelo deslocamento da crosta \
terrestre devido a movimentação de massa provocada pelas cargas oceânicas. </p><p>O arquivo no formato \
BLQ deverá conter os coeficientes específicos para as estações com os dados submetidos nos arquivos \
RINEX. A identificação dos coeficientes de cada estação é feita pelo nome que é composto do MARKER \
NAME e MARKER NUMBER do cabeçalho do arquivo RINEX.</p><p>Este arquivo BLQ pode ser gerado em \
<a href="http://holt.oso.chalmers.se/loading/#select" target="_blank">http://holt.oso.chalmers.se/loading/</a>. \
Sugere-se o uso do modelo FES2004.</p><p>O cabeçalho do arquivo BLQ deverá conter os coeficientes do \
centro de massa (CMC) conforme o cabeçalho deste arquivo de exemplo \
<a href="/static/exemplo.blq" target="_blank">http://gnss.ufv.br/static/exemplo.blq</a>.</p>',

    tectonic_plate: '<p>Placa tectônica que a estação se encontra conforme figura abaixo.</p><img src="/static/home/tectonic_plate.png" class="img-responsive" alt="Placas Tectônicas">',
    tectonic_plate_base: '<p>Placa tectônica que a estação se encontra conforme figura abaixo.</p><img src="/static/home/tectonic_plate.png" class="img-responsive" alt="Placas Tectônicas">',
    tectonic_plate_rover: '<p>Placa tectônica que a estação se encontra conforme figura abaixo.</p><img src="/static/home/tectonic_plate.png" class="img-responsive" alt="Placas Tectônicas">',
    
    coord_ref_type: "<p>Coordenadas cartesianas X, Y, e Z da estação BASE que servirão de referência \
para determinar as coordenadas da estação ROVER.</p>",

    coord_ref_type_header_rinex: "<p>Selecionado este campo, se utilizará as coordenadas presentes no \
cabeçalho do arquivo RINEX no campo APPROX POSITION XYZ.</p>",

    coord_ref_type_user_set: "<p>Selecionado este campo será habilitado o campo para inserção \
das coordenadas manualmente no final da página.</p>",

    base_select_max_distance: "<p>Raio máximo para definir a área de busca caso seja selecionado \
o modo automático para seleção das estações de referência.</p>",

    bases_rbmc_choices: "<p>Estações para servir de referência no processamento caso seja selecionado \
o modo manual de seleção das estações de referência.</p>\
    <p>Uma busca de arquivos de observações é feita no servidor FTP do IBGE para o dia de rastreio do arquivo ROVER.</p>",
    
    base_select_type: "<p>Defina a forma como as estações de referência serão selecionadas para o processamento.</p>",

    base_select_type_auto: "<p>Neste modo é feita uma busca no servidor FTP do IBGE para localizar \
arquivos de observações para as estações da rede RBMC contidas dentro da área definida no raio indicado \
no campo “Raio máximo” e no dia de rastreio do arquivo ROVER.</p>",

    base_select_type_manual: "<p>Neste modo deverão ser informadas as estações a serem utilizadas como \
referência no campo “Seleção das estações RBMC”.</p>\
    <p>Uma busca de arquivos de observações é feita no servidor FTP do IBGE para o dia de rastreio do arquivo ROVER.</p>",

    datum: "<p>Sistemas de referência geocêntricos que será atribuído as coordenadas de referência \
apresentadas. Consequentemente, será o sistema de referência das coordenadas estimadas.</p>",

    epoch: "<p>Época que será atribuído as coordenadas de referência apresentadas. Consequentemente, \
será á época das coordenadas estimadas.</p>\
    <p>Época no formato ano decimal. Exemplo 2000.4 = 25/05/2000</p>",

}

$('#helpModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var helptitle = button.data('helptitle');
    var modal = $(this);
    modal.find('.modal-title').text(helptitle);
    var helpid = button.data('helpid');

    var rltForm = $('#rltForm');
    var redeForm = $('#redeForm');
    var rapForm = $('#rapForm');
    var suffix = '';

    if(typeof rltForm[0] !== "undefined"){
        suffix = '_rlt_sgl';
    } else if (typeof redeForm[0] !== "undefined"){
        suffix = '_rlt_rede';
    } else if (typeof rapForm[0] !== "undefined"){
        suffix = '_rlt_rap';
    }

    if(helpid == 'rinex_base_file' || helpid == 'rinex_rover_file'){ 
        helpid += suffix;
    }
    document.getElementById('modal-message').innerHTML = helpMessages[helpid];
});

$('#helpCollapse').on('show.bs.collapse', function () {
document.getElementById('helpCollapse-btn').innerHTML = 'Fechar'
});

$('#helpCollapse').on('hidden.bs.collapse', function () {
document.getElementById('helpCollapse-btn').innerHTML = 'Descrição'
});
