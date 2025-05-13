import os
import pygame
from settings import *

def import_image(*path, format='png', alpha=True):
    # Join the provided path components into a complete file path
    full_path = os.path.join(*path) + f'.{format}'
    
    # Check if the file exists before trying to load it
    if not os.path.exists(full_path):
        print(f"Error: {full_path} does not exist!")
        return None  # You could return a placeholder image here instead, if desired
    
    # If the file exists, load it
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path):
    frames = []
    for folder_path, _, file_names in os.walk(os.path.join(*path)):
        for file_name in sorted(file_names, key=lambda name: int(name.split( '.')[0])):
            full_path = os.path.join(folder_path, file_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames

def audio_importer(*path):
    audio_dict = {}
    for folder_path, _, file_names in os.walk(os.path.join(*path)):
        for file_name in file_names:
            full_path = os.path.join(folder_path, file_name)
            audio_dict[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
    return audio_dict
