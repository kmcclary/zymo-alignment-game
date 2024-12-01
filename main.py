import pygame
import random
import asyncio
from moviepy.video.io.VideoFileClip import VideoFileClip

# Initialize pygame
pygame.init()
random.seed()

# Get the display info to set up dynamic window sizing
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Calculate the maximum size while maintaining 16:9 aspect ratio
if SCREEN_WIDTH / 16 > SCREEN_HEIGHT / 9:
    WIDTH = SCREEN_HEIGHT * 16 // 9
    HEIGHT = SCREEN_HEIGHT
else:
    WIDTH = SCREEN_WIDTH
    HEIGHT = SCREEN_WIDTH * 9 // 16

# Create the window
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("DNA Sequence Alignment")

# Scale factor for dynamic resizing
SCALE_X = WIDTH / 1920
SCALE_Y = HEIGHT / 1080

# Buttons - scale with window size
submit_button_rect = pygame.Rect(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
play_again_button_rect = pygame.Rect(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)

# Fonts - scale with window size
font_size = int(24 * min(SCALE_X, SCALE_Y))
small_font_size = int(16 * min(SCALE_X, SCALE_Y))
font = pygame.font.SysFont('Arial', font_size)
small_font = pygame.font.SysFont('Arial', small_font_size)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 255, 0)

# Colors for nucleotides
COLORS = {
    'A': (255, 0, 0),  # Red
    'T': (0, 255, 0),  # Green
    'G': (0, 0, 255),  # Blue
    'C': (255, 255, 0),  # Yellow
    '-': (100, 100, 100)  # Gray for gaps
}

# Scoring values
MATCH = 1
MISMATCH = -1
GAP_OPENING = -2
GAP_EXTENSION = -1

# Display dimensions for genome sequence
GENOME_ROW_LENGTH = 50
NUM_GENOME_ROWS = 5
ROW_SPACING = int(80 * SCALE_Y)

# Video file path
video_path = "/Users/kylemcclary/Documents/seq_align_game-main/zymologo.mov"

def play_video(video_path):
    clip = VideoFileClip(video_path)
    clip = clip.set_size((WIDTH, HEIGHT))
    clip.preview()

