import pygame
import random

# Inicializa o pygame (biblioteca usada para o jogo)
pygame.init()

# Cria um clock para controlar FPS
clock = pygame.time.Clock()

# Define largura e altura da tela
screen_width = 600
screen_height = 400

# Cria a janela onde o jogo será exibido
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dungeon Mage")

# Carrega imagem do fundo
background = pygame.image.load("dungeon_floor.png").convert()

# Controla se o jogo continua rodando
running = True

# =====================================================================
#  COIN – Moeda normal
# =====================================================================
class Coin:
    def __init__(self):
        # Gera uma posição aleatória na tela
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)

        # Carrega a imagem da moeda normal
        self.image = pygame.image.load("coin.png")
        self.rect = self.image.get_rect(center=(self.x, self.y))

    # Desenha moeda
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# =====================================================================
#  SUPERCOIN – Moeda especial (vale 5 pontos)
# =====================================================================
class SuperCoin(Coin):
    def __init__(self):
        super().__init__()
        # Carrega imagem especial da moeda "SuperCoin"
        self.image = pygame.image.load("supercoin.png")
        self.rect = self.image.get_rect(center=(self.x, self.y))


# =====================================================================
#  Mage – Jogador com movimento simples baseado em teclas
# =====================================================================
class Mage:
    def __init__(self, x, y, image):
        # Guarda coordenadas
        self.x = x
        self.y = y

        # Carrega imagem e posição
        self.image = image
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Velocidade fixa de movimento
        self.speed = 500

        # Pontuação total
        self.score = 0

    # Desenha o mage na tela
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # Move mage com dx e dy
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x, self.y)

        # Impede o mage de sair da tela (limite de bordas)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

        # Atualiza coordenadas centrais
        self.x, self.y = self.rect.center

    # Atualiza movimento baseado no teclado pressionado
    def update(self,dt):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        # movimento baseado em tempo real
        if keys[pygame.K_UP]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN]:
            dy += self.speed * dt
        if keys[pygame.K_LEFT]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            dx += self.speed * dt

        self.move(dx, dy)

# =====================================================================
#  CONFIGURAÇÕES DO JOGO
# =====================================================================

# Carrega imagem do mage
mage_image = pygame.image.load("mage.png")

# Cria instancia do mage
mage = Mage(screen_width // 2, screen_height // 2, mage_image)
mage.original_image = mage_image  # Apenas para compatibilidade

# Lista de moedas presentes na tela
coins = []

# Conta quantas moedas NORMAIS foram coletadas
normal_coins_collected = 0
special_coins_collected = 0 

# =====================================================================
#  SPAWN DE MOEDAS (normal e especial)
# =====================================================================
def spawn_coin():
    global normal_coins_collected

    # Apenas cria moedas se houver menos de 4 na tela
    if len(coins) < 2:

        # Condição para gerar SuperCoin:
        # - Já coletou algum múltiplo de 10 moedas normais
        # - Não existe nenhuma SuperCoin na tela ainda
        if (
            normal_coins_collected != 0 and
            normal_coins_collected % 10 == 0 and
            not any(isinstance(c, SuperCoin) for c in coins)
        ):
            coins.append(SuperCoin())
        else:
            coins.append(Coin())


# =====================================================================
#  CHECAGEM DE COLISÃO ENTRE DRONE E MOEDAS
# =====================================================================
def check_coin_collision():
    global normal_coins_collected
    global special_coins_collected

    # Copia da lista pra evitar problemas ao remover itens
    for coin in coins[:]:
        # Verifica colisão entre mage e moeda
        if mage.rect.colliderect(coin.rect):
            coins.remove(coin)

            # Se for moeda especial → vale 5 pontos
            if isinstance(coin, SuperCoin):
                mage.score += 5
                special_coins_collected += 1
            else:
                # Moeda normal → vale 1 ponto
                mage.score += 2
                normal_coins_collected += 1

            # Após pegar moeda, tenta spawnar outra
            spawn_coin()


# Fonte usada para escrever texto na tela
font = pygame.font.SysFont('Arial', 30) 

# =====================================================================
#  LOOP PRINCIPAL DO JOGO
# =====================================================================
while running:   
    dt = clock.tick(60) / 1000.0

    # Lida com eventos do teclado e janela
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
   # Desenha a imagem de fundo da dungeon
    screen.blit(background, (0, 0))

    # Checa colisões com moedas
    check_coin_collision()

    # Gera novas moedas quando necessário
    spawn_coin()

    # Exibe pontuação
    score_text = font.render('Score: ' + str(mage.score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Desenha moedas na tela
    for coin in coins:
        coin.draw(screen)

    # Atualiza o movimento do mage
    mage.update(dt)
    mage.draw(screen)

    # Atualiza a tela (desenha tudo)
    pygame.display.flip()
