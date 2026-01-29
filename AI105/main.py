import pygame
import random
import copy

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Tetromino colors (one per shape type)
COLORS = {
    'I': (0, 255, 255),      # Cyan
    'O': (255, 255, 0),      # Yellow
    'T': (128, 0, 128),      # Purple
    'S': (0, 255, 0),        # Green
    'Z': (255, 0, 0),        # Red
    'J': (0, 0, 255),        # Blue
    'L': (255, 165, 0)       # Orange
}

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE + SIDEBAR_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# Tetromino shapes with proper rotations
SHAPES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]]
    ],
    'J': [
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[0, 1], [0, 1], [1, 1]]
    ],
    'L': [
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]]
    ]
}

class Tetromino:
    def __init__(self, x, y, shape_type):
        self.x = x
        self.y = y
        self.shape_type = shape_type
        self.color = COLORS[shape_type]
        self.rotation = 0
        self.shapes = SHAPES[shape_type]
        self.shape = copy.deepcopy(self.shapes[0])
    
    def rotate(self):
        """Rotate the tetromino clockwise"""
        if len(self.shapes) > 1:
            self.rotation = (self.rotation + 1) % len(self.shapes)
            self.shape = copy.deepcopy(self.shapes[self.rotation])
    
    def get_rotated_shape(self):
        """Get the next rotation without applying it"""
        if len(self.shapes) > 1:
            next_rotation = (self.rotation + 1) % len(self.shapes)
            return copy.deepcopy(self.shapes[next_rotation])
        return copy.deepcopy(self.shape)
    
    def copy(self):
        """Create a copy of this tetromino"""
        new_tet = Tetromino(self.x, self.y, self.shape_type)
        new_tet.rotation = self.rotation
        new_tet.shape = copy.deepcopy(self.shape)
        return new_tet

def draw_block(screen, x, y, color, size=BLOCK_SIZE, outline=True):
    """Draw a single block"""
    pygame.draw.rect(screen, color, (x, y, size, size))
    if outline:
        pygame.draw.rect(screen, DARK_GRAY, (x, y, size, size), 2)
        # Add highlight
        pygame.draw.line(screen, WHITE, (x, y), (x + size - 1, y), 1)
        pygame.draw.line(screen, WHITE, (x, y), (x, y + size - 1), 1)

