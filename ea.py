import pygame
import math
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pembantaian Suki Liar - JMK48 Edition")
clock = pygame.time.Clock()

CX, CY = WIDTH // 2, HEIGHT // 2

def to_screen(x, y):
    return CX + x, CY - y

def draw_axes():
    pygame.draw.line(screen, (50,50,50), (0, CY), (WIDTH, CY), 1)
    pygame.draw.line(screen, (50,50,50), (CX, 0), (CX, HEIGHT), 1)

# ===== LOAD IMAGE =====
player_img = pygame.image.load("assets/rus.jpg").convert_alpha()
enemy_img = pygame.image.load("assets/suki.jpg").convert_alpha()
boss_img = pygame.image.load("assets/boss.jpg").convert_alpha()
win_img = pygame.image.load("assets/win.png").convert_alpha()
lose_img = pygame.image.load("assets/lose.png").convert_alpha()

font = pygame.font.SysFont(None, 26)
big_font = pygame.font.SysFont(None, 56)

MAX_WAVE = 6
p_size = 65

def reset_game():
    return {
        "px": 0,
        "py": 0,
        "angle": 0,
        "health": 100,
        "bullets": [],
        "enemies": [],
        "score": 0,
        "wave": 1,
        "spawned": 0,
        "killed": 0,
        "spawn_delay": 60,
        "boss_spawned": False,
        "game_over": False,
        "game_win": False
    }

state = reset_game()

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return {"x": random.randint(-400, 400), "y": 350}
    if side == "bottom":
        return {"x": random.randint(-400, 400), "y": -350}
    if side == "left":
        return {"x": -450, "y": random.randint(-300, 300)}
    return {"x": 450, "y": random.randint(-300, 300)}

def draw_button(rect, text):
    pygame.draw.rect(screen, (40,40,40), rect, border_radius=8)
    pygame.draw.rect(screen, (255,255,255), rect, 2, border_radius=8)
    label = font.render(text, True, (255,255,255))
    screen.blit(label, label.get_rect(center=rect.center))

