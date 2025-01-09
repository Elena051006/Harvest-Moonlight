import pygame, sys
from settings import *
from level import Level

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.image.load(r'..\graphics\images\start.png') 
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render('Press Enter to Start  Press Space to view', True, (255, 255, 255))

    def display(self):
        # display the background
        self.screen.blit(self.background, (0, 0))

        # display the text
        text_rect = self.text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
        self.screen.blit(self.text, text_rect)

        pygame.display.update()

class InstructionsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.image.load(r'..\graphics\images\page.png')  
        self.font = pygame.font.Font(None, 35)
        self.text = self.font.render('Press ESC to Go Back to Start Screen', True, (100, 100, 255))

    def display(self):
        # display the background
        self.screen.blit(self.background, (0, 0))
        # display the text
        pygame.display.update()

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.background = pygame.image.load(r'..\graphics\images\lose.png') 
        self.text = self.font.render('Game Over! Press Enter to Restart', True, (255, 0, 0))

    def display(self):
        self.screen.blit(self.background, (0, 0))
        text_rect = self.text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(self.text, text_rect)

        pygame.display.update()

class GameVictoryScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.background = pygame.image.load(r'..\graphics\images\win.png')  
        self.text = self.font.render('Game Victory! Press Enter to Restart', True, (255, 0, 0))

    def display(self):
        self.screen.blit(self.background, (0, 0))
        text_rect = self.text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen.blit(self.text, text_rect)

        pygame.display.update()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Harvest Moonlight')
        self.clock = pygame.time.Clock()
        self.level = Level()

        self.start_screen = StartScreen(self.screen)
        self.instructions_screen  = InstructionsScreen(self.screen)
        self.game_over_screen = GameOverScreen(self.screen)
        self.game_victory_screen = GameVictoryScreen(self.screen)

    def run(self):
        game_started = False
        game_over = False
        gave_victory = False
        showing_instructions = False
        
        # main game loop
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if not game_started and not game_over:
                            game_started = True
                        elif game_over:
                            # if game over, restart the game
                            game_started = False
                            game_over = False
                            self.level = Level()

                    # press space to view instructions
                    if event.key == pygame.K_SPACE and not game_started and not game_over:
                        showing_instructions = True

                    # press escape to go back to start screen
                    if event.key == pygame.K_ESCAPE and showing_instructions:
                        showing_instructions = False

            if game_over:
                # if game over, display game over screen
                self.game_over_screen.display()
            elif showing_instructions:
                # if showing instructions, display instructions screen
                self.instructions_screen.display()
            elif gave_victory:
                self.game_victory_screen.display()
            elif not game_started:
                # if not game started, display start screen
                self.start_screen.display()
            else:
                dt = self.clock.tick(60) / 1000
                self.level.run(dt, events)
                # check if player is dead
                if self.level.player.money < 100:
                    self.level.player.money = 10000
                    game_over = True

                if self.level.player.money > 11000:
                    gave_victory = True
                    print('金币超过上限，游戏结束！')
                    game_over = True

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()
