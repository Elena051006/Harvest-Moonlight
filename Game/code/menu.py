import pygame
from settings import *
from timer import Timer
from llm_agent import LLMChatAgent

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

class Menu:
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        
        # font
        try:
            self.font = pygame.font.Font('../font/NotoSansCJK-Regular.ttc', 24)
            self.chat_font = pygame.font.Font('../font/NotoSansCJK-Regular.ttc', 20)
        except Exception:
            self.font = pygame.font.SysFont(None, 24)
            self.chat_font = pygame.font.SysFont(None, 20)

        # the setup of the menu
        self.width = 400
        self.space = 10
        self.padding = 8
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

        self.index = 0
        self.timer = Timer(200)

        self.chat_active = False
        self.chat_messages = []
        self.chat_input = ''
        self.chat_height = 150

        # chat agent
        self.llm_chat_agent = LLMChatAgent()

        # text of buy and sell
        self.buy_text = self.font.render('买', False, 'Black')
        self.sell_text = self.font.render('卖', False, 'Black')

        # shop visibility
        self.shop_visible = False

    def show_shop(self):
        self.shop_visible = True

    def hide_shop(self):
        self.shop_visible = False
        self.chat_active = False

    def display_money(self):
        text_surf = self.font.render(f'金币: ${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        # set up the menu
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height
        )

    def handle_shop_navigation(self, keys):
        if not self.chat_active:
            self.timer.update()

            if not self.timer.active:
                if keys[pygame.K_UP]:
                    self.index = max(self.index - 1, 0)
                    self.timer.activate()

                if keys[pygame.K_DOWN]:
                    self.index = min(self.index + 1, len(self.options) - 1)
                    self.timer.activate()

                if keys[pygame.K_z]:
                    current_item = self.options[self.index]
                    if self.index <= self.sell_border:
                        if self.player.item_inventory[current_item] > 0:
                            self.player.item_inventory[current_item] -= 1
                            self.player.money += SALE_PRICES[current_item]
                    else:
                        seed_price = PURCHASE_PRICES[current_item]
                        if self.player.money >= seed_price:
                            self.player.seed_inventory[current_item] += 1
                            self.player.money -= PURCHASE_PRICES[current_item]

    def handle_shop_event(self, event):
        if not self.chat_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.chat_active = True
                    self.chat_input = ''


    def handle_chat_event(self, event):
        if self.chat_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.chat_input.strip():
                        self.chat_messages.append(("玩家", self.chat_input))
                        assistant_reply = self.llm_chat_agent.send_message(self.chat_input)
                        self.chat_messages.append(("商人", assistant_reply))
                    self.chat_input = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]

                else:
                    if event.unicode.isprintable():
                        self.chat_input += event.unicode

    def show_entry(self, text_surf, amount, top, selected):
        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        # text
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # sell/buy
        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)
            if self.index <= self.sell_border:
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def draw_chat(self):
        # chat background
        chat_rect = pygame.Rect(0, SCREEN_HEIGHT - self.chat_height, SCREEN_WIDTH, self.chat_height)
        pygame.draw.rect(self.display_surface, GRAY, chat_rect)

        # draw chat messages
        y_offset = SCREEN_HEIGHT - self.chat_height + 10
        for speaker, message in self.chat_messages[-5:]:
            speaker_color = (0, 255, 0) if speaker == "玩家" else (0, 0, 255)
            speaker_surf = self.chat_font.render(f"{speaker}:", True, speaker_color)
            message_surf = self.chat_font.render(message, True, WHITE)
            self.display_surface.blit(speaker_surf, (10, y_offset))
            self.display_surface.blit(message_surf, (100, y_offset))
            y_offset += 25

        # chat input box
        if self.chat_active:
            input_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, SCREEN_WIDTH - 20, 30)
            pygame.draw.rect(self.display_surface, WHITE, input_rect, 0, 4)
            pygame.draw.rect(self.display_surface, BLACK, input_rect, 2, 4)

            cursor_x = input_rect.x + 5 + self.chat_font.size(self.chat_input)[0]
            cursor_y = input_rect.y + 5
            pygame.draw.line(self.display_surface, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + self.chat_font.get_height()), 2)

            input_surf = self.chat_font.render(self.chat_input, True, BLACK)
            self.display_surface.blit(input_surf, (input_rect.x + 5, input_rect.y + 5))

    def update(self, events):
        for event in events:
            if self.shop_visible:
                if self.chat_active:
                    self.handle_chat_event(event)
                else:
                    self.handle_shop_event(event)

        if self.shop_visible:
            keys = pygame.key.get_pressed()
            if not self.chat_active:
                self.handle_shop_navigation(keys)

        self.display_money()

        if self.shop_visible:
            for text_index, text_surf in enumerate(self.text_surfs):
                top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
                amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
                amount = amount_list[text_index]
                self.show_entry(text_surf, amount, top, self.index == text_index)

        # draw chat box
        if self.shop_visible and self.chat_active:
            self.draw_chat()
