# /// script
# dependencies = ["pygame"]
# ///

import asyncio
import pygame
import sys
import os

# Web detection
IS_WEB = "pygbag" in sys.modules or hasattr(sys, '_emscripten_info')

async def main():
    # Initialize pygame (nahrazuje pythonrc.py)
    pygame.init()
    
    if IS_WEB:
        # Web-specific setup
        screen = pygame.display.set_mode((1280, 720))
    else:
        # Desktop setup
        screen = pygame.display.set_mode((1920, 1080))
    
    pygame.display.set_caption("Carcassonne")
    
    # Přidejte cestu k src
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        # Import a spuštění vaší hry
        from game import Game
        game = Game()
        
        running = True
        while running:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            if hasattr(game, '_current_scene') and game._current_scene:
                game._current_scene.handle_events(events)
                game._current_scene.update()  
                game._current_scene.draw()
            
            await asyncio.sleep(0)
            
    except Exception as e:
        # Fallback - jednoduchý test
        print(f"Game import failed: {e}")
        
        running = True
        font = pygame.font.Font(None, 74)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.fill((50, 70, 50))
            text = font.render("Carcassonne Loading...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(640, 360))
            screen.blit(text, text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())