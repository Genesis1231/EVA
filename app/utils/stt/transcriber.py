from config import logger
import os
from datetime import datetime
import threading
import secrets
from queue import Queue
from typing import Dict, Optional, Callable

from utils.stt.voiceid import VoiceIdentifier

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
    
    def __init__(self, model_name: str = "faster-whisper", language: str = "en"):
        self._model_selection: str = model_name.upper()
        self._model_language: str = language
        
        self.model = self._initialize_model()
        self.identifier = VoiceIdentifier()
        self.name_queue = Queue()
        
        logger.info(f"Transcriber: {self._model_selection} is ready.")
    
    def _get_model_factory(self) -> Dict[str, Callable]:
        return {
            "FASTER-WHISPER" : self._create_fasterwhisper_model,
            "WHISPER" : self._create_whisper_model,
            "GROQ" : self._create_groq_model,
        }
        
    def _create_groq_model(self):
        from utils.stt.model_groq import GroqTranscriber
        
        try:
            return GroqTranscriber(self._model_language)
        except Exception as e:
            raise Exception(f"Error: failed to load Whisper Model {str(e)}")
        
    def _create_fasterwhisper_model(self):
        from utils.stt.model_fasterwhisper import FWTranscriber
        
        try:
            return FWTranscriber(self._model_language)
        except Exception as e:
            raise Exception(f"Error: Fail to load Faster Whisper Model {str(e)}")
        
    def _create_whisper_model(self):
        from utils.stt.model_whisper import WhisperTranscriber
        
        try:
            return WhisperTranscriber(self._model_language)
        except Exception as e:
            raise Exception(f"Error: failed to load Whisper Model {str(e)}")
        
    def _initialize_model(self):
        """ Initialize the selected transcription model """
        
        model_factory = self._get_model_factory()
        model = model_factory.get(self._model_selection)
        
        if model is None:
            raise ValueError(f"Error: Model {self._model_selection} is not supported")
        
        return model()
    

    def transcribe(self, audioclip) -> Optional[tuple[str, str]]:  
        """ Transcribe the given audio clip and identify the speaker """
        
        while not self.name_queue.empty(): # Clear queue 
            self.name_queue.get()
        
        thread = threading.Thread(target=self.identifier.identify, args=(audioclip, self.name_queue))
        thread.start()
        
        transcription, language = self.model.transcribe_audio(audioclip)
        if not transcription:
            thread.join()
            return None, None
        
        # Get the speaker identification result
        identification = self.name_queue.get()   
        thread.join()
        
        # if the name is unknown, return content with a new line, there is a new person speaking, save it into a database
        if identification == "unknown":
            content = f"{transcription.strip()} (I couldn't ID the voice.)"
            display = f"Unknown voice: {transcription}"
        else:
            name = self.identifier.get_name(identification)
            content = f"{name} ({identification}):: {transcription.strip()}"
            display = f"{name}: {transcription}"
        # if name == "unknown person":
        #     speaker_id = secrets.token_hex(4)
        #     filepath = os.path.join(os.getcwd(), "data", "voids", f"{speaker_id}.wav")
        #     self.identifier.save_audio_file(audioclip, filepath)
        #     content += f" (<speaker_id>{speaker_id}</speaker_id>)"

        print(f"\n({datetime.now().strftime('%H:%M:%S')}) {display}")
        
        return content, language
