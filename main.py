import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
GRID_COLS = WIDTH // TILE_SIZE
GRID_ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("October 13th")
clock = pygame.time.Clock()

player_width = 28
player_height = 28
player_speed = 4

world_width = 2
world_height = 2
current_screen_x = 0
current_screen_y = 0

spawn_screen_x = 0
spawn_screen_y = 0
spawn_player_x = WIDTH // 2 - player_width // 2
spawn_player_y = HEIGHT // 2 - player_height // 2

player_x = spawn_player_x
player_y = spawn_player_y
facing = "down"

has_sword = False
pickup_timer = 0
pickup_duration = 45

attack_duration = 10
attack_timer = 0
is_attacking = False
attack_hit_enemies = set()

walk_frame = 0
walk_timer = 0

is_transitioning = False
transition_direction = None
transition_progress = 0
transition_speed = 18

old_screen_x = 0
old_screen_y = 0
new_screen_x = 0
new_screen_y = 0

arrival_cooldown = 0

max_health = 8
player_health = 8

money = 0

invincible_timer = 0
invincible_duration = 60
player_flash_timer = 0
player_knockback_timer = 0
player_knockback_dx = 0
player_knockback_dy = 0

dialogue_open = False
dialogue_text = ""
dialogue_visible_count = 0
dialogue_type_speed = 2
dialogue_type_timer = 0

game_state = "playing"

interaction_objects = [
    {
        "id": "warning_sign",
        "screen_x": 1,
        "screen_y": 0,
        "x": 470,
        "y": 210,
        "width": 28,
        "height": 28,
        "text": "Beware of enemy.",
    }
]

interaction_objects = [
    {
        "id": "warning_sign",
        "screen_x": 1,
        "screen_y": 0,
        "x": 470,
        "y": 210,
        "width": 28,
        "height": 28,
        "text": "Beware of enemy.",
    }
]

dialogue_open = False
dialogue_text = ""
dialogue_visible_count = 0
dialogue_type_speed = 2
dialogue_type_timer = 0

sword_pickup = {
    "screen_x": 0,
    "screen_y": 0,
    "x": 520,
    "y": 300,
    "collected": False,
}

drops = []

enemies = [
    {
        "id": "enemy_1",
        "screen_x": 1,
        "screen_y": 0,
        "spawn_x": 620,
        "spawn_y": 160,
        "x": 620,
        "y": 160,
        "width": 26,
        "height": 26,
        "alive": True,
        "hp": 2,
        "max_hp": 2,
        "speed": 2,
        "damage": 1,
        "type": "normal",
        "move_dir": 1,
        "move_timer": 0,
        "axis": "vertical",
        "hurt_flash_timer": 0,
    },
    {
        "id": "enemy_big",
        "screen_x": 1,
        "screen_y": 1,
        "spawn_x": 420,
        "spawn_y": 360,
        "x": 420,
        "y": 360,
        "width": 40,
        "height": 40,
        "alive": True,
        "hp": 4,
        "max_hp": 4,
        "speed": 1,
        "damage": 2,
        "type": "heavy",
        "move_dir": 1,
        "move_timer": 0,
        "axis": "vertical",
        "hurt_flash_timer": 0,
    },
    {
        "id": "enemy_fast",
        "screen_x": 0,
        "screen_y": 1,
        "spawn_x": 120,
        "spawn_y": 120,
        "x": 120,
        "y": 120,
        "width": 22,
        "height": 22,
        "alive": True,
        "hp": 1,
        "max_hp": 1,
        "speed": 4,
        "damage": 1,
        "type": "fast",
        "path_index": 0,
        "path_dir": 1,
        "dir_change_timer": 0,
        "hurt_flash_timer": 0,
    }
]


