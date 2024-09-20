import pygame
import sys
import random
from PIL import Image

# Inicializa o Pygame
pygame.init()

# Configurações da tela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Vai Fumar?')

# Cores
black = (0, 0, 0)
white = (255, 255, 255)
dark_yellow = (204, 153, 0)
light_gray = (200, 200, 200)
gray = (100, 100, 100)

# Carregar sons (certifique-se de que os arquivos de som estão no mesmo diretório)
paddle_hit_sound = pygame.mixer.Sound('paddle_hit.wav')
block_hit_sound = pygame.mixer.Sound('block_hit.wav')
wall_hit_sound = pygame.mixer.Sound('wall_hit.wav')
game_over_sound = pygame.mixer.Sound('game_over.wav')

# Configurações das fontes
title_font = pygame.font.SysFont('Arial', 40)
button_font = pygame.font.SysFont('Arial', 25)
small_font = pygame.font.SysFont('Arial', 15)
counter_font = pygame.font.SysFont('Arial', 20)

# Função para redimensionar a imagem e convertê-la para padrão de matriz
def image_to_pattern(image_path, new_width, new_height, threshold=128):
    img = Image.open(image_path).convert('L')  # Converte a imagem para escala de cinza
    img = img.resize((new_width, new_height))  # Redimensiona a imagem
    width, height = img.size
    pixels = img.load()

    pattern = []
    for y in range(height):
        row = ""
        for x in range(width):
            if pixels[x, y] < threshold:
                row += "1"
            else:
                row += "0"
        pattern.append(row)
    
    return pattern

# Caminho da imagem
image_path = 'pulmao.png'  # Certifique-se de que a imagem está no mesmo diretório

# Configurações do novo tamanho da imagem
new_width = 80
new_height = 60

# Converte a imagem para padrão de matriz
lung_pattern = image_to_pattern(image_path, new_width, new_height)

# Classe da Raquete
class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 10
        self.speed = 10
        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.yellow_width = int(self.width * 0.2)
        self.smoke = []

    def move(self, direction):
        if direction == 'left' and self.rect.left > 0:
            self.rect.x -= self.speed
        if direction == 'right' and self.rect.right < screen_width:
            self.rect.x += self.speed

    def draw(self, screen):
        # Desenhar a parte amarela da raquete (cigarro)
        pygame.draw.rect(screen, dark_yellow, (self.rect.left, self.rect.top, self.yellow_width, self.height))
        # Desenhar a parte branca da raquete
        pygame.draw.rect(screen, white, (self.rect.left + self.yellow_width, self.rect.top, self.width - self.yellow_width, self.height))
        # Desenhar a fumaça do cigarro
        for smoke in self.smoke:
            pygame.draw.circle(screen, light_gray, smoke, 1)

    def update_smoke(self):
        if random.random() < 0.5:
            self.smoke.append((self.rect.right, self.rect.top))
        if len(self.smoke) > 10:
            self.smoke.pop(0)

# Classe da Bola
class Ball:
    def __init__(self, x, y):
        self.size = 10
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.speed_x = 0  # Movimento horizontal zero inicialmente
        self.speed_y = 3  # Velocidade inicial para cair lentamente
        self.smoke_trail = []
        self.first_contact = False  # Indica se já tocou a raquete pela primeira vez

    def move(self):
        # Se ainda não teve o primeiro contato, mover apenas verticalmente
        if not self.first_contact:
            self.speed_x = 0  # Garantir que não haja movimento horizontal

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Adicionar posição atual da bola à trilha de fumaça
        self.smoke_trail.append((self.rect.centerx, self.rect.centery))
        if len(self.smoke_trail) > 10:
            self.smoke_trail.pop(0)

        # Colisão com as paredes (laterais) após o primeiro contato
        if self.first_contact and (self.rect.left <= 0 or self.rect.right >= screen_width):
            self.speed_x *= -1  # Inverte a direção horizontal
            if game.sound_on:
                wall_hit_sound.play()

        # Colisão com o topo da tela após o primeiro contato
        if self.rect.top <= 0 and self.first_contact:
            # Maior probabilidade de continuar descendo
            if random.random() < 0.7:
                self.speed_y = abs(self.speed_y)  # Continua descendo
            else:
                self.speed_y *= -1  # Inverte a direção (sobe)
            if game.sound_on:
                wall_hit_sound.play()

    def draw(self, screen):
        pygame.draw.ellipse(screen, white, self.rect)
        for smoke in self.smoke_trail:
            pygame.draw.circle(screen, light_gray, smoke, 1)

    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 3
        self.smoke_trail.clear()
        self.first_contact = False  # Resetar o estado

