from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

# Définition du nouveau type
DetectedObjects = Dict[str, List[Tuple[float, float]]]
def detect_and_categorize_objects(video_path:str)-> DetectedObjects :
    """
    Fonction qui détecte et catégorise les objets dans une vidéo.
    Args:
    - video_path (str): Chemin de la vidéo à analyser.

    Returns:
    - dict: Dictionnaire des catégories d'objets détectées avec les instants de début et de fin de chaque détection.
      DetectedObjects : Dict[str, List[Tuple[int, int]]]
         Le format du dictionnaire est le suivant :
      {
        "humains": [(debut_detection_humain_1, detection_humain_fin_1),...],
        "animaux": [(debut_detection_animal_1, detection_animal_fin_1), ...],
        "véhicules": [(debut_detection_véhicule_1, detection_véhicule_fin_1), ...],
        "autres": [(debut_detection_autre_1, detection_autre_fin_1), ...]
      }
    """
    

    categorized_objects = {
        "humains": [],
        "animaux": [],
        "vehicules": [],
        "autres": []
    }

    
    ...
    
    
    
    
    
    return categorized_objects





def extract_video_segment(video_path: str,
                          start_time: int, 
                          end_time: int,
                          categorisation: str | None = None) -> None:
    """
    Extrait un segment de vidéo à partir d'un fichier vidéo.
    Args:
    - video_path (str): Chemin de la vidéo source.
    - start_time (int): Instant de début du segment à extraire (en secondes).
    - end_time (int): Instant de fin du segment à extraire (en secondes).
    Returns:
    - None
    """
    load_dotenv(".env")
    output_path=os.getenv('OUTPUT_PATH', 'Videos')  if categorisation is None else os.path.join(os.getenv('OUTPUT_PATH', 'Videos'),categorisation)
    
    print(output_path)
    
    
    ...
    
    
    #file_name=f"{categorisation}_{start_time}_{end_time}.mp4"



