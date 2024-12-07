import pygame
import random
import asyncio
from moviepy.video.io.VideoFileClip import VideoFileClip
import pygame.joystick
import math


# Initialize pygame
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
random.seed()


# Add these after your pygame initialization code
background_path = "C:\\Users\\kmccl\\Documents\\GitHub\\seq_align_game-main\\gamebackground2.png"
startscreen_background_path = "C:\\Users\\kmccl\\Documents\\GitHub\\seq_align_game-main\\tutorial.png"
logo_path = "C:\\Users\\kmccl\\Documents\\GitHub\\seq_align_game-main\\zymologo2.png"

# Load both images
try:
    background_image = pygame.image.load(background_path)
except pygame.error as e:
    print(f"Could not load background image: {e}")
    background_image = None

try:
    logo_image = pygame.image.load(logo_path)
except pygame.error as e:
    print(f"Could not load logo image: {e}")
    logo_image = None

try:
    startscreen_background_image = pygame.image.load(startscreen_background_path)
except pygame.error as e:
    print(f"Could not load start screen background image: {e}")
    startscreen_background_image = None

# Add banner height constant after the other display constants
BANNER_HEIGHT = 80  # Height of the banner in pixels
# Get the display info to set up dynamic window sizing
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Calculate the maximum size while maintaining aspect ratio
target_ratio = 16/9
current_ratio = SCREEN_WIDTH/SCREEN_HEIGHT

if current_ratio > target_ratio:
    # Width is the limiting factor
    HEIGHT = int(SCREEN_HEIGHT * 0.9)  # Use 90% of screen height
    HEIGHT_WITH_BANNER = HEIGHT + BANNER_HEIGHT  # Add banner height
    WIDTH = int(HEIGHT * target_ratio)
else:
    # Height is the limiting factor
    WIDTH = int(SCREEN_WIDTH * 0.9)  # Use 90% of screen width
    HEIGHT = int(WIDTH / target_ratio)
    HEIGHT_WITH_BANNER = HEIGHT + BANNER_HEIGHT  # Add banner height

# Create padding to maintain same empty space
VERTICAL_PADDING = int(HEIGHT * 0.05)

# Create the window - modified to use hardware acceleration
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("DNA Sequence Alignment")

# Adjust scale factors
SCALE_X = WIDTH / 1920
SCALE_Y = HEIGHT / 1080

