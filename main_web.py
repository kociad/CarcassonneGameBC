# /// script
# dependencies = ["pygame"]
# ///

import asyncio
import pygame
import sys
import os

# Přidáme src do Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

async def main():
    try:
        # Import až po nastavení cesty
        from game import Game
        
        print("Initializing game...")
        game = Game()
        print("Game initialized, starting main loop...")
        
        running = True
        while running:
            events = pygame.event.get()
            
            # Kontrola quit událostí
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break
            
            if not running:
                break
                
            # Update hry
            if hasattr(game, '_current_scene') and game._current_scene:
                try:
                    game._current_scene.handle_events(events)
                    game._current_scene.update()
                    game._current_scene.draw()
                    pygame.display.flip()
                except Exception as e:
                    print(f"Error in game loop: {e}")
                    
            # Kritické pro pygbag - yield control
            await asyncio.sleep(0)
            
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
    
    print("Game loop ended")
    pygame.quit()

if __name__ == "__main__":
    print("Starting Carcassonne web version...")
    asyncio.run(main())