def draw_start_screen():
    window.fill(WHITE)
    draw_text("Press any key to start the game", font, BLACK, window, WIDTH // 2 - 150 * SCALE_X, HEIGHT // 2)
    pygame.display.update()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def generate_dna_sequence(length):
    random.seed()
    return ''.join(random.choice('ATGC') for _ in range(length))

def generate_player_sequence_from_genome(genome_seq):
    start_idx = random.randint(0, len(genome_seq) - 55)
    player_seq = list(genome_seq[start_idx:start_idx + random.randint(50, 55)])

    while len(player_seq) > 50:
        del player_seq[random.randint(0, len(player_seq) - 1)]

    num_mutations = random.randint(0, 5)
    for _ in range(num_mutations):
        mutation_idx = random.randint(0, len(player_seq) - 1)
        original_base = player_seq[mutation_idx]
        possible_bases = [base for base in 'ATGC' if base != original_base]
        player_seq[mutation_idx] = random.choice(possible_bases)

    return ''.join(player_seq)

def draw_sequences(player_seq, genome_seq, alignment_start, selected_position):
    window.fill(WHITE, (0, 0, WIDTH, HEIGHT - 200 * SCALE_Y))

    y_offset = 50 * SCALE_Y
    char_spacing = 15 * SCALE_X

    for row in range(NUM_GENOME_ROWS):
        start_idx = row * GENOME_ROW_LENGTH
        end_idx = start_idx + GENOME_ROW_LENGTH
        genome_subseq = genome_seq[start_idx:end_idx]
        for i, base in enumerate(genome_subseq):
            color = COLORS[base]
            draw_text(base, font, color, window, 50 * SCALE_X + i * char_spacing, y_offset + row * ROW_SPACING)

    player_seq_y_offset = y_offset + 35 * SCALE_Y
    for row in range(NUM_GENOME_ROWS):
        start_idx = row * GENOME_ROW_LENGTH
        end_idx = start_idx + GENOME_ROW_LENGTH
        alignment_end = alignment_start + len(player_seq) - 1
        if alignment_start >= start_idx and alignment_start <= end_idx:
            player_subseq = player_seq[:end_idx-alignment_start]
            for i, base in enumerate(player_subseq):
                color = COLORS[base]
                draw_text(base, font, color, window, 50 * SCALE_X + (i+alignment_start-start_idx) * char_spacing, 
                         player_seq_y_offset + row * ROW_SPACING)
        elif alignment_end >= start_idx and alignment_end <= end_idx:
            player_subseq = player_seq[start_idx-alignment_start:]
            for i, base in enumerate(player_subseq):
                color = COLORS[base]
                draw_text(base, font, color, window, 50 * SCALE_X + i * char_spacing, 
                         player_seq_y_offset + row * ROW_SPACING)

    score = calculate_score(player_seq, genome_seq, alignment_start)
    score_text = font.render(f"Score: {score}", True, BLACK)
    window.blit(score_text, (50 * SCALE_X, y_offset + NUM_GENOME_ROWS * ROW_SPACING + 50 * SCALE_Y))

    if selected_position is not None:
        row = selected_position // GENOME_ROW_LENGTH
        col = selected_position % GENOME_ROW_LENGTH
        pygame.draw.rect(window, BLACK, (50 * SCALE_X + col * char_spacing, 
                                       85 * SCALE_Y + row * ROW_SPACING, 
                                       16 * SCALE_X, 30 * SCALE_Y), 1)
    pygame.display.update()

def draw_buttons(clicked_button):
    window.fill(WHITE, (0, HEIGHT - 200 * SCALE_Y, WIDTH, HEIGHT))
    if clicked_button == "submit":
        pygame.draw.rect(window, (0, 200, 0), submit_button_rect)
    else:
        pygame.draw.rect(window, GREEN, submit_button_rect)

    if clicked_button == "play_again":
        pygame.draw.rect(window, (0, 0, 200), play_again_button_rect)
    else:
        pygame.draw.rect(window, BLUE, play_again_button_rect)
    
    draw_text("Submit", font, BLACK, window, submit_button_rect.x + 50 * SCALE_X, submit_button_rect.y + 10 * SCALE_Y)
    draw_text("Play Again", font, WHITE, window, play_again_button_rect.x + 25 * SCALE_X, play_again_button_rect.y + 10 * SCALE_Y)
    draw_text("A/W/S/D: move the read", small_font, BLACK, window, 550 * SCALE_X, 600 * SCALE_Y)
    draw_text("Arrow keys: move the cursor", small_font, BLACK, window, 550 * SCALE_X, 650 * SCALE_Y)
    draw_text("Space: add a gap", small_font, BLACK, window, 550 * SCALE_X, 700 * SCALE_Y)
    draw_text("Backspace: delete a gap", small_font, BLACK, window, 550 * SCALE_X, 750 * SCALE_Y)

def draw_leaderboard(leaderboard, score, time, name, status, clicked_button):
    window.fill(WHITE)
    score_text = "Your final score is {} in {:.2f} seconds. ".format(score, time)
    if status == "won":
        score_text += "You made the leaderboard! Please enter your name: "
        color = RED
    else:
        score_text += "Sorry you didn't make the leaderboard! Try again?"
        color = BLACK
    
    draw_text(score_text, small_font, color, window, 50 * SCALE_X, 50 * SCALE_Y)
    
    if status == "won":
        pygame.draw.rect(window, BLACK, (50 * SCALE_X, 100 * SCALE_Y, 200 * SCALE_X, 30 * SCALE_Y), 1)
        draw_text("press Enter to confirm", small_font, BLACK, window, 275 * SCALE_X, 110 * SCALE_Y)
        if name:
            draw_text(name, font, BLACK, window, 55 * SCALE_X, 100 * SCALE_Y)
    
    y_offset = 150 * SCALE_Y
    draw_text("Rank", font, BLACK, window, 50 * SCALE_X, y_offset)
    draw_text("Name", font, BLACK, window, 250 * SCALE_X, y_offset)
    draw_text("Score", font, BLACK, window, 450 * SCALE_X, y_offset)
    draw_text("Time", font, BLACK, window, 650 * SCALE_X, y_offset)
    
    for i, player in enumerate(leaderboard):
        color = GREEN if name == player["name"] else BLACK
        row_y = (200 + 50 * i) * SCALE_Y
        draw_text(str(i+1), font, color, window, 50 * SCALE_X, row_y)
        draw_text(player["name"], font, color, window, 250 * SCALE_X, row_y)
        draw_text(str(player["score"]), font, color, window, 450 * SCALE_X, row_y)
        draw_text("{:.2f}".format(player["time"]), font, color, window, 650 * SCALE_X, row_y)

    if clicked_button == "play_again":
        pygame.draw.rect(window, (0, 0, 200), play_again_button_rect)
    else:
        pygame.draw.rect(window, BLUE, play_again_button_rect)
    
    draw_text("Play Again", font, WHITE, window, play_again_button_rect.x + 25 * SCALE_X, play_again_button_rect.y + 10 * SCALE_Y)
    pygame.display.update()

def calculate_score(player_seq, genome_seq, alignment_start):
    score = 0
    gap_open = False

    for i in range(len(player_seq)):
        if player_seq[i] == '-':
            if not gap_open:
                score += GAP_OPENING
                gap_open = True
            else:
                score += GAP_EXTENSION
        else:
            gap_open = False
            if player_seq[i] == genome_seq[alignment_start+i]:
                score += MATCH
            else:
                score += MISMATCH
    return score

async def main():
    global WIDTH, HEIGHT, SCALE_X, SCALE_Y, font, small_font, submit_button_rect, play_again_button_rect, window

    clip = VideoFileClip(video_path)
    video_surface = pygame.Surface((WIDTH, HEIGHT))
    
    # Move the video drawing logic outside of a nested function
    start_time = pygame.time.get_ticks()
    video_duration = clip.duration
    playing_video = True

    while playing_video:
        t = (pygame.time.get_ticks() - start_time) / 1000
        if t >= video_duration:
            playing_video = False
            break
            
        # Draw the current video frame
        frame = clip.get_frame(t)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
        video_surface.blit(frame_surface, (0, 0))
        window.blit(video_surface, (0, 0))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                playing_video = False
                break
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                SCALE_X = WIDTH / 1920
                SCALE_Y = HEIGHT / 1080
                font_size = int(24 * min(SCALE_X, SCALE_Y))
                small_font_size = int(16 * min(SCALE_X, SCALE_Y))
                font = pygame.font.SysFont('Arial', font_size)
                small_font = pygame.font.SysFont('Arial', small_font_size)
                submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                video_surface = pygame.Surface((WIDTH, HEIGHT))
        
        await asyncio.sleep(0)
        
    draw_start_screen()
    waiting_for_start = True
    while waiting_for_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_start = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                SCALE_X = WIDTH / 1920
                SCALE_Y = HEIGHT / 1080
                font_size = int(24 * min(SCALE_X, SCALE_Y))
                small_font_size = int(16 * min(SCALE_X, SCALE_Y))
                font = pygame.font.SysFont('Arial', font_size)
                small_font = pygame.font.SysFont('Arial', small_font_size)
                submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)

    pygame.key.set_repeat(150, 20)
    running = True
    genome_seq = generate_dna_sequence(250)
    player_seq = generate_player_sequence_from_genome(genome_seq)
    alignment_start = 0
    selected_position = None
    clicked_button = None
    start_time = pygame.time.get_ticks()
    display_time = 0
    status = "playing"
    leaderboard = [{"name":"BLAST", "score":50, "time": 0.2}]
    final_score = 0
    final_time = 10000
    player_name = ""
    input_active = False

    while running:
        if status == "playing":
            draw_sequences(player_seq, genome_seq, alignment_start, selected_position)
            draw_buttons(clicked_button)
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            if elapsed_time - display_time >= 0.1:
                display_time = elapsed_time
            draw_text(f"Time: {display_time:.2f} sec", font, BLACK, window, 50 * SCALE_X, 600 * SCALE_Y)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if submit_button_rect.collidepoint(mouse_pos):
                        clicked_button = "submit"
                        status = "score"
                        final_score = calculate_score(player_seq, genome_seq, alignment_start)
                        final_time = elapsed_time
                        if len(leaderboard) < 10 or final_score > leaderboard[-1]["score"] or (final_score == leaderboard[-1]["score"] and final_time < leaderboard[-1]["time"]):
                            status = "won"
                            input_active = True
                        else:
                            status = "lost"
                    elif play_again_button_rect.collidepoint(mouse_pos):
                        clicked_button = "play_again"
                        genome_seq = generate_dna_sequence(250)
                        player_seq = generate_player_sequence_from_genome(genome_seq)
                        alignment_start = 0
                        selected_position = None
                        start_time = pygame.time.get_ticks()
                        display_time = 0
                        final_score = 0
                        final_time = 10000
                        player_name = ""
                elif event.type == pygame.MOUSEBUTTONUP:
                    clicked_button = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and selected_position is not None:
                        if selected_position >= alignment_start and selected_position < alignment_start + len(player_seq) - 1:
                            player_seq = player_seq[:selected_position-alignment_start] + '-' + player_seq[selected_position-alignment_start:]

                    if event.key == pygame.K_BACKSPACE and selected_position is not None:
                        if selected_position >= alignment_start and selected_position < alignment_start + len(player_seq) - 1:
                            if player_seq[selected_position-alignment_start] == '-':
                                player_seq = player_seq[:selected_position-alignment_start] + player_seq[selected_position-alignment_start+1:]

                    if event.key == pygame.K_LEFT:
                        if selected_position is None:
                            selected_position = len(genome_seq) - 1
                        else:
                            selected_position = max(0, selected_position - 1)
                    elif event.key == pygame.K_RIGHT:
                        if selected_position is None:
                            selected_position = 0
                        else:
                            selected_position = min(len(genome_seq) - 1, selected_position + 1)
                    elif event.key == pygame.K_UP:
                        if selected_position is None:
                            selected_position = len(genome_seq) - 1
                        else:
                            selected_position = max(0, selected_position - GENOME_ROW_LENGTH)
                    elif event.key == pygame.K_DOWN:
                        if selected_position is None:
                            selected_position = 0
                        else:
                            selected_position = min(len(genome_seq) - 1, selected_position + GENOME_ROW_LENGTH)

                    if event.key == pygame.K_a:
                        alignment_start = max(0, alignment_start - 1)
                    elif event.key == pygame.K_d:
                        alignment_start = min(len(genome_seq) - len(player_seq), alignment_start + 1)
                    elif event.key == pygame.K_w:
                        alignment_start = max(0, alignment_start - GENOME_ROW_LENGTH)
                    elif event.key == pygame.K_s:
                        alignment_start = min(len(genome_seq) - len(player_seq), alignment_start + GENOME_ROW_LENGTH)
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.size
                    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    SCALE_X = WIDTH / 1920
                    SCALE_Y = HEIGHT / 1080
                    font_size = int(24 * min(SCALE_X, SCALE_Y))
                    small_font_size = int(16 * min(SCALE_X, SCALE_Y))
                    font = pygame.font.SysFont('Arial', font_size)
                    small_font = pygame.font.SysFont('Arial', small_font_size)
                    submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                    play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
        else:
            draw_leaderboard(leaderboard, final_score, final_time, player_name, status, clicked_button)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_again_button_rect.collidepoint(mouse_pos):
                        clicked_button = "play_again"
                        genome_seq = generate_dna_sequence(250)
                        player_seq = generate_player_sequence_from_genome(genome_seq)
                        alignment_start = 0
                        selected_position = None
                        start_time = pygame.time.get_ticks()
                        display_time = 0
                        final_score = 0
                        final_time = 10000
                        player_name = ""
                        status = "playing"
                        input_active = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    clicked_button = None
                elif event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN and player_name:
                        leaderboard.append({'name': player_name, 'score': final_score, 'time': final_time})
                        leaderboard = sorted(leaderboard, key=lambda x: (-x['score'], x['time'], x['name']))
                        if len(leaderboard) > 10:
                            leaderboard.pop()
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE and player_name:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 15:
                            player_name += event.unicode
                elif event.type == pygame.VIDEORESIZE:
                    WIDTH, HEIGHT = event.size
                    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    SCALE_X = WIDTH / 1920
                    SCALE_Y = HEIGHT / 1080
                    font_size = int(24 * min(SCALE_X, SCALE_Y))
                    small_font_size = int(16 * min(SCALE_X, SCALE_Y))
                    font = pygame.font.SysFont('Arial', font_size)
                    small_font = pygame.font.SysFont('Arial', small_font_size)
                    submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                    play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())