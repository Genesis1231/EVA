from config import logger
import os
import threading
import secrets
from queue import Queue
from typing import Dict, Optional, Callable

from utils.stt.voiceid import VoiceIdentifier
from utils.stt.models import (
    create_fasterwhisper_model, 
    create_whisper_model, 
    create_groq_model
)

class Transcriber:
    """
    The Transcriber class is responsible for transcribing audio clips using different models.
    Args:
        model_name (str): The name of the model to use for transcription. Default is "faster-whisper".
    Attributes:
        _model_selection (str): The selected model name.
        model: The initialized transcription model instance.
        identifier: The initialized voice identifier instance.
        name_queue: A queue to store the speaker identification results.
    Methods:
        _initialize_model: Initialize the selected transcription model.
        _get_model_factory: Get the model factory.
        transcribe: Combine the transcription and identification of the speaker.
        transcribe_audio: Transcribe the given audio clip using the selected model.
    """
    
    def __init__(self, model_name: str = "faster-whisper"):
        self._model_selection: str = model_name.upper()
        self.model = self._initialize_model()
        self.identifier = VoiceIdentifier()
        self.name_queue = Queue()
        
        logger.info(f"Transcriber: {self._model_selection} is ready.")
    
    def _get_model_factory(self) -> Dict[str, Callable]:
        return {
            "FASTER-WHISPER" : create_fasterwhisper_model,
            "WHISPER" : create_whisper_model,
            "GROQ" : create_groq_model,
        }

    def _initialize_model(self):
        model_factory = self._get_model_factory()
        model = model_factory.get(self._model_selection)
        
        if model is None:
            raise ValueError(f"Error: Model {self._model_selection} is not supported")
        
        return model()
    

    def transcribe(self, audioclip) -> Optional[str]:  
        """ Transcribe the given audio clip and identify the speaker """
        
        while not self.name_queue.empty(): # Clear queue 
            self.name_queue.get()
        
        thread = threading.Thread(target=self.identifier.identify, args=(audioclip, self.name_queue))
        thread.start()
        
        transcription = self.model.transcribe_audio(audioclip)
        if not transcription:
            thread.join()
            return None
        
        # Get the speaker identification result
        name = self.name_queue.get()   
        thread.join()
        
        # if the name is unknown, return content with a new line, there is a new person speaking, save it into a database
        if name == "unknown":
            content = f"{transcription.strip()} (I couldn't tell whose voice it is.)"
        else:
            content = f"{name}:: {transcription.strip()}"
        # if name == "unknown person":
        #     speaker_id = secrets.token_hex(4)
        #     filepath = os.path.join(os.getcwd(), "data", "voids", f"{speaker_id}.wav")
        #     self.identifier.save_audio_file(audioclip, filepath)
        #     content += f" (<speaker_id>{speaker_id}</speaker_id>)"

        return content