# /// script
# dependencies = ["pygame"]
# ///

import asyncio
import pygame
import sys

async def main():
    print("Starting pygame...")
    pygame.init()
    
    # Jednoduchý test
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Carcassonne")
    
    clock = pygame.time.Clock()
    running = True
    
    print("Entering main loop...")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Vyplnit obrazovku modrou barvou
        screen.fill((0, 100, 200))
        
        # Nakreslit text
        font = pygame.font.Font(None, 74)
        text = font.render("Carcassonne Web Test", True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 300))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        # Kritické pro pygbag
        await asyncio.sleep(0)
    
    pygame.quit()
    print("Game ended")

if __name__ == "__main__":
    print("Python script started")
    asyncio.run(main())