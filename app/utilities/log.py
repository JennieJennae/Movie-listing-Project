import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logger = logging.getLogger("movie_listing_logger")
logger.setLevel(logging.INFO)

# Create a file handler that logs messages to a file with rotation
handler = RotatingFileHandler("movie_listing.log", maxBytes=2000, backupCount=5)
handler.setLevel(logging.INFO)

# Create a console handler to output logs to the console as well
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)
logger.addHandler(console_handler)

