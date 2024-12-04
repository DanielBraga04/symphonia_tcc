import cv2
import os
import random
import numpy as np
from .discriminador import Discriminador
from tcc_symphonia.settings import BASE_DIR

# Variáveis globais para armazenar ROIs, a distancia entre as linhas da pauta e a quantidade de pixels onde irá servir para a ordem aleatoria dos pixels para o treinamento
rois = []
cropping = False
maior_diferenca_y = 0
qntPixels = 0

def binarize_image(image):
    # Converter a imagem para escala de cinza
    gray_im_cropped = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Binarizar a imagem (pixels brancos tornam-se 1, pixels pretos tornam-se 0)
    binary_array = np.where(gray_im_cropped > 128, 1, 0)

    # Converter o array binário de volta para uma imagem
    reconstructed_image = np.zeros_like(gray_im_cropped, dtype=np.uint8)
    reconstructed_image[binary_array == 1] = 255

    return reconstructed_image

def encontrar_linhas_pretas(imagem_binaria, imagem_original, largura_minima=600, altura_maxima_pixels_brancos=35):
    global maior_diferenca_y
    # Dimensões da imagem
    altura, largura = imagem_binaria.shape

    # Lista para armazenar as linhas pretas encontradas
    linhas_pretas = []

    # Percorre a imagem
    for y in range(altura):
        x = 0
        while x < largura:
            # Se o pixel for preto
            if imagem_binaria[y, x] == 0:
                # Inicia a contagem
                contador = 1
                inicio_x = x
                x += 1
                # Percorre o eixo X
                while x < largura and imagem_binaria[y, x] == 0:
                    contador += 1
                    x += 1
                # Se a largura da linha preta for maior ou igual à largura mínima
                if contador >= largura_minima:
                    # Adiciona a linha preta à lista com as coordenadas
                    linhas_pretas.append((y, inicio_x, x-1))
                    break
            else:
                x += 1

    # Verifica se há diferença de altura de apenas um pixel entre as linhas pretas
    i = 0
    numeracao = 0
    pautas = []
    while i < len(linhas_pretas) - 1:
        numeracao += 1
        if linhas_pretas[i + 1][0] - linhas_pretas[i][0] == 1:
            # Linha contínua encontrada
            pauta = (linhas_pretas[i], linhas_pretas[i + 1])
            pautas.append(pauta)
            print(f"{numeracao}° Linha encontrada entre Y={linhas_pretas[i][0]} e Y={linhas_pretas[i + 1][0]}")
            print(f"Y={linhas_pretas[i][0]}, Início da linha em X={linhas_pretas[i][1]} e final em X={linhas_pretas[i][2]}")
            print(f"Y={linhas_pretas[i + 1][0]}, Início da linha em X={linhas_pretas[i + 1][1]} e final em X={linhas_pretas[i + 1][2]}")
            print("")
            i += 2
        else:
            # Linha única encontrada
            pauta = (linhas_pretas[i],)
            pautas.append(pauta)
            print(f"{numeracao}° Linha única encontrada em Y={linhas_pretas[i][0]}, de X={linhas_pretas[i][1]} a {linhas_pretas[i][2]}")
            print("")
            i += 1

    if i == len(linhas_pretas) - 1:
        pauta = (linhas_pretas[i],)
        pautas.append(pauta)
        print(f"{numeracao + 1}° Linha única encontrada em Y={linhas_pretas[i][0]}, de X={linhas_pretas[i][1]} a {linhas_pretas[i][2]}")
        print("")

    print("## ESPAÇAMENTO ENTRE AS LINHAS ##")
    # Agrupar as linhas em grupos de 5 e calcular a diferença entre os eixos Y
    for i in range(0, len(linhas_pretas) - 1, 5):
        for j in range(i, min(i + 5, len(linhas_pretas))):
            # Se for a primeira linha do grupo
            if j == i:
                continue
            y1, _, _ = linhas_pretas[j - 1]
            y2, _, _ = linhas_pretas[j]
            # Pegar o eixo Y maior para a primeira linha do grupo e o menor para as demais
            if j == i + 1:
                y1, y2 = max(y1, y2), min(y1, y2)
            # Calcular a diferença entre os eixos Y
            diferenca_y = abs(y2 - y1)
            if diferenca_y != 1 and diferenca_y < 50:
                print(f"Espaçamento entre Y={y1} e Y={y2}: {diferenca_y - 1} pixels brancos")
                print("")

                if diferenca_y > maior_diferenca_y:
                    maior_diferenca_y = diferenca_y

    print(f"Maior espaçamento global: {maior_diferenca_y-1}")

    # Dividir linhas em pautas
    total_linhas = len(pautas)
    numero_de_pautas = total_linhas // 5

    pautas_dict = {}
    for i in range(numero_de_pautas):
        pautas_dict[f"Pauta {i+1}"] = pautas[i*5:(i+1)*5]

    for nome_pauta, linhas in pautas_dict.items():
        print(f"{nome_pauta}: {linhas}")

        # Verificar intervalos entre as linhas pretas para encontrar pixels brancos e pintar pixels pretos de azul
        for i in range(len(linhas_pretas) - 1):
            y1 = linhas_pretas[i][0]
            y2 = linhas_pretas[i + 1][0]
            x_inicial = linhas_pretas[i][1]
            x_final = linhas_pretas[i][2]

            if y2 - y1 > 1 and y2 - y1 <= altura_maxima_pixels_brancos:
                for y in range(y1 + 1, y2):
                    for x in range(x_inicial, x_final + 1):
                        if imagem_binaria[y, x] == 0:
                            imagem_original[y, x] = [255, 0, 0]  # Pintar o pixel preto de azul (em BGR)

    return pautas_dict, numero_de_pautas, linhas_pretas

