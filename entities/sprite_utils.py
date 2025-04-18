import pygame

def load_sprite_sheet(filename, frame_width, frame_height, horizontal=True):
    """Load a sprite sheet and return a list of frames as surfaces. If horizontal, split only along x axis (single row)."""
    sheet = pygame.image.load(filename).convert_alpha()
    sheet_rect = sheet.get_rect()
    frames = []
    if horizontal:
        y = 0
        for x in range(0, sheet_rect.width, frame_width):
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height)).copy()
            frames.append(frame)
    else:
        for y in range(0, sheet_rect.height, frame_height):
            for x in range(0, sheet_rect.width, frame_width):
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height)).copy()
                frames.append(frame)
    return frames
