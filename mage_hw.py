import pygame
import random

# Importa funções de hardware (driver char via /dev/mydev)
# - read_button(): lê o estado dos botões e traduz para 'UP', 'DOWN', etc.
# - write_left_display / write_right_display: escreve 32-bit no display
# - digit_to_7seg: converte número (0-9999) -> padrão 7 segmentos (4 dígitos)
from controls import read_button, write_left_display, write_right_display, digit_to_7seg

# ============================================================
# Inicialização do pygame
# ============================================================
pygame.init()

# Clock para FPS estável (e dt em segundos)
clock = pygame.time.Clock()

# Dimensões da tela (mantive do seu mage.py)
screen_width = 600
screen_height = 400

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dungeon Mage (Hardware)")

# Fundo da dungeon (imagem)
background = pygame.image.load("dungeon_floor.png").convert()

running = True

# ============================================================
# Classes do jogo
# ============================================================
class Coin:
    """Moeda normal (vale 1 ponto)."""

    def __init__(self):
        self.image = pygame.image.load("coin.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.center = (
            random.randint(20, screen_width - 20),
            random.randint(20, screen_height - 20),
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class SuperCoin(Coin):
    """Moeda especial (vale 5 pontos)."""

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("supercoin.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.respawn()


class Mage:
    """Personagem controlado pelos BOTÕES (driver)."""

    def __init__(self, x, y):
        self.image = pygame.image.load("mage.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        # velocidade em pixels por segundo
        self.speed = 250

        # pontos (score)
        self.score = 0

        # contagem total de moedas coletadas (normais + super)
        self.coins_collected = 0

    def move(self, dx, dy):
        self.rect.x += int(dx)
        self.rect.y += int(dy)

        # trava nas bordas
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def update(self, dt):
        """
        Atualiza o movimento lendo botões via driver.
        read_button() retorna: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'LEFT+RIGHT' ou ''.
        """
        key = read_button()

        dx = 0.0
        dy = 0.0

        if key == "UP":
            dy -= self.speed * dt
        elif key == "DOWN":
            dy += self.speed * dt
        elif key == "LEFT":
            dx -= self.speed * dt
        elif key == "RIGHT":
            dx += self.speed * dt
        elif key == "LEFT+RIGHT":
            # comportamento opcional (dash)
            dx += self.speed * dt * 2

        self.move(dx, dy)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ============================================================
# Lógica de moedas / score
# ============================================================

mage = Mage(screen_width // 2, screen_height // 2)

coins = []
normal_coins_collected = 0  # controla quando aparece supermoeda


def spawn_coin():
    """
    Mantém no máximo 2 moedas na tela.
    A cada 10 moedas normais coletadas, tenta spawnar 1 SuperCoin.
    """
    global normal_coins_collected

    if len(coins) >= 2:
        return

    # se chegou em múltiplo de 10 e ainda não tem SuperCoin na tela
    if (
        normal_coins_collected != 0
        and normal_coins_collected % 10 == 0
        and not any(isinstance(c, SuperCoin) for c in coins)
    ):
        coins.append(SuperCoin())
    else:
        coins.append(Coin())


def update_displays():
    """
    Atualiza os 7-seg:
    - Display esquerdo: SCORE (pontos)
    - Display direito: TOTAL de moedas coletadas
    """
    # Mostra apenas 0-9999
    score_to_show = mage.score % 10000
    coins_to_show = mage.coins_collected % 10000

    write_left_display(digit_to_7seg(score_to_show))
    write_right_display(digit_to_7seg(coins_to_show))


def check_coin_collision():
    """
    Se mago colidir com moeda:
    - remove moeda
    - atualiza score e contadores
    - atualiza displays imediatamente
    """
    global normal_coins_collected

    for coin in coins[:]:
        if mage.rect.colliderect(coin.rect):
            coins.remove(coin)

            # incrementa contador total de moedas (para display direito)
            mage.coins_collected += 1

            # pontuação
            if isinstance(coin, SuperCoin):
                mage.score += 5
            else:
                mage.score += 1
                normal_coins_collected += 1

            # Atualiza displays toda vez que coleta
            update_displays()

            # tenta repor moeda
            spawn_coin()


# Inicializa displays em 0 no começo do jogo
update_displays()

# Gera moedas iniciais
for _ in range(2):
    spawn_coin()

# ============================================================
# Loop principal
# ============================================================
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # desenha fundo
    screen.blit(background, (0, 0))

    # lógica
    mage.update(dt)
    check_coin_collision()
    spawn_coin()

    # desenha moedas e mago
    for coin in coins:
        coin.draw(screen)

    mage.draw(screen)

    pygame.display.flip()

pygame.quit()