def pintar_pixels_acima_primeira_linha(imagem_binaria, imagem_original, pautas_dict):
    for nome_pauta, linhas in pautas_dict.items():
        primeira_linha = linhas[0][0]  # Pegar a primeira linha da pauta
        y_atual = primeira_linha[0] - 1  # Posição acima da primeira linha
        x_inicial = primeira_linha[1]
        x_final = primeira_linha[2]

        while y_atual >= 0:
            pixel_pintado = False
            for x in range(x_inicial, x_final + 1):
                if imagem_binaria[y_atual, x] == 0:  # Pixel preto encontrado
                    imagem_original[y_atual, x] = [255, 0, 0]  # Pinta o pixel de vermelho (em BGR)
                    pixel_pintado = True
            if not pixel_pintado:
                break  # Para se não houver mais pixels pretos na linha atual
            y_atual -= 1

    return imagem_original

def pintar_pixels_abaixo_ultima_linha(imagem_binaria, imagem_original, pautas_dict):
    for nome_pauta, linhas in pautas_dict.items():
        ultima_linha = linhas[-1][-1]  # Pegar a última linha da pauta
        #print(linhas[-1][-1])
        y_atual = ultima_linha[0] + 1  # Posição abaixo da última linha
        x_inicial = ultima_linha[1]
        x_final = ultima_linha[2]

        while y_atual < imagem_binaria.shape[0]:
            pixel_pintado = False
            for x in range(x_inicial, x_final + 1):
                if imagem_binaria[y_atual, x] == 0:  # Pixel preto encontrado
                    imagem_original[y_atual, x] = [255, 0, 0]  # Pinta o pixel de vermelho (em BGR)
                    pixel_pintado = True
            if not pixel_pintado:
                break  # Para se não houver mais pixels pretos na linha atual
            y_atual += 1

    return imagem_original

def extrair_partes_azuis(imagem):
    # Cria uma nova imagem em branco com as mesmas dimensões da imagem original
    nova_imagem = np.ones_like(imagem) * 255  # Inicializa como branco

    # Percorre a imagem para encontrar os pixels azuis
    for y in range(imagem.shape[0]):
        for x in range(imagem.shape[1]):
            # Verifica se o pixel está pintado de azul (em BGR, azul é [255, 0, 0])
            if np.array_equal(imagem[y, x], [255, 0, 0]):
                nova_imagem[y, x] = imagem[y, x]  # Copia o pixel azul para a nova imagem

    return nova_imagem


