import pygame 
import random
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
from llm_agent import LLMDecisionAgent

class PlayEnemy(Player):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop_ui, id=1):
        super().__init__(pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop_ui, id)
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # General setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 100

    # import assets
    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': []
        }

        for animation in self.animations.keys():
            full_path = '../graphics/enemy/' + animation
            self.animations[animation] = import_folder(full_path)

    # movement
    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    # enemy movement
    def set_play_pos(self, play_pos):
        if self.pos.x < play_pos.x:
            self.direction.x = 1
            self.status = 'right'
        elif self.pos.x > play_pos.x:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

        if self.pos.y < play_pos.y:
            self.direction.y = 1
            self.status = 'down'
        elif self.pos.y > play_pos.y:
            self.direction.y = -1
            self.status = 'up'
        else:
            self.direction.y = 0

    def input(self):
        pass

    def update(self, dt):
        self.move(dt)
        self.animate(dt)

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        self.sky = Sky()

        # shop
        self.menu = Menu(self.player)
        self.shop_active = False

        # music
        pygame.mixer.init()
        
        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.3)
        self.music = pygame.mixer.Sound('../audio/music.mp3')
        self.music.play(loops=-1)

        # weather music
        self.rain_music = pygame.mixer.Sound('../audio/rain.mp3')
        self.rain_music.set_volume(0.7)
        self.rain_channel = pygame.mixer.Channel(1)

        self.sun_music = pygame.mixer.Sound('../audio/day.mp3')
        self.sun_music.set_volume(0.7)
        self.sun_channel = pygame.mixer.Channel(2)

        self.update_weather_music()

        # decision agent
        self.decision_agent = LLMDecisionAgent() 

    def setup(self):
        tmx_data = load_pygame('../data/map.tmx')

        # house 
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE,y * TILE_SIZE), surf, self.all_sprites)

        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE,y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        # water 
        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE,y * TILE_SIZE), water_frames, self.all_sprites)

        # trees 
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos = (obj.x, obj.y), 
                surf = obj.image, 
                groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
                name = obj.name,
                player_add = self.player_add)

        # wildflowers 
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        # Player 
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos = (obj.x,obj.y), 
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop_ui = self.toggle_shop_ui)
            
                self.player_enemy = PlayEnemy(
                    pos = ((obj.x + random.randint(-20,20)),obj.y + random.randint(-20,20)), 
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop_ui = self.toggle_shop_ui)
            if obj.name == 'Bed':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x,obj.y), (obj.width,obj.height), self.interaction_sprites, obj.name)

        Generic(
            pos = (0,0),
            surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground'])

    def player_add(self, item):
        self.player.item_inventory[item] += 1
        self.success.play()

    # change shop ui
    def toggle_shop_ui(self):
        self.shop_active = not self.shop_active
        if self.shop_active:
            self.menu.show_shop()
        else:
            self.menu.hide_shop()

    def update_weather_music(self):
        if self.raining:
            if not self.rain_channel.get_busy():
                self.rain_channel.play(self.rain_music, loops=-1)
        else:
            if not self.sun_channel.get_busy():
                self.sun_channel.play(self.sun_music, loops=-1)

    def reset(self):
        # set up all sprites
        self.soil_layer.update_plants()

        self.soil_layer.remove_water()
        self.raining = randint(0,10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        for tree in self.tree_sprites.sprites():
            if isinstance(tree, Generic):
                continue
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # the color of the sky
        self.sky.start_color = [255,255,255]

        # update weather music
        self.update_weather_music()

        # decision agent
        self.raining = self.decision_agent.decide(self.player.money)

    # plant collision
    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def run(self, dt, events):
        self.player_enemy.set_play_pos(self.player.pos)

        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.player.check_enemy_pos(self.player_enemy.pos)
        
        # update shop
        if self.shop_active:
            self.menu.update(events)
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        for event in events:
            self.player.handle_event(event, self.menu)

        # weather
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display(dt)

        # music
        self.update_weather_music()

        # transition
        if self.player.sleep:
            self.transition.play()

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in sorted(LAYERS, key=lambda x: LAYERS[x]):
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == LAYERS[layer]:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
