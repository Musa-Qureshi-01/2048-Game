import pygame
import random
import math

pygame.init()

FPS = 60
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 4, 4

RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS

OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (210, 200, 160)
FONT_COLOR = (119, 110, 101)

FONT = pygame.font.SysFont("comicsans", 60, bold=True)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('2048')


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        return self.COLORS[min(color_index, len(self.COLORS) - 1)]

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2)
            )
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)
    for tile in tiles.values():
        tile.draw(window)
    draw_grid(window)
    pygame.display.update()


def get_random_pos(tiles):
    while True:
        row = random.randrange(ROWS)
        col = random.randrange(COLS)
        if f'{row}{col}' not in tiles:
            return row, col


MOVE_VEL = 20


def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == 'left':
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f'{tile.row}{tile.col - 1}')
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        ceil = True

    elif direction == 'right':
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f'{tile.row}{tile.col + 1}')
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        ceil = False

    elif direction == 'up':
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f'{tile.row - 1}{tile.col}')
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        ceil = True

    elif direction == 'down':
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f'{tile.row + 1}{tile.col}')
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)
        tiles_to_remove = []

        for tile in sorted_tiles:
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    tiles_to_remove.append(tile)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        for t in tiles_to_remove:
            if t in sorted_tiles:
                sorted_tiles.remove(t)

        updated_tiles(window, tiles, sorted_tiles)

    return end_tiles(tiles)


def end_tiles(tiles):
    if len(tiles) == ROWS * COLS:
        return 'lost'

    row, col = get_random_pos(tiles)
    tiles[f'{row}{col}'] = Tile(random.choice([2, 4]), row, col)
    return 'continue'


def updated_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f'{tile.row}{tile.col}'] = tile
    draw(window, tiles)


def generator_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f'{row}{col}'] = Tile(2, row, col)
    return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True
    tiles = generator_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, 'left')
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, 'right')
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, 'up')
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, 'down')

        draw(window, tiles)

    pygame.quit()

def draw_text_center(window, text, font_size, y_offset=0, color=FONT_COLOR):
    font = pygame.font.SysFont("comicsans", font_size, bold=True)
    label = font.render(text, 1, color)
    x = WIDTH // 2 - label.get_width() // 2
    y = HEIGHT // 2 - label.get_height() // 2 + y_offset
    window.blit(label, (x, y))


def draw_button(window, text, y_offset):
    button_font = pygame.font.SysFont("comicsans", 50, bold=True)
    label = button_font.render(text, 1, (255, 255, 255))
    button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + y_offset, 300, 70)
    pygame.draw.rect(window, (119, 110, 101), button_rect, border_radius=15)
    window.blit(label, (button_rect.x + 150 - label.get_width() // 2, button_rect.y + 35 - label.get_height() // 2))
    return button_rect


def start_screen():
    while True:
        WINDOW.fill(BACKGROUND_COLOR)
        draw_text_center(WINDOW, "2048", 100, -100)
        button_rect = draw_button(WINDOW, "Start Game", 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return


def game_over_screen():
    while True:
        WINDOW.fill(BACKGROUND_COLOR)
        draw_text_center(WINDOW, "Game Over", 80, -100)
        button_rect = draw_button(WINDOW, "Play Again", 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return


def main(window):
    start_screen()
    run = True

    while run:
        clock = pygame.time.Clock()
        tiles = generator_tiles()
        status = 'continue'

        while status == 'continue':
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        status = move_tiles(window, tiles, clock, 'left')
                    if event.key == pygame.K_RIGHT:
                        status = move_tiles(window, tiles, clock, 'right')
                    if event.key == pygame.K_UP:
                        status = move_tiles(window, tiles, clock, 'up')
                    if event.key == pygame.K_DOWN:
                        status = move_tiles(window, tiles, clock, 'down')

            draw(window, tiles)

        # Game Over screen
        game_over_screen()



if __name__ == "__main__":
    main(WINDOW)
