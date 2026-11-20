import pygame
import sys
import os
import random

pygame.init()

# ---------- Window settings ----------
WIDTH, HEIGHT = 600, 780        # bigger window (was 400 x 520)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 120)

# =====================================================
#  COLORS (DARK MODE)  -> change these to customize!
#  Each color is (Red, Green, Blue), values 0 to 255
# =====================================================
BG_COLOR = (30, 30, 30)              # window background
LINE_COLOR = (230, 230, 230)         # board grid lines
X_COLOR = (255, 90, 90)              # color of X
O_COLOR = (90, 150, 255)             # color of O
TEXT_COLOR = (240, 240, 240)         # normal text
BUTTON_COLOR = (200, 55, 55)         # button background (red)
MENU_TITLE_OUTLINE = (0, 0, 0)        # dark edge around the menu title (None = no edge)
BUTTON_TEXT_COLOR = (255, 255, 255)  # text inside buttons
WIN_LINE_COLOR = (255, 215, 0)       # line drawn over winning cells
HINT_COLOR = (150, 150, 150)         # "Press ESC" hint text

# =====================================================
#  IMAGES  -> put your pictures in the SAME folder as
#  this file and change the file names here
# =====================================================
WIN_IMAGE_FILE = "win.png"
LOSE_IMAGE_FILE = "lose.png"
MENU_IMAGE_FILE = "menu.png"   # menu background picture ("" = no picture)
SHOW_BOARD_MS = 1000   # show the final board for 1 second, then the picture

# =====================================================
#  COMPUTER DELAY -> time (in milliseconds) the computer
#  waits before it plays. 1000 = 1 second
# =====================================================
CPU_DELAY_MS = 800

# ---------- Board settings ----------
CELL = 180                          # size of one cell
BOARD_X = (WIDTH - 3 * CELL) // 2   # keeps the board centred in the window
BOARD_Y = 30                        # top-left corner of the board

# ---------- Text positions ----------
TURN_TEXT_Y = BOARD_Y + 3 * CELL + 50    # "Turn: X" line
HINT_TEXT_Y = BOARD_Y + 3 * CELL + 130   # "Press ESC for Menu"
STRIP_HEIGHT = 195                       # dark strip on the result screen
RESULT_TEXT_Y = HEIGHT - STRIP_HEIGHT + 35   # "Player X wins!"

# All 8 ways to win (using board positions 0-8)
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]

# ---------- Buttons ----------
# Menu screen
MENU_BTN_W, MENU_BTN_H = 320, 84
MENU_BTN_X = (WIDTH - MENU_BTN_W) // 2
btn_2p = pygame.Rect(MENU_BTN_X, 300, MENU_BTN_W, MENU_BTN_H)
btn_cpu = pygame.Rect(MENU_BTN_X, 410, MENU_BTN_W, MENU_BTN_H)

# Menu title position
MENU_TITLE_Y = 140

