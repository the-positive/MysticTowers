import pygame
import os

# Dictionary to store loaded fonts
_font_cache = {}

def get_font(size, font_name="morris-roman"):
    """Get a font of specified size, using caching for efficiency.
    
    Args:
        size: Font size in points
        font_name: Name of the font file without extension (defaults to morris-roman)
        
    Returns:
        pygame.font.Font object
    """
    # Handle special font names
    if font_name.lower() == "morrisroman-black":
        font_name = "MorrisRoman-Black"
    # Create a unique key for this font request
    key = f"{font_name}_{size}"
    
    # Return cached font if available
    if key in _font_cache:
        return _font_cache[key]
    
    # Try loading the custom font
    try:
        font_path = os.path.join('assets', 'fonts', f'{font_name}.ttf')
        if os.path.exists(font_path):
            font = pygame.font.Font(font_path, size)
        else:
            # Fallback to system font if file not found
            print(f"Warning: Font file {font_path} not found, using system font.")
            font = pygame.font.SysFont('arial', size)
    except Exception as e:
        print(f"Error loading font: {e}, falling back to system font")
        font = pygame.font.SysFont('arial', size)
    
    # Cache the font
    _font_cache[key] = font
    return font
