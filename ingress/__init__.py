__version__= "1.0"

import logging
import logging.config

logging.config.fileConfig('logging.conf')

# create logger
logger = logging.getLogger(__name__)