def create_screen_map(screen_x, screen_y):
    map_data = []

    for row in range(GRID_ROWS):
        new_row = []
        for col in range(GRID_COLS):
            if row == 0 or row == GRID_ROWS - 1 or col == 0 or col == GRID_COLS - 1:
                new_row.append(1)
            else:
                new_row.append(0)
        map_data.append(new_row)

    door_width = 3
    middle_cols_start = (GRID_COLS // 2) - 1
    middle_rows_start = (GRID_ROWS // 2) - 1

    has_up = screen_y > 0
    has_down = screen_y < world_height - 1
    has_left = screen_x > 0
    has_right = screen_x < world_width - 1

    if has_up:
        for col in range(middle_cols_start, middle_cols_start + door_width):
            map_data[0][col] = 2

    if has_down:
        for col in range(middle_cols_start, middle_cols_start + door_width):
            map_data[GRID_ROWS - 1][col] = 2

    if has_left:
        for row in range(middle_rows_start, middle_rows_start + door_width):
            map_data[row][0] = 2

    if has_right:
        for row in range(middle_rows_start, middle_rows_start + door_width):
            map_data[row][GRID_COLS - 1] = 2

    if screen_x == 0 and screen_y == 0:
        for col in range(4, 16):
            map_data[4][col] = 1
        for row in range(8, 12):
            map_data[row][6] = 1

    elif screen_x == 1 and screen_y == 0:
        for row in range(3, 12):
            map_data[row][9] = 1
        for col in range(11, 17):
            map_data[8][col] = 1

    elif screen_x == 0 and screen_y == 1:
        for col in range(3, 9):
            map_data[7][col] = 1
        for col in range(11, 17):
            map_data[7][col] = 1
        for row in range(3, 6):
            map_data[row][13] = 1

    elif screen_x == 1 and screen_y == 1:
        for row in range(3, 12):
            map_data[row][5] = 1
        for row in range(3, 12):
            map_data[row][14] = 1
        for col in range(5, 15):
            map_data[6][col] = 1

    return map_data


def collides_with_wall(test_x, test_y, map_data, width, height):
    test_rect = pygame.Rect(test_x, test_y, width, height)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if map_data[row][col] == 1:
                wall_rect = pygame.Rect(
                    col * TILE_SIZE,
                    row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                if test_rect.colliderect(wall_rect):
                    return True

    return False

def start_transition(direction, target_x, target_y, new_px, new_py):
    global is_transitioning
    global transition_direction
    global transition_progress
    global old_screen_x, old_screen_y
    global new_screen_x, new_screen_y
    global current_screen_x, current_screen_y
    global player_x, player_y
    global arrival_cooldown

    is_transitioning = True
    transition_direction = direction
    transition_progress = 0

    old_screen_x = current_screen_x
    old_screen_y = current_screen_y
    new_screen_x = target_x
    new_screen_y = target_y

    current_screen_x = target_x
    current_screen_y = target_y

    player_x = new_px
    player_y = new_py

    arrival_cooldown = 10

def try_move(current_x, current_y, move_x, move_y, map_data, width, height):
    new_x = current_x
    new_y = current_y

    if move_x != 0:
        test_x = current_x + move_x
        if not collides_with_wall(test_x, current_y, map_data, width, height):
            new_x = test_x

    if move_y != 0:
        test_y = current_y + move_y
        if not collides_with_wall(new_x, test_y, map_data, width, height):
            new_y = test_y

    return new_x, new_y


def get_attack_rect(x, y, direction):
    attack_size = 18

    if direction == "up":
        return pygame.Rect(
            x + (player_width // 2) - (attack_size // 2),
            y - attack_size,
            attack_size,
            attack_size
        )
    elif direction == "down":
        return pygame.Rect(
            x + (player_width // 2) - (attack_size // 2),
            y + player_height,
            attack_size,
            attack_size
        )
    elif direction == "left":
        return pygame.Rect(
            x - attack_size,
            y + (player_height // 2) - (attack_size // 2),
            attack_size,
            attack_size
        )
    else:
        return pygame.Rect(
            x + player_width,
            y + (player_height // 2) - (attack_size // 2),
            attack_size,
            attack_size
        )


def draw_sword(surface, x, y, direction):
    blade_color = (220, 220, 90)
    hilt_color = (130, 80, 30)

    if direction == "up":
        pygame.draw.rect(surface, blade_color, (x + 11, y - 16, 6, 16))
        pygame.draw.rect(surface, hilt_color, (x + 8, y - 3, 12, 4))
    elif direction == "down":
        pygame.draw.rect(surface, blade_color, (x + 11, y + player_height, 6, 16))
        pygame.draw.rect(surface, hilt_color, (x + 8, y + player_height + 12, 12, 4))
    elif direction == "left":
        pygame.draw.rect(surface, blade_color, (x - 16, y + 11, 16, 6))
        pygame.draw.rect(surface, hilt_color, (x - 3, y + 8, 4, 12))
    elif direction == "right":
        pygame.draw.rect(surface, blade_color, (x + player_width, y + 11, 16, 6))
        pygame.draw.rect(surface, hilt_color, (x + player_width + 12, y + 8, 4, 12))


def draw_player(surface, x, y, direction, moving, frame, attacking, sword_owned, picking_up, flashing):
    body_color = (255, 255, 255) if flashing else (80, 200, 120)
    eye_color = (20, 20, 20)
    foot_color = (220, 220, 220) if flashing else (50, 160, 95)

    pygame.draw.rect(surface, body_color, (x, y, player_width, player_height))

    if picking_up:
        pygame.draw.rect(surface, eye_color, (x + 6, y + 6, 4, 4))
        pygame.draw.rect(surface, eye_color, (x + 18, y + 6, 4, 4))
    else:
        if direction == "up":
            pygame.draw.rect(surface, eye_color, (x + 6, y + 5, 4, 4))
            pygame.draw.rect(surface, eye_color, (x + 18, y + 5, 4, 4))
        elif direction == "down":
            pygame.draw.rect(surface, eye_color, (x + 6, y + 19, 4, 4))
            pygame.draw.rect(surface, eye_color, (x + 18, y + 19, 4, 4))
        elif direction == "left":
            pygame.draw.rect(surface, eye_color, (x + 5, y + 7, 4, 4))
            pygame.draw.rect(surface, eye_color, (x + 5, y + 17, 4, 4))
        elif direction == "right":
            pygame.draw.rect(surface, eye_color, (x + 19, y + 7, 4, 4))
            pygame.draw.rect(surface, eye_color, (x + 19, y + 17, 4, 4))

    left_foot_y = y + player_height - 4
    right_foot_y = y + player_height - 4

    if moving and not picking_up:
        if frame == 0:
            left_foot_y -= 2
        else:
            right_foot_y -= 2

    pygame.draw.rect(surface, foot_color, (x + 5, left_foot_y, 6, 4))
    pygame.draw.rect(surface, foot_color, (x + 17, right_foot_y, 6, 4))

    if sword_owned:
        if picking_up:
            blade_color = (220, 220, 90)
            hilt_color = (130, 80, 30)
            pygame.draw.rect(surface, blade_color, (x + 11, y - 22, 6, 20))
            pygame.draw.rect(surface, hilt_color, (x + 8, y - 6, 12, 4))
        elif attacking:
            draw_sword(surface, x, y, direction)


def draw_pickup_sword(surface, x, y):
    blade_color = (220, 220, 90)
    hilt_color = (130, 80, 30)
    pygame.draw.rect(surface, blade_color, (x + 7, y, 6, 18))
    pygame.draw.rect(surface, hilt_color, (x + 4, y + 14, 12, 4))


def draw_enemy(surface, enemy):
    if enemy["type"] == "heavy":
        base_color = (140, 60, 60)
    elif enemy["type"] == "fast":
        base_color = (210, 110, 110)
    else:
        base_color = (180, 70, 70)

    color = (255, 255, 255) if enemy["hurt_flash_timer"] > 0 else base_color

    pygame.draw.rect(surface, color, (enemy["x"], enemy["y"], enemy["width"], enemy["height"]))
    pygame.draw.rect(surface, (20, 20, 20), (enemy["x"] + 5, enemy["y"] + 6, 4, 4))
    pygame.draw.rect(surface, (20, 20, 20), (enemy["x"] + enemy["width"] - 9, enemy["y"] + 6, 4, 4))


def draw_sign(surface, obj):
    x = obj["x"]
    y = obj["y"]
    pygame.draw.rect(surface, (145, 105, 65), (x + 10, y + 14, 8, 14))
    pygame.draw.rect(surface, (210, 190, 120), (x, y, 28, 18))
    pygame.draw.rect(surface, (90, 65, 30), (x, y, 28, 18), 2)
    pygame.draw.rect(surface, (90, 65, 30), (x + 7, y + 5, 14, 3))
    pygame.draw.rect(surface, (90, 65, 30), (x + 7, y + 10, 10, 3))


def get_player_rect():
    return pygame.Rect(player_x, player_y, player_width, player_height)


def get_interaction_target():
    player_rect = get_player_rect()

    for obj in interaction_objects:
        if obj["screen_x"] != current_screen_x or obj["screen_y"] != current_screen_y:
            continue

        obj_rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
        prompt_rect = obj_rect.inflate(28, 28)

        if player_rect.colliderect(prompt_rect):
            return obj

    return None


def open_dialogue(text):
    global dialogue_open
    global dialogue_text
    global dialogue_visible_count
    global dialogue_type_timer
    global is_attacking

    dialogue_open = True
    dialogue_text = text
    dialogue_visible_count = 0
    dialogue_type_timer = 0
    is_attacking = False


def update_dialogue():
    global dialogue_visible_count
    global dialogue_type_timer

    if not dialogue_open:
        return

    if dialogue_visible_count < len(dialogue_text):
        dialogue_type_timer += 1
        if dialogue_type_timer >= dialogue_type_speed:
            dialogue_type_timer = 0
            dialogue_visible_count += 1


def draw_text_box(surface):
    if not dialogue_open:
        return

    box_rect = pygame.Rect(40, HEIGHT - 170, WIDTH - 80, 130)
    inner_rect = pygame.Rect(48, HEIGHT - 162, WIDTH - 96, 114)

    pygame.draw.rect(surface, (0, 0, 0), box_rect)
    pygame.draw.rect(surface, (235, 235, 235), box_rect, 3)
    pygame.draw.rect(surface, (25, 25, 25), inner_rect)

    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

    visible_text = dialogue_text[:dialogue_visible_count]
    rendered = font.render(visible_text, True, (240, 240, 240))
    surface.blit(rendered, (70, HEIGHT - 130))

    if dialogue_visible_count >= len(dialogue_text):
        prompt = small_font.render("Press E", True, (220, 220, 140))
        surface.blit(prompt, (WIDTH - 120, HEIGHT - 70))


def draw_interaction_prompt(surface, obj):
    if obj is None or dialogue_open:
        return

    font = pygame.font.SysFont(None, 24)
    text = font.render("E", True, (20, 20, 20))
    label = font.render("Read", True, (235, 235, 235))

    bubble_rect = pygame.Rect(obj["x"] - 2, obj["y"] - 28, 24, 24)
    pygame.draw.rect(surface, (245, 245, 210), bubble_rect)
    pygame.draw.rect(surface, (40, 40, 40), bubble_rect, 2)
    surface.blit(text, (obj["x"] + 5, obj["y"] - 24))
    surface.blit(label, (obj["x"] + 28, obj["y"] - 24))


def draw_health(surface):
    start_x = 22
    start_y = 42
    spacing = 34
    radius = 11

    for i in range(4):
        container_value = max(0, min(2, player_health - (i * 2)))
        center_x = start_x + (i * spacing)
        center_y = start_y

        pygame.draw.circle(surface, (65, 65, 65), (center_x, center_y), radius)
        pygame.draw.circle(surface, (235, 235, 235), (center_x, center_y), radius, 2)

        if container_value == 2:
            pygame.draw.circle(surface, (210, 50, 50), (center_x, center_y), radius - 1)
        elif container_value == 1:
            points = [
                (center_x, center_y - (radius - 1)),
                (center_x, center_y + (radius - 1)),
                (center_x - (radius - 1), center_y + (radius - 1)),
                (center_x - (radius - 1), center_y - (radius - 1)),
            ]
            pygame.draw.polygon(surface, (210, 50, 50), points)
            pygame.draw.circle(surface, (235, 235, 235), (center_x, center_y), radius, 2)

def draw_sign(surface, obj):
    x = obj["x"]
    y = obj["y"]
    pygame.draw.rect(surface, (145, 105, 65), (x + 10, y + 14, 8, 14))
    pygame.draw.rect(surface, (210, 190, 120), (x, y, 28, 18))
    pygame.draw.rect(surface, (90, 65, 30), (x, y, 28, 18), 2)
    pygame.draw.rect(surface, (90, 65, 30), (x + 7, y + 5, 14, 3))
    pygame.draw.rect(surface, (90, 65, 30), (x + 7, y + 10, 10, 3))


def get_interaction_target():
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    for obj in interaction_objects:
        if obj["screen_x"] != current_screen_x or obj["screen_y"] != current_screen_y:
            continue

        obj_rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
        prompt_rect = obj_rect.inflate(28, 28)

        if player_rect.colliderect(prompt_rect):
            return obj

    return None


def open_dialogue(text):
    global dialogue_open
    global dialogue_text
    global dialogue_visible_count
    global dialogue_type_timer
    global is_attacking

    dialogue_open = True
    dialogue_text = text
    dialogue_visible_count = 0
    dialogue_type_timer = 0
    is_attacking = False


def update_dialogue():
    global dialogue_visible_count
    global dialogue_type_timer

    if not dialogue_open:
        return

    if dialogue_visible_count < len(dialogue_text):
        dialogue_type_timer += 1
        if dialogue_type_timer >= dialogue_type_speed:
            dialogue_type_timer = 0
            dialogue_visible_count += 1


def draw_interaction_prompt(surface, obj):
    if obj is None or dialogue_open:
        return

    font = pygame.font.SysFont(None, 24)
    text = font.render("E", True, (20, 20, 20))
    label = font.render("Read", True, (235, 235, 235))

    bubble_rect = pygame.Rect(obj["x"] - 2, obj["y"] - 28, 24, 24)
    pygame.draw.rect(surface, (245, 245, 210), bubble_rect)
    pygame.draw.rect(surface, (40, 40, 40), bubble_rect, 2)
    surface.blit(text, (obj["x"] + 5, obj["y"] - 24))
    surface.blit(label, (obj["x"] + 28, obj["y"] - 24))


def draw_text_box(surface):
    if not dialogue_open:
        return

    box_rect = pygame.Rect(40, HEIGHT - 170, WIDTH - 80, 130)
    inner_rect = pygame.Rect(48, HEIGHT - 162, WIDTH - 96, 114)

    pygame.draw.rect(surface, (0, 0, 0), box_rect)
    pygame.draw.rect(surface, (235, 235, 235), box_rect, 3)
    pygame.draw.rect(surface, (25, 25, 25), inner_rect)

    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 24)

    visible_text = dialogue_text[:dialogue_visible_count]
    rendered = font.render(visible_text, True, (240, 240, 240))
    surface.blit(rendered, (70, HEIGHT - 130))

    if dialogue_visible_count >= len(dialogue_text):
        prompt = small_font.render("Press E", True, (220, 220, 140))
        surface.blit(prompt, (WIDTH - 120, HEIGHT - 70))

def draw_money(surface):
    font = pygame.font.SysFont(None, 28)
    coin = pygame.draw.circle(surface, (180, 120, 40), (28, 80), 8)
    pygame.draw.circle(surface, (235, 210, 120), (28, 80), 8, 2)
    label = font.render(str(money), True, (235, 235, 235))
    surface.blit(label, (44, 70))


def spawn_drop(x, y, screen_x, screen_y, drop_type):
    drops.append({
        "x": x,
        "y": y,
        "screen_x": screen_x,
        "screen_y": screen_y,
        "type": drop_type,
    })


def draw_drops(surface, screen_x, screen_y):
    for d in drops:
        if d["screen_x"] != screen_x or d["screen_y"] != screen_y:
            continue

        if d["type"] == "health":
            pygame.draw.circle(surface, (200, 40, 40), (int(d["x"]), int(d["y"])), 6)
            pygame.draw.circle(surface, (245, 245, 245), (int(d["x"]), int(d["y"])), 6, 1)
        elif d["type"] == "money":
            pygame.draw.circle(surface, (180, 120, 40), (int(d["x"]), int(d["y"])), 6)
            pygame.draw.circle(surface, (235, 210, 120), (int(d["x"]), int(d["y"])), 6, 1)


def update_drops():
    global player_health
    global money

    player_rect = get_player_rect()

    for d in drops[:]:
        if d["screen_x"] != current_screen_x or d["screen_y"] != current_screen_y:
            continue

        drop_rect = pygame.Rect(d["x"] - 6, d["y"] - 6, 12, 12)

        if player_rect.colliderect(drop_rect):
            if d["type"] == "health":
                player_health = min(max_health, player_health + 2)
            elif d["type"] == "money":
                money += 1

            drops.remove(d)


def reset_world_state():
    global player_health
    global invincible_timer
    global player_flash_timer
    global player_knockback_timer
    global player_knockback_dx
    global player_knockback_dy
    global current_screen_x
    global current_screen_y
    global player_x
    global player_y
    global facing
    global dialogue_open
    global is_attacking
    global attack_timer
    global attack_hit_enemies
    global arrival_cooldown
    global is_transitioning
    global transition_progress
    global drops
    global game_state

    player_health = max_health
    invincible_timer = 0
    player_flash_timer = 0
    player_knockback_timer = 0
    player_knockback_dx = 0
    player_knockback_dy = 0

    current_screen_x = spawn_screen_x
    current_screen_y = spawn_screen_y
    player_x = spawn_player_x
    player_y = spawn_player_y
    facing = "down"

    dialogue_open = False
    is_attacking = False
    attack_timer = 0
    attack_hit_enemies.clear()
    arrival_cooldown = 0
    is_transitioning = False
    transition_progress = 0
    drops = []
    game_state = "playing"

    for enemy in enemies:
        enemy["alive"] = True
        enemy["hp"] = enemy["max_hp"]
        enemy["x"] = enemy["spawn_x"]
        enemy["y"] = enemy["spawn_y"]
        enemy["hurt_flash_timer"] = 0

        if enemy["type"] in ("normal", "heavy"):
            enemy["move_dir"] = 1
            enemy["move_timer"] = 0

        if enemy["type"] == "fast":
            enemy["path_index"] = 0
            enemy["path_dir"] = 1
            enemy["dir_change_timer"] = 0


def get_fast_enemy_target_points():
    return [
        (80, 80),
        (WIDTH - 120, 80),
        (WIDTH - 120, HEIGHT - 120),
        (80, HEIGHT - 120),
    ]


def move_fast_enemy(enemy, current_map):
    enemy["dir_change_timer"] += 1

    if enemy["dir_change_timer"] >= 45:
        enemy["dir_change_timer"] = 0
        if random.random() < 0.25:
            enemy["path_dir"] *= -1
def draw_money(surface):
    font = pygame.font.SysFont(None, 28)
    money_text = font.render(f"${money}", True, (190, 140, 60))
    surface.blit(money_text, (18, 72))


def draw_game_over(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont(None, 72)
    option_font = pygame.font.SysFont(None, 40)

    title = title_font.render("GAME OVER", True, (230, 230, 230))
    option = option_font.render("> Continue?", True, (220, 220, 140))

    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 210))
    surface.blit(option, (WIDTH // 2 - option.get_width() // 2, 320))


def render_screen(surface, screen_x, screen_y, draw_player_on_this_screen):
    map_data = create_screen_map(screen_x, screen_y)
    surface.fill((30, 30, 30))

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            tile = map_data[row][col]
            tile_x = col * TILE_SIZE
            tile_y = row * TILE_SIZE

            if tile == 1:
                pygame.draw.rect(surface, (95, 95, 95), (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
            elif tile == 2:
                pygame.draw.rect(surface, (200, 180, 40), (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(surface, (45, 45, 45), (tile_x, tile_y, TILE_SIZE, TILE_SIZE))

            pygame.draw.rect(surface, (60, 60, 60), (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)

    # draw interaction objects like the sign
    for obj in interaction_objects:
        if obj["screen_x"] == screen_x and obj["screen_y"] == screen_y:
            draw_sign(surface, obj)

    # draw sword
    if (
        not sword_pickup["collected"]
        and sword_pickup["screen_x"] == screen_x
        and sword_pickup["screen_y"] == screen_y
    ):
        draw_pickup_sword(surface, sword_pickup["x"], sword_pickup["y"])

    # draw enemies
    for enemy in enemies:
        if enemy["alive"] and enemy["screen_x"] == screen_x and enemy["screen_y"] == screen_y:
            draw_enemy(surface, enemy)

    # draw drops for this room only
    draw_drops(surface, screen_x, screen_y)

    # draw player
    if draw_player_on_this_screen:
        flashing = invincible_timer > 0 and (player_flash_timer // 4) % 2 == 0

        draw_player(
            surface,
            player_x,
            player_y,
            facing,
            was_moving,
            walk_frame,
            is_attacking,
            has_sword,
            pickup_timer > 0,
            flashing,
        )

        for obj in interaction_objects:
            if obj["screen_x"] == screen_x and obj["screen_y"] == screen_y:
                draw_sign(surface, obj)

        if screen_x == current_screen_x and screen_y == current_screen_y:
            draw_interaction_prompt(surface, get_interaction_target())
            draw_text_box(surface)

    draw_health(surface)
    draw_money(surface)

    font = pygame.font.SysFont(None, 28)
    label = font.render(f"Screen: ({screen_x}, {screen_y})", True, (220, 220, 220))
    surface.blit(label, (10, 10))


def damage_player(enemy):
    global player_health, invincible_timer, player_flash_timer
    global player_knockback_timer, player_knockback_dx, player_knockback_dy
    global game_state

    if invincible_timer > 0:
        return

    damage = 1
    if enemy["type"] == "heavy":
        damage = 2

    player_health -= damage

    if player_health <= 0:
        game_state = "game_over"

    invincible_timer = invincible_duration
    player_flash_timer = invincible_duration
    player_knockback_timer = 8

    dx = player_x - enemy["x"]
    dy = player_y - enemy["y"]

    if abs(dx) > abs(dy):
        player_knockback_dx = 6 if dx >= 0 else -6
        player_knockback_dy = 0
    else:
        player_knockback_dx = 0
        player_knockback_dy = 6 if dy >= 0 else -6


def update_player_knockback(current_map):
    global player_x, player_y, player_knockback_timer

    if player_knockback_timer > 0:
        player_x, player_y = try_move(
            player_x,
            player_y,
            player_knockback_dx,
            player_knockback_dy,
            current_map,
            player_width,
            player_height,
        )
        player_knockback_timer -= 1


def update_enemies():
    current_map = create_screen_map(current_screen_x, current_screen_y)
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    for enemy in enemies:
        if not enemy["alive"]:
            continue

        if enemy["screen_x"] != current_screen_x or enemy["screen_y"] != current_screen_y:
            continue

        if enemy["type"] == "fast":
            # perimeter movement
            path = [
                (120, 120),
                (WIDTH - 120, 120),
                (WIDTH - 120, HEIGHT - 120),
                (120, HEIGHT - 120),
            ]

            target = path[enemy["path_index"]]

            dx = target[0] - enemy["x"]
            dy = target[1] - enemy["y"]

            if abs(dx) < 5 and abs(dy) < 5:
                if pygame.time.get_ticks() % 2 == 0:
                    enemy["path_dir"] *= -1
                enemy["path_index"] = (enemy["path_index"] + enemy["path_dir"]) % len(path)

            move_x = enemy["speed"] if dx > 0 else -enemy["speed"] if dx < 0 else 0
            move_y = enemy["speed"] if dy > 0 else -enemy["speed"] if dy < 0 else 0

        else:
            enemy["move_timer"] += 1

            if enemy["move_timer"] >= 45:
                enemy["move_timer"] = 0
                enemy["move_dir"] *= -1

            if enemy["axis"] == "vertical":
                move_x = 0
                move_y = enemy["speed"] * enemy["move_dir"]
            else:
                move_x = enemy["speed"] * enemy["move_dir"]
                move_y = 0

        new_x, new_y = try_move(
            enemy["x"],
            enemy["y"],
            move_x,
            move_y,
            current_map,
            enemy["width"],
            enemy["height"]
        )

        enemy["x"] = new_x
        enemy["y"] = new_y

        enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["width"], enemy["height"])

        if enemy_rect.colliderect(player_rect):
            damage_player(enemy)


running = True
was_moving = False

while running:
    current_map = create_screen_map(current_screen_x, current_screen_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if dialogue_open:
                if event.key == pygame.K_e:
                    if dialogue_visible_count < len(dialogue_text):
                        dialogue_visible_count = len(dialogue_text)
                    else:
                        dialogue_open = False
                continue

            if game_state == "game_over":
                if event.key == pygame.K_e:
                    player_health = max_health
                    current_screen_x = 0
                    current_screen_y = 0
                    player_x = WIDTH // 2 - player_width // 2
                    player_y = HEIGHT // 2 - player_height // 2
                    invincible_timer = 0
                    player_flash_timer = 0
                    player_knockback_timer = 0
                    game_state = "playing"
                continue

            if not is_transitioning and pickup_timer == 0:
                if event.key == pygame.K_SPACE and has_sword and not is_attacking:
                    is_attacking = True
                    attack_timer = attack_duration

                elif event.key == pygame.K_e:
                    interaction_target = get_interaction_target()
                    if interaction_target is not None:
                        open_dialogue(interaction_target["text"])

    if game_state == "playing":
        update_dialogue()
        if arrival_cooldown > 0:
            arrival_cooldown -= 1

        if invincible_timer > 0:
            invincible_timer -= 1

        if player_flash_timer > 0:
            player_flash_timer -= 1

        if pickup_timer > 0:
            pickup_timer -= 1
            facing = "down"
            was_moving = False
            if pickup_timer == 0:
                has_sword = True
        else:
            keys = pygame.key.get_pressed()

            move_x = 0
            move_y = 0
            was_moving = False

            
        if not is_transitioning and not dialogue_open:
            if not is_transitioning:
                if player_knockback_timer > 0:
                    update_player_knockback(current_map)
                else:
                    left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
                    right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
                    up_pressed = keys[pygame.K_UP] or keys[pygame.K_w]
                    down_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]

                    if left_pressed:
                        move_x = -player_speed
                        facing = "left"
                    elif right_pressed:
                        move_x = player_speed
                        facing = "right"

                    if up_pressed:
                        move_y = -player_speed
                        if move_x == 0:
                            facing = "up"
                    elif down_pressed:
                        move_y = player_speed
                        if move_x == 0:
                            facing = "down"

                    was_moving = move_x != 0 or move_y != 0

                    player_x, player_y = try_move(
                        player_x,
                        player_y,
                        move_x,
                        move_y,
                        current_map,
                        player_width,
                        player_height
                    )

                if was_moving:
                    walk_timer += 1
                    if walk_timer >= 10:
                        walk_timer = 0
                        walk_frame = 1 - walk_frame
                else:
                    walk_timer = 0
                    walk_frame = 0

                if is_attacking:
                    attack_timer -= 1
                    if attack_timer <= 0:
                        is_attacking = False

                # sword pickup
                if (
                    not sword_pickup["collected"]
                    and current_screen_x == sword_pickup["screen_x"]
                    and current_screen_y == sword_pickup["screen_y"]
                ):
                    sword_rect = pygame.Rect(sword_pickup["x"], sword_pickup["y"], 18, 18)
                    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

                    if player_rect.colliderect(sword_rect):
                        sword_pickup["collected"] = True
                        pickup_timer = pickup_duration
                        is_attacking = False

                # attack enemies
                if is_attacking:
                    attack_rect = get_attack_rect(player_x, player_y, facing)

                    for enemy in enemies:
                        if not enemy["alive"]:
                            continue
                        if enemy["screen_x"] != current_screen_x or enemy["screen_y"] != current_screen_y:
                            continue

                        enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy["width"], enemy["height"])

                        if attack_rect.colliderect(enemy_rect):
                            enemy["hp"] -= 1

                            if enemy["hp"] <= 0:
                                enemy["alive"] = False

                                if enemy["type"] == "normal":
                                    spawn_drop(enemy["x"], enemy["y"], enemy["screen_x"], enemy["screen_y"], "health")

                                elif enemy["type"] == "heavy":
                                    spawn_drop(enemy["x"], enemy["y"], enemy["screen_x"], enemy["screen_y"], "money")

                                elif enemy["type"] == "fast":
                                    spawn_drop(enemy["x"], enemy["y"], enemy["screen_x"], enemy["screen_y"], "money")

                # doors / transitions
                if arrival_cooldown == 0:
                    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
                    transitioned = False

                    for row in range(GRID_ROWS):
                        for col in range(GRID_COLS):
                            if current_map[row][col] == 2:
                                door_rect = pygame.Rect(
                                    col * TILE_SIZE,
                                    row * TILE_SIZE,
                                    TILE_SIZE,
                                    TILE_SIZE
                                )

                                if player_rect.colliderect(door_rect):
                                    if row == 0 and current_screen_y > 0:
                                        target_x = current_screen_x
                                        target_y = current_screen_y - 1
                                        new_px = col * TILE_SIZE + (TILE_SIZE - player_width) // 2
                                        new_py = HEIGHT - TILE_SIZE - player_height - 5
                                        facing = "up"
                                        start_transition("up", target_x, target_y, new_px, new_py)
                                        transitioned = True

                                    elif row == GRID_ROWS - 1 and current_screen_y < world_height - 1:
                                        target_x = current_screen_x
                                        target_y = current_screen_y + 1
                                        new_px = col * TILE_SIZE + (TILE_SIZE - player_width) // 2
                                        new_py = TILE_SIZE + 5
                                        facing = "down"
                                        start_transition("down", target_x, target_y, new_px, new_py)
                                        transitioned = True

                                    elif col == 0 and current_screen_x > 0:
                                        target_x = current_screen_x - 1
                                        target_y = current_screen_y
                                        new_px = WIDTH - TILE_SIZE - player_width - 5
                                        new_py = row * TILE_SIZE + (TILE_SIZE - player_height) // 2
                                        facing = "left"
                                        start_transition("left", target_x, target_y, new_px, new_py)
                                        transitioned = True

                                    elif col == GRID_COLS - 1 and current_screen_x < world_width - 1:
                                        target_x = current_screen_x + 1
                                        target_y = current_screen_y
                                        new_px = TILE_SIZE + 5
                                        new_py = row * TILE_SIZE + (TILE_SIZE - player_height) // 2
                                        facing = "right"
                                        start_transition("right", target_x, target_y, new_px, new_py)
                                        transitioned = True

                            if transitioned:
                                break
                        if transitioned:
                            break

        if not is_transitioning and pickup_timer == 0 and not dialogue_open:
            update_enemies()
            update_drops()

        if is_transitioning:
            transition_progress += transition_speed
            if transition_progress >= WIDTH and transition_direction in ("left", "right"):
                transition_progress = WIDTH
                is_transitioning = False
            elif transition_progress >= HEIGHT and transition_direction in ("up", "down"):
                transition_progress = HEIGHT
                is_transitioning = False

    if not is_transitioning:
        render_screen(screen, current_screen_x, current_screen_y, True)
    else:
        old_surface = pygame.Surface((WIDTH, HEIGHT))
        new_surface = pygame.Surface((WIDTH, HEIGHT))

        render_screen(old_surface, old_screen_x, old_screen_y, False)
        render_screen(new_surface, new_screen_x, new_screen_y, True)

        if transition_direction == "right":
            screen.blit(old_surface, (-transition_progress, 0))
            screen.blit(new_surface, (WIDTH - transition_progress, 0))
        elif transition_direction == "left":
            screen.blit(old_surface, (transition_progress, 0))
            screen.blit(new_surface, (-WIDTH + transition_progress, 0))
        elif transition_direction == "down":
            screen.blit(old_surface, (0, -transition_progress))
            screen.blit(new_surface, (0, HEIGHT - transition_progress))
        elif transition_direction == "up":
            screen.blit(old_surface, (0, transition_progress))
            screen.blit(new_surface, (0, -HEIGHT + transition_progress))

    if game_state == "game_over":
        draw_game_over(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()