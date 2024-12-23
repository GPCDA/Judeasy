//Variáveis que pegam o nome da base
var mainBaseName;	
var baseName='';

var inicio;
var fim;
var periodo;
var qtdDeProcessos;
var clicouNoOk = false;
var classificador;
var tecnicasPP = Array();
var pp_or_treinamento = "";

//Definindo a variável das etiquetas que são escolhidas pelo usuário, a ser pré-processadas
var etiquetas_escolhidas_global = [];

// Definindo a variável que vai controlar se o usuário vai seguir o passo a passo completo do framework ou vai direto para tela de validação
var stepByStep_or_validacao = "";

function voltarInicio() {
	if(stepByStep_or_validacao == "stepByStep"){
		document.getElementById("tab0").className = "tab-pane active";
		document.getElementById("tab1").className = "tab-pane fade";
		document.getElementById("aba1").className = "tab-pane";
		document.getElementById("aba0").className = "tab-pane active";
	}
}

//INICIO DA FUNÇÃO PARA VOLTAR PARA A ABA DATABASE
function voltarDatabase() {
	document.getElementById("tab1").className = "tab-pane active";
	document.getElementById("tab2").className = "tab-pane fade";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba1").className = "tab-pane active";
	pp_or_treinamento = "";
}
//FIM DA FUNÇÃO PARA VOLTAR PARA A ABA DATABASE


//INICIO DA FUNÇÃO PARA VOLTAR PARA A ABA PRÉ-PROCESSAMENTO
function voltarPP() {
	if (pp_or_treinamento == "pp") {
		document.getElementById("tab2").className = "tab-pane active";
		document.getElementById("tab3").className = "tab-pane fade";
		document.getElementById("aba3").className = "tab-pane";
		document.getElementById("aba2").className = "tab-pane active";
	} else if (pp_or_treinamento == "treinamento") {
		document.getElementById("tab1").className = "tab-pane active";
		document.getElementById("tab3").className = "tab-pane fade";
		document.getElementById("aba3").className = "tab-pane";
		document.getElementById("aba1").className = "tab-pane active";
	}
}
//FIM DA FUNÇÃO PARA VOLTAR PARA A ABA PRÉ-PROCESSAMENTO

//INICIO DA FUNÇÃO PARA VOLTAR PARA A ABA TREINAMENTO
function voltarTreinamento() {
	document.getElementById("tab3").className = "tab-pane active";
	document.getElementById("tab4").className = "tab-pane fade";
	document.getElementById("aba4").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane active";
}
//FIM DA FUNÇÃO PARA VOLTAR PARA A ABA TREINAMENTO

//INICIO DA FUNÇÃO PARA VOLTAR PARA A ABA RESULTADOS
function voltarResultados() {
	if (stepByStep_or_validacao != "validacao") {
		document.getElementById("tab4").className = "tab-pane active";
		document.getElementById("tab5").className = "tab-pane fade";
		document.getElementById("aba5").className = "tab-pane";
		document.getElementById("aba4").className = "tab-pane active";
	} else {
		document.getElementById("tab0").className = "tab-pane active";
		document.getElementById("tab5").className = "tab-pane fade";
		document.getElementById("aba5").className = "tab-pane";
		document.getElementById("aba0").className = "tab-pane active";
	}
}
//FIM DA FUNÇÃO PARA VOLTAR PARA A ABA RESULTADOS

//INICIO DA FUNÇÃO PARA VOLTAR PARA A ABA VALIDAÇÃO
function voltarValidacao() {
	document.getElementById("tab5").className = "tab-pane active";
	document.getElementById("tab6").className = "tab-pane fade";
	document.getElementById("aba6").className = "tab-pane";
	document.getElementById("aba5").className = "tab-pane active";
}
//FIM DA FUNÇÃO PARA VOLTAR PARA A ABA VALIDAÇÃO




function abrirTecnicaStopWords(){
	$("#tecnica_info_sw").modal({backdrop: 'static', show: true});
}

function abrirTecnicaRedesComplexas(){
	$("#tecnica_info_rc").modal({backdrop: 'static', show: true});
}

function abrirTecnicaRemoverPontuacao(){
	$("#tecnica_info_removPontuacao").modal({backdrop: 'static', show: true});
}

function abrirTecnicaStemming(){
	$("#tecnica_info_stem").modal({backdrop: 'static', show: true});
}

function abrirTecnicaLematizacao(){
	$("#tecnica_info_lemat").modal({backdrop: 'static', show: true});
}

