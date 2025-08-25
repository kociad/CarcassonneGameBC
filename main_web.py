import asyncio
import pygame
import sys
import os

# Přidáme src do Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game import Game

async def main():
    game = Game()
    
    # Hlavní herní smyčka s async/await
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Zpracování událostí
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Update a draw
        if hasattr(game, '_current_scene'):
            game._current_scene.handle_events(events)
            game._current_scene.update()
            game._current_scene.draw()
        
        # Důležité pro pygbag - umožňuje browser zpracovat jiné úkoly
        await asyncio.sleep(0)
        
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())