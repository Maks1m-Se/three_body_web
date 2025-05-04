# /// script
# dependencies = [
#  "pygame",
#  "numpy",
#  "asyncio"
# ]
# ///

import pygame
import numpy as np
import asyncio

# Constants
G = 1  # Gravitational constant (normalized for simplicity)
dt = 0.01  # Time step for numerical integration
num_steps = 1000  # Number of simulation steps
WIDTH, HEIGHT = 1200, 800  # Screen dimensions
SCALE = 100  # Scaling factor to visualize position values in pixels

# UI Controls
paused = False
display_info = False
speed_multiplier = 1.0  # Speed control factor
button_font = None

# Load Background Image
pygame.init()
BACKGROUND_IMAGE = pygame.image.load("assets/background/space.png")
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = BACKGROUND_IMAGE.get_size()
pygame.RESIZABLE   
image_scale = BACKGROUND_IMAGE.get_height()/BACKGROUND_IMAGE.get_width() #save scale of image height and width
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, WIDTH*image_scale)) #scale image to its original proportion according to width
bg_x, bg_y = 0, 0
bg_x_speed, bg_y_speed = 0.05, 0.2 






# Load and Play Background Music
pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/epiano.ogg")
pygame.mixer.music.play(-1)  # Loop music indefinitely
pygame.mixer.music.set_volume(.5)

# Cut off max speed of bodies
max_body_speed = 8

# Default Initial Conditions - Slightly Unstable System
def default_bodies():
    return [
        {'mass': 1.0, 'pos': np.array([-1.02, 0.25]), 'vel': np.array([0.47, 0.42]), 'color': (255, 0, 0)},
        {'mass': .4, 'pos': np.array([2.01, -0.24]), 'vel': np.array([-0.8, .85]), 'color': (0, 255, 0)},
        {'mass': 2.0, 'pos': np.array([0.0, 0.0]), 'vel': np.array([-0.92, -0.97]), 'color': (0, 0, 255)}
    ]

bodies = default_bodies()
trails = [[] for _ in bodies]  # Restore trails
max_trail_length = 3000  # Controls how long the trails remain visible

