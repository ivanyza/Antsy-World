import pygame as pg

class BaseObject:
    def __init__(self, ):
        self.visible = False
        self.sprite = pg.sprite.Sprite()
        self.interactable = False
        self.depth = 0

    def draw(self, screen):
        screen.blit(self.sprite.image, self.sprite.rect)

class Wall:
    def __init__(self, ):
        self.visible = False
        self.sprite = pg.sprite.Sprite()
        self.sprite.image = None
        self.interactable = False
        self.depth = 0

    def draw(self, screen):
        screen.blit(self.sprite.image, self.sprite.rect)
