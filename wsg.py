import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/Ubuntu/subdomain_scanner")

from app import app as application
