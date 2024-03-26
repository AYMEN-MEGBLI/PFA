from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv
import cv2
from tqdm import tqdm
import sys
from ultralytics import YOLO
from datetime import datetime
# Définition du nouveau type
DetectedObjects = Dict[str, List[Tuple[float, float]]]
def detect_and_categorize_objects(video_path:str,NB_FRAMES:int=5)-> DetectedObjects :
    """
    Fonction qui détecte et catégorise les objets dans une vidéo.
    Args:
    - video_path (str): Chemin de la vidéo à analyser.
    
    Returns:
    - dict: Dictionnaire des catégories d'objets détectées avec les instants de début et de fin de chaque détection.
      DetectedObjects : Dict[str, List[Tuple[float, float]]]
    """

    categorized_objects = {
        "humains": [],
        "animaux": [],
        "vehicules": [],
        "autres": []
    }
    # Vérifier si le fichier vidéo existe
    assert os.path.isfile(video_path), "Erreur: Le fichier vidéo spécifié n'existe pas."
 
    
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(video_path)
    detect_vehicle_start_time=detect_human_start_time=detect_animal_start_time=detect_other_start_time = None
    no_human_detection_in_frame=no_vehicle_detection_in_frame=no_animal_detection_in_frame =no_other_detection_in_frame = 0
    while cap.isOpened():
        success, frame = cap.read()
        if success:  
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            seconds = frame_count / fps
            pbar = tqdm(total=seconds,position=0, leave=True,desc="Processing video",file=sys.stdout)
            timestamp_sec = float("{:.3f}".format(cap.get(cv2.CAP_PROP_POS_MSEC)/1000))
            results = model(frame,classes=[0,1,2,3,5,7,*range(14,24)],conf=0.5,verbose=False )
            if len(results[0].boxes.cls)==0  :
                no_other_detection_in_frame=0
                if detect_other_start_time  is None :
                    detect_other_start_time = timestamp_sec  
            else:
                if  detect_other_start_time is not None:
                        no_other_detection_in_frame+=1
                        if no_other_detection_in_frame > NB_FRAMES:
                            categorized_objects["autres"].append((detect_other_start_time, timestamp_sec))
                            detect_other_start_time = None                            
            #verbose=False remove the print of the results 
            for r in results:
                boxes = r.boxes
                for box in boxes: 
                    cls = int(box.cls[0])
                    #conf = math.ceil((box.conf[0] * 100)) / 100
                    if cls in range(1,9):
                        no_vehicle_detection_in_frame=0
                        if detect_vehicle_start_time is None:
                            detect_vehicle_start_time = timestamp_sec    
                    else:
                        if detect_vehicle_start_time is not None:
                            no_vehicle_detection_in_frame+=1
                            
                            if no_vehicle_detection_in_frame > NB_FRAMES:
                                categorized_objects["vehicules"].append((detect_vehicle_start_time, timestamp_sec))
                                detect_vehicle_start_time = None
                    if cls in range(14,24):
                        no_animal_detection_in_frame=0
                        if detect_animal_start_time is None:
                            detect_animal_start_time = timestamp_sec      
                    else:
                        if detect_animal_start_time is not None:
                            no_animal_detection_in_frame+=1
                            if no_animal_detection_in_frame > NB_FRAMES:
                                categorized_objects["animaux"].append((detect_animal_start_time, timestamp_sec)) 
                                detect_vehicle_start_time = None
                    if cls == 0 :
                        no_human_detection_in_frame=0
                        if detect_human_start_time is None:
                            detect_human_start_time = timestamp_sec         
                    else:
                        if detect_human_start_time is not None:
                            no_human_detection_in_frame+=1
                            if no_human_detection_in_frame > NB_FRAMES:
                                categorized_objects["humains"].append((detect_human_start_time, timestamp_sec))
                                detect_human_start_time = None
            pbar.update(timestamp_sec)
            sys.stdout.flush()
        else:
            if detect_vehicle_start_time is not None:
                categorized_objects["vehicules"].append((detect_vehicle_start_time, timestamp_sec))
                detect_vehicle_start_time = None
            if detect_animal_start_time is not None:
                categorized_objects["animaux"].append((detect_animal_start_time, timestamp_sec))
                detect_animal_start_time = None
            if detect_human_start_time is not None:
                categorized_objects["humains"].append((detect_human_start_time, timestamp_sec))
                detect_human_start_time = None
            if detect_other_start_time is not None:
                categorized_objects["autres"].append((detect_other_start_time, timestamp_sec))
                detect_other_start_time = None
            break
    pbar.close()
    cap.release()
    cv2.destroyAllWindows()
    return categorized_objects






