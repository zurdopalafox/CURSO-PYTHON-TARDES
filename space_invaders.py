#!/usr/bin/env python3
"""
Space Invaders minimal en Python + Pygame
Archivo: space_invaders.py

Requisitos: pip install pygame

Controles:
 - Izquierda/Derecha o A/D: mover la nave
 - Espacio: disparar
 - R: reiniciar tras perder
 - Esc / cerrar ventana: salir
"""

import pygame
import random
import sys

# --- Configuración ---
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_WIDTH, PLAYER_HEIGHT = 60, 20
PLAYER_COLOR = (50, 200, 255)
PLAYER_SPEED = 6
PLAYER_Y_OFFSET = 60
PLAYER_LIVES = 3

BULLET_COLOR = (255, 255, 0)
BULLET_SPEED = -9
BULLET_RADIUS = 4
MAX_PLAYER_BULLETS = 1

ENEMY_ROWS = 4
ENEMY_COLS = 8
ENEMY_X_GAP = 80
ENEMY_Y_GAP = 60
ENEMY_START_X = 80
ENEMY_START_Y = 60
ENEMY_WIDTH, ENEMY_HEIGHT = 44, 26
ENEMY_COLOR = (200, 80, 80)
ENEMY_X_SPEED = 1.2
ENEMY_DROP = 20

ENEMY_BULLET_SPEED = 4
ENEMY_BULLET_COLOR = (255, 120, 50)
ENEMY_SHOOT_PROB = 0.0025  # probabilidad por enemigo por frame de disparar

FONT_NAME = None  # usa la fuente por defecto


# --- Inicialización ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - PyGame")
clock = pygame.time.Clock()
font = pygame.font.SysFont(FONT_NAME, 22)
big_font = pygame.font.SysFont(FONT_NAME, 48)


# --- Clases del juego ---
class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = WIDTH // 2
        self.y = HEIGHT - PLAYER_Y_OFFSET
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES

    @property
    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))

    def draw(self, surf):
        pygame.draw.rect(surf, PLAYER_COLOR, self.rect)


class Bullet:
    def __init__(self, x, y, vy, color):
        self.x = x
        self.y = y
        self.vy = vy
        self.color = color

    def update(self):
        self.y += self.vy

    def off_screen(self):
        return self.y < -10 or self.y > HEIGHT + 10

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), BULLET_RADIUS)

    def rect(self):
        return pygame.Rect(self.x - BULLET_RADIUS, self.y - BULLET_RADIUS, BULLET_RADIUS * 2, BULLET_RADIUS * 2)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def draw(self, surf):
        if not self.alive:
            return
        pygame.draw.rect(surf, ENEMY_COLOR, self.rect)


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.enemy_dir = 1
        self.enemy_speed = ENEMY_X_SPEED
        self.spawn_enemies()

    def spawn_enemies(self):
        self.enemies = []
        for r in range(ENEMY_ROWS):
            for c in range(ENEMY_COLS):
                x = ENEMY_START_X + c * ENEMY_X_GAP
                y = ENEMY_START_Y + r * ENEMY_Y_GAP
                self.enemies.append(Enemy(x, y))

    def update_enemies(self):
        # calcular bounds de enemigos vivos
        alive = [e for e in self.enemies if e.alive]
        if not alive:
            self.game_over = True
            return
        min_x = min(e.x for e in alive)
        max_x = max(e.x for e in alive)

        # invertir dirección si toca borde
        if (max_x + ENEMY_WIDTH // 2 >= WIDTH and self.enemy_dir > 0) or (min_x - ENEMY_WIDTH // 2 <= 0 and self.enemy_dir < 0):
            self.enemy_dir *= -1
            for e in alive:
                e.y += ENEMY_DROP
        else:
            for e in alive:
                e.x += self.enemy_dir * self.enemy_speed

        # disparos aleatorios
        for e in alive:
            if random.random() < ENEMY_SHOOT_PROB:
                self.enemy_bullets.append(Bullet(e.x, e.y + e.h // 2 + 6, ENEMY_BULLET_SPEED, ENEMY_BULLET_COLOR))

    def handle_collisions(self):
        # player bullets vs enemies
        for b in list(self.player_bullets):
            br = b.rect()
            for e in self.enemies:
                if e.alive and br.colliderect(e.rect):
                    e.alive = False
                    try:
                        self.player_bullets.remove(b)
                    except ValueError:
                        pass
                    self.score += 10
                    break

        # enemy bullets vs player
        for b in list(self.enemy_bullets):
            if b.rect().colliderect(self.player.rect):
                try:
                    self.enemy_bullets.remove(b)
                except ValueError:
                    pass
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_over = True

        # enemies reaching player
        for e in self.enemies:
            if e.alive and e.y + e.h // 2 >= self.player.y - self.player.height // 2:
                self.game_over = True

    def update(self, keys):
        if self.game_over:
            return

        # player movement
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        self.player.move(dx)

        # bullets
        for b in list(self.player_bullets):
            b.update()
            if b.off_screen():
                try:
                    self.player_bullets.remove(b)
                except ValueError:
                    pass

        for b in list(self.enemy_bullets):
            b.update()
            if b.off_screen():
                try:
                    self.enemy_bullets.remove(b)
                except ValueError:
                    pass

        self.update_enemies()
        self.handle_collisions()

    def player_shoot(self):
        if len(self.player_bullets) < MAX_PLAYER_BULLETS and not self.game_over:
            x = self.player.x
            y = self.player.y - self.player.height // 2 - 6
            self.player_bullets.append(Bullet(x, y, BULLET_SPEED, BULLET_COLOR))

    def draw(self, surf):
        surf.fill((10, 10, 30))
        # draw player
        self.player.draw(surf)

        # draw bullets
        for b in self.player_bullets:
            b.draw(surf)
        for b in self.enemy_bullets:
            b.draw(surf)

        # draw enemies
        for e in self.enemies:
            e.draw(surf)

        # UI
        score_s = font.render(f"Puntos: {self.score}", True, (255, 255, 255))
        lives_s = font.render(f"Vidas: {self.player.lives}", True, (255, 255, 255))
        surf.blit(score_s, (10, 10))
        surf.blit(lives_s, (WIDTH - 110, 10))

        if self.game_over:
            msg = "Has perdido - R para reiniciar"
            if all(not e.alive for e in self.enemies):
                msg = "Has ganado! - R para jugar de nuevo"
            text = big_font.render(msg, True, (255, 255, 255))
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            surf.blit(text, rect)


def main():
    game = Game()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.player_shoot()
                elif event.key == pygame.K_r:
                    game.reset()

        keys = pygame.key.get_pressed()
        game.update(keys)

        game.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error en ejecución:', e)
        pygame.quit()
        raise
