import pygame

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
    
    
