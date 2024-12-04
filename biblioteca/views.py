from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Partitura
from .processamento_imagem import etapa1_processamento_inicial, etapa2_selecao_e_ajuste_rois_mod, etapa3_deslocamento_e_finalizacao
import cv2
import os
import numpy as np
import base64
import json
import time
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def formulario(request):
    if request.method == "GET":
        return render(request, 'formulario_partitura.html')
    elif request.method == "POST":
        partitura = request.FILES.get('partitura')
        nome = request.POST.get('nomePartitura')
        clave = request.POST.get('clave')
        tempo = request.POST.get('tempo')

        # Salva a partitura associada ao usuário logado
        imagem1 = Partitura(
            partitura=partitura,
            nome=nome,
            clave=clave,
            tempo=tempo,
            usuario=request.user
        )
        imagem1.save()

        return redirect('perfil')

def visualizar_partitura(request, id):
    partitura = get_object_or_404(Partitura, id=id)

    if request.user.is_authenticated:
        voltar_url = 'carregarbanco_logado'  # URL para usuários logados
    else:
        voltar_url = 'carregarbanco'  # URL para usuários não logados

    return render(request, 'visualizar_partitura.html', {'partitura': partitura, 'voltar_url': voltar_url})

@login_required
def visualizar_partitura_logado(request, partitura_id):
    partitura = get_object_or_404(Partitura, id=partitura_id)
    return render(request, 'visualizar_partitura_logado.html', {'partitura': partitura})

def carregarbanco(request):
    partitura = Partitura.objects.all()
    
    clave = request.GET.get('clave')
    tempo = request.GET.get('tempo')
    query = request.GET.get('q')

    if clave and clave != '':
        partitura = partitura.filter(clave=clave)
    
    if tempo and tempo != '':
        partitura = partitura.filter(tempo=tempo)
    
    if query:
        partitura = partitura.filter(nome__icontains=query)
    
    context = {
        'partitura': partitura,  # Atualizado para 'partitura'
        'filtro_clave': clave,
        'filtro_tempo': tempo,
        'query': query
    }

    return render(request, 'biblioteca.html', context)

def carregarbanco_logado(request):
    partitura = Partitura.objects.all()
    
    clave = request.GET.get('clave')
    tempo = request.GET.get('tempo')
    query = request.GET.get('q')

    if clave and clave != '':
        partitura = partitura.filter(clave=clave)
    
    if tempo and tempo != '':
        partitura = partitura.filter(tempo=tempo)
    
    if query:
        partitura = partitura.filter(nome__icontains=query)
    
    context = {
        'partitura': partitura,  # Atualizado para 'partitura'
        'filtro_clave': clave,
        'filtro_tempo': tempo,
        'query': query
    }

    return render(request, 'biblioteca_logado.html', context)

def excluir_partitura(request, partitura_id):
    partitura = get_object_or_404(Partitura, pk=partitura_id)
    if request.method == 'POST':
        partitura.delete()
        return redirect('carregarbanco')  # Redireciona para a página principal após excluir
    return render(request, 'excluir_partitura.html', {'partitura': partitura})

def processar_partitura(request):
    if request.method == "POST":
        imagem_id = request.POST.get("imagem_id")
        mudar_tom = int(request.POST.get("mudanca_tom", 0))

        partitura = get_object_or_404(Partitura, id=imagem_id)
        caminho_imagem = os.path.join(settings.MEDIA_ROOT, partitura.partitura.name)

        imagem_original = cv2.imread(caminho_imagem)
        if imagem_original is None:
            return render(request, 'erro.html', {'mensagem': 'Erro ao carregar a imagem.'})

        # Etapa 1: Processamento inicial
        notas_pintadas, pautas_dict, num_pautas, linhas_pretas, binario = etapa1_processamento_inicial(imagem_original, mudar_tom)

        # Salvar o ID da imagem e dados de processamento na sessão
        request.session['imagem_id'] = imagem_id
        request.session['mudar_tom'] = mudar_tom
        request.session['pautas_dict'] = pautas_dict
        request.session['num_pautas'] = num_pautas
        request.session['linhas_pretas'] = linhas_pretas

        # Codificar imagem binária em Base64 para armazenar na sessão
        _, buffer = cv2.imencode('.png', binario)
        binario_base64 = base64.b64encode(buffer).decode('utf-8')
        request.session['binario'] = binario_base64

        # Converte notas_pintadas para Base64 para salvar na sessão
        _, buffer = cv2.imencode('.png', notas_pintadas)
        notas_pintadas_base64 = base64.b64encode(buffer).decode('utf-8')
        request.session['notas_pintadas'] = notas_pintadas_base64  # Armazena na sessão

        return redirect('selecionar_notas')

    return render(request, "visualizar_partitura.html")