def compute_accelerations(bodies):
    """Computes gravitational acceleration for each body due to all other bodies."""
    n = len(bodies)
    accelerations = [np.zeros(2) for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                r = bodies[j]['pos'] - bodies[i]['pos']  # Vector from body[i] to body[j]
                distance = np.linalg.norm(r)  # Euclidean distance
                if distance > 0:
                    force = G * bodies[j]['mass'] / distance**3 * r  # Newton's law of gravity (normalized)
                    accelerations[i] += force
    return accelerations

def update_positions(bodies, dt):
    """Updates positions and velocities using the Euler method."""
    accels = compute_accelerations(bodies)
    for i, body in enumerate(bodies):
        body['vel'] += accels[i] * dt * speed_multiplier  # Adjust simulation speed
        
        # Speed control
        if body['vel'][0] > max_body_speed:
            print(f"body {i} vel x: {body['vel'][0]}")
            print('SPEED CONTROL')
            body['vel'][0] = max_body_speed     
        if body['vel'][1] > max_body_speed:
            print(f"body {i} vel y: {body['vel'][1]}")
            print('SPEED CONTROL')
            body['vel'][1] = max_body_speed
        if body['vel'][0] < -max_body_speed:
            print(f"body {i} vel x: {body['vel'][0]}")
            print('SPEED CONTROL')
            body['vel'][0] = -max_body_speed
        if body['vel'][1] < -max_body_speed:
            print(f"body {i} vel y: {body['vel'][1]}")
            print('SPEED CONTROL')
            body['vel'][1] = -max_body_speed

        #print(f"body {i} vel x,y:", body['vel'] ) ### Debugging
        body['pos'] += body['vel'] * dt * speed_multiplier
    return bodies

def toggle_pause():
    """Toggles the simulation pause state."""
    global paused
    paused = not paused

def toggle_display_info():
    """Display infos of the bodies"""
    global display_info
    display_info = not display_info

def adjust_speed(factor):
    """Adjusts the simulation speed multiplier."""
    global speed_multiplier
    speed_multiplier += factor
    #speed_multiplier = max(0.1, min(speed_multiplier * factor, 10))  # Keep speed within reasonable bounds

def reset_simulation():
    """Resets the simulation to the default initial conditions."""
    global bodies, paused, speed_multiplier, trails
    bodies = default_bodies()
    paused = False
    speed_multiplier = 1.0
    trails = [[] for _ in bodies]  # Reset trails

def get_center_of_mass():
    """Computes the center of mass of the system to keep it centered in the view."""
    total_mass = sum(body['mass'] for body in bodies)
    center_of_mass = sum(body['pos'] * body['mass'] for body in bodies) / total_mass
    return center_of_mass

async def main():
    """Runs the simulation loop using Pygame to visualize motion and add UI controls."""
    global button_font, background_x, background_y, elapsed_time
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    button_font = pygame.font.Font(None, 25)
    elapsed_time = 0  # Initialize simulation time in days
    running = True
    
    while running:
        global bg_x, bg_y, bg_x_speed, bg_y_speed
        screen.fill((0,0,0)) #redraws BG
        screen.blit(BACKGROUND_IMAGE, (bg_x,bg_y)) #x,y; x changes in nagativ direction: to the left
        screen.blit(BACKGROUND_IMAGE, (WIDTH + bg_x, HEIGHT + bg_y)) # image to the right bottom (diagonally)
        screen.blit(BACKGROUND_IMAGE, (WIDTH + bg_x, bg_y)) # image to the right
        if (bg_y<=-HEIGHT):
            screen.blit(BACKGROUND_IMAGE, (WIDTH + bg_x, HEIGHT + bg_y))
            bg_y=0
        elif (bg_x<=-HEIGHT):
            screen.blit(BACKGROUND_IMAGE, (WIDTH + bg_x, HEIGHT + bg_y))
            bg_x=0
        bg_x -= bg_x_speed
        bg_y -= bg_y_speed
        
        ###########



        if not paused:
            update_positions(bodies, dt)  
            elapsed_time += dt *100 * speed_multiplier  # Update simulation time in days 
        
        center_of_mass = get_center_of_mass()
        
        for i, body in enumerate(bodies):
            pos_adjusted = (body['pos'] - center_of_mass) * SCALE + np.array([WIDTH / 2, HEIGHT / 2])
            x, y = int(pos_adjusted[0]), int(pos_adjusted[1])
            radius = int(body['mass'] * 5)  
            
            # Draw trails
            trails[i].append((x, y))
            if len(trails[i]) > max_trail_length:
                trails[i].pop(0)
            for j, trail_pos in enumerate(trails[i]):
                fade_factor = j / len(trails[i])
                trail_color = tuple(int(c * fade_factor) * 0.3 for c in body['color'])
                pygame.draw.circle(screen, trail_color, trail_pos, 1)


            # Draw bodies
            pygame.draw.circle(screen, body['color'], (x, y), radius)
            pygame.draw.circle(screen, body['color'], (x, y), radius, 1)  # White outline


            # Calculate speed in km/s
            speed_km_s = np.linalg.norm(body['vel']) * 30  # Assuming 1 velocity unit = 30 km/s (earth speed)

            # Display mass, size, and speed
            info_text = f"Mass: {body['mass']:.1f}x Sun | Radius: {radius * 700}k km | Vel: {speed_km_s:.1f} km/s"
            info_surface = button_font.render(info_text, True, (255, 255, 255))
            if display_info:
                screen.blit(info_surface, (x + 10, y - 10))  # Position text near body

        # UI Buttons
        button_color = (50, 50, 150)  
        hover_color = (70, 70, 200)  
        text_color = (255, 255, 255)  

        buttons = [
            {"rect": pygame.Rect(10, HEIGHT - 50, 70, 30), "label": "Pause", "action": toggle_pause},
            {"rect": pygame.Rect(100, HEIGHT - 50, 70, 30), "label": "Reset", "action": reset_simulation},
            {"rect": pygame.Rect(200, HEIGHT - 50, 30, 30), "label": "+", "action": lambda: adjust_speed(0.1)},
            {"rect": pygame.Rect(240, HEIGHT - 50, 30, 30), "label": "-", "action": lambda: adjust_speed(-0.1)},
            {"rect": pygame.Rect(360, HEIGHT - 50, 110, 30), "label": "Info bodies", "action": toggle_display_info},
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        button["action"]()

        # Draw buttons
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in buttons:
            rect = button["rect"]
            color = hover_color if rect.collidepoint(mouse_x, mouse_y) else button_color  
            pygame.draw.rect(screen, color, rect, border_radius=10)  
            label_surface = button_font.render(button["label"], True, text_color)
            screen.blit(label_surface, (rect.x + 10, rect.y + 5))  

        # Display elapsed time
        years = elapsed_time / 365  
        centuries = years / 100  
        time_text = button_font.render(f"Time: {years:.1f} earth years", True, text_color)
        #time_text = button_font.render(f"Time: {elapsed_time:.1f} days ({years:.2f} years, {centuries:.2f} centuries)", True, text_color)
        screen.blit(time_text, (10, 10))

        # Display speed multiplier value
        speed_text = button_font.render(f"x{speed_multiplier:.1f}", True, text_color)  
        screen.blit(speed_text, (280, HEIGHT - 45))  

        pygame.display.flip()

    
        clock.tick(60)
        
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
