import pygame
import math

# Inicialização do Pygame
pygame.init()

# Configurações da Janela (Agora o 3D ocupa tudo, minimapa fica por cima)
LARGURA_TELA = 800
ALTURA_TELA = 600
# Damos uma pequena margem (ex: 12 unidades) para o jogador não "entrar" na parede visualmente
MARGEM = 12
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Motor Matemático Estilo DOOM/Wolfenstein")

# Configurações do Jogo e Matemática do Raycasting
FPS = 60
TAMANHO_BLOCO = 64
FOV = math.radians(60)  # Campo de visão (60 graus)
NUM_RAIOS = 400    # Número de colunas na tela 3D
LARGURA_COLUNA = LARGURA_TELA / NUM_RAIOS
# AJUSTE MATEMÁTICO: Mudou de 400 para LARGURA_TELA (800) para ajustar o aspecto visual
DIST_PROJECAO = (LARGURA_TELA / 2) / math.tan(FOV / 2)

# Cores
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
BEGE = (200, 200, 200)
TETO_COR = (40, 40, 50)     # Cinza azulado escuro
CHAO_COR = (70, 70, 70)     # Cinza chão

# O Mapa do Jogo (1 = Parede, 0 = Espaço Vazio)
MAPA = [
    "11111111",
    "10000001",
    "10001001",
    "1000P001",
    "10001001",
    "10000001",
    "10000001",
    "11111111"
]

# Variáveis da Porta
porta_abertura = 0.0      # 0.0 = Totalmente Fechada, 1.0 = Totalmente Aberta
porta_estado = "fechada"  # Pode ser: "fechada", "abrindo", "aberta", "fechando"

# Variáveis do Jogador
player_x = 120
player_y = 300
player_angle = 0.0
velocidade = 4  # Reduzi um pouco para o movimento ficar mais suave

relogio = pygame.time.Clock()
rodando = True

def player_draw(player_x, player_y):
    # Desenhar o jogador no mapa 2D
    pygame.draw.circle(tela, VERMELHO, (int(player_x * (25/64)), int(player_y * (25/64))), 5)

def map2D_draw():
    # --- DESENHAR MINIMAPA NO CANTO SUPERIOR ESQUERDO ---
    for linha_idx, linha in enumerate(MAPA):
        for col_idx, bloco in enumerate(linha):
            if bloco == '1':
                pygame.draw.rect(tela, BEGE, (col_idx * 25, linha_idx * 25, 24, 24))

def cenario_fundo_draw():
    # MATEMÁTICA SIMPLES: Metade superior é teto, metade inferior é chão
    # Desenha o Teto
    pygame.draw.rect(tela, TETO_COR, (0, 0, LARGURA_TELA, ALTURA_TELA / 2))
    # Desenha o Chão
    pygame.draw.rect(tela, CHAO_COR, (0, ALTURA_TELA / 2, LARGURA_TELA, ALTURA_TELA / 2))

