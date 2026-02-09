import os
from dotenv import load_dotenv

import pygame

load_dotenv()

ROOT_DIR = os.getenv("ROOT_DIR")

class ImageCache:
    _images: dict[str, pygame.Surface] = {}
    _scaled: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}

    @classmethod
    def load(cls, name: str, path: str):
        if name not in cls._images:
            cls._images[name] = pygame.image.load(path).convert_alpha()

    @classmethod
    def get(cls, name: str, size: tuple[int, int]):
        key = (name, size)

        if key not in cls._scaled:
            base = cls._images[name]
            cls._scaled[key] = pygame.transform.smoothscale(base, size)

        return cls._scaled[key]
    
def load_assets():
    for color in ("white", "black"):
            for piece in ("pawn", "rook", "knight", "bishop", "queen", "king"):
                name = f"{color}-{piece}"
                ImageCache.load(name, f"{ROOT_DIR}/images/{name}.png")

