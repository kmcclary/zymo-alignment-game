import pygame
import sys

# Initialize Pygame and the joystick module
pygame.init()
pygame.joystick.init()

# Set up a simple display window
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Xbox Controller Test")

# Constants from your main game
DEADZONE = 0.2  # Adjust as needed
STICK_SENSITIVITY = 10

# Initialize the first joystick/controller
joysticks = []
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joysticks.append(joystick)
    print(f"Detected controller: {joystick.get_name()}")
except pygame.error:
    print("No controller detected")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Test D-pad buttons
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 13:  # D-pad left
                print("D-pad Left pressed")
            elif event.button == 14:  # D-pad right
                print("D-pad Right pressed")
            elif event.button == 11:  # D-pad up
                print("D-pad Up pressed")
            elif event.button == 12:  # D-pad down
                print("D-pad Down pressed")
    
    # Test analog sticks
    if joysticks:
        # Left stick
        x_axis = joystick.get_axis(0)  # Left/Right
        y_axis = joystick.get_axis(1)  # Up/Down
        
        # Only print if beyond deadzone
        if abs(x_axis) > DEADZONE:
            print(f"Left stick X: {x_axis:.2f}")
        if abs(y_axis) > DEADZONE:
            print(f"Left stick Y: {y_axis:.2f}")

    # Clear screen
    screen.fill((255, 255, 255))
    pygame.display.flip()
    pygame.time.wait(100)  # Small delay to prevent printing too fast

pygame.quit()
sys.exit()