# Função de callback do mouse para capturar os ROIs
def mouse_crop(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end, cropping, current_image

    # Inicia a seleção do ROI
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        cropping = True

    # Atualiza o ROI enquanto o botão esquerdo está pressionado
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping:
            x_end, y_end = x, y
            current_image_copy = current_image.copy()
            cv2.rectangle(current_image_copy, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
            for roi in rois:
                cv2.rectangle(current_image_copy, (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]), (255, 0, 0), 2)
            cv2.imshow("Selecione as Notas", current_image_copy)

    # Finaliza a seleção do ROI ao soltar o botão
    elif event == cv2.EVENT_LBUTTONUP:
        x_end, y_end = x, y
        cropping = False
        # Armazena o ROI (x, y, largura, altura)
        rois.append((x_start, y_start, x_end - x_start, y_end - y_start))
        # Desenha todos os ROIs selecionados até o momento
        for roi in rois:
            cv2.rectangle(current_image, (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]), (255, 0, 0), 2)
        cv2.imshow("Selecione as Notas", current_image)


def selecionar_rois(imagem):
    global current_image
    current_image = imagem.copy()

    # Exibe a janela de seleção de ROIs
    cv2.imshow("Selecione as Notas", current_image)
    cv2.setMouseCallback("Selecione as Notas", mouse_crop)

    # Aguarda até que o usuário pressione a tecla 'q' para sair
    while True:
        cv2.imshow("Selecione as Notas", current_image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):  # Pressione 'q' para finalizar a seleção
            break

    cv2.destroyAllWindows()
    
    return rois


def identificar_pixels_azuis(imagem_com_notas):
    # Criando uma lista para armazenar as coordenadas dos pixels azuis
    coordenadas_azuis = []

    # Percorrendo a imagem com notas para encontrar os pixels azuis
    for y in range(imagem_com_notas.shape[0]):
        for x in range(imagem_com_notas.shape[1]):
            # O pixel azul no formato BGR é quando o valor do canal azul (B) é alto
            # e os canais verde (G) e vermelho (R) são baixos (por exemplo, 0).
            if imagem_com_notas[y, x][0] > 100 and imagem_com_notas[y, x][1] < 50 and imagem_com_notas[y, x][2] < 50:
                coordenadas_azuis.append((x, y))

    return coordenadas_azuis

def identificar_pixels_pretos(imagem):
    # Criando uma lista para armazenar as coordenadas dos pixels azuis
    coordenadas_pretos = []

    # Percorrendo a imagem com notas para encontrar os pixels azuis
    for y in range(imagem.shape[0]):
        for x in range(imagem.shape[1]):
            # O pixel azul no formato BGR é quando o valor do canal azul (B) é alto
            # e os canais verde (G) e vermelho (R) são baixos (por exemplo, 0).
            if imagem[y, x][0] < 50 and imagem[y, x][1] < 50 and imagem[y, x][2] < 50:
                coordenadas_pretos.append((x, y))

    return coordenadas_pretos

def preencher_brancos_entre_azuis(imagem):
    # Definir as cores: azul (para os pixels que foram marcados) e branco
    azul = [255, 0, 0]  # Cor azul em RGB
    branco = [255, 255, 255]  # Cor branca em RGB

    # Tamanho da imagem
    altura, largura = imagem.shape[:2]

    # Percorrer a imagem verticalmente (por colunas)
    for x in range(largura):
        y = 0
        while y < altura - 1:  # Percorrer as linhas
            if np.array_equal(imagem[y, x], azul):
                # Verificar os pixels seguintes para encontrar brancos
                y_branco_inicio = y + 1
                contagem_brancos = 0

                # Contar pixels brancos consecutivos
                while y_branco_inicio < altura and np.array_equal(imagem[y_branco_inicio, x], branco):
                    contagem_brancos += 1
                    y_branco_inicio += 1

                # Se o pixel seguinte à sequência de brancos for azul
                if y_branco_inicio < altura and np.array_equal(imagem[y_branco_inicio, x], azul):
                    # Se houver apenas 1 ou 2 pixels brancos, pinte-os de azul
                    if 1 <= contagem_brancos <= 2:
                        for i in range(1, contagem_brancos + 1):
                            imagem[y + i, x] = azul

                # Avançar para o próximo grupo de pixels
                y = y_branco_inicio
            else:
                y += 1

    return imagem


