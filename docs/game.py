import pygame
import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Carcassonne")
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((50, 50, 70))
        
        text = font.render("Carcassonne Works!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(640, 360))
        screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
        
        await asyncio.sleep(0)
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())