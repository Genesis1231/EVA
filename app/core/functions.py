from functools import partial
from config import logger
from tqdm import tqdm
from config import validate_language
from typing import Dict, Any

from client import WSLClient, MobileClient
from utils.agent import ChatAgent
from utils.memory import Memory
from tools import ToolManager
from utils.tts.speaker import Speaker


def load_classes(class_dict)-> Dict:
    """ Load the classes from the dictionary, using tqdm to show progress """
    
    instances = {}
    with tqdm(total=len(class_dict), desc="Initializing EVA...") as pbar:
        for name, class_init in class_dict.items():
            pbar.set_description(f"Loading module: {name}")
            instances[name] = class_init()
            pbar.update(1)
            
    return instances

def initialize_modules(config : Dict[str, str]) -> Dict[str, Any]:
    """ Initialize the modules for EVA """
    
    client_type = config.get("DEVICE").upper()
    base_url = config.get("BASE_URL")
    language = config.get("LANGUAGE")
    chat_model = config.get("CHAT_MODEL")
    summarize_model = config.get("SUMMARIZE_MODEL")
    stt_model = config.get("STT_MODEL")
    vision_model = config.get("VISION_MODEL")
    tts_model = config.get("TTS_MODEL")
    
    # Validate the language
    if not (full_lang := validate_language(language)):
        logger.error(f"Language {language} not supported, defaulting to multilingual")
        language = full_lang = "multilingual"
    
    # Initialize the modules
    module_list = {
        "agent": partial(ChatAgent, chat_model, base_url, full_lang),
        "memory": partial(Memory, summarize_model, base_url),
        "toolbox": partial(ToolManager, client_type),
        "tts_model": partial(Speaker, tts_model, language)  # Common for both types
    }

    # Client-specific initialization
    match client_type:
        case "DESKTOP":
            from utils.stt import PCListener
            from utils.vision import Watcher
            
            module_list.update({
                "client": WSLClient,
                "stt_model": partial(PCListener, stt_model, language),
                "vision_model": partial(Watcher, vision_model, base_url),
            })

        case "MOBILE":
            from utils.stt.transcriber import Transcriber
            from utils.vision.describer import Describer

            module_list.update({
                "client": MobileClient,
                "stt_model": partial(Transcriber, stt_model),
                "vision_model": partial(Describer, vision_model, base_url),
            })

        case _:
            raise ValueError(f"Client type {client_type} not supported.")

    # Load the modules
    modules = load_classes(module_list)
    modules["client"].initialize_modules(modules["stt_model"], modules["vision_model"], modules["tts_model"])    
    modules["agent"].set_tools(modules["toolbox"].get_tools_info())
    
    return modules