def draw_grid(screen, grid):
    """Draw the game grid"""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 0:
                draw_block(screen, x * BLOCK_SIZE, y * BLOCK_SIZE, grid[y][x])
            else:
                pygame.draw.rect(screen, BLACK, 
                                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, DARK_GRAY, 
                                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_tetromino(screen, tetromino, offset_x=0, offset_y=0):
    """Draw a tetromino"""
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                draw_block(screen,
                          (tetromino.x + x + offset_x) * BLOCK_SIZE,
                          (tetromino.y + y + offset_y) * BLOCK_SIZE,
                          tetromino.color)

def valid_position(tetromino, grid, dx=0, dy=0, shape=None):
    """Check if tetromino position is valid"""
    if shape is None:
        shape = tetromino.shape
    
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = tetromino.x + x + dx
                new_y = tetromino.y + y + dy
                
                # Check boundaries
                if new_x < 0 or new_x >= GRID_WIDTH:
                    return False
                if new_y >= GRID_HEIGHT:
                    return False
                if new_y < 0:
                    continue
                
                # Check collision with placed blocks
                if grid[new_y][new_x] != 0:
                    return False
    return True

def merge_tetromino(grid, tetromino):
    """Merge tetromino into the grid"""
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                grid_y = tetromino.y + y
                if grid_y >= 0:
                    grid[grid_y][tetromino.x + x] = tetromino.color

def remove_full_lines(grid):
    """Remove full lines and return new grid and number of lines removed"""
    lines_to_remove = []
    for y in range(GRID_HEIGHT):
        if all(cell != 0 for cell in grid[y]):
            lines_to_remove.append(y)
    
    for y in reversed(lines_to_remove):
        del grid[y]
    
    lines_removed = len(lines_to_remove)
    for _ in range(lines_removed):
        grid.insert(0, [0] * GRID_WIDTH)
    
    return grid, lines_removed

def draw_sidebar(screen, score, level, lines, next_tetromino):
    """Draw the sidebar with game info"""
    sidebar_x = GRID_WIDTH * BLOCK_SIZE
    
    # Background
    pygame.draw.rect(screen, DARK_GRAY, (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
    
    # Score
    font_large = pygame.font.SysFont(None, 36)
    font_medium = pygame.font.SysFont(None, 28)
    font_small = pygame.font.SysFont(None, 24)
    
    y_offset = 20
    
    # Title
    title = font_large.render("TETRIS", True, WHITE)
    screen.blit(title, (sidebar_x + 10, y_offset))
    y_offset += 50
    
    # Score
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (sidebar_x + 10, y_offset))
    y_offset += 40
    
    # Level
    level_text = font_medium.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (sidebar_x + 10, y_offset))
    y_offset += 40
    
    # Lines
    lines_text = font_medium.render(f"Lines: {lines}", True, WHITE)
    screen.blit(lines_text, (sidebar_x + 10, y_offset))
    y_offset += 60
    
    # Next piece
    next_text = font_medium.render("Next:", True, WHITE)
    screen.blit(next_text, (sidebar_x + 10, y_offset))
    y_offset += 30
    
    # Draw next tetromino preview
    preview_size = 20
    preview_x = sidebar_x + 30
    preview_y = y_offset
    
    for y, row in enumerate(next_tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                draw_block(screen, preview_x + x * preview_size, 
                          preview_y + y * preview_size, 
                          next_tetromino.color, preview_size, False)
    
    y_offset += 100
    
    # Controls
    controls_text = font_small.render("Controls:", True, WHITE)
    screen.blit(controls_text, (sidebar_x + 10, y_offset))
    y_offset += 25
    
    controls = [
        "← → Move",
        "↑ Rotate",
        "↓ Soft Drop",
        "Space Hard Drop"
    ]
    
    for control in controls:
        control_text = font_small.render(control, True, GRAY)
        screen.blit(control_text, (sidebar_x + 10, y_offset))
        y_offset += 20

def draw_game_over(screen, score):
    """Draw game over screen"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 36)
    
    game_over_text = font_large.render("GAME OVER", True, WHITE)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text, text_rect)
    
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(score_text, score_rect)
    
    restart_text = font_medium.render("Press R to Restart", True, GRAY)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    screen.blit(restart_text, restart_rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    # Game state
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    score = 0
    level = 1
    lines_cleared = 0
    fall_time = 0
    fall_speed = 0.5  # seconds per fall
    game_over = False
    
    # Create first tetromino
    def create_new_tetromino():
        shape_type = random.choice(list(SHAPES.keys()))
        return Tetromino(GRID_WIDTH // 2 - 1, 0, shape_type)
    
    current_tetromino = create_new_tetromino()
    next_tetromino = create_new_tetromino()
    
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # Restart game
                        grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                        score = 0
                        level = 1
                        lines_cleared = 0
                        fall_time = 0
                        game_over = False
                        current_tetromino = create_new_tetromino()
                        next_tetromino = create_new_tetromino()
                    continue
                
                # Movement controls
                if event.key == pygame.K_LEFT:
                    if valid_position(current_tetromino, grid, dx=-1):
                        current_tetromino.x -= 1
                
                elif event.key == pygame.K_RIGHT:
                    if valid_position(current_tetromino, grid, dx=1):
                        current_tetromino.x += 1
                
                elif event.key == pygame.K_DOWN:
                    if valid_position(current_tetromino, grid, dy=1):
                        current_tetromino.y += 1
                        score += 1  # Small bonus for soft drop
                
                elif event.key == pygame.K_UP:
                    # Rotate
                    rotated_shape = current_tetromino.get_rotated_shape()
                    if valid_position(current_tetromino, grid, shape=rotated_shape):
                        current_tetromino.rotate()
                    # Try wall kicks
                    elif valid_position(current_tetromino, grid, dx=-1, shape=rotated_shape):
                        current_tetromino.x -= 1
                        current_tetromino.rotate()
                    elif valid_position(current_tetromino, grid, dx=1, shape=rotated_shape):
                        current_tetromino.x += 1
                        current_tetromino.rotate()
                
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    drop_distance = 0
                    while valid_position(current_tetromino, grid, dy=drop_distance + 1):
                        drop_distance += 1
                    current_tetromino.y += drop_distance
                    score += drop_distance * 2  # Bonus for hard drop
        
        # Game logic (only if not game over)
        if not game_over:
            fall_time += dt
            
            # Calculate fall speed based on level
            current_fall_speed = fall_speed * (0.8 ** (level - 1))
            if current_fall_speed < 0.05:
                current_fall_speed = 0.05
            
            if fall_time >= current_fall_speed:
                fall_time = 0
                
                if valid_position(current_tetromino, grid, dy=1):
                    current_tetromino.y += 1
                else:
                    # Lock tetromino
                    merge_tetromino(grid, current_tetromino)
                    
                    # Check for full lines
                    grid, lines_removed = remove_full_lines(grid)
                    lines_cleared += lines_removed
                    
                    # Update score
                    if lines_removed > 0:
                        line_scores = [0, 100, 300, 500, 800]
                        score += line_scores[min(lines_removed, 4)] * level
                    
                    # Update level (every 10 lines)
                    level = (lines_cleared // 10) + 1
                    
                    # Spawn new tetromino
                    current_tetromino = next_tetromino
                    next_tetromino = create_new_tetromino()
                    
                    # Check game over
                    if not valid_position(current_tetromino, grid):
                        game_over = True
        
        # Draw everything
        screen.fill(BLACK)
        draw_grid(screen, grid)
        
        if not game_over:
            draw_tetromino(screen, current_tetromino)
        
        draw_sidebar(screen, score, level, lines_cleared, next_tetromino)
        
        if game_over:
            draw_game_over(screen, score)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()