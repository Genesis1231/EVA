import os
from pathlib import Path
from config import logger
import sqlite3
from queue import Queue
from typing import Dict

import wespeaker as wp
import torch
import numpy as np

class VoiceIdentifier:
    """ 
    The VoiceIdentifier class is responsible for identifying the speaker using voice recognition.
    It uses the wespeaker library to identify the speaker from the audio clip.
    """
    def __init__(self):
        self._dblink: str = self._get_database_path()
        self._void_list: Dict = self._initialize_database()
        self.voice_recognizer = self._initialize_recognizer()
    
    def _initialize_recognizer(self):
        try:
            vmodel = wp.load_model('english') # or chinese
            num = 0
            
            vid_directory = Path(__file__).resolve().parents[2] / 'data' / 'voids'
            if not vid_directory.exists():
                vid_directory.mkdir(parents=True)
                
            for filename in os.listdir(vid_directory):
                if filename.lower().endswith('.wav'):
                    name = os.path.splitext(filename)[0]
                    if name in self._void_list:
                        filepath = os.path.join(vid_directory, filename)
                        vmodel.register(name, filepath)
                        num += 1
            
        except Exception as e:
            raise Exception(f"Error: Failed to set up voice recognizer: {str(e)}")
        
        logger.info(f"Voice Identifier: {num} Voice ID loaded.")
        
        return vmodel    
   
    def _initialize_database(self)-> Dict:
        """ Initialize the database and create the voice id table """
        
        with sqlite3.connect(self._dblink) as conn:
            conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
            cursor = conn.cursor()

            try:
                cursor.execute(f'SELECT void, user_name FROM ids;')
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}

            except sqlite3.Error as e:
                # If table doesn't exist, create it and return an empty list
                self._create_table(conn)
                return {}

    @staticmethod
    def _create_table(conn)-> None:    
        """ Create a new voiceid table """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                void TEXT,
                pid TEXT,
                user_name TEXT NOT NULL
            )
        ''')
        conn.commit()
        
        # cursor = conn.cursor()
        # cursor.execute(f'''
        #     INSERT INTO ids (void, user_name) VALUES (?, ?);
        # ''', ('V000001', 'Initial User'))
        # conn.commit()

    @staticmethod
    def _get_database_path() -> str:
        """Return the path to the memory log database."""
        return Path(__file__).resolve().parents[2] / 'data' / 'database' / 'eva.db'
        
    @staticmethod
    def _convert_numpy_to_torch(audio_array: np.ndarray) -> torch.Tensor:
        """ Convert numpy audio array to torch tensor with proper formatting. """
        
        # Convert to float32 and normalize if needed
        if audio_array.dtype in [np.int16, np.int32]:
            audio_array = audio_array.astype(np.float32) / 32768.0
        
        # Ensure the array is 2D (channels, samples)
        if audio_array.ndim == 1:
            audio_array = audio_array[np.newaxis, :]
        
        # Convert to torch tensor
        audio_tensor = torch.tensor(audio_array, dtype=torch.float32)
        
        return audio_tensor


    def _recognize_audio(self, audio: torch.Tensor, sample_rate: int = 16000):
        """ Recognize the audio and return the name and confidence """
        
        q = self.voice_recognizer.extract_embedding_from_pcm(audio, sample_rate)
        
        best_score = 0.0
        best_name = ''
        
        for name, e in self.voice_recognizer.table.items():
            score = self.voice_recognizer.cosine_similarity(q, e)
            if best_score < score:
                best_score = score
                best_name = name
        
        if best_score > 0.6:
            return best_name
        else:
            return "unknown"
    
    def identify(self, audioclip: np.ndarray, name_queue: Queue) -> None:
        """
        Voice identification using wespeaker cli. 
        this could be improved by importing a whole voice dict from the directory
        and comparing the cosine similarity of the voice embeddings one by one
        """

        try:
            torch_audio = self._convert_numpy_to_torch(audioclip)
            recognition = self._recognize_audio(torch_audio)
              
        except Exception as e:
            logger.error(f"Failed to recognize audio: {str(e)}")
            name_queue.put("unknown")
            return
        
        if name_queue:
            name_queue.put(recognition)

    def get_name(self, void: str) -> str:
        """ Get the name from the List """
        try:
            return self._void_list[void]
        except KeyError:
            logger.error(f"Database mismatch, failed to get name from void list: {void}")
            return "unknown"
    