def pintar_branco_na_binarizada(imagem_binarizada, coordenadas_azuis):
    # Percorrer as coordenadas azuis e pintar esses pixels de branco na imagem binarizada
    for coord in coordenadas_azuis:
        x, y = coord
        imagem_binarizada[y, x] = 255  # Pintar o pixel de branco

    return imagem_binarizada

def pintar_preto_na_binarizada(imagem_binarizada, coordenadas_azuis):
    # Percorrer as coordenadas azuis e pintar esses pixels de branco na imagem binarizada
    for coord in coordenadas_azuis:
        x, y = coord
        imagem_binarizada[y, x] = 0  # Pintar o pixel de preto

    return imagem_binarizada

def pintar_preto_linhas(imagem_binarizada, linhas_pretas):
    # Percorrer as linhas pretas e pintar esses pixels de preto na imagem binarizada
    for linha in linhas_pretas:
        y, x_inicial, x_final = linha
        for x in range(x_inicial, x_final + 1):
            imagem_binarizada[y, x] = 0  # Pintar o pixel de preto

    return imagem_binarizada


def deslocar_eixo_Y(imagem, mudar_tom):
    global maior_diferenca_y
    deslocamento_Y = 0

    # Tamanho da imagem original
    altura, largura = imagem.shape[:2]

    # Criar uma nova imagem em branco com o mesmo tamanho da imagem original
    nova_imagem = np.zeros_like(imagem)

    if mudar_tom == 1 or mudar_tom == -1:
        deslocamento_Y = maior_diferenca_y // 2
    #elif mudar_tom == 2 or mudar_tom == -2:
        #deslocamento_Y = maior_diferenca_y
   #elif mudar_tom == 3 or mudar_tom == -3:
        #deslocamento_Y = (maior_diferenca_y // 2) * 3

    # Percorrer todos os pixels da imagem original
    for y in range(altura):
        for x in range(largura):
            # Novo Y será o valor original + o deslocamento
            if mudar_tom > 0:
                novo_y = y - deslocamento_Y
            else:
                novo_y = y + deslocamento_Y

            # Verificar se o novo Y está dentro dos limites da imagem
            if 0 <= novo_y < altura:
                # Copiar o pixel da posição (x, y) para (x, novo_y)
                nova_imagem[novo_y, x] = imagem[y, x]

    return nova_imagem

def redimensionar(img):

    imagem_redimensionada = cv2.resize(img, (80, 130))

    return imagem_redimensionada

def carregar_imagens_diretorio(diretorio_relativo):
    # Constrói o caminho completo usando o BASE_DIR
    caminho_diretorio = os.path.join(BASE_DIR, diretorio_relativo)
    
    imagens = []
    for arquivo in os.listdir(caminho_diretorio):
        if arquivo.endswith('.png') or arquivo.endswith('.jpg'):
            caminho_imagem = os.path.join(caminho_diretorio, arquivo)
            imagem = cv2.imread(caminho_imagem, cv2.IMREAD_UNCHANGED)
            if imagem is not None:
                imagens.append(imagem)
    return imagens

def inverter_valor(valor):
    if valor == 0: # Se o valor for 0 (preto), retorna 1
        return 1
    else: # Se o valor for diferente de 0 (branco), retorna 0
        return 0

