import pygame
import math

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
# Metade esquerda será o Mapa 2D, metade direita será a Visão 3D
LARGURA_TELA = 800
ALTURA_TELA = 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Motor Matemático Estilo DOOM/Wolfenstein")

# Configurações do Jogo e Matemática do Raycasting
FPS = 60
TAMANHO_BLOCO = 64
FOV = math.pi / 3  # Campo de visão (60 graus)
NUM_RAIOS = 400    # Número de colunas na tela 3D
LARGURA_COLUNA = 800 / NUM_RAIOS
DIST_PROJECAO = (400 / 2) / math.tan(FOV / 2)

#cores
VERMELHO = (255, 0, 0)
BEGE = (200, 200, 200)

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
player_y = 120
player_angle = 0.0
velocidade = 10

relogio = pygame.time.Clock()
rodando = True

def player_draw(player_x, player_y):
    # Desenhar o jogador no mapa 2D
    pygame.draw.circle(tela, VERMELHO, (int(player_x * (25/64)), int(player_y * (25/64))), 5)

def map2D_draw():
    # --- DESENHAR METADE ESQUERDA: MAPA 2D ---
    for linha_idx, linha in enumerate(MAPA):
        for col_idx, bloco in enumerate(linha):
            if bloco == '1':
                pygame.draw.rect(tela, BEGE, (col_idx * 25, linha_idx * 25, 24, 24))

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # 1. Controles do Jogador
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        player_angle -= 0.05
    if teclas[pygame.K_RIGHT]:
        player_angle += 0.05
    if teclas[pygame.K_UP]:
        # Move para frente usando Seno e Cosseno (Vetor de Direção)
        player_x += math.cos(player_angle) * velocidade
        player_y += math.sin(player_angle) * velocidade
    if teclas[pygame.K_DOWN]:
        player_x -= math.cos(player_angle) * velocidade
        player_y -= math.sin(player_angle) * velocidade

    # Limpar a tela (Fundo)
    tela.fill((30, 30, 30))

    # --- EQUAÇÃO DO RAYCASTING (VISÃO 3D) ---
    # Começa a varredura de raios do lado esquerdo do FOV até o lado direito
    angulo_inicial = player_angle - (FOV / 2)
    passo_angulo = FOV / NUM_RAIOS

    for i in range(NUM_RAIOS):
        angulo_raio = angulo_inicial + i * passo_angulo
        
        # Avança o raio centímetro por centímetro até colidir com uma parede
        for dist in range(1, 800):
            raio_x = player_x + math.cos(angulo_raio) * dist
            raio_y = player_y + math.sin(angulo_raio) * dist

            # Converte a coordenada do raio para a célula do mapa
            mapa_x = int(raio_x / TAMANHO_BLOCO)
            mapa_y = int(raio_y / TAMANHO_BLOCO)

            # Se colidir com uma parede (1)
            if MAPA[mapa_y][mapa_x] == '1':
                # Desenha a linha do raio no mapa 2D (apenas alguns raios para não poluir)
                if i % 10 == 0:
                    pygame.draw.line(tela, (0, 255, 0), 
                                     (int(player_x * (25/64)), int(player_y * (25/64))), 
                                     (int(raio_x * (25/64)), int(raio_y * (25/64))), 1)

                # Correção do efeito "olho de peixe" (Matemática pura)
                dist_corrigida = dist * math.cos(angulo_raio - player_angle)

                # EQUAÇÃO DO DOOM: Calcula a altura da coluna baseado na distância
                altura_parede = (TAMANHO_BLOCO / dist_corrigida) * DIST_PROJECAO

                # Limita o tamanho para não quebrar a tela
                if altura_parede > ALTURA_TELA:
                    altura_parede = ALTURA_TELA

                # Calcula a cor (Paredes mais distantes ficam mais escuras)
                cor_fator = 255 / (1 + (dist_corrigida * dist_corrigida * 0.0001))
                cor = (0, cor_fator, cor_fator)

                # --- DESENHAR METADE DIREITA: PROJEÇÃO 3D ---
                x_3d = i * LARGURA_COLUNA
                y_3d = (ALTURA_TELA / 2) - (altura_parede / 2)
                
                pygame.draw.rect(tela, cor, (x_3d, y_3d, LARGURA_COLUNA + 1, altura_parede))
                break

    map2D_draw()
    player_draw(player_x, player_y)
    
    pygame.display.flip()
    relogio.tick(FPS)

pygame.quit()