# Buttons - scale with window size
submit_button_rect = pygame.Rect(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
play_again_button_rect = pygame.Rect(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
exit_button_rect = pygame.Rect(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)
instructions_button_rect = pygame.Rect(750 * SCALE_X, HEIGHT - 100 * SCALE_Y, 180 * SCALE_X, 50 * SCALE_Y)

# Update font sizes with better scaling
font_size = int(36 * min(SCALE_X, SCALE_Y))  # Reduced from 48
small_font_size = int(24 * min(SCALE_X, SCALE_Y))  # Reduced from 32
font = pygame.font.SysFont('Arial', font_size)
small_font = pygame.font.SysFont('Arial', small_font_size)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Colors for nucleotides
COLORS = {
    'A': (220, 20, 60),   # Crimson red
    'T': (46, 139, 87),   # Sea green
    'G': (25, 25, 112),   # Midnight blue
    'C': (218, 165, 32),  # Golden rod
    '-': (128, 128, 128)  # Gray for gaps
}



# Scoring values
MATCH = 1
MISMATCH = -1
GAP_OPENING = -2
GAP_EXTENSION = -1

# Display dimensions for genome sequence
GENOME_ROW_LENGTH = 42
NUM_GENOME_ROWS = 6
ROW_SPACING = int(200 * SCALE_Y)

BUTTON_A = 0  # Typically the A button is index 0
BUTTON_B = 1  # Typically the B button is index 1
BUTTON_Y = 3 
BUTTON_X = 2

# Video file path
video_path = "C:\\Users\\kmccl\\Documents\\GitHub\\seq_align_game-main\\zymologo.mov"

def draw_banner():
    # Draw black banner
    banner_rect = pygame.Rect(0, 0, WIDTH, BANNER_HEIGHT)
    pygame.draw.rect(window, BLACK, banner_rect)
    
    if logo_image is not None:
        # Calculate logo dimensions (maintain aspect ratio)
        logo_height = BANNER_HEIGHT - 4  # Leave 2px padding top and bottom
        aspect_ratio = logo_image.get_width() / logo_image.get_height()
        logo_width = int(logo_height * aspect_ratio)
        
        # Scale logo with smoothscale for better quality
        try:
            # Convert image to RGB mode if it's not already
            if logo_image.get_bitsize() != 32:
                temp_surface = pygame.Surface((logo_image.get_width(), logo_image.get_height()), pygame.SRCALPHA)
                temp_surface.blit(logo_image, (0, 0))
                logo_image_rgb = temp_surface
            else:
                logo_image_rgb = logo_image
                
            # Use smoothscale for better quality scaling
            scaled_logo = pygame.transform.smoothscale(logo_image_rgb, (logo_width, logo_height))
        except:
            # Fallback to regular scale if smoothscale fails
            scaled_logo = pygame.transform.scale(logo_image, (logo_width, logo_height))
        
        # Position logo on far right with 5px padding
        logo_x = WIDTH - logo_width - 5
        logo_y = 2  # 2px padding from top
        
        # Draw logo
        window.blit(scaled_logo, (logo_x, logo_y))

# Add this function after your other function definitions
def draw_background():
    if background_image is not None:
        # Scale the background image to match the window size
        scaled_background = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        window.blit(scaled_background, (0, 0))
    else:
        # Fallback to white background if image couldn't be loaded
        window.fill(WHITE)

def get_score_color(score):
    """
    Returns a color tuple (R,G,B) that smoothly transitions from red to yellow to green,
    with -20 appearing yellowish and transitioning to full green by 10
    """
    if score <= -40:
        return (255, 0, 0)  # Pure red for very low scores
    elif score <= -20:
        # Transition from red to yellow (-40 to -20)
        ratio = (score + 40) / 20
        return (255, int(255 * ratio), 0)
    elif score <= 10:
        # Transition from yellow to green (-20 to 10)
        ratio = (score + 20) / 30
        return (int(255 * (1 - ratio)), 255, 0)
    else:
        return (0, 255, 0)  # Pure green for scores above 10

# Update video handling in play_video function
def play_video(video_path):
    clip = VideoFileClip(video_path)
    # Calculate video dimensions maintaining aspect ratio
    video_ratio = clip.w / clip.h
    if video_ratio > target_ratio:
        video_width = WIDTH
        video_height = int(WIDTH / video_ratio)
    else:
        video_height = HEIGHT
        video_width = int(HEIGHT * video_ratio)
    
    # Center the video
    x_offset = (WIDTH - video_width) // 2
    y_offset = (HEIGHT - video_height) // 2
    
    clip = clip.resize((video_width, video_height))
    clip.preview()

def create_blinking_text_surface(text, font_size, color, current_time):
    """
    Creates a text surface that changes alpha based on time.
    Returns a surface with the text at the current alpha value.
    """
    # Create font for the blinking text
    blink_font = pygame.font.SysFont('Arial', font_size)
    
    # Calculate alpha value using sine wave for smooth blinking
    # Complete cycle every 1000ms (1 second)
    alpha = abs(math.sin(current_time * 0.003)) * 255
    
    # Create the text surface
    text_surface = blink_font.render(text, True, color)
    
    # Create a surface with alpha channel
    alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    
    # Set the alpha value for the entire surface
    alpha_surface.fill((color[0], color[1], color[2], alpha))
    
    # Blit the text onto a new surface with alpha
    final_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    final_surface.blit(text_surface, (0, 0))
    final_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    return final_surface

def draw_start_screen():
    if startscreen_background_image is not None:
        # Scale the background image to match the window size
        scaled_background = pygame.transform.scale(startscreen_background_image, (WIDTH, HEIGHT))
        window.blit(scaled_background, (0, 0))
    
    # Draw black banner at the top
    banner_rect = pygame.Rect(0, 0, WIDTH, BANNER_HEIGHT)
    pygame.draw.rect(window, BLACK, banner_rect)
    
    # Add blinking text
    current_time = pygame.time.get_ticks()
    blink_font_size = int(36 * min(SCALE_X, SCALE_Y))  # Scale font size with window
    blink_text = "Press any button to continue"
    
    # Create blinking text surface
    blink_surface = create_blinking_text_surface(blink_text, blink_font_size, WHITE, current_time)
    
    # Center the text in the banner
    text_x = (WIDTH - blink_surface.get_width()) // 2
    text_y = (BANNER_HEIGHT - blink_surface.get_height()) // 2
    
    # Draw the blinking text
    window.blit(blink_surface, (text_x, text_y))
    
    # If you have a logo, draw it as well
    if logo_image is not None:
        # Calculate logo dimensions (maintain aspect ratio)
        logo_height = BANNER_HEIGHT - 4  # Leave 2px padding top and bottom
        aspect_ratio = logo_image.get_width() / logo_image.get_height()
        logo_width = int(logo_height * aspect_ratio)
        
        try:
            # Convert image to RGB mode if needed
            if logo_image.get_bitsize() != 32:
                temp_surface = pygame.Surface((logo_image.get_width(), logo_image.get_height()), pygame.SRCALPHA)
                temp_surface.blit(logo_image, (0, 0))
                logo_image_rgb = temp_surface
            else:
                logo_image_rgb = logo_image
            
            # Scale the logo
            scaled_logo = pygame.transform.smoothscale(logo_image_rgb, (logo_width, logo_height))
        except:
            scaled_logo = pygame.transform.scale(logo_image, (logo_width, logo_height))
        
        # Position logo on far right with padding
        logo_x = WIDTH - logo_width - 5
        logo_y = 2
        
        # Draw logo
        window.blit(scaled_logo, (logo_x, logo_y))
    
    pygame.display.update()
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def generate_dna_sequence(length):
    # Generate a random sequence of specified length
    return ''.join(random.choice('ATGC') for _ in range(length))

def generate_player_sequence_from_genome(genome_seq):
    """
    Generate a player sequence that requires ONLY gap insertions (no deletions) to achieve maximum score.
    The sequence will be derived from the genome sequence with:
    - Gaps that need to be inserted by the player (sequence is shorter than matching genome region)
    - Some point mutations
    - NO need for deletions
    
    Maximum score is fixed at 50 points:
    - Each match = +1 point
    - Each mismatch = -1 point
    - Gap opening = -2 points
    - Gap extension = -1 point
    """
    # Find all possible 54-base windows in the genome (we'll create a 50-base player sequence from this)
    window_size = 54  # Larger window to accommodate the gaps we'll need
    possible_windows = []
    
    for i in range(len(genome_seq) - window_size + 1):
        window = genome_seq[i:i + window_size]
        possible_windows.append((i, window))
    
    # Select a random window
    start_idx, genome_window = random.choice(possible_windows)
    
    # Create player sequence by removing 4 bases (creating gaps that need to be filled)
    # First, convert genome window to list and make a copy for the player sequence
    genome_bases = list(genome_window)
    player_seq = list(genome_window)
    
    # Select 4 positions to remove (these will need gaps added by player)
    gap_positions = random.sample(range(len(genome_bases)), 4)
    gap_positions.sort(reverse=True)  # Remove from end to avoid index issues
    
    # Remove these positions from player sequence
    for pos in gap_positions:
        player_seq.pop(pos)
    
    # Add 2 point mutations
    # Make sure we don't mutate positions next to our gap positions
    gap_adjacent = set()
    for pos in gap_positions:
        gap_adjacent.add(pos - 1)
        gap_adjacent.add(pos)
        gap_adjacent.add(pos + 1)
    
    available_positions = [i for i in range(len(player_seq)) if i not in gap_adjacent]
    mutation_positions = random.sample(available_positions, 2)
    
    for pos in mutation_positions:
        original_base = player_seq[pos]
        possible_bases = [b for b in 'ATGC' if b != original_base]
        player_seq[pos] = random.choice(possible_bases)
    
    # Now the setup for scoring 50 points:
    # - Player sequence is 50 bases (54 - 4 removals)
    # - Need to add 4 gaps to match genome sequence
    # - Score breakdown:
    #   * 48 matches (+48 points)
    #   * 2 mismatches (-2 points)
    #   * 4 gap openings (-8 points)
    #   * 4 gap extensions (-4 points)
    #   * Total = 48 - 2 - 8 - 4 = 34 points
    # - Add 16 more bases that match perfectly to reach 50
    extra_genome = genome_seq[start_idx + window_size:start_idx + window_size + 16]
    player_seq.extend(list(extra_genome))
    
    return ''.join(player_seq)
def create_glow_surface(text, font, color, alpha):
    # Create text surface with the base color
    text_surface = font.render(text, True, color)
    
    # Create a surface for the glow effect with alpha channel
    glow_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
    
    # Create a larger surface for the blur effect
    blur_size = 2
    blur_surface = pygame.Surface((text_surface.get_width() + blur_size * 1.5, 
                                 text_surface.get_height() + blur_size * 2), 
                                pygame.SRCALPHA)
    
    # Draw the text multiple times with slight offsets for blur effect
    for offset in range(blur_size):
        for x in range(-offset, offset + 1):
            for y in range(-offset, offset + 1):
                blur_surface.blit(text_surface, 
                                (blur_size + x, blur_size + y))
    
    # Scale the blur effect's alpha
    blur_surface.fill((0, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    
    # Combine the glow and text
    glow_surface.blit(blur_surface, (-blur_size, -blur_size))
    glow_surface.blit(text_surface, (0, 0))
    
    return glow_surface

def draw_sequences(player_seq, genome_seq, alignment_start, selected_position, current_time, showing_hint=False, optimal_position=None):
    # Draw background instead of filling with white
    draw_background()
    draw_banner()
    base_font_size = int(50 * min(SCALE_X, SCALE_Y))  # Make this larger for bigger letters
    base_font = pygame.font.SysFont('Arial', base_font_size)

    # Calculate optimal spacing and positioning
    char_width = 35 * SCALE_X
    char_height = 60 * SCALE_Y
    
    # Calculate total width needed for sequence display
    sequence_width = GENOME_ROW_LENGTH * char_width
    
    # Center the sequences horizontally
    x_start = (WIDTH - sequence_width) / 2
    y_start = BANNER_HEIGHT + (50 * SCALE_Y)
    
    game_area_height = HEIGHT - (2 * VERTICAL_PADDING)
    row_spacing = game_area_height / (NUM_GENOME_ROWS + 1)

    # Calculate glow alpha using sine wave for animation
    glow_alpha = int(128 + 64 * math.sin(current_time * 0.004))  # Adjust speed with multiplier
    
    # Draw genome sequence
    for row in range(NUM_GENOME_ROWS):
        start_idx = row * GENOME_ROW_LENGTH
        end_idx = start_idx + GENOME_ROW_LENGTH
        genome_subseq = genome_seq[start_idx:end_idx]
        
        # Draw row label
        label_x = x_start - 140 * SCALE_X
        row_y = y_start + row * row_spacing + 10
        draw_text(f"Genome:", small_font, BLACK, window, label_x, row_y + 10)
        
        # Draw sequence
        for i, base in enumerate(genome_subseq):
            x_pos = x_start + i * char_width
            color = COLORS[base]
            
            if showing_hint and optimal_position is not None:
                absolute_pos = start_idx + i + 4
                # Add length of player sequence without gaps to get correct end position
                player_len = len([c for c in player_seq if c != '-']) + 4
                if optimal_position <= absolute_pos < optimal_position + player_len:
                    # Draw a yellow highlight rectangle behind the base
                    highlight_rect = pygame.Rect(x_pos - 2, row_y - 2,
                                            char_width + 4, char_height + 4)
                    pygame.draw.rect(window, YELLOW, highlight_rect)
            
            draw_text(base, base_font, color, window, x_pos, row_y)
            
            if (selected_position is not None and 
                selected_position == start_idx + i and 
                alignment_start <= selected_position < alignment_start + len(player_seq)):
                pygame.draw.rect(window, BLACK, 
                               (x_pos - 2, row_y + 43, 
                                char_width, char_height * 0.7), 1)
    
    # Draw player sequence with glow effect
    player_seq_y_offset = 40 * SCALE_Y
    
    for row in range(NUM_GENOME_ROWS):
        row_start_idx = row * GENOME_ROW_LENGTH
        row_end_idx = row_start_idx + GENOME_ROW_LENGTH
        row_y = y_start + row * row_spacing
        
        if row_start_idx <= alignment_start < row_end_idx:
            # Draw row label
            label_x = x_start - 140 * SCALE_X
            glow_label = create_glow_surface("Read:", small_font, WHITE, glow_alpha)
            window.blit(glow_label, (label_x, row_y + player_seq_y_offset +25))
            
            # First row of player sequence
            bases_in_row = min(row_end_idx - alignment_start, len(player_seq))
            player_subseq = player_seq[:bases_in_row]
            offset = alignment_start - row_start_idx
            
            for i, base in enumerate(player_subseq):
                color = COLORS[base]
                x_pos = x_start + (offset + i) * char_width
                
                # Create and draw the glowing text
                glow_surface = create_glow_surface(base, base_font, color, glow_alpha)  # Use base_font here
                window.blit(glow_surface, (x_pos, row_y + player_seq_y_offset + 10))
        
        elif alignment_start <= row_start_idx < alignment_start + len(player_seq):
            # Draw row label
            label_x = x_start - 140 * SCALE_X
            glow_label = create_glow_surface("Read:", small_font, WHITE, glow_alpha)
            window.blit(glow_label, (label_x, row_y + player_seq_y_offset +25))
            
            # Middle or last row of player sequence
            seq_offset = row_start_idx - alignment_start
            bases_in_row = min(GENOME_ROW_LENGTH, len(player_seq) - seq_offset)
            player_subseq = player_seq[seq_offset:seq_offset + bases_in_row]
            
            for i, base in enumerate(player_subseq):
                color = COLORS[base]
                x_pos = x_start + i * char_width
                
                # Create and draw the glowing text
                glow_surface = create_glow_surface(base, base_font, color, glow_alpha)  # Use base_font here
                window.blit(glow_surface, (x_pos, row_y + player_seq_y_offset + 10))


def draw_buttons(clicked_button, score):
    # Create footer section for buttons and instructions
    footer_height = 100 * SCALE_Y
    footer_y = HEIGHT - footer_height
    
    # Clear the footer area
    window.fill(BLACK, (0, footer_y, WIDTH, footer_height))
    
    # Calculate improved widths for layout - make buttons wider to better fit text
    button_width = 180 * SCALE_X  # Increased from 160
    button_height = 60 * SCALE_Y  # Increased from 50 for better proportions
    instructions_width = 800 * SCALE_X
    score_width = 200 * SCALE_X
    button_spacing = 30 * SCALE_X  # Consistent spacing between buttons
    
    # Layout: [Score] [Submit] [Play Again] [Exit] [Instructions Panel]
    total_width = score_width + (button_width * 3) + (button_spacing * 3) + instructions_width
    start_x = (WIDTH - total_width) / 2
    
    # Helper function to center text in button
    def center_text_in_button(text, button_rect, color):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = button_rect.center
        window.blit(text_surface, text_rect)
    
    # Draw score panel with improved centering
    score_rect = pygame.Rect(start_x, footer_y + (footer_height - button_height) / 2, 
                           score_width, button_height)
    pygame.draw.rect(window, get_score_color(score), score_rect, border_radius=int(10 * min(SCALE_X, SCALE_Y)))
    score_text = f"Score: {score}"
    center_text_in_button(score_text, score_rect, BLACK)
    
    # Update button rectangles with new positions and consistent spacing
    x_pos = start_x + score_width + button_spacing
    button_y = footer_y + (footer_height - button_height) / 2
    
    # Submit button
    submit_button_rect.update(x_pos, button_y, button_width, button_height)
    x_pos += button_width + button_spacing
    
    # Play Again button
    play_again_button_rect.update(x_pos, button_y, button_width, button_height)
    x_pos += button_width + button_spacing
    
    # Exit button
    exit_button_rect.update(x_pos, button_y, button_width, button_height)
    
    # Draw buttons with improved colors and consistent styling
    def draw_button(rect, text, base_color, highlight_color, is_clicked, text_color):
        color = highlight_color if is_clicked else base_color
        pygame.draw.rect(window, color, rect, border_radius=int(10 * min(SCALE_X, SCALE_Y)))
        center_text_in_button(text, rect, text_color)
    
    # Draw all buttons using the helper function
    draw_button(submit_button_rect, "Submit", GREEN, (0, 180, 0), 
                clicked_button == "submit", BLACK)
    draw_button(play_again_button_rect, "Play Again", BLUE, (0, 0, 180), 
                clicked_button == "play_again", WHITE)
    draw_button(exit_button_rect, "Exit Game", RED, (180, 0, 0), 
                clicked_button == "exit", WHITE)
    draw_button(instructions_button_rect, "Instructions", BLUE, (0, 0, 180), 
                clicked_button == "instructions", WHITE)
    
    # Draw instructions panel
    instructions_x = exit_button_rect.right + 40 * SCALE_X
    instructions_height = footer_height * 0.8  # Slightly reduced height for better appearance
    instructions_y = footer_y + (footer_height - instructions_height) / 2  # Center vertically
    
    # Draw panel background
    pygame.draw.rect(window, (200, 200, 200),
                    (instructions_x, instructions_y,
                     instructions_width, instructions_height),
                    border_radius=int(10 * min(SCALE_X, SCALE_Y)))
    
    # Define all instructions with proper grouping and spacing
    instruction_groups = [
        {
            "title": "Movement Controls",
            "title_color": BLACK,
            "items": [
                ("Left Stick/WASD: Move sequence", BLUE),
                ("Right Stick/Arrows: Move cursor", BLUE)
            ]
        },
        {
            "title": "Editing Controls",
            "title_color": BLACK,
            "items": [
                ("A/Space: Add gap at cursor", RED),
                ("B/Backspace: Delete gap", RED)
            ]
        }
    ]
    
    # Calculate layout dimensions for instructions
    col_width = instructions_width / 2
    padding_x = 25 * SCALE_X
    padding_y = SCALE_Y
    line_height = 20 * SCALE_Y
    
    # Draw each instruction group
    for col_idx, group in enumerate(instruction_groups):
        x_offset = instructions_x + col_idx * col_width + padding_x
        y_offset = instructions_y + padding_y
        
        # Draw group title
        draw_text(group["title"], small_font, group["title_color"], 
                 window, x_offset, y_offset)
        y_offset += line_height + 5 * SCALE_Y
        
        # Draw instruction items with improved spacing
        for control, color in group["items"]:
            # Draw the control part (before the colon)
            draw_text(f"{control}", small_font, color, 
                     window, x_offset + 10 * SCALE_X, y_offset)
            
            y_offset += line_height
    
    pygame.display.update()

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
    """
    Calculate alignment score with bounds checking:
    Match: +1
    Mismatch: -1
    Gap opening: -2
    Gap extension: -1
    """
    # First check if alignment_start + player sequence length would exceed genome length
    if alignment_start + len(player_seq) > len(genome_seq):
        return float('-inf')  # Return very low score if alignment would go out of bounds
    
    score = 0
    gap_open = False
    
    for i in range(len(player_seq)):
        if player_seq[i] == '-':
            if not gap_open:
                score += GAP_OPENING  # -2
                gap_open = True
            else:
                score += GAP_EXTENSION  # -1
        else:
            gap_open = False
            try:
                if player_seq[i] == genome_seq[alignment_start + i]:
                    score += MATCH  # +1
                else:
                    score += MISMATCH  # -1
            except IndexError:
                return float('-inf')  # Return very low score if we somehow hit an index error
                
    return score

def find_optimal_position(player_seq, genome_seq):
    """Find the position in the genome sequence that gives the highest alignment score."""
    max_score = float('-inf')
    best_position = 0
    
    # We know the sequence needs 4 gaps, so the aligned region will be 54 bases long 
    # (50 bases from player sequence + 4 gaps)
    optimal_window_size = len(player_seq) + 4
    
    # Try every possible position
    for pos in range(len(genome_seq) - optimal_window_size + 1):
        score = calculate_score(player_seq, genome_seq, pos)
        if score > max_score:
            max_score = score
            best_position = pos
    
    return best_position, max_score

async def main():
    global WIDTH, HEIGHT, SCALE_X, SCALE_Y, font, small_font, submit_button_rect, play_again_button_rect, window

    showing_hint = False
    optimal_position = None

    # Add input cooldown variables
    last_input_time = pygame.time.get_ticks()
    input_cooldown = 500  # 500ms cooldown between inputs


    # Movement timing variables
    last_horizontal_movement_time = 0
    last_vertical_movement_time = 0
    base_horizontal_cooldown = 200  # Base cooldown values
    base_vertical_cooldown = 300
    horizontal_cooldown = base_horizontal_cooldown  # Current cooldown values
    vertical_cooldown = base_vertical_cooldown

    # Acceleration tracking
    horizontal_hold_start = 0
    vertical_hold_start = 0
    last_x_direction = 0  # Track direction to detect changes
    last_y_direction = 0
    
    # Acceleration parameters
    min_horizontal_cooldown = 10  # Fastest possible movement speed
    min_vertical_cooldown = 10
    acceleration_time = 2000  # Time in ms over which to reach max speed

    # D-pad timing variables
    last_dpad_horizontal_movement_time = 0
    last_dpad_vertical_movement_time = 0
    dpad_horizontal_cooldown = base_horizontal_cooldown
    dpad_vertical_cooldown = base_vertical_cooldown
    dpad_horizontal_hold_start = 0
    dpad_vertical_hold_start = 0
    last_dpad_x_direction = 0
    last_dpad_y_direction = 0

    # Right stick timing variables
    last_right_stick_horizontal_movement_time = 0
    last_right_stick_vertical_movement_time = 0
    right_stick_horizontal_cooldown = base_horizontal_cooldown
    right_stick_vertical_cooldown = base_vertical_cooldown
    right_stick_horizontal_hold_start = 0
    right_stick_vertical_hold_start = 0
    last_right_stick_x_direction = 0
    last_right_stick_y_direction = 0

    # First, add these variables at the start of your main() function with your other timing variables:
    button_a_last_press = 0
    button_b_last_press = 0
    button_x_last_press = 0
    button_cooldown = 300  # 300ms = 0.3 seconds


    clip = VideoFileClip(video_path)
    video_surface = pygame.Surface((WIDTH, HEIGHT))
    
    # Move the video drawing logic outside of a nested function
    start_time = pygame.time.get_ticks()
    video_duration = clip.duration
    playing_video = True

    while playing_video:
        current_time = pygame.time.get_ticks()
        t = (current_time - start_time) / 1000
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
        
        # Only check for inputs if enough time has passed
        if current_time - last_input_time >= input_cooldown:
            # Check for controller button presses
            if len(joysticks) > 0:
                joystick = joysticks[0]
                for i in range(joystick.get_numbuttons()):
                    if joystick.get_button(i):
                        playing_video = False
                        last_input_time = current_time
                        break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                playing_video = False
                break
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                current_ratio = WIDTH/HEIGHT

                if current_ratio > target_ratio:
                    HEIGHT = event.size[1]
                    WIDTH = int(HEIGHT * target_ratio)
                else:
                    WIDTH = event.size[0]
                    HEIGHT = int(WIDTH / target_ratio)

                window = pygame.display.set_mode((WIDTH, HEIGHT), 
                                            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
                SCALE_X = WIDTH / 1920
                SCALE_Y = HEIGHT / 1080
    
                # Update font sizes with better scaling
                font_size = int(36 * min(SCALE_X, SCALE_Y))
                small_font_size = int(24 * min(SCALE_X, SCALE_Y))
                font = pygame.font.SysFont('Arial', font_size)
                small_font = pygame.font.SysFont('Arial', small_font_size)
    
                # Update button positions
                submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                exit_button_rect.update(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)
                    
        await asyncio.sleep(0)

    draw_start_screen()
    waiting_for_start = True
    while waiting_for_start:
        current_time = pygame.time.get_ticks()
        # Only check for inputs if enough time has passed
        if current_time - last_input_time >= input_cooldown:
            # Check for controller button presses
            if len(joysticks) > 0:
                joystick = joysticks[0]
                for i in range(joystick.get_numbuttons()):
                    if joystick.get_button(i):
                        waiting_for_start = False
                        last_input_time = current_time
                        break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_start = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                current_ratio = WIDTH/HEIGHT
    
                if current_ratio > target_ratio:
                    HEIGHT = event.size[1]
                    WIDTH = int(HEIGHT * target_ratio)
                else:
                    WIDTH = event.size[0]
                    HEIGHT = int(WIDTH / target_ratio)
    
                window = pygame.display.set_mode((WIDTH, HEIGHT), 
                                                pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    
                SCALE_X = WIDTH / 1920
                SCALE_Y = HEIGHT / 1080
    
                # Update font sizes with better scaling
                font_size = int(36 * min(SCALE_X, SCALE_Y))
                small_font_size = int(24 * min(SCALE_X, SCALE_Y))
                font = pygame.font.SysFont('Arial', font_size)
                small_font = pygame.font.SysFont('Arial', small_font_size)
    
                # Update button positions
                submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                exit_button_rect.update(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)

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
            current_time = pygame.time.get_ticks()
            draw_sequences(player_seq, genome_seq, alignment_start, selected_position, current_time, showing_hint, optimal_position)
            score = calculate_score(player_seq, genome_seq, alignment_start)
            draw_buttons(clicked_button, score)
            elapsed_time = (current_time - start_time) / 1000
            if elapsed_time - display_time >= 0.1:
                display_time = elapsed_time
            draw_text(f"Time: {display_time:.2f} sec", font, BLACK, window, 50 * SCALE_X, 600 * SCALE_Y)            
            if len(joysticks) > 0:
                joystick = joysticks[0]
                x_axis = joystick.get_axis(0)  # Left/Right
                y_axis = joystick.get_axis(1)  # Up/Down

                # Determine current x direction (-1, 0, or 1)
                current_x_direction = 0
                if abs(x_axis) > 0.4:
                    current_x_direction = 1 if x_axis > 0 else -1

                # Handle direction changes for horizontal movement
                if current_x_direction != last_x_direction:
                    if current_x_direction != 0:  # Started moving in a direction
                        horizontal_hold_start = current_time
                        horizontal_cooldown = base_horizontal_cooldown
                    else:  # Stopped moving
                        horizontal_cooldown = base_horizontal_cooldown
                last_x_direction = current_x_direction

                # Calculate horizontal acceleration if holding a direction
                if current_x_direction != 0:
                    hold_time = current_time - horizontal_hold_start
                    if hold_time > 0:
                        # Gradually decrease cooldown based on hold time
                        progress = min(1.0, hold_time / acceleration_time)
                        horizontal_cooldown = max(min_horizontal_cooldown,
                            base_horizontal_cooldown - (base_horizontal_cooldown - min_horizontal_cooldown) * progress)

                # Handle horizontal movement with current cooldown
                if current_time - last_horizontal_movement_time >= horizontal_cooldown:
                    if abs(x_axis) > 0.4:
                        move_amount = 1
                        if x_axis > 0:  # Moving right
                            alignment_start = min(len(genome_seq) - len(player_seq), 
                                            alignment_start + move_amount)
                        else:  # Moving left
                            alignment_start = max(0, alignment_start - move_amount)
                        last_horizontal_movement_time = current_time

                # Same logic for vertical movement
                current_y_direction = 0
                if abs(y_axis) > 0.9:
                    current_y_direction = 1 if y_axis > 0 else -1

                if current_y_direction != last_y_direction:
                    if current_y_direction != 0:
                        vertical_hold_start = current_time
                        vertical_cooldown = base_vertical_cooldown
                    else:
                        vertical_cooldown = base_vertical_cooldown
                last_y_direction = current_y_direction

                if current_y_direction != 0:
                    hold_time = current_time - vertical_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        vertical_cooldown = max(min_vertical_cooldown,
                            base_vertical_cooldown - (base_vertical_cooldown - min_vertical_cooldown) * progress)

                if current_time - last_vertical_movement_time >= vertical_cooldown:
                    if abs(y_axis) > 0.9:
                        move_amount = 1
                        if y_axis > 0:  # Moving down
                            new_pos = alignment_start + move_amount * GENOME_ROW_LENGTH
                            alignment_start = min(len(genome_seq) - len(player_seq), new_pos)
                        else:  # Moving up
                            new_pos = alignment_start - move_amount * GENOME_ROW_LENGTH
                            alignment_start = max(0, new_pos)
                        last_vertical_movement_time = current_time

            if len(joysticks) > 0:
                joystick = joysticks[0]
                # Handle analog stick
                x_axis = joystick.get_axis(0)  # Left/Right
                y_axis = joystick.get_axis(1)  # Up/Down

                # Handle analog stick movement (your existing code)
                current_x_direction = 0
                if abs(x_axis) > 0.4:
                    current_x_direction = 1 if x_axis > 0 else -1

                if current_x_direction != last_x_direction:
                    if current_x_direction != 0:
                        horizontal_hold_start = current_time
                        horizontal_cooldown = base_horizontal_cooldown
                    else:
                        horizontal_cooldown = base_horizontal_cooldown
                last_x_direction = current_x_direction

                if current_x_direction != 0:
                    hold_time = current_time - horizontal_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        horizontal_cooldown = max(min_horizontal_cooldown,
                            base_horizontal_cooldown - (base_horizontal_cooldown - min_horizontal_cooldown) * progress)

                # Handle analog horizontal movement with cooldown
                if current_time - last_horizontal_movement_time >= horizontal_cooldown:
                    if abs(x_axis) > 0.4:
                        move_amount = 1
                        if x_axis > 0:
                            alignment_start = min(len(genome_seq) - len(player_seq), 
                                            alignment_start + move_amount)
                        else:
                            alignment_start = max(0, alignment_start - move_amount)
                        last_horizontal_movement_time = current_time

                # Handle analog vertical movement (your existing code)
                current_y_direction = 0
                if abs(y_axis) > 0.9:
                    current_y_direction = 1 if y_axis > 0 else -1

                if current_y_direction != last_y_direction:
                    if current_y_direction != 0:
                        vertical_hold_start = current_time
                        vertical_cooldown = base_vertical_cooldown
                    else:
                        vertical_cooldown = base_vertical_cooldown
                last_y_direction = current_y_direction

                if current_y_direction != 0:
                    hold_time = current_time - vertical_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        vertical_cooldown = max(min_vertical_cooldown,
                            base_vertical_cooldown - (base_vertical_cooldown - min_vertical_cooldown) * progress)

                if current_time - last_vertical_movement_time >= vertical_cooldown:
                    if abs(y_axis) > 0.9:
                        move_amount = 1
                        if y_axis > 0:
                            new_pos = alignment_start + move_amount * GENOME_ROW_LENGTH
                            alignment_start = min(len(genome_seq) - len(player_seq), new_pos)
                        else:
                            new_pos = alignment_start - move_amount * GENOME_ROW_LENGTH
                            alignment_start = max(0, new_pos)
                        last_vertical_movement_time = current_time

                
                # Right stick controls for cursor movement
                right_x_axis = joystick.get_axis(2)  # Right stick horizontal
                right_y_axis = joystick.get_axis(3)  # Right stick vertical
                
                # Handle right stick horizontal movement
                current_right_stick_x_direction = 0
                if abs(right_x_axis) > 0.4:  # Using same threshold as left stick
                    current_right_stick_x_direction = 1 if right_x_axis > 0 else -1

                if current_right_stick_x_direction != last_right_stick_x_direction:
                    if current_right_stick_x_direction != 0:
                        right_stick_horizontal_hold_start = current_time
                        right_stick_horizontal_cooldown = base_horizontal_cooldown
                    else:
                        right_stick_horizontal_cooldown = base_horizontal_cooldown
                last_right_stick_x_direction = current_right_stick_x_direction

                if current_right_stick_x_direction != 0:
                    hold_time = current_time - right_stick_horizontal_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        right_stick_horizontal_cooldown = max(min_horizontal_cooldown,
                            base_horizontal_cooldown - (base_horizontal_cooldown - min_horizontal_cooldown) * progress)

                # Apply right stick horizontal movement with cooldown
                if current_time - last_right_stick_horizontal_movement_time >= right_stick_horizontal_cooldown:
                    if abs(right_x_axis) > 0.4:
                        if right_x_axis < 0:  # Right stick Left
                            if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                                selected_position = alignment_start + len(player_seq) - 1
                            elif selected_position > alignment_start:
                                selected_position -= 1
                        else:  # Right stick Right
                            if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                                selected_position = alignment_start
                            elif selected_position < alignment_start + len(player_seq) - 1:
                                selected_position += 1
                        last_right_stick_horizontal_movement_time = current_time

                # Handle right stick vertical movement
                current_right_stick_y_direction = 0
                if abs(right_y_axis) > 0.9:  # Using same threshold as left stick
                    current_right_stick_y_direction = 1 if right_y_axis > 0 else -1

                if current_right_stick_y_direction != last_right_stick_y_direction:
                    if current_right_stick_y_direction != 0:
                        right_stick_vertical_hold_start = current_time
                        right_stick_vertical_cooldown = base_vertical_cooldown
                    else:
                        right_stick_vertical_cooldown = base_vertical_cooldown
                last_right_stick_y_direction = current_right_stick_y_direction

                if current_right_stick_y_direction != 0:
                    hold_time = current_time - right_stick_vertical_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        right_stick_vertical_cooldown = max(min_vertical_cooldown,
                            base_vertical_cooldown - (base_vertical_cooldown - min_vertical_cooldown) * progress)

                # Apply right stick vertical movement with cooldown
                if current_time - last_right_stick_vertical_movement_time >= right_stick_vertical_cooldown:
                    if abs(right_y_axis) > 0.9:
                        if right_y_axis < 0:  # Right stick Up
                            if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                                # If we're outside the read sequence, go directly to the first position
                                selected_position = alignment_start
                            else:
                                # Move up one row while maintaining column position
                                current_col = selected_position % GENOME_ROW_LENGTH
                                target_position = selected_position - GENOME_ROW_LENGTH
                                if target_position >= alignment_start:
                                    selected_position = target_position
                                else:
                                    # If we're at the top row and moving up, go to first position
                                    selected_position = alignment_start
                        else:  # Right stick Down
                            if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                                # If we're outside the read sequence, go directly to the last position
                                selected_position = alignment_start + len(player_seq) - 1
                            else:
                                # Move down one row while maintaining column position
                                current_col = selected_position % GENOME_ROW_LENGTH
                                target_position = selected_position + GENOME_ROW_LENGTH
                                if target_position < alignment_start + len(player_seq):
                                    selected_position = target_position
                                else:
                                    # If we're at the bottom row and moving down, go to last position
                                    selected_position = alignment_start + len(player_seq) - 1
                        
                        last_right_stick_vertical_movement_time = current_time
                
                dpad_x, dpad_y = joystick.get_hat(0)

                # Handle D-pad horizontal movement
                current_dpad_x_direction = dpad_x
                if current_dpad_x_direction != last_dpad_x_direction:
                    if current_dpad_x_direction != 0:
                        dpad_horizontal_hold_start = current_time
                        dpad_horizontal_cooldown = base_horizontal_cooldown
                    else:
                        dpad_horizontal_cooldown = base_horizontal_cooldown
                last_dpad_x_direction = current_dpad_x_direction

                if current_dpad_x_direction != 0:
                    hold_time = current_time - dpad_horizontal_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        dpad_horizontal_cooldown = max(min_horizontal_cooldown,
                            base_horizontal_cooldown - (base_horizontal_cooldown - min_horizontal_cooldown) * progress)

                # Apply D-pad horizontal movement with cooldown
                if current_time - last_dpad_horizontal_movement_time >= dpad_horizontal_cooldown:
                    if dpad_x != 0:
                        move_amount = 1
                        if dpad_x < 0:  # D-pad Left
                            alignment_start = max(0, alignment_start - move_amount)
                        else:  # D-pad Right
                            alignment_start = min(len(genome_seq) - len(player_seq), 
                                                alignment_start + move_amount)
                        last_dpad_horizontal_movement_time = current_time

                # Handle D-pad vertical movement
                current_dpad_y_direction = dpad_y
                if current_dpad_y_direction != last_dpad_y_direction:
                    if current_dpad_y_direction != 0:
                        dpad_vertical_hold_start = current_time
                        dpad_vertical_cooldown = base_vertical_cooldown
                    else:
                        dpad_vertical_cooldown = base_vertical_cooldown
                last_dpad_y_direction = current_dpad_y_direction

                if current_dpad_y_direction != 0:
                    hold_time = current_time - dpad_vertical_hold_start
                    if hold_time > 0:
                        progress = min(1.0, hold_time / acceleration_time)
                        dpad_vertical_cooldown = max(min_vertical_cooldown,
                            base_vertical_cooldown - (base_vertical_cooldown - min_vertical_cooldown) * progress)

                # Apply D-pad vertical movement with cooldown
                if current_time - last_dpad_vertical_movement_time >= dpad_vertical_cooldown:
                    if dpad_y != 0:
                        move_amount = 1
                        if dpad_y > 0:  # D-pad Up
                            new_pos = alignment_start - move_amount * GENOME_ROW_LENGTH
                            alignment_start = max(0, new_pos)
                        else:  # D-pad Down
                            new_pos = alignment_start + move_amount * GENOME_ROW_LENGTH
                            alignment_start = min(len(genome_seq) - len(player_seq), new_pos)
                        last_dpad_vertical_movement_time = current_time

                # Handle A button (spacebar equivalent) with cooldown
                if joystick.get_button(BUTTON_A) and selected_position is not None:
                    current_time = pygame.time.get_ticks()
                    if current_time - button_a_last_press >= button_cooldown:
                        if selected_position >= alignment_start and selected_position < alignment_start + len(player_seq) - 1:
                            player_seq = player_seq[:selected_position-alignment_start] + '-' + player_seq[selected_position-alignment_start:]
                            button_a_last_press = current_time

                # Handle B button (delete equivalent) with cooldown
                if joystick.get_button(BUTTON_B) and selected_position is not None:
                    current_time = pygame.time.get_ticks()
                    if current_time - button_b_last_press >= button_cooldown:
                        if selected_position >= alignment_start and selected_position < alignment_start + len(player_seq) - 1:
                            if player_seq[selected_position-alignment_start] == '-':
                                player_seq = player_seq[:selected_position-alignment_start] + player_seq[selected_position-alignment_start+1:]
                                button_b_last_press = current_time

                if joystick.get_button(BUTTON_Y):
                    clicked_button = "submit"
                    status = "score"
                    final_score = calculate_score(player_seq, genome_seq, alignment_start)
                    final_time = elapsed_time
                    if len(leaderboard) < 10 or final_score > leaderboard[-1]["score"] or (final_score == leaderboard[-1]["score"] and final_time < leaderboard[-1]["time"]):
                        status = "won"
                        input_active = True
                    else:
                        status = "lost"

                

                if joystick.get_button(BUTTON_X):
                    current_time = pygame.time.get_ticks()
                    if current_time - button_x_last_press >= button_cooldown:
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
                        showing_hint = False
                        optimal_position = None
                        status = "playing"
                        input_active = False
                        button_x_last_press = current_time

                if joystick.get_button(BUTTON_X) and joystick.get_button(BUTTON_Y):  # Press X+Y together to restart
                    current_time = pygame.time.get_ticks()
                    if current_time - button_x_last_press >= button_cooldown:
                        clicked_button = "instructions"
                        # Reset everything and go back to start screen
                        genome_seq = generate_dna_sequence(250)
                        player_seq = generate_player_sequence_from_genome(genome_seq)
                        alignment_start = 0
                        selected_position = None
                        start_time = pygame.time.get_ticks()
                        display_time = 0
                        final_score = 0
                        final_time = 10000
                        player_name = ""
                        showing_hint = False
                        optimal_position = None
                        status = "start"
                        input_active = False
                        draw_start_screen()
                        waiting_for_start = True
                        while waiting_for_start:
                            current_time = pygame.time.get_ticks()
                            # Only check for inputs if enough time has passed
                            if current_time - last_input_time >= input_cooldown:
                                # Check for controller button presses
                                if len(joysticks) > 0:
                                    joystick = joysticks[0]
                                    for i in range(joystick.get_numbuttons()):
                                        if joystick.get_button(i):
                                            waiting_for_start = False
                                            last_input_time = current_time
                                            break
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                                    waiting_for_start = False
                                elif event.type == pygame.VIDEORESIZE:
                                    WIDTH, HEIGHT = event.size
                                    current_ratio = WIDTH/HEIGHT
                        
                                    if current_ratio > target_ratio:
                                        HEIGHT = event.size[1]
                                        WIDTH = int(HEIGHT * target_ratio)
                                    else:
                                        WIDTH = event.size[0]
                                        HEIGHT = int(WIDTH / target_ratio)
                        
                                    window = pygame.display.set_mode((WIDTH, HEIGHT), 
                                                                    pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
                        
                                    SCALE_X = WIDTH / 1920
                                    SCALE_Y = HEIGHT / 1080
                        
                                    # Update font sizes with better scaling
                                    font_size = int(36 * min(SCALE_X, SCALE_Y))
                                    small_font_size = int(24 * min(SCALE_X, SCALE_Y))
                                    font = pygame.font.SysFont('Arial', font_size)
                                    small_font = pygame.font.SysFont('Arial', small_font_size)
                        
                                    # Update button positions
                                    submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                                    play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                                    exit_button_rect.update(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)

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
                        showing_hint = False
                        optimal_position = None
                        status = "playing"
                        input_active = False
                    elif exit_button_rect.collidepoint(mouse_pos):
                        clicked_button = "exit"
                        running = False  # This will exit the game
                    elif instructions_button_rect.collidepoint(mouse_pos):
                        clicked_button = "instructions"
                        # Reset everything but ensure we go back to playing state
                        genome_seq = generate_dna_sequence(250)
                        player_seq = generate_player_sequence_from_genome(genome_seq)
                        alignment_start = 0
                        selected_position = None
                        start_time = pygame.time.get_ticks()
                        display_time = 0
                        showing_hint = False
                        optimal_position = None
                        input_active = False
                        
                        # Show instructions screen
                        draw_start_screen()
                        waiting_for_start = True
                        
                        while waiting_for_start:
                            current_time = pygame.time.get_ticks()
                            if current_time - last_input_time >= input_cooldown:
                                if len(joysticks) > 0:
                                    joystick = joysticks[0]
                                    for i in range(joystick.get_numbuttons()):
                                        if joystick.get_button(i):
                                            waiting_for_start = False
                                            last_input_time = current_time
                                            break
                            
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                                    waiting_for_start = False
                                elif event.type == pygame.VIDEORESIZE:
                                    WIDTH, HEIGHT = event.size
                                    current_ratio = WIDTH/HEIGHT
                        
                                    if current_ratio > target_ratio:
                                        HEIGHT = event.size[1]
                                        WIDTH = int(HEIGHT * target_ratio)
                                    else:
                                        WIDTH = event.size[0]
                                        HEIGHT = int(WIDTH / target_ratio)
                        
                                    window = pygame.display.set_mode((WIDTH, HEIGHT), 
                                                                    pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
                        
                                    SCALE_X = WIDTH / 1920
                                    SCALE_Y = HEIGHT / 1080
                        
                                    # Update font sizes with better scaling
                                    font_size = int(36 * min(SCALE_X, SCALE_Y))
                                    small_font_size = int(24 * min(SCALE_X, SCALE_Y))
                                    font = pygame.font.SysFont('Arial', font_size)
                                    small_font = pygame.font.SysFont('Arial', small_font_size)
                        
                                    # Update button positions
                                    submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                                    play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                                    exit_button_rect.update(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)
                elif event.type == pygame.MOUSEBUTTONUP:
                    clicked_button = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        if not showing_hint:
                            optimal_position, max_score = find_optimal_position(player_seq, genome_seq)
                            showing_hint = True
                        else:
                            showing_hint = False
                            optimal_position = None
                    elif event.key == pygame.K_SPACE and selected_position is not None:
                        if selected_position >= alignment_start and selected_position < alignment_start + len(player_seq) - 1:
                            player_seq = player_seq[:selected_position-alignment_start] + '-' + player_seq[selected_position-alignment_start:]

                    if event.key == pygame.K_BACKSPACE and selected_position is not None:
                        if selected_position >= alignment_start and selected_position < alignment_start + len(player_seq) - 1:
                            if player_seq[selected_position-alignment_start] == '-':
                                player_seq = player_seq[:selected_position-alignment_start] + player_seq[selected_position-alignment_start+1:]

                    if event.key == pygame.K_LEFT:
                        if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                            selected_position = alignment_start + len(player_seq) - 1
                        elif selected_position > alignment_start:
                            selected_position -= 1
                    elif event.key == pygame.K_RIGHT:
                        if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                            selected_position = alignment_start
                        elif selected_position < alignment_start + len(player_seq) - 1:
                            selected_position += 1
                    elif event.key == pygame.K_UP:
                        if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                            selected_position = alignment_start
                        elif selected_position - GENOME_ROW_LENGTH >= alignment_start:
                            selected_position -= GENOME_ROW_LENGTH
                    elif event.key == pygame.K_DOWN:
                        if selected_position is None or selected_position < alignment_start or selected_position >= alignment_start + len(player_seq):
                            selected_position = alignment_start + len(player_seq) - 1
                        elif selected_position + GENOME_ROW_LENGTH < alignment_start + len(player_seq):
                            selected_position += GENOME_ROW_LENGTH

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
                    current_ratio = WIDTH/HEIGHT
    
                    if current_ratio > target_ratio:
                        HEIGHT = event.size[1]
                        WIDTH = int(HEIGHT * target_ratio)
                    else:
                        WIDTH = event.size[0]
                        HEIGHT = int(WIDTH / target_ratio)
    
                    window = pygame.display.set_mode((WIDTH, HEIGHT), 
                                                    pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    
                    SCALE_X = WIDTH / 1920
                    SCALE_Y = HEIGHT / 1080
    
                    # Update font sizes with better scaling
                    font_size = int(36 * min(SCALE_X, SCALE_Y))
                    small_font_size = int(24 * min(SCALE_X, SCALE_Y))
                    font = pygame.font.SysFont('Arial', font_size)
                    small_font = pygame.font.SysFont('Arial', small_font_size)
    
                    # Update button positions
                    submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                    play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                    exit_button_rect.update(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)
        else:
            draw_leaderboard(leaderboard, final_score, final_time, player_name, status, clicked_button)
            for event in pygame.event.get():
                if len(joysticks) > 0:
                    joystick = joysticks[0]
                    if joystick.get_button(BUTTON_X):
                        current_time = pygame.time.get_ticks()
                        if current_time - button_x_last_press >= button_cooldown:
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
                            showing_hint = False
                            optimal_position = None
                            status = "playing"
                            input_active = False
                            button_x_last_press = current_time
                elif event.type == pygame.QUIT:
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
                        showing_hint = False
                        optimal_position = None
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
                    current_ratio = WIDTH/HEIGHT
    
                    if current_ratio > target_ratio:
                        HEIGHT = event.size[1]
                        WIDTH = int(HEIGHT * target_ratio)
                    else:
                        WIDTH = event.size[0]
                        HEIGHT = int(WIDTH / target_ratio)
    
                    window = pygame.display.set_mode((WIDTH, HEIGHT), 
                                                    pygame.RESIZABLE | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
                    pygame.display.set_caption("DNA Sequence Alignment")

                    # Maximize the window after creation
                    if hasattr(pygame, 'WINDOWMAXIMIZED'):  # Check if the system supports window maximization
                        pygame.event.post(pygame.event.Event(pygame.WINDOWMAXIMIZED))
                    else:
                        # Alternative method for older Pygame versions
                        import ctypes
                        if hasattr(ctypes, 'windll'):  # Windows systems
                            hwnd = pygame.display.get_wm_info()['window']
                            ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3

                    SCALE_X = WIDTH / 1920
                    SCALE_Y = HEIGHT / 1080
    
                    # Update font sizes with better scaling
                    font_size = int(36 * min(SCALE_X, SCALE_Y))
                    small_font_size = int(24 * min(SCALE_X, SCALE_Y))
                    font = pygame.font.SysFont('Arial', font_size)
                    small_font = pygame.font.SysFont('Arial', small_font_size)
    
                    # Update button positions
                    submit_button_rect.update(50 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                    play_again_button_rect.update(300 * SCALE_X, HEIGHT - 100 * SCALE_Y, 200 * SCALE_X, 50 * SCALE_Y)
                    exit_button_rect.update(550 * SCALE_X, HEIGHT - 100 * SCALE_Y, 160 * SCALE_X, 50 * SCALE_Y)

        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())