def pixelAleatorio(imagem, nBits):
    global qntPixels

    height, width = imagem.shape[:2]

    qntPixels = width * height

    # Embaralhar os índices dos pixels
    random_pixels_indices = list(range(width * height))
    random.shuffle(random_pixels_indices)

    # Escolher pixels aleatórios na ordem embaralhada
    random_pixel_order = [(index // width, index % width) for index in random_pixels_indices]

    ordemAleatoria = random_pixel_order.copy()

    #print("Ordem dos pixels sorteados e seus valores binários na imagens:")
    #for i, pixel in enumerate(random_pixel_order):
        #valor_invertido = inverter_valor(imagem[pixel])
        #print(f"Índice: ({pixel[1]}, {pixel[0]}), Valor: {valor_invertido}")

    int_values = []

    # Converter cada grupo de nBits em um número inteiro
    current_value = 0
    bits_count = 0
    for i, pixel in enumerate(random_pixel_order):
        valor_invertido = inverter_valor(imagem[pixel])
        # Adicionar o bit invertido ao valor atual
        current_value = (current_value << 1) | valor_invertido
        bits_count += 1
        # Se atingirmos o número de bits necessário, adicione o valor inteiro à lista
        if bits_count == nBits:
            int_values.append(current_value)
            current_value = 0
            bits_count = 0

    # Imprimir os valores inteiros
    #print("")
    #print("Valores inteiros:")
    #for i, value in enumerate(int_values):
        #print(f"Índice: {i}, Valor: {value}")

    return int_values, ordemAleatoria

def similarImagem(imagem, ordemAleatoria, nBits):

    int_values = []

    # Converter cada grupo de nBits em um número inteiro
    current_value = 0
    bits_count = 0
    for i, pixel in enumerate(ordemAleatoria):
        valor_invertido = inverter_valor(imagem[pixel])
        # Adicionar o bit invertido ao valor atual
        current_value = (current_value << 1) | valor_invertido
        bits_count += 1
        # Se atingirmos o número de bits necessário, adicione o valor inteiro à lista
        if bits_count == nBits:
            int_values.append(current_value)
            current_value = 0
            bits_count = 0

    return int_values


def identificacao_da_clave(imagem, num_pautas):
    global maior_diferenca_y

    limite_percentual = 0
    nBits = 11

    # Verificar se a imagem está em tons de cinza
    if len(imagem.shape) == 2:
        # Converter para BGR (imagem colorida)
        imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)

    # Tamanho padrão do retângulo
    largura = 50
    altura = 105

    # Ajustar o tamanho do retângulo com base no espaçamento
    if 8 < maior_diferenca_y - 1 <= 11:
        # Mantém o tamanho padrão
        largura = 45
        altura = 90
        limite_percentual = 72.48
    elif 11 < maior_diferenca_y - 1 <= 13:
        # Mantém o tamanho padrão
        largura = 50
        altura = 108
        limite_percentual = 75.2
    elif 13 < maior_diferenca_y - 1 <= 15:
        # Multiplica o tamanho por 1,5
        largura = 50
        altura = 108
        limite_percentual = 76.5
    elif 15 < maior_diferenca_y - 1 <= 19:
        # Multiplica o tamanho por 1,5
        largura = largura + 22
        altura = int(altura * 1.6)
        limite_percentual = 75.25
    elif maior_diferenca_y - 1 > 20:
        # Multiplica o tamanho por 2
        largura = int(50 * 2)
        altura = int(105 * 2)
        limite_percentual = 79.0

    # Dimensões da imagem
    altura_imagem, largura_imagem = imagem.shape[:2]
    coordenadas_bloqueadas = []
    claves_detectadas = 0
    coordenadas_claves = []

    imagem_branca = np.ones_like(imagem) * 120

    imagens_sol = carregar_imagens_diretorio("media/ClaveSol")

    img_teste = os.path.join(BASE_DIR, "media/img/teste.png")
    teste_img = cv2.imread(img_teste, cv2.IMREAD_UNCHANGED)
    binario_teste = binarize_image(teste_img)
    _, ordemAlea = pixelAleatorio(binario_teste, nBits)

    total_bits = int(qntPixels / nBits)

    discri_sol = Discriminador()
    discri_sol.criar_e_adicionar_rams(total_bits, nBits)

    for i, img in enumerate(imagens_sol):
        img_red_sol = redimensionar(img)
        binario_sol = binarize_image(img_red_sol)
        endereco_sol = similarImagem(binario_sol, ordemAlea, nBits)
        discri_sol.incluir_endereco(endereco_sol)
        #print(f"Endereços dados de SOL {i + 1}: ", endereco_sol)

    discri_roi = Discriminador()
    discri_roi.criar_e_adicionar_rams(total_bits, nBits)
    #print("DISCRI SOL")
    #discri_sol.imprimir_rams()

    # Loop para percorrer a imagem
    for x in range(0, largura_imagem - largura, 2):  # Avança 1 pixel no eixo Y
        for y in range(0, altura_imagem - altura, 2):  # Avança 1 pixel no eixo X

            ignorar = False
            for (x_topo_bloq, y_topo_bloq, x_base_bloq, y_base_bloq) in coordenadas_bloqueadas:
                if (x_topo_bloq - 10 <= x <= x_base_bloq + 10) and (y_topo_bloq - 10 <= y <= y_base_bloq + 10):
                    ignorar = True
                    break  # Se estiver dentro da área bloqueada, ignore este ROI

            if ignorar:
                continue


            # Criar uma cópia da imagem para desenhar o retângulo
            img_copy = imagem.copy()

            # Desenhar o retângulo na posição atual (x, y)
            cv2.rectangle(img_copy, (x, y), (x + largura, y + altura), (255, 0, 0), 2)

            # Redimensionar a área para o tamanho necessário para a similaridade
            roi = imagem[y:y + altura, x:x + largura]

            total_pixels = roi.size
            pixels_brancos = np.sum(roi == 255)
            percentual_brancos = (pixels_brancos / total_pixels) * 100

            if percentual_brancos > limite_percentual:  # Limite de pixels brancos
                print(f"ROI ignorado na posição X={x}, Y={y} por ter {percentual_brancos:.2f}% de pixels brancos")
                continue  # Pular esta iteração

            roi_redimensionado = redimensionar(roi)
            binario_roi = binarize_image(roi_redimensionado)

            endereco_roi = similarImagem(binario_roi, ordemAlea, nBits)
            discri_roi.incluir_endereco(endereco_roi)
            #print("DISCRI ROI")
            #discri_roi.imprimir_rams()

            #cv2.imshow("ROI", roi)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()


            # Calcular a similaridade com a clave treinada
            similaridade = discri_roi.calcular_similaridade(discri_sol)


            # Se a similaridade for maior que 96%, identificamos uma clave
            if similaridade >= 96.22:
                #print(f"Clave detectada na posição: X={x}, Y={y} com {similaridade}% de similaridade")
                coordenadas_clave = (x, y, x + largura, y + altura)
                print(f"Clave detectada com maior similaridade em: X_topo={coordenadas_clave[0]}, Y_topo={coordenadas_clave[1]}, X_base={coordenadas_clave[2]}, Y_base={coordenadas_clave[3]}")
                coordenadas_claves.append(coordenadas_clave)
                coordenadas_bloqueadas.append(coordenadas_clave)

                imagem_branca[y:y + roi.shape[0], x:x + roi.shape[1]] = roi

                claves_detectadas += 1

                #cv2.imshow(f"ROI com Clave Detectada - Similaridade: {similaridade}%", roi)
                #cv2.waitKey(0)

                # Verifica se já encontrou todas as claves de acordo com o número de pautas
                if claves_detectadas >= num_pautas:
                    #cv2.imwrite("imagem_claves_detectadas_final.png", imagem_branca)
                    return imagem_branca, coordenadas_claves

            # Exibir a imagem com o retângulo
            #cv2.imshow("Imagem com Retângulo Percorrendo", img_copy)
            #cv2.waitKey(1)  # Aguarda 1 milissegundo para a próxima iteração

    # Fechar todas as janelas quando terminar
    cv2.destroyAllWindows()

    return imagem_branca, coordenadas_claves


def aumentar_tamanho_x_imagem(imagem, coordenadas_claves, mudar_tom):
    global maior_diferenca_y

    if len(imagem.shape) == 2:  # Imagem em escala de cinza
        imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)

    altura, largura = imagem.shape[:2]
    pixels_a_aumentar = 0  # Variável para armazenar o valor do aumento em pixels
    img_clave = None  # Variável para carregar a imagem da clave

    #cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_pequeno_2sustenido.png"),

    # Condições baseadas em maior_diferenca_y e mudar_tom
    if 8 < maior_diferenca_y - 1 <= 11 and mudar_tom == 1:
        pixels_a_aumentar = 20
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_pequenino_2sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 8 < maior_diferenca_y - 1 <= 11 and mudar_tom == -1:
        pixels_a_aumentar = 65
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_pequenino_5sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 11 < maior_diferenca_y <= 13 and mudar_tom == 1:
        pixels_a_aumentar = 25
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_pequeno_2sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 11 < maior_diferenca_y <= 13 and mudar_tom == -1:
        pixels_a_aumentar = 75
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_pequeno_5sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 13 < maior_diferenca_y - 1 <= 15 and mudar_tom == 1:
        pixels_a_aumentar = 35
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_medio_2sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 13 < maior_diferenca_y - 1 <= 15 and mudar_tom == -1:
        pixels_a_aumentar = 90
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_medio_5sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 15 < maior_diferenca_y - 1 <= 19 and mudar_tom == 1:
        pixels_a_aumentar = 60
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_mediano_2sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif 15 < maior_diferenca_y - 1 <= 19 and mudar_tom == -1:
        pixels_a_aumentar = 130
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_mediano_5sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif maior_diferenca_y > 20 and mudar_tom == 1:
        pixels_a_aumentar = 50
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_grande_2sustenido.png"), cv2.IMREAD_UNCHANGED)
    elif maior_diferenca_y > 20 and mudar_tom == -1:
        pixels_a_aumentar = 150
        img_clave = cv2.imread(os.path.join(BASE_DIR, "media/img/clavesol_grande_5sustenido.png"), cv2.IMREAD_UNCHANGED)

    # Verificar se a imagem da clave foi carregada corretamente
    if img_clave is None:
        raise FileNotFoundError("Imagem da clave não foi encontrada.")

    # Criar uma nova imagem com o tamanho aumentado à esquerda
    nova_largura = largura + pixels_a_aumentar
    nova_imagem = np.ones((altura, nova_largura, 3), dtype=np.uint8) * 255  # Fundo branco

    # Copiar a imagem original para a nova imagem, deslocada à direita
    nova_imagem[:, pixels_a_aumentar:] = imagem

    # Inserir a imagem da clave nas coordenadas detectadas
    for i, (x_topo, y_topo, x_base, y_base) in enumerate(coordenadas_claves):
        altura_clave, largura_clave = img_clave.shape[:2]

        if i == 2 and len(coordenadas_claves) == 3:
            # Para a terceira clave, não subtrair pixels_a_aumentar (manter a posição original)
            nova_x_topo = x_topo + 2
        else:
            # Ajustar as coordenadas X para que a clave seja posicionada corretamente na nova imagem
            nova_x_topo = x_topo - pixels_a_aumentar  # Decrementar os pixels aumentados

        # Para a primeira clave, subtrair 5 pixels do eixo Y
        if i == 0:
            y_topo -= 7

        # Verificar se as coordenadas ajustadas estão dentro dos limites da nova imagem
        if nova_x_topo < 0:
            # Ajustar para começar no início da imagem se nova_x_topo for negativo
            nova_x_topo = 13

        # Verificar se a clave cabe dentro da imagem aumentada e ajustar, se necessário
        if nova_x_topo + largura_clave <= nova_largura and y_topo + altura_clave <= altura:
            # Inserir a clave na nova imagem usando transparência (se for PNG com canal alfa)
            if img_clave.shape[2] == 4:  # Imagem com canal alfa (transparência)
                for c in range(0, 3):  # Aplicar apenas nos três canais de cor (BGR)
                    nova_imagem[y_topo:y_topo + altura_clave, nova_x_topo:nova_x_topo + largura_clave, c] = \
                        img_clave[:, :, c] * (img_clave[:, :, 3] / 255.0) + \
                        nova_imagem[y_topo:y_topo + altura_clave, nova_x_topo:nova_x_topo + largura_clave, c] * (
                                1.0 - img_clave[:, :, 3] / 255.0)
            else:
                 # Inserir diretamente a imagem da clave se não houver canal alfa
                nova_imagem[y_topo:y_topo + altura_clave, nova_x_topo:nova_x_topo + largura_clave] = img_clave
        else:
            print(f"Erro: Clave não cabe na imagem aumentada nas coordenadas X={nova_x_topo}, Y={y_topo}.")

    return nova_imagem

