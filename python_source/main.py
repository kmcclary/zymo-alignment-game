import pygame
import random
import asyncio

# Initialize pygame
pygame.init()
random.seed()

# Game window dimensions
WIDTH, HEIGHT = 850, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DNA Sequence Alignment")
# Buttons
submit_button_rect = pygame.Rect(50, HEIGHT - 100, 200, 50)
play_again_button_rect = pygame.Rect(300, HEIGHT - 100, 200, 50)
# Fonts
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 16)
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
GENOME_ROW_LENGTH = 50  # 50 characters per row
NUM_GENOME_ROWS = 5  # Display 5 rows for the genome
ROW_SPACING = 80  # Space between rows

# Generate random DNA sequence
def generate_dna_sequence(length):
    random.seed()
    return ''.join(random.choice('ATGC') for _ in range(length))

def generate_player_sequence_from_genome(genome_seq):
    # Step 1: Take a random substring of length 50 to 60 from the genome sequence
    start_idx = random.randint(0, len(genome_seq) - 55)
    player_seq = list(genome_seq[start_idx:start_idx + random.randint(50, 55)])

    # Step 2: Randomly delete characters until the length is 50
    while len(player_seq) > 50:
        del player_seq[random.randint(0, len(player_seq) - 1)]

    # Step 3: Randomly mutate 5 to 10 bases in the sequence
    num_mutations = random.randint(0,5)
    for _ in range(num_mutations):
        mutation_idx = random.randint(0, len(player_seq) - 1)
        original_base = player_seq[mutation_idx]
        possible_bases = [base for base in 'ATGC' if base != original_base]
        player_seq[mutation_idx] = random.choice(possible_bases)

    return ''.join(player_seq)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Draw the sequences on the screen
def draw_sequences(player_seq, genome_seq, alignment_start, selected_position):
    window.fill(WHITE,(0,0,WIDTH,HEIGHT-200))  # Clear screen to white

    # Draw genome sequence in 5 rows of 50 bases each
    y_offset = 50
    for row in range(NUM_GENOME_ROWS):
        start_idx = row * GENOME_ROW_LENGTH
        end_idx = start_idx + GENOME_ROW_LENGTH
        genome_subseq = genome_seq[start_idx:end_idx]
        for i, base in enumerate(genome_subseq):
            color = COLORS[base]
            draw_text(base, font, color, window, 50 + i * 15, y_offset + row * ROW_SPACING)
  
    # Draw player sequence in between the rows of the genome sequence
    player_seq_y_offset = y_offset + 35  # Start in the first empty line
    for row in range(NUM_GENOME_ROWS):
        start_idx = row * GENOME_ROW_LENGTH
        end_idx = start_idx + GENOME_ROW_LENGTH
        alignment_end = alignment_start + len(player_seq) - 1
        if alignment_start >= start_idx and alignment_start <= end_idx:
            player_subseq = player_seq[:end_idx-alignment_start]
            for i, base in enumerate(player_subseq):
                color = COLORS[base]
                draw_text(base, font, color, window, 50 + (i+alignment_start-start_idx) * 15, player_seq_y_offset + row * ROW_SPACING)

        elif alignment_end >= start_idx and alignment_end <= end_idx:
            player_subseq = player_seq[start_idx-alignment_start:]
            for i, base in enumerate(player_subseq):
                color = COLORS[base]
                draw_text(base, font, color, window, 50 + i * 15, player_seq_y_offset + row * ROW_SPACING)

    # Display current score
    score = calculate_score(player_seq, genome_seq, alignment_start)
    score_text = font.render(f"Score: {score}", True, BLACK)
    window.blit(score_text, (50, y_offset + NUM_GENOME_ROWS * ROW_SPACING + 50))

    # Highlight selected position for gaps
    if selected_position is not None:
        row = selected_position // GENOME_ROW_LENGTH
        col = selected_position % GENOME_ROW_LENGTH
        pygame.draw.rect(window, BLACK, (50 + col * 15, 85 + row * ROW_SPACING, 16, 30), 1)

    pygame.display.update()

def draw_buttons(clicked_button):
    window.fill(WHITE,(0,HEIGHT-200,WIDTH,HEIGHT))  # Clear screen to white
    if clicked_button == "submit":
        pygame.draw.rect(window, (0, 200, 0), submit_button_rect)  # Darker green when clicked
    else:
        pygame.draw.rect(window, GREEN, submit_button_rect)  # Regular green

    if clicked_button == "play_again":
        pygame.draw.rect(window, (0, 0, 200), play_again_button_rect)  # Darker blue when clicked
    else:
        pygame.draw.rect(window, BLUE, play_again_button_rect)  # Regular blue
    
    draw_text("Submit", font, BLACK, window, submit_button_rect.x + 50, submit_button_rect.y + 10)
    draw_text("Play Again", font, WHITE, window, play_again_button_rect.x + 25, play_again_button_rect.y + 10)
    draw_text("A/W/S/D: move the read", small_font, BLACK, window, 550, 600)
    draw_text("Arrow keys: move the cursor", small_font, BLACK, window, 550, 650)
    draw_text("Space: add a gap", small_font, BLACK, window, 550, 700)
    draw_text("Backspace: delete a gap", small_font, BLACK, window, 550, 750)