@login_required
def processar_partitura_logado(request):
    if request.method == "POST":
        imagem_id = request.POST.get("imagem_id")
        mudar_tom = int(request.POST.get("mudanca_tom", 0))

        partitura = get_object_or_404(Partitura, id=imagem_id)
        caminho_imagem = os.path.join(settings.MEDIA_ROOT, partitura.partitura.name)

        imagem_original = cv2.imread(caminho_imagem)
        if imagem_original is None:
            return render(request, 'erro.html', {'mensagem': 'Erro ao carregar a imagem.'})

        # Etapa 1: Processamento inicial
        notas_pintadas, pautas_dict, num_pautas, linhas_pretas, binario = etapa1_processamento_inicial(imagem_original, mudar_tom)

        # Salvar o ID da imagem e dados de processamento na sessão
        request.session['imagem_id'] = imagem_id
        request.session['mudar_tom'] = mudar_tom
        request.session['pautas_dict'] = pautas_dict
        request.session['num_pautas'] = num_pautas
        request.session['linhas_pretas'] = linhas_pretas

        # Codificar imagem binária em Base64 para armazenar na sessão
        _, buffer = cv2.imencode('.png', binario)
        binario_base64 = base64.b64encode(buffer).decode('utf-8')
        request.session['binario'] = binario_base64

        # Converte notas_pintadas para Base64 para salvar na sessão
        _, buffer = cv2.imencode('.png', notas_pintadas)
        notas_pintadas_base64 = base64.b64encode(buffer).decode('utf-8')
        request.session['notas_pintadas'] = notas_pintadas_base64  # Armazena na sessão

        return redirect('selecionar_notas_logado')

    return render(request, "visualizar_partitura_logado.html")


def selecionar_notas(request):
    # Recupera a imagem `notas_pintadas` em base64 e converte para `np.array`
    notas_pintadas_base64 = request.session.get('notas_pintadas')

    if request.method == 'POST':
        # Obtém as coordenadas dos ROIs a partir do formulário
        rois_data = request.POST.get('rois')
        if rois_data:
            rois = json.loads(rois_data)  # Converte de JSON para lista de dicionários
            # Armazena os ROIs na sessão para usar na próxima função
            request.session['rois'] = rois

            # Redireciona para a página de loading
            return redirect('loading')

    # Exibe a imagem para seleção das notas na página inicial (GET)
    imagem_url = f"data:image/png;base64,{notas_pintadas_base64}"
    return render(request, 'selecionar_notas.html', {'imagem_url': imagem_url})

@login_required
def selecionar_notas_logado(request):
    # Recupera a imagem `notas_pintadas` em base64 e converte para `np.array`
    notas_pintadas_base64 = request.session.get('notas_pintadas')

    if request.method == 'POST':
        # Obtém as coordenadas dos ROIs a partir do formulário
        rois_data = request.POST.get('rois')
        if rois_data:
            rois = json.loads(rois_data)  # Converte de JSON para lista de dicionários
            # Armazena os ROIs na sessão para usar na próxima função
            request.session['rois'] = rois

            # Redireciona para a página de loading
            return redirect('loading_logado')

    # Exibe a imagem para seleção das notas na página inicial (GET)
    imagem_url = f"data:image/png;base64,{notas_pintadas_base64}"
    return render(request, 'selecionar_notas_logado.html', {'imagem_url': imagem_url})

def visualizar_imagem_rois(request):
    imagem_modificada_base64 = request.session.get('imagem_modificada')
    imagem_branca_base64 = request.session.get('imagem_branca')

    imagem_url = f"data:image/png;base64,{imagem_branca_base64}"
    return render(request, 'mostrar_imagem_rois.html', {'imagem_url': imagem_url})

def visualizar_rois(request):
    rois = []
    if request.method == 'POST':
        rois_json = request.POST.get('rois')
        if rois_json:
            import json
            rois = json.loads(rois_json)  # Carrega os ROIs como uma lista de dicionários
    
    return render(request, 'visualizar_rois.html', {'rois': rois})