def check_for_colisions(player_x, proximo_x, player_y, proximo_y):
    # --- MATEMÁTICA DA COLISÃO ---
    # 1. Testar colisão apenas no eixo X
    # Dependendo da direção que andamos, checamos um pouco mais à frente ou atrás (usando a MARGEM)
    sinal_x = 1 if (proximo_x > player_x) else -1
    teste_mapa_x = int((proximo_x + sinal_x * MARGEM) / TAMANHO_BLOCO)
    mapa_atual_y = int(player_y / TAMANHO_BLOCO)
    
    if MAPA[mapa_atual_y][teste_mapa_x] != '1':
        if MAPA[mapa_atual_y][teste_mapa_x] != 'P' or porta_abertura >= 0.9:
            player_x = proximo_x  # Se estiver livre em X, o jogador pode andar neste eixo

    # 2. Testar colisão apenas no eixo Y
    sinal_y = 1 if (proximo_y > player_y) else -1
    teste_mapa_y = int((proximo_y + sinal_y * MARGEM) / TAMANHO_BLOCO)
    mapa_atual_x = int(player_x / TAMANHO_BLOCO)
    
    if MAPA[teste_mapa_y][mapa_atual_x] != '1':
        if MAPA[mapa_atual_y][teste_mapa_x] != 'P' or porta_abertura >= 0.9:
            player_y = proximo_y  # Se estiver livre em Y, o jogador pode andar neste eixo

    return player_x, player_y

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        # 1. Controles do Jogador com Cálculo de Colisão (Eixos Separados)
    teclas = pygame.key.get_pressed()
    
    # Rotação (ângulo) não precisa de colisão
    if teclas[pygame.K_LEFT]:
        player_angle -= 0.05
    if teclas[pygame.K_RIGHT]:
        player_angle += 0.05

    # Inicializa variáveis para calcular o próximo passo (proposta de movimento)
    proximo_x = player_x
    proximo_y = player_y

    if teclas[pygame.K_UP]:
        proximo_x += math.cos(player_angle) * velocidade
        proximo_y += math.sin(player_angle) * velocidade
    if teclas[pygame.K_DOWN]:
        proximo_x -= math.cos(player_angle) * velocidade
        proximo_y -= math.sin(player_angle) * velocidade

    player_x, player_y = check_for_colisions(player_x, proximo_x, player_y, proximo_y)


    # 1. PRIMEIRO: Desenha o fundo (Teto e Chão) ocupando a tela inteira
    cenario_fundo_draw()

        # --- EQUAÇÃO DO RAYCASTING CORRIGIDA (SEM VAZAMENTO DE COR) ---
    angulo_inicial = player_angle - (FOV / 2)
    passo_angulo = FOV / NUM_RAIOS

    raios_para_desenhar = []

    for i in range(NUM_RAIOS):
        angulo_raio = angulo_inicial + i * passo_angulo
        cos_a = math.cos(angulo_raio)
        sin_a = math.sin(angulo_raio)
        
        # Variáveis para rastrear a colisão precisa
        colidiu = False
        dist_final = 0
        bloco_final = '0'
        raio_x_final, raio_y_final = 0, 0

        # Avança o raio linearmente
        for dist in range(1, 800):
            raio_x = player_x + cos_a * dist
            raio_y = player_y + sin_a * dist

            mapa_x = int(raio_x / TAMANHO_BLOCO)
            mapa_y = int(raio_y / TAMANHO_BLOCO)

            # Evita travamento fora dos limites do mapa
            if mapa_y >= len(MAPA) or mapa_x >= len(MAPA[0]) or mapa_y < 0 or mapa_x < 0:
                break

            bloco_detectado = MAPA[mapa_y][mapa_x]
            
            if bloco_detectado in ('1', 'P'):
                # MATEMÁTICA DA DETECÇÃO DE FACE: Descobre se bateu na face X ou face Y
                fração_x = raio_x % TAMANHO_BLOCO
                fração_y = raio_y % TAMANHO_BLOCO
                
                # Se estiver mais perto das quinas horizontais do bloco, é face Y, senão X
                dist_borda_x = min(fração_x, TAMANHO_BLOCO - fração_x)
                dist_borda_y = min(fração_y, TAMANHO_BLOCO - fração_y)
                bateu_na_face_x = dist_borda_x < dist_borda_y

                if bloco_detectado == 'P':

                    porta_x = mapa_x * TAMANHO_BLOCO + TAMANHO_BLOCO / 2

                    if abs(cos_a) > 0.0001:

                        t = (porta_x - player_x) / cos_a

                        if t > 0:

                            y_intersec = player_y + sin_a * t

                            y_local = y_intersec - mapa_y * TAMANHO_BLOCO

                            abertura_real = porta_abertura * TAMANHO_BLOCO

                            if abertura_real <= y_local <= TAMANHO_BLOCO:

                                dist_final = t
                                raio_x_final = porta_x
                                raio_y_final = y_intersec
                                bloco_final = 'P'
                                colidiu = True
                                break

                    continue
                else:
                    # Se bateu em uma parede comum ('1'), registra imediatamente
                    dist_final = dist
                    raio_x_final, raio_y_final = raio_x, raio_y
                    bloco_final = '1'
                    colidiu = True
                    break

        if colidiu:
            # Armazena os raios para o minimapa 2D
            if i % 10 == 0:
                raios_para_desenhar.append(((int(player_x * (25/64)), int(player_y * (25/64))), 
                                            (int(raio_x_final * (25/64)), int(raio_y_final * (25/64)))))

            dist_corrigida = dist_final * math.cos(angulo_raio - player_angle)
            if dist_corrigida < 1: dist_corrigida = 1
            
            altura_parede = (TAMANHO_BLOCO / dist_corrigida) * DIST_PROJECAO
            if altura_parede > ALTURA_TELA:
                altura_parede = ALTURA_TELA

            cor_fator = 255 / (1 + (dist_corrigida * dist_corrigida * 0.0002))
            
            # ATRIBUIÇÃO EXATA: Agora a cor depende do bloco rigidamente validado pelo teste de quina
            if bloco_final == 'P':
                cor = (cor_fator, cor_fator * 0.6, 0)  # Laranja para Porta
            else:
                cor = (0, cor_fator, cor_fator)        # Azul/Verde para Parede

            x_3d = i * LARGURA_COLUNA
            y_3d = (ALTURA_TELA / 2) - (altura_parede / 2)
            
            pygame.draw.rect(tela, cor, (x_3d, y_3d, LARGURA_COLUNA + 1, altura_parede))




    # 3. TERCEIRO: Desenha o minimapa e os raios por cima do mundo 3D
    map2D_draw()
    for raio in raios_para_desenhar:
        pygame.draw.line(tela, VERDE, raio[0], raio[1], 1)
    player_draw(player_x, player_y)
    
    pygame.display.flip()
    relogio.tick(FPS)

pygame.quit()