def draw_leaderboard(leaderboard, score, time, name, status, clicked_button):
    window.fill(WHITE,(0,0,WIDTH,HEIGHT))
    score_text = "Your final score is {} in {:.2f} seconds. ".format(score, time)
    if status == "won":
        score_text += "You made the leaderboard! Please enter your name: "
        color = RED
    else:
        score_text += "Sorry you didn't make the leaderboard! Try again?"
        color = BLACK
    draw_text(score_text, small_font, color, window, 50, 50)
    if status == "won":
        pygame.draw.rect(window, BLACK, (50, 100, 200, 30), 1)
        draw_text("press Enter to confirm", small_font, BLACK, window, 275, 110)
        if name:
            draw_text(name, font, BLACK, window, 55, 100)
    draw_text("Rank", font, BLACK, window, 50, 150)
    draw_text("Name", font, BLACK, window, 250, 150)
    draw_text("Score", font, BLACK, window, 450, 150)
    draw_text("Time", font, BLACK, window, 650, 150)
    for i,player in enumerate(leaderboard):
        color = GREEN if name==player["name"] else BLACK
        draw_text(str(i+1), font, color, window, 50, 200+50*i)
        draw_text(player["name"], font, color, window, 250, 200+50*i)
        draw_text(str(player["score"]), font, color, window, 450, 200+50*i)
        draw_text("{:.2f}".format(player["time"]), font, color, window, 650, 200+50*i) 
    if clicked_button == "play_again":
        pygame.draw.rect(window, (0, 0, 200), play_again_button_rect)  # Darker blue when clicked
    else:
        pygame.draw.rect(window, BLUE, play_again_button_rect)  # Regular blue    
    draw_text("Play Again", font, WHITE, window, play_again_button_rect.x + 25, play_again_button_rect.y + 10)
    pygame.display.update()

# Calculate the score based on alignment
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

# Main game loop
async def main():
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
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Time in seconds
            # Display the timer
            if elapsed_time-display_time>=0.1:
                display_time = elapsed_time
            draw_text(f"Time: {display_time:.2f} sec", font, BLACK, window, 50, 600)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if the mouse clicked a button
                    if submit_button_rect.collidepoint(mouse_pos):
                        clicked_button = "submit"  # Set clicked effect
                        status = "score"
                        final_score = calculate_score(player_seq, genome_seq, alignment_start)
                        final_time = elapsed_time
                        if len(leaderboard)<10 or final_score>leaderboard[-1]["score"] or (final_score==leaderboard[-1]["score"] and final_time<leaderboard[-1]["time"]):
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
                    clicked_button = None  # Reset clicked button
                elif event.type == pygame.KEYDOWN:
                    # Add a gap at the selected position
                    if event.key == pygame.K_SPACE and selected_position is not None:
                        if selected_position>=alignment_start and selected_position<alignment_start+len(player_seq)-1:
                            player_seq = player_seq[:selected_position-alignment_start]+'-'+player_seq[selected_position-alignment_start:]

                    # Delete a gap at the selected position
                    if event.key == pygame.K_BACKSPACE and selected_position is not None:
                        if selected_position>=alignment_start and selected_position<alignment_start+len(player_seq)-1:
                            if player_seq[selected_position-alignment_start] == '-':
                                player_seq = player_seq[:selected_position-alignment_start]+player_seq[selected_position-alignment_start+1:]

                    # Move the selected position for gap insertion
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

                    # Move the alignment start position (A for left, D for right)
                    if event.key == pygame.K_a:  # Move alignment left
                        alignment_start = max(0, alignment_start - 1)
                    elif event.key == pygame.K_d:  # Move alignment right
                        alignment_start = min(len(genome_seq) - len(player_seq), alignment_start + 1)
                    elif event.key == pygame.K_w: # Move alignment up
                        alignment_start = max(0, alignment_start - GENOME_ROW_LENGTH)
                    elif event.key == pygame.K_s: # Move alignment down
                        alignment_start = min(len(genome_seq) - len(player_seq), alignment_start + GENOME_ROW_LENGTH)
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
                    clicked_button = None  # Reset clicked button
                elif event.type == pygame.KEYDOWN and input_active:
                    # Allow player to type their name
                    if event.key == pygame.K_RETURN and player_name:
                        # Confirm player name submission
                        leaderboard.append({'name': player_name, 'score': final_score, 'time': final_time})
                        leaderboard = sorted(leaderboard, key=lambda x:(-x['score'], x['time'], x['name']))
                        if len(leaderboard)>10:
                            leaderboard.pop()
                        input_active = False  # Deactivate input box after submitting
                    elif event.key == pygame.K_BACKSPACE and player_name:
                        # Remove last character if backspace is pressed
                        player_name = player_name[:-1]
                    else:
                        # Add new character to player name (ignore special keys)
                        if len(player_name) < 15:  # Limit name length
                            player_name += event.unicode

        #pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