def partitura_final(request):
    
    # Recupera variáveis da sessão
    mudar_tom = request.session.get('mudar_tom')
    num_pautas = request.session.get('num_pautas')
    linhas_pretas = request.session.get('linhas_pretas')
    imagem_id = request.session.get('imagem_id')

    partitura = get_object_or_404(Partitura, id=imagem_id)
    caminho_imagem = os.path.join(settings.MEDIA_ROOT, partitura.partitura.name)
    partitura_original = cv2.imread(caminho_imagem)
    
    # Recupera a imagem `imagem_branca` (nova_imagem) e `binario`
    imagem_branca_base64 = request.session.get('imagem_branca')
    imagem_modificada_base64 = request.session.get('imagem_modificada')

    if not imagem_branca_base64 or not imagem_modificada_base64:
        return render(request, 'erro.html', {'mensagem': 'Erro: Imagem não encontrada na sessão.'})
    
    # Decodifica as imagens de base64 para `np.array`
    imagem_branca = cv2.imdecode(np.frombuffer(base64.b64decode(imagem_branca_base64), np.uint8), cv2.IMREAD_COLOR)
    imagem_modficada = cv2.imdecode(np.frombuffer(base64.b64decode(imagem_modificada_base64), np.uint8), cv2.IMREAD_GRAYSCALE)

    # Aplica a etapa 3 de processamento final na imagem
    partitura_completa, imagem_movida = etapa3_deslocamento_e_finalizacao(imagem_branca, mudar_tom, imagem_modficada, linhas_pretas, num_pautas)

    # Converte `partitura_completa` para base64 para exibir na página
    _, buffer = cv2.imencode('.png', partitura_completa)
    partitura_completa_base64 = base64.b64encode(buffer).decode('utf-8')

    _, buffer = cv2.imencode('.png', partitura_original)
    partitura_original_base64 = base64.b64encode(buffer).decode('utf-8')

    # Renderiza a partitura completa em uma nova página HTML
    return render(request, 'partitura_final.html', {
        'imagem_url': f"data:image/png;base64,{partitura_completa_base64}",
        'imagem_original_url': f"data:image/png;base64,{partitura_original_base64}",
        'imagem_id': imagem_id
    })

@login_required
def partitura_final_logado(request):
    
    # Recupera variáveis da sessão
    mudar_tom = request.session.get('mudar_tom')
    num_pautas = request.session.get('num_pautas')
    linhas_pretas = request.session.get('linhas_pretas')
    imagem_id = request.session.get('imagem_id')

    partitura = get_object_or_404(Partitura, id=imagem_id)
    caminho_imagem = os.path.join(settings.MEDIA_ROOT, partitura.partitura.name)
    partitura_original = cv2.imread(caminho_imagem)
    
    # Recupera a imagem `imagem_branca` (nova_imagem) e `binario`
    imagem_branca_base64 = request.session.get('imagem_branca')
    imagem_modificada_base64 = request.session.get('imagem_modificada')

    if not imagem_branca_base64 or not imagem_modificada_base64:
        return render(request, 'erro.html', {'mensagem': 'Erro: Imagem não encontrada na sessão.'})
    
    # Decodifica as imagens de base64 para `np.array`
    imagem_branca = cv2.imdecode(np.frombuffer(base64.b64decode(imagem_branca_base64), np.uint8), cv2.IMREAD_COLOR)
    imagem_modficada = cv2.imdecode(np.frombuffer(base64.b64decode(imagem_modificada_base64), np.uint8), cv2.IMREAD_GRAYSCALE)

    # Aplica a etapa 3 de processamento final na imagem
    partitura_completa, imagem_movida = etapa3_deslocamento_e_finalizacao(imagem_branca, mudar_tom, imagem_modficada, linhas_pretas, num_pautas)

    # Converte `partitura_completa` para base64 para exibir na página
    _, buffer = cv2.imencode('.png', partitura_completa)
    partitura_completa_base64 = base64.b64encode(buffer).decode('utf-8')

    _, buffer = cv2.imencode('.png', partitura_original)
    partitura_original_base64 = base64.b64encode(buffer).decode('utf-8')

    # Renderiza a partitura completa em uma nova página HTML
    return render(request, 'partitura_final_logado.html', {
        'imagem_url': f"data:image/png;base64,{partitura_completa_base64}",
        'imagem_original_url': f"data:image/png;base64,{partitura_original_base64}",
        'imagem_id': imagem_id
    })