function abrirTecnicaRemoverNumeros(){
	$("#tecnica_info_removNum").modal({backdrop: 'static', show: true});
}

function abrirTecnicaTokenizacao(){
	$("#tecnica_info_tok").modal({backdrop: 'static', show: true});
}


// Modal para cadastrar uma nova base
function abrirNovaBase(){
	$("#novabase_info").modal({backdrop: 'static', show: true});
}
// Modal para cadastrar uma nova base


// Filtrar os motores inferências de bases já treinadas
$(function(){
    $("#base_motor_busca").keyup(function(){       
        var index = 1;
        var nth = "#table-bases-treinadas td:nth-child("+(index+1).toString()+")";
        var valor = $(this).val().toUpperCase();
        $("#table-bases-treinadas tbody tr").show();
        $(nth).each(function(){
            if($(this).text().toUpperCase().indexOf(valor) < 0){
                $(this).parent().hide();
            }
        });
    });
 
    $("#base_motor_busca").blur(function(){
        $(this).val("");
    });
});
// Filtrar os motores inferências de bases já treinadas   

// Filtrar os motores inferências de bases já treinadas
$(function(){
    $("#classificador_motor_busca").keyup(function(){       
        var index = 3;
        var nth = "#table-bases-treinadas td:nth-child("+(index+1).toString()+")";
        var valor = $(this).val().toUpperCase();
        $("#table-bases-treinadas tbody tr").show();
        $(nth).each(function(){
            if($(this).text().toUpperCase().indexOf(valor) < 0){
                $(this).parent().hide();
            }
        });
    });
 
    $("#classificador_motor_busca").blur(function(){
        $(this).val("");
    });
});
// Filtrar os motores inferências de bases já treinadas   


// Seleciona todos os checkbox das técnicas (aba PP)
$("#checkTodos").click(function(){
    $('input:checkbox').not(this).prop('checked', this.checked);
});
// Seleciona todos os checkbox das técnicas (aba PP)

// Função para o usuário seguir o passo a passo do framework
$('#database, #aba1').click(function(){

	 $.ajax({

        url: '/database/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab1').html(data);
        }
    });

	stepByStep_or_validacao = "stepByStep"

	document.getElementById("tab0").className = "tab-pane";
    document.getElementById("tab1").className = "tab-pane active";
    document.getElementById("tab2").className = "tab-pane";
    document.getElementById("tab3").className = "tab-pane";
    document.getElementById("tab4").className = "tab-pane";
    document.getElementById("tab5").className = "tab-pane";
    document.getElementById("tab6").className = "tab-pane";

	document.getElementById("aba0").className = "tab-pane";
	document.getElementById("aba1").className = "tab-pane active";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane";
	document.getElementById("aba4").className = "tab-pane";
	document.getElementById("aba5").className = "tab-pane";
	document.getElementById("aba6").className = "tab-pane";

//    document.getElementById("tab1").className = "tab-pane active";
//	document.getElementById("tab0").className = "tab-pane fade";
//	document.getElementById("aba0").className = "tab-pane";
//	document.getElementById("aba1").className = "tab-pane active";

});

$('#aba0').click(function(){
	 $.ajax({

        url: '/index/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab0').html(data);
        }
    });

	stepByStep_or_validacao = "stepByStep"

    document.getElementById("tab0").className = "tab-pane active";
    document.getElementById("tab1").className = "tab-pane";
    document.getElementById("tab2").className = "tab-pane";
    document.getElementById("tab3").className = "tab-pane";
    document.getElementById("tab4").className = "tab-pane";
    document.getElementById("tab5").className = "tab-pane";
    document.getElementById("tab6").className = "tab-pane";

	document.getElementById("aba0").className = "tab-pane active";
	document.getElementById("aba1").className = "tab-pane";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane";
	document.getElementById("aba4").className = "tab-pane";
	document.getElementById("aba5").className = "tab-pane";
	document.getElementById("aba6").className = "tab-pane";


});

$('#aba2').click(function(){
     $.ajax({
        url: '/pp/',
        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab2').html(data);
        }
    });

    stepByStep_or_validacao = "stepByStep"

    document.getElementById("tab0").className = "tab-pane";
    document.getElementById("tab1").className = "tab-pane";
    document.getElementById("tab2").className = "tab-pane active";
    document.getElementById("tab3").className = "tab-pane";
    document.getElementById("tab4").className = "tab-pane";
    document.getElementById("tab5").className = "tab-pane";
    document.getElementById("tab6").className = "tab-pane";

    document.getElementById("aba0").className = "tab-pane";
    document.getElementById("aba1").className = "tab-pane";
    document.getElementById("aba2").className = "tab-pane active";
    document.getElementById("aba3").className = "tab-pane";
    document.getElementById("aba4").className = "tab-pane";
    document.getElementById("aba5").className = "tab-pane";
    document.getElementById("aba6").className = "tab-pane";

});

