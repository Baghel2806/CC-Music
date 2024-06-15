import sys
import site

site.addsitedir('/var/www/s3882120/venv/lib/python3.8/site-packages')

sys.path.insert(0, '/var/www/s3882120')

from app import app as application