def loading_page(request):
    # Carrega os ROIs da sessão
    rois = request.session.get('rois')
    if rois:

        binario_base64 = request.session.get('binario')
        notas_pintadas_base64 = request.session.get('notas_pintadas')

        # Decodifica as imagens binário e notas pintadas
        binario = cv2.imdecode(np.frombuffer(base64.b64decode(binario_base64), np.uint8), cv2.IMREAD_GRAYSCALE)
        notas_pintadas = cv2.imdecode(np.frombuffer(base64.b64decode(notas_pintadas_base64), np.uint8), cv2.IMREAD_COLOR)

        # Formata os ROIs como listas de [x, y, w, h]
        rois_formatados = [[roi['x'], roi['y'], roi['width'], roi['height']] for roi in rois]

        # Cria uma imagem branca com as mesmas dimensões de `notas_pintadas`
        imagem_branca = np.ones_like(notas_pintadas) * 255

        # Copia os ROIs de `notas_pintadas` para `imagem_branca`
        for roi in rois_formatados:
            x, y, w, h = map(int, roi)  # Converte x, y, w, e h para inteiros
            imagem_branca[y:y + h, x:x + w] = notas_pintadas[y:y + h, x:x + w]

        imagem_modificada = etapa2_selecao_e_ajuste_rois_mod(binario, imagem_branca)

        # Converte a imagem branca com os ROIs para base64
        _, buffer = cv2.imencode('.png', imagem_modificada)
        imagem_modificada_base64 = base64.b64encode(buffer).decode('utf-8')

        _, buffer = cv2.imencode('.png', imagem_branca)
        imagem_branca_base64 = base64.b64encode(buffer).decode('utf-8')

        # Armazena a imagem com os ROIs na sessão e redireciona para a página de visualização
        request.session['imagem_modificada'] = imagem_modificada_base64
        request.session['imagem_branca'] = imagem_branca_base64

        # Após o processamento, redireciona para a página de resultado final
        return redirect('partitura_final')

    # Renderiza a página de loading (caso necessário)
    return render(request, 'loading.html')

def loading(request):
    return render(request, 'loading.html')

@login_required
def loading_logado(request):
    return render(request, 'loading_logado.html')

def processar_rois(request):
    # Verifica se a solicitação é AJAX usando o cabeçalho
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Carrega os ROIs e as imagens da sessão
        rois = request.session.get('rois')
        binario_base64 = request.session.get('binario')
        notas_pintadas_base64 = request.session.get('notas_pintadas')

        time.sleep(5)

        # Decodifica as imagens binário e notas pintadas
        binario = cv2.imdecode(np.frombuffer(base64.b64decode(binario_base64), np.uint8), cv2.IMREAD_GRAYSCALE)
        notas_pintadas = cv2.imdecode(np.frombuffer(base64.b64decode(notas_pintadas_base64), np.uint8), cv2.IMREAD_COLOR)

        if rois:
            # Formata os ROIs e cria a imagem branca com os ROIs copiados
            rois_formatados = [[roi['x'], roi['y'], roi['width'], roi['height']] for roi in rois]
            imagem_branca = np.ones_like(notas_pintadas) * 255
            for roi in rois_formatados:
                x, y, w, h = map(int, roi)
                imagem_branca[y:y + h, x:x + w] = notas_pintadas[y:y + h, x:x + w]

            # Processa a imagem
            imagem_modificada = etapa2_selecao_e_ajuste_rois_mod(binario, imagem_branca)

            # Converte a imagem para base64 e salva na sessão
            _, buffer = cv2.imencode('.png', imagem_modificada)
            imagem_modificada_base64 = base64.b64encode(buffer).decode('utf-8')
            _, buffer = cv2.imencode('.png', imagem_branca)
            imagem_branca_base64 = base64.b64encode(buffer).decode('utf-8')

            request.session['imagem_modificada'] = imagem_modificada_base64
            request.session['imagem_branca'] = imagem_branca_base64

            # Retorna uma resposta de sucesso
            return JsonResponse({"status": "success"})

    # Caso contrário, retorna um erro
    return JsonResponse({"status": "error"}, status=400)