# Classe dos Blocos
class Block:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = white

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Classe do Jogo
class Game:
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball(screen_width // 2 - 5, 0)  # Começar no topo central
        self.blocks = []
        self.block_size = 8
        self.block_spacing = 1
        self.block_y_offset = 1
        self.level = 1
        self.score = 0
        self.anos_de_vida = 100
        self.total_blocks = 0
        self.in_menu = True
        self.in_game_over = False
        self.running = True
        self.paused = False  # Estado de pausa
        self.sound_on = True  # Som ligado por padrão
        self.clock = pygame.time.Clock()
        self.load_level(self.level)

    def load_level(self, level):
        self.blocks.clear()
        start_x = (screen_width - (len(lung_pattern[0]) * (self.block_size + self.block_spacing))) // 2
        for row_idx, row in enumerate(lung_pattern):
            for col_idx, col in enumerate(row):
                if col == "1":
                    x = start_x + col_idx * (self.block_size + self.block_spacing)
                    y = row_idx * (self.block_size + self.block_spacing) + self.block_y_offset
                    block = Block(x, y, self.block_size, self.block_size)
                    self.blocks.append(block)
        self.total_blocks = len(self.blocks)

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball(screen_width // 2 - 5, 0)  # Começar no topo central
        self.level = 1
        self.score = 0
        self.load_level(self.level)
        self.in_game_over = False
        self.paused = False

    def draw_menu(self):
        screen.fill(black)
        title_text = title_font.render("Vai fumar?", True, white)
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
        screen.blit(title_text, title_rect)

        # Botão Jogar
        play_button = pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 25, 100, 50)
        pygame.draw.rect(screen, gray, play_button)
        play_text = button_font.render("Jogar", True, white)
        play_text_rect = play_text.get_rect(center=play_button.center)
        screen.blit(play_text, play_text_rect)

        # Botão de Som
        sound_button = pygame.Rect(screen_width // 2 - 50, screen_height // 2 + 40, 100, 50)
        pygame.draw.rect(screen, gray, sound_button)
        sound_text = button_font.render(f"Som: {'On' if self.sound_on else 'Off'}", True, white)
        sound_text_rect = sound_text.get_rect(center=sound_button.center)
        screen.blit(sound_text, sound_text_rect)

        # Créditos
        credit_text = small_font.render("Criado por Lauro, como forma de estudo", True, white)
        credit_rect = credit_text.get_rect(bottomright=(screen_width - 10, screen_height - 10))
        screen.blit(credit_text, credit_rect)

        pygame.display.flip()
        return play_button, sound_button

    def draw_game_over(self):
        # Calcular os anos de vida com base nos blocos restantes
        self.anos_de_vida = int((len(self.blocks) / self.total_blocks) * 100)

        screen.fill(black)
        game_over_text1 = title_font.render("Você parou de fumar!", True, white)
        game_over_text2 = title_font.render("Anos de Vida restantes:", True, white)
        game_over_rect1 = game_over_text1.get_rect(center=(screen_width // 2, screen_height // 2 - 130))
        game_over_rect2 = game_over_text2.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
        screen.blit(game_over_text1, game_over_rect1)
        screen.blit(game_over_text2, game_over_rect2)

        anos_de_vida_text = title_font.render(f"{self.anos_de_vida}", True, white)
        anos_de_vida_rect = anos_de_vida_text.get_rect(center=(screen_width // 2, screen_height // 2 - 30))
        screen.blit(anos_de_vida_text, anos_de_vida_rect)

        retry_button = pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 20, 150, 50)
        pygame.draw.rect(screen, gray, retry_button)
        retry_text = button_font.render("Jogar de novo", True, white)
        retry_text_rect = retry_text.get_rect(center=retry_button.center)
        screen.blit(retry_text, retry_text_rect)

        credit_text = small_font.render("Criado por Lauro, como forma de estudo", True, white)
        credit_rect = credit_text.get_rect(bottomright=(screen_width - 10, screen_height - 10))
        screen.blit(credit_text, credit_rect)

        pygame.display.flip()
        return retry_button

    def draw(self):
        screen.fill(black)
        self.paddle.draw(screen)
        self.ball.draw(screen)
        for block in self.blocks:
            block.draw(screen)

        # Exibir a pontuação
        score_text = counter_font.render(f"Pontos: {self.score}", True, white)
        score_rect = score_text.get_rect(topleft=(10, 10))
        screen.blit(score_text, score_rect)

        # Calcular e exibir os Anos de Vida durante o jogo
        self.anos_de_vida = int((len(self.blocks) / self.total_blocks) * 100)
        vida_text = counter_font.render(f"Anos de Vida: {self.anos_de_vida}", True, white)
        vida_rect = vida_text.get_rect(topleft=(10, 40))
        screen.blit(vida_text, vida_rect)

        # Exibir mensagem de pausa
        if self.paused:
            pause_text = title_font.render("Pausado", True, white)
            pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(pause_text, pause_rect)

        text_surface = small_font.render("Pressione 'P' para pausar", True, white)
        text_rect = text_surface.get_rect(bottomright=(screen_width - 10, screen_height - 5))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

    def handle_collisions(self):
        # Colisão da bola com a raquete
        if self.ball.rect.colliderect(self.paddle.rect):
            self.ball.speed_y = -abs(self.ball.speed_y)  # Bola sempre sobe após bater na raquete
            if self.sound_on:
                paddle_hit_sound.play()
            if not self.ball.first_contact:
                self.ball.first_contact = True
                # Após o primeiro contato, definir uma velocidade horizontal aleatória
                self.ball.speed_x = random.choice([3, -3])
                self.ball.speed_y = -3  # Iniciar com movimento para cima após rebater

        # Colisão da bola com os blocos
        hit_index = self.ball.rect.collidelist([block.rect for block in self.blocks])
        if hit_index != -1:
            if self.sound_on:
                block_hit_sound.play()
            block = self.blocks.pop(hit_index)
            self.score += 10
            if self.ball.first_contact:
                # Maior probabilidade de continuar descendo após colidir com blocos
                if random.random() < 0.7:
                    self.ball.speed_y = abs(self.ball.speed_y)  # Continua descendo
                else:
                    self.ball.speed_y = -abs(self.ball.speed_y)  # Sobe
            else:
                # Durante a descida inicial, a bola não muda de direção
                pass  # A bola continua descendo

    def run(self):
        while self.running:
            if self.in_menu:
                play_button, sound_button = self.draw_menu()
            elif self.in_game_over:
                retry_button = self.draw_game_over()
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.paddle.move('left')
                if keys[pygame.K_RIGHT]:
                    self.paddle.move('right')

                if not self.paused:
                    self.ball.move()
                    self.paddle.update_smoke()
                    self.handle_collisions()

                    # Verificar se a bola saiu da tela inferior
                    if self.ball.rect.bottom >= screen_height:
                        self.in_game_over = True
                        if self.sound_on:
                            game_over_sound.play()

                self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.in_menu:
                        if play_button.collidepoint(event.pos):
                            self.in_menu = False
                        elif sound_button.collidepoint(event.pos):
                            self.sound_on = not self.sound_on  # Alternar som
                    elif self.in_game_over:
                        if retry_button.collidepoint(event.pos):
                            self.reset_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and not self.in_menu and not self.in_game_over:
                        self.paused = not self.paused  # Alternar pausa

            self.clock.tick(60)

        pygame.quit()
        sys.exit()

# Iniciar o jogo
if __name__ == '__main__':
    game = Game()
    game.run()