def pintar_pauta(imagem, pautas_dict):
    # Verifica se a imagem está em escala de cinza e converte para BGR
    if len(imagem.shape) == 2:
        imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2BGR)

    # Itera sobre as pautas no dicionário
    for nome_pauta, linhas in pautas_dict.items():
        # Obtém o primeiro pixel da primeira linha e o último pixel da última linha, com deslocamento de 1 pixel
        y_inicial = linhas[0][0][0]  # Y da primeira linha
        x_inicial = max(0, linhas[0][0][1] - 1)  # X do primeiro pixel da primeira linha menos 1 (limitado ao mínimo 0)
        y_final = linhas[-1][0][0]  # Y da última linha
        x_final = max(0, linhas[-1][0][2] - 1)  # X do último pixel da última linha menos 1 (limitado ao mínimo 0)

        # Pinta verticalmente entre o primeiro e o último pixel ajustado de cada linha da pauta
        for y in range(y_inicial, y_final + 1):
            imagem[y, x_inicial] = (0, 0, 0)  # Pinta o primeiro pixel ajustado da linha em preto
            imagem[y, x_final] = (0, 0, 0)  # Pinta o último pixel ajustado da linha em preto

    return imagem


def etapa1_processamento_inicial(imagem_original, mudar_tom):
    # Passos de 1 a 6
    binario = binarize_image(imagem_original)
    pautas_dict, num_pautas, linhas_pretas = encontrar_linhas_pretas(binario, imagem_original)
    pixel_pintado_embaixo = pintar_pixels_abaixo_ultima_linha(binario, imagem_original, pautas_dict)
    resultado = pintar_pixels_acima_primeira_linha(binario, pixel_pintado_embaixo, pautas_dict)
    notas_pintadas = extrair_partes_azuis(resultado)
    return notas_pintadas, pautas_dict, num_pautas, linhas_pretas, binario