running = True
while running:
    clock.tick(60)
    screen.fill((15,15,15))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state["game_over"] or state["game_win"]:
                if restart_btn.collidepoint(event.pos):
                    state = reset_game()
                if exit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    if not state["game_over"] and not state["game_win"]:
        draw_axes()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: state["px"] -= 5
        if keys[pygame.K_d]: state["px"] += 5
        if keys[pygame.K_w]: state["py"] += 5
        if keys[pygame.K_s]: state["py"] -= 5

        mx, my = pygame.mouse.get_pos()
        dx = mx - (CX + state["px"])
        dy = (CY - state["py"]) - my
        state["angle"] = math.degrees(math.atan2(dy, dx))

        if pygame.mouse.get_pressed()[0]:
            rad = math.radians(state["angle"])
            state["bullets"].append({
                "x": state["px"],
                "y": state["py"],
                "dx": math.cos(rad) * 12,
                "dy": math.sin(rad) * 12
            })

        for b in state["bullets"][:]:
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            if abs(b["x"]) > 600 or abs(b["y"]) > 500:
                state["bullets"].remove(b)

        enemy_limit = 6 + state["wave"] * 4
        boss_exist = 1 if state["wave"] % 3 == 0 else 0
        total_enemy = enemy_limit + boss_exist

        if state["spawned"] < enemy_limit:
            state["spawn_delay"] -= 1
            if state["spawn_delay"] <= 0:
                pos = spawn_enemy()
                state["enemies"].append({
                    "x": pos["x"],
                    "y": pos["y"],
                    "size": 50 + state["wave"] * 4,
                    "speed": 1.2 + state["wave"] * 0.2,
                    "hp": 60 + state["wave"] * 25,
                    "max_hp": 60 + state["wave"] * 25,
                    "is_boss": False
                })
                state["spawned"] += 1
                state["spawn_delay"] = max(20, 60 - state["wave"] * 5)

        if state["wave"] % 3 == 0 and state["spawned"] == enemy_limit and not state["boss_spawned"]:
            pos = spawn_enemy()
            state["enemies"].append({
                "x": pos["x"],
                "y": pos["y"],
                "size": 160,
                "speed": 0.8,
                "hp": 1500,
                "max_hp": 1500,
                "is_boss": True
            })
            state["spawned"] += 1
            state["boss_spawned"] = True

        for e in state["enemies"][:]:
            vx = state["px"] - e["x"]
            vy = state["py"] - e["y"]
            dist = math.hypot(vx, vy)
            if dist != 0:
                vx /= dist
                vy /= dist
            e["x"] += vx * e["speed"]
            e["y"] += vy * e["speed"]

            if math.hypot(e["x"] - state["px"], e["y"] - state["py"]) < e["size"]/2:
                state["enemies"].remove(e)
                state["health"] -= 25 if e["is_boss"] else 10
                if state["health"] <= 0:
                    state["game_over"] = True

        for b in state["bullets"][:]:
            for e in state["enemies"][:]:
                if math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["size"]/2:
                    state["bullets"].remove(b)
                    e["hp"] -= 20
                    if e["hp"] <= 0:
                        state["enemies"].remove(e)
                        state["killed"] += 1
                        state["score"] += 150 if e["is_boss"] else 10
                    break

        # ===== FIX WAVE CLEAR =====
        if state["spawned"] >= total_enemy and len(state["enemies"]) == 0:
            if state["wave"] < MAX_WAVE:
                state["wave"] += 1
                state["spawned"] = 0
                state["killed"] = 0
                state["spawn_delay"] = 60
                state["boss_spawned"] = False
            else:
                state["game_win"] = True

    # ===== DRAW PLAYER =====
    p_img = pygame.transform.rotate(
        pygame.transform.scale(player_img, (p_size, p_size)),
        state["angle"]
    )
    psx, psy = to_screen(state["px"], state["py"])
    screen.blit(p_img, p_img.get_rect(center=(psx, psy)))

    # ===== BULLET =====
    for b in state["bullets"]:
        sx, sy = to_screen(b["x"], b["y"])
        pygame.draw.circle(screen, (255,255,0), (sx, sy), 4)

    # ===== ENEMY =====
    for e in state["enemies"]:
        img = boss_img if e["is_boss"] else enemy_img
        size = e["size"]
        img = pygame.transform.scale(img, (size, size))
        sx, sy = to_screen(e["x"], e["y"])
        rect = img.get_rect(center=(sx, sy))
        screen.blit(img, rect)

        ratio = e["hp"] / e["max_hp"]
        pygame.draw.rect(screen, (120,0,0), (rect.left, rect.top - 8, size, 5))
        pygame.draw.rect(screen, (0,255,0), (rect.left, rect.top - 8, size * ratio, 5))

    # ===== UI =====
    pygame.draw.rect(screen, (40,40,40), (0, 0, WIDTH, 30))
    screen.blit(font.render(f"Wave {state['wave']} / {MAX_WAVE}", True, (255,200,50)), (10, 6))

    pygame.draw.rect(screen, (255,0,0), (10, 50, 200, 15))
    pygame.draw.rect(screen, (0,255,0), (10, 50, 200 * (state["health"]/100), 15))
    screen.blit(font.render("HP", True, (255,255,255)), (10, 30))
    screen.blit(font.render(f"Score: {state['score']}", True, (255,255,255)), (10, 75))

    # ===== END SCREEN =====
    if state["game_over"] or state["game_win"]:
        dark = pygame.Surface((WIDTH, HEIGHT))
        dark.set_alpha(120)
        dark.fill((0,0,0))
        screen.blit(dark, (0,0))

        img = win_img if state["game_win"] else lose_img
        img = pygame.transform.scale(img, (380, 260))
        img.set_alpha(180)
        screen.blit(img, img.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))

        title = "YOU WIN" if state["game_win"] else "YOU LOSE"
        color = (0,255,0) if state["game_win"] else (255,70,70)
        screen.blit(big_font.render(title, True, color), (WIDTH//2 - 120, 60))

        restart_btn = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 150, 220, 40)
        exit_btn = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 200, 220, 40)
        draw_button(restart_btn, "Retry")
        draw_button(exit_btn, "Exit Game")

    pygame.display.flip()

pygame.quit()
