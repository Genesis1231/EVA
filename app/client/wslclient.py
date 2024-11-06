import os
from config import logger
from typing_extensions import Dict, List, Optional

from utils.tts import Speaker, AudioPlayer
from utils.vision import Watcher
from utils.stt import Listener
from utils.extension import Window
from client.html import load_html

class WSLClient:
    """
    Class for eva to interact with the desktop client.
    You will need to install chrome browser for the display.
    Methods:
        send: Send the data to the client.
        receive: Receive the data from the client.
        speak: Speak the response to the client.
        stream_music: Stream the music to the client.
        launch_youtube: Launch the youtube video to the client.
        launch_epad: Launch the epad with HTML to the client.
        launch_gallery: Display the image to the client.
        deactivate: Deactivate the client.
    
    """
    def __init__(self, stt_model: str, vision_model: str, tts_model: str, base_url: str):
        self.speaker = Speaker(tts_model)
        self.watcher = Watcher(vision_model, base_url)
        self.listener = Listener(stt_model)
        self.player = AudioPlayer()
        self.window = Window()
    
    def send(self, data: Dict) -> None:
        if not data:
            logger.error("No data is sent to client.")
            return

        speech = data["speech"]
        wait = data["wait"]
        self.speaker.speak(speech, wait)
        
    def receive(self) -> Dict:
        observation = self.watcher.glance()
        message = self.listener.listen()
        
        return {
            "user_message": message,
            "observation": observation
        }
    
    def start(self) -> Dict:
        observation = self.watcher.glance()
        
        html = load_html("hello.html", message="Hello there!")
        self.window.launch_html(html)
        
        return {"observation": observation}

    def speak(self, response: str, wait: bool=True) -> None:
        self.speaker.speak(response, wait)
    
    def stream_music(self, url: str, cover_url: str, title: str) -> str:
        """ Client tool function, Stream the media to the client """
        try:
            html = load_html("music.html", image_url=cover_url, music_title=title)
            self.window.launch_html(html)
            self.player.stream(url)
            
            return f"The song '{title}' is playing."
        
        except Exception as e:
            logger.error(f"Error: Failed to stream to client: {str(e)}")
            return "Client Error: Failed to launch the media player."

    def launch_youtube(self, id: str, title: str) -> str:
        """ Client tool function, Stream the youtube video to the client """
        try:
            html = load_html("youtube.html", video_id=id, video_title=title)
            self.window.launch_html(html)
        
        except Exception as e:
            logger.error(f"Error: Failed to launch youtube video to client: {str(e)}")
            return "Client Error: The video player could not be launched properly."
    
    def launch_epad(self, html: str) -> Optional[str]:
        """ Client tool function, Launch the epad with HTML to the client """
        try:
            html = load_html("blank.html", full_html=html)
            self.window.launch_html(html)
            
            return None
        except Exception as e:
            logger.error(f"Error: Failed to launch epad to client: {str(e)}")
            return "Client Error: The epad could not be launched properly." 
    
    def launch_gallery(self, image_urls: List) -> Optional[str]:
        """ Client tool function, Display the image to the client """
        
        html = "\n".join([f"<div class='slide'><img src='{url}'></div>" for url in image_urls])

        try:
            html = load_html("gallery.html", image_block=html)
            self.window.launch_html(html)
            
            return None
        
        except Exception as e:
            logger.error(f"Error: Failed to display images: {str(e)}")
            return "Client Error: The images could not be displayed."
        
    def deactivate(self) -> None:
        self.watcher.deactivate()
            
    def send_over(self) -> None:
        pass
    