# Result screen
BTN_W, BTN_H, BTN_GAP = 255, 75, 30
BTN_ROW_Y = HEIGHT - STRIP_HEIGHT + 90
btn_again = pygame.Rect((WIDTH - 2 * BTN_W - BTN_GAP) // 2, BTN_ROW_Y, BTN_W, BTN_H)
btn_menu = pygame.Rect(btn_again.right + BTN_GAP, BTN_ROW_Y, BTN_W, BTN_H)


def load_fullscreen_image(file_name):
    """Load a picture and resize it to fill the whole window.
    The picture keeps its shape; extra parts are cropped off.
    If the file is missing, return None (the game will not crash)."""
    if not file_name:
        return None
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, file_name)
    try:
        img = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None

    # scale so the picture covers the whole window
    w, h = img.get_size()
    scale = max(WIDTH / w, HEIGHT / h)
    new_size = (int(w * scale), int(h * scale))
    img = pygame.transform.smoothscale(img, new_size)

    # put it in the middle of a window-sized surface (crops the edges)
    result_surface = pygame.Surface((WIDTH, HEIGHT))
    result_surface.blit(img, ((WIDTH - new_size[0]) // 2,
                              (HEIGHT - new_size[1]) // 2))
    return result_surface


win_image = load_fullscreen_image(WIN_IMAGE_FILE)
lose_image = load_fullscreen_image(LOSE_IMAGE_FILE)
menu_image = load_fullscreen_image(MENU_IMAGE_FILE)

# Dark strip drawn behind the text/buttons so they are easy to read
strip = pygame.Surface((WIDTH, STRIP_HEIGHT), pygame.SRCALPHA)
strip.fill((0, 0, 0, 170))

# ---------- Game variables ----------
board = [""] * 9      # each spot is "", "X" or "O"
turn = "X"            # whose turn it is
mode = "2p"           # "2p" or "cpu"
state = "menu"        # "menu", "playing" or "gameover"
result = ""           # text shown when the game ends
win_line = None       # the winning line (to draw a line over it)
outcome = ""          # "win", "lose" or "draw" (decides which picture to show)
over_time = 0         # the time when the game ended
cpu_time = 0          # the time when the computer will play (0 = not set)


def new_game():
    """Reset everything for a fresh game."""
    global board, turn, state, result, win_line, outcome, cpu_time
    cpu_time = 0
    board = [""] * 9
    turn = "X"
    state = "playing"
    result = ""
    win_line = None
    outcome = ""


def check_winner():
    """Return the winning line if someone won, otherwise None."""
    for a, b, c in WIN_LINES:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return (a, b, c)
    return None


def check_result():
    """After each move: check for a win or a draw."""
    global state, result, win_line, outcome, over_time
    line = check_winner()
    if line:
        win_line = line
        winner = board[line[0]]
        result = "Player " + winner + " wins!"
        state = "gameover"
        # In vs-Computer mode, O is the computer, so O winning = you lose
        if mode == "cpu" and winner == "O":
            outcome = "lose"
        else:
            outcome = "win"
        over_time = pygame.time.get_ticks()
    elif "" not in board:
        result = "It's a draw!"
        outcome = "draw"
        state = "gameover"
        over_time = pygame.time.get_ticks()


def computer_move():
    """Simple computer: win if it can, block the player, else random."""
    for symbol in ("O", "X"):
        for a, b, c in WIN_LINES:
            line = [board[a], board[b], board[c]]
            if line.count(symbol) == 2 and line.count("") == 1:
                spot = (a, b, c)[line.index("")]
                board[spot] = "O"
                return
    empty = [i for i in range(9) if board[i] == ""]
    board[random.choice(empty)] = "O"


def draw_text(text, fnt, color, center):
    img = fnt.render(text, True, color)
    screen.blit(img, img.get_rect(center=center))


def draw_text_outlined(text, fnt, color, center, outline_color):
    """Draw text with a thin dark edge, so it stays readable on any picture.
    Pass outline_color=None to draw normal (not outlined) text."""
    if outline_color is None:
        draw_text(text, fnt, color, center)
        return
    edge = fnt.render(text, True, outline_color)
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        screen.blit(edge, edge.get_rect(center=(center[0] + dx, center[1] + dy)))
    draw_text(text, fnt, color, center)


def draw_button(rect, text, color=BUTTON_COLOR):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    draw_text(text, font, BUTTON_TEXT_COLOR, rect.center)


def draw_board():
    # grid lines
    for i in range(1, 3):
        x = BOARD_X + i * CELL
        y = BOARD_Y + i * CELL
        pygame.draw.line(screen, LINE_COLOR, (x, BOARD_Y), (x, BOARD_Y + 3 * CELL), 4)
        pygame.draw.line(screen, LINE_COLOR, (BOARD_X, y), (BOARD_X + 3 * CELL, y), 4)

    # X and O symbols
    for i in range(9):
        if board[i] != "":
            row, col = i // 3, i % 3
            center = (BOARD_X + col * CELL + CELL // 2,
                      BOARD_Y + row * CELL + CELL // 2)
            color = X_COLOR if board[i] == "X" else O_COLOR
            draw_text(board[i], big_font, color, center)

    # line through the winning cells
    if win_line:
        a, c = win_line[0], win_line[2]
        start = (BOARD_X + (a % 3) * CELL + CELL // 2,
                 BOARD_Y + (a // 3) * CELL + CELL // 2)
        end = (BOARD_X + (c % 3) * CELL + CELL // 2,
               BOARD_Y + (c // 3) * CELL + CELL // 2)
        pygame.draw.line(screen, WIN_LINE_COLOR, start, end, 8)


def draw_fullscreen_result():
    """Fill the whole window with the win or lose picture."""
    if outcome == "win":
        img, file_name = win_image, WIN_IMAGE_FILE
    else:
        img, file_name = lose_image, LOSE_IMAGE_FILE

    if img:
        screen.blit(img, (0, 0))
    else:
        # picture file not found -> show a note instead
        draw_text("Add " + file_name, font, HINT_COLOR, (WIDTH // 2, HEIGHT // 2))

    screen.blit(strip, (0, HEIGHT - STRIP_HEIGHT))   # dark strip at the bottom


# ---------- Main game loop ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ESC key -> go back to the menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and state != "menu":
                state = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if state == "menu":
                if btn_2p.collidepoint(pos):
                    mode = "2p"
                    new_game()
                elif btn_cpu.collidepoint(pos):
                    mode = "cpu"
                    new_game()

            elif state == "playing":
                # Ignore clicks while it's the computer's turn
                if mode == "2p" or turn == "X":
                    col = (pos[0] - BOARD_X) // CELL
                    row = (pos[1] - BOARD_Y) // CELL
                    if 0 <= col < 3 and 0 <= row < 3:
                        spot = row * 3 + col
                        if board[spot] == "":
                            board[spot] = turn
                            check_result()
                            if state == "playing":
                                turn = "O" if turn == "X" else "X"

            elif state == "gameover":
                if btn_again.collidepoint(pos):
                    new_game()
                elif btn_menu.collidepoint(pos):
                    state = "menu"

    # Computer's turn
    if state == "playing" and mode == "cpu" and turn == "O":
        now = pygame.time.get_ticks()
        if cpu_time == 0:
            # the player just moved -> start the countdown
            cpu_time = now + CPU_DELAY_MS
        elif now >= cpu_time:
            # the delay is over -> the computer plays
            computer_move()
            cpu_time = 0
            check_result()
            if state == "playing":
                turn = "X"

    # ---------- Drawing ----------
    screen.fill(BG_COLOR)

    if state == "menu":
        if menu_image:
            # full-window picture, nothing else covering it
            screen.blit(menu_image, (0, 0))
        draw_text_outlined("Tic-Tac-Toe", big_font, TEXT_COLOR,
                           (WIDTH // 2, MENU_TITLE_Y), MENU_TITLE_OUTLINE)
        draw_button(btn_2p, "2 Players")
        draw_button(btn_cpu, "vs Computer")
    else:
        draw_board()
        if state == "playing":
            draw_text("Turn: " + turn, font, TEXT_COLOR, (WIDTH // 2, TURN_TEXT_Y))
            draw_text("Press ESC for Menu", small_font, HINT_COLOR, (WIDTH // 2, HINT_TEXT_Y))
        else:
            # after 1 second, cover the screen with the win/lose picture
            waited = pygame.time.get_ticks() - over_time
            if outcome != "draw" and waited >= SHOW_BOARD_MS:
                draw_fullscreen_result()
            draw_text(result, font, TEXT_COLOR, (WIDTH // 2, RESULT_TEXT_Y))
            draw_button(btn_again, "Play Again")
            draw_button(btn_menu, "Menu")

    pygame.display.update()
