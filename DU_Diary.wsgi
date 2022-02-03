activate_this = '/var/www/DU_Diary/DU_Diary/venv/bin/activate_this.py'
with open(activate_this) as file:
    exec(file.read(), dict(__file__=activate_this))

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/DU_Diary/")
from DU_Diary import app as application
application.secret_key = "thisissecret"