$('#aba3').click(function(){
	 $.ajax({

        url: '/treinamento/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab3').html(data);
        }
    });

	stepByStep_or_validacao = "stepByStep"

    document.getElementById("tab0").className = "tab-pane";
    document.getElementById("tab1").className = "tab-pane";
    document.getElementById("tab2").className = "tab-pane";
    document.getElementById("tab3").className = "tab-pane active";
    document.getElementById("tab4").className = "tab-pane";
    document.getElementById("tab5").className = "tab-pane";
    document.getElementById("tab6").className = "tab-pane";

	document.getElementById("aba0").className = "tab-pane";
	document.getElementById("aba1").className = "tab-pane";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane active";
	document.getElementById("aba4").className = "tab-pane";
	document.getElementById("aba5").className = "tab-pane";
	document.getElementById("aba6").className = "tab-pane";

});

$('#aba4').click(function(){
	 $.ajax({

        url: '/resultados/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab4').html(data);
        }
    });

	stepByStep_or_validacao = "stepByStep"

    document.getElementById("tab0").className = "tab-pane";
    document.getElementById("tab1").className = "tab-pane";
    document.getElementById("tab2").className = "tab-pane";
    document.getElementById("tab3").className = "tab-pane";
    document.getElementById("tab4").className = "tab-pane active";
    document.getElementById("tab5").className = "tab-pane";
    document.getElementById("tab6").className = "tab-pane";

	document.getElementById("aba0").className = "tab-pane";
	document.getElementById("aba1").className = "tab-pane";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane";
	document.getElementById("aba4").className = "tab-pane active";
	document.getElementById("aba5").className = "tab-pane";
	document.getElementById("aba6").className = "tab-pane";

});

$('#aba5').click(function(){
	 $.ajax({

        url: '/validacaoVisualizar/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab5').html(data);
        }
    });

	stepByStep_or_validacao = "stepByStep"

    document.getElementById("tab0").className = "tab-pane";
    document.getElementById("tab1").className = "tab-pane";
    document.getElementById("tab2").className = "tab-pane";
    document.getElementById("tab3").className = "tab-pane";
    document.getElementById("tab4").className = "tab-pane";
    document.getElementById("tab5").className = "tab-pane active";
    document.getElementById("tab6").className = "tab-pane";

	document.getElementById("aba0").className = "tab-pane";
	document.getElementById("aba1").className = "tab-pane";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane";
	document.getElementById("aba4").className = "tab-pane";
	document.getElementById("aba5").className = "tab-pane active";
	document.getElementById("aba6").className = "tab-pane";

});

$('#aba6').click(function(){
	 $.ajax({

        url: '/historico/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#tab6').html(data);
        }
    });

	stepByStep_or_validacao = "stepByStep"

    document.getElementById("tab0").className = "tab-pane";
    document.getElementById("tab1").className = "tab-pane";
    document.getElementById("tab2").className = "tab-pane";
    document.getElementById("tab3").className = "tab-pane";
    document.getElementById("tab4").className = "tab-pane";
    document.getElementById("tab5").className = "tab-pane";
    document.getElementById("tab6").className = "tab-pane active";

	document.getElementById("aba0").className = "tab-pane";
	document.getElementById("aba1").className = "tab-pane";
	document.getElementById("aba2").className = "tab-pane";
	document.getElementById("aba3").className = "tab-pane";
	document.getElementById("aba4").className = "tab-pane";
	document.getElementById("aba5").className = "tab-pane";
	document.getElementById("aba6").className = "tab-pane active";

});


// Modal pra escolher uma motor de uma base já treinada
$('#irDiretoValidacao').click(function(){

	$("#loading").modal({backdrop: 'static', show: true, keyboard: false});

	$.ajax({

        url: '/buscarBasesTreinadas/',

        //Incluindo o conteúdo na div
        success: function(data){
            $('#info_motores').html(data);
        }
    });

	$('#loading').fadeOut();
	$('#loading').modal('hide');
	$("#escolher_motor_validacao").modal({backdrop: 'static', show: true});

});