def extract_video_segment(video_path: str, 
                          start_time: int = 0,
                          end_time: int = None, 
                          *,
                          categorisation: str | None = None,
                          time_segments: List[Tuple[float, float]] = None) -> None:
    """
    Extrait un segment de vidéo à partir d'un fichier vidéo.
    Args:
    - video_path (str): Chemin de la vidéo source.
    - start_time (int): Instant de début du segment à extraire (en secondes).
    - end_time (int): Instant de fin du segment à extraire (en secondes).
    - categorisation (str | None): Catégorie pour l'enregistrement (facultatif).
    - time_segments (List[Tuple[float, float]]): Liste de paires de temps à extraire (en secondes).
    Returns:
    - None
    """
    load_dotenv("../../.env")
    
    # Vérifier si le fichier vidéo existe
    assert os.path.isfile(video_path), "Erreur: Le fichier vidéo spécifié n'existe pas."
    # Vérifier et ajuster les valeurs de temps
    if end_time is None:
        video_capture = cv2.VideoCapture(video_path)
        end_time = video_capture.get(cv2.CAP_PROP_FRAME_COUNT) / video_capture.get(cv2.CAP_PROP_FPS)
        video_capture.release()
    if start_time < 0 or end_time < 0:
        print("Erreur: Les valeurs de temps doivent être positives.")
        return
    if time_segments is None:
        time_segments = [(start_time, end_time)]
    
    # Créer le répertoire de sortie si nécessaire
    output_directory = os.getenv('OUTPUT_PATH', 'Videos') if categorisation is None else os.path.join(os.getenv('OUTPUT_PATH', 'Videos'), categorisation)
    os.makedirs(output_directory, exist_ok=True)
    
    for segment_start, segment_end in time_segments:
        # Initialiser la capture vidéo
        video_capture = cv2.VideoCapture(video_path)
        
        # Vérifier si la vidéo est ouverte avec succès
        if not video_capture.isOpened():
            print("Erreur: Impossible d'ouvrir la vidéo.")
            return
        if start_time < 0 or end_time < 0:
            print("Erreur: Les valeurs de temps doivent être positives.")
            continue
        if segment_start > segment_end:
            print("Erreur: Le temps de début doit être inférieur au temps de fin.")
            continue
        
        
        # Récupérer les propriétés de la vidéo (FPS, largeur, hauteur)
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculer le numéro de frame correspondant au temps de début et de fin
        frame_start = int(segment_start * fps)
        frame_end = int(segment_end * fps)
        
        # Vérifier que le temps de début est inférieur au temps de fin
        if frame_start >= frame_end:
           
            print("Erreur: Le temps de début doit être inférieur au temps de fin.")
            return
        
        # Définir le codec et créer l'objet VideoWriter pour enregistrer le segment
        codec = cv2.VideoWriter_fourcc(*'XVID')
        output_filename = f'{datetime.now().strftime("%d-%m-%Y(%H-%M-%S)")}_{segment_start}_{segment_end}.avi'
        output_path = os.path.join(output_directory, output_filename)
        video_writer = cv2.VideoWriter(output_path, codec, fps, (frame_width, frame_height))
        
        # Parcourir les frames jusqu'au temps de début
        for _ in range(frame_start):
            ret, _ = video_capture.read()
            if not ret:
                print("Erreur: Impossible de lire la vidéo.")
                return
        
        # Enregistrer le segment
        for _ in range(frame_start, frame_end):
            ret, frame = video_capture.read()
            if not ret:
                print("Erreur: Impossible de lire la vidéo.")
                return
            video_writer.write(frame)
        
        # Libérer les ressources pour ce segment
        video_capture.release()
        video_writer.release()
        print(f"{output_path} enregistré avec succès dans {output_path}")



