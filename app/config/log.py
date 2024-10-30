import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Create a console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# # Create a file handler and set level to warning
# file_handler = logging.FileHandler('app.log')
# file_handler.setLevel(logging.WARNING)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
# logger.addHandler(file_handler)