def etapa2_selecao_e_ajuste_rois(notas_pintadas, binario, rois):
    # Passos de 7 a 10
    nova_imagem = np.ones_like(notas_pintadas) * 255  # imagem branca
    for i, roi in enumerate(rois):
        x, y, w, h = roi
        nota = notas_pintadas[y:y + h, x:x + w]
        nova_imagem[y:y + h, x:x + w] = nota
    coordenadas_azuis = identificar_pixels_azuis(nova_imagem)
    imagem_modificada = pintar_branco_na_binarizada(binario, coordenadas_azuis)
    novas_perfeitas = preencher_brancos_entre_azuis(nova_imagem)
    return nova_imagem, imagem_modificada

def etapa2_selecao_e_ajuste_rois_mod(binario, nova_imagem):
    coordenadas_azuis = identificar_pixels_azuis(nova_imagem)
    imagem_modificada = pintar_branco_na_binarizada(binario, coordenadas_azuis)
    novas_perfeitas = preencher_brancos_entre_azuis(nova_imagem)
    return imagem_modificada

def etapa3_deslocamento_e_finalizacao(nova_imagem, mudar_tom, imagem_modificada, linhas_pretas, num_pautas):
    # Passos de 11 a 21
    imagem_movida = deslocar_eixo_Y(nova_imagem, mudar_tom)
    novas_coords_azuis = identificar_pixels_azuis(imagem_movida)
    nova_partitura = pintar_preto_na_binarizada(imagem_modificada, novas_coords_azuis)
    achar_clave, coords_clave = identificacao_da_clave(nova_partitura, num_pautas)
    coords_preto = identificar_pixels_pretos(achar_clave)
    imagem_modificada_2 = pintar_branco_na_binarizada(nova_partitura, coords_preto)
    partitura_commaispixels = aumentar_tamanho_x_imagem(imagem_modificada_2, coords_clave, mudar_tom)
    partitura_completa = pintar_preto_linhas(partitura_commaispixels, linhas_pretas)
    return partitura_completa, imagem_movida
