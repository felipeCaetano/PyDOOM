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
FOV = math.pi / 3  # Campo de visão (60 graus)
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
    "10010001",
    "10000001",
    "10001001",
    "10000001",
    "10000001",
    "11111111"
]

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
        player_x = proximo_x  # Se estiver livre em X, o jogador pode andar neste eixo

    # 2. Testar colisão apenas no eixo Y
    sinal_y = 1 if (proximo_y > player_y) else -1
    teste_mapa_y = int((proximo_y + sinal_y * MARGEM) / TAMANHO_BLOCO)
    mapa_atual_x = int(player_x / TAMANHO_BLOCO)
    
    if MAPA[teste_mapa_y][mapa_atual_x] != '1':
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

    # --- EQUAÇÃO DO RAYCASTING (VISÃO 3D) ---
    angulo_inicial = player_angle - (FOV / 2)
    passo_angulo = FOV / NUM_RAIOS

    # Lista temporária para guardar as linhas dos raios e desenhar depois por cima do minimapa
    raios_para_desenhar = []

    for i in range(NUM_RAIOS):
        angulo_raio = angulo_inicial + i * passo_angulo
        
        for dist in range(1, 800):
            raio_x = player_x + math.cos(angulo_raio) * dist
            raio_y = player_y + math.sin(angulo_raio) * dist

            mapa_x = int(raio_x / TAMANHO_BLOCO)
            mapa_y = int(raio_y / TAMANHO_BLOCO)

            if MAPA[mapa_y][mapa_x] == '1':
                if i % 10 == 0:
                    # Guardamos as coordenadas do minimapa para desenhar no final
                    raios_para_desenhar.append(((int(player_x * (25/64)), int(player_y * (25/64))), 
                                                (int(raio_x * (25/64)), int(raio_y * (25/64)))))

                dist_corrigida = dist * math.cos(angulo_raio - player_angle)
                altura_parede = (TAMANHO_BLOCO / dist_corrigida) * DIST_PROJECAO

                if altura_parede > ALTURA_TELA:
                    altura_parede = ALTURA_TELA

                # Efeito de sombreamento (paredes longe ficam pretas)
                cor_fator = 255 / (1 + (dist_corrigida * dist_corrigida * 0.0002))
                cor = (0, cor_fator, cor_fator)

                # 2. SEGUNDO: Desenha as colunas 3D por cima do teto/chão
                x_3d = i * LARGURA_COLUNA
                y_3d = (ALTURA_TELA / 2) - (altura_parede / 2)
                
                pygame.draw.rect(tela, cor, (x_3d, y_3d, LARGURA_COLUNA + 1, altura_parede))
                break

    # 3. TERCEIRO: Desenha o minimapa e os raios por cima do mundo 3D
    map2D_draw()
    for raio in raios_para_desenhar:
        pygame.draw.line(tela, VERDE, raio[0], raio[1], 1)
    player_draw(player_x, player_y)
    
    pygame.display.flip()
    relogio.tick(FPS)

pygame.quit()
