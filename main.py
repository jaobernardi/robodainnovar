from lib.patching import patch
import os
# Path urlib stuff
patch()

from lib import config
from lib.whatsapp import Whatsapp, SessionStatus
from lib.database import setup_tables
from lib.utils import load_handlers
import logging
from pyding import on
from qrcode import QRCode
import argparse
import time

parser = argparse.ArgumentParser(description='Whatsapp Automation Service.')

parser.add_argument('-f', '--headfull', action='store_true', help="Starts chrome on headfull mode")
parser.add_argument('-sd', '--setup-database', action='store_true', help="Setups database")
parser.add_argument('-sf', '--skip-safeguards', action='store_true', help="Skips the whatsapp waiting safeguard")
parser.add_argument('-sl', '--skip-loop', action='store_true', help="Skips the whatsapp waiting safeguard")
parser.add_argument('-t', '--threaded', action='store_true', help="Whatsapp main loop thread status")
parser.add_argument('-d', '--debug', action='store_true', help="Set logging level to debug")
parser.add_argument('--debug_module', action='store', help='Set logging level of a specific module to debug')
parser.add_argument('--reset_session', action='store_true', help='Resets chromedriver user session')


args = parser.parse_args()


def setup_logger(level, filename):
    logging.basicConfig(
        level=level,
        handlers=[
            logging.FileHandler(filename),
            logging.StreamHandler()
        ]
    )


if args.reset_session:
    os.system(f'rm -rf {config.get_session_path()}*')

if args.debug:
    logging.getLogger("selenium").setLevel(logging.INFO)
    setup_logger(logging.DEBUG, f'logs/{int(time.time())}-DEBUG.log')
else:
    setup_logger(logging.INFO, f'logs/{int(time.time())}.log')


if args.debug_module:
    for module in args.debug_module.split(" "):
        logging.info(f'Setting logging level of {module} to debug')
        logging.getLogger(module).setLevel(logging.DEBUG)

if args.setup_database:
    setup_tables()

whats = Whatsapp(headless=not args.headfull, threaded=args.threaded)

@on("whatsapp_new_qr")
def new_qr(event, whatsapp: Whatsapp, qrcode):
    logging.info("Please, log in using the following qr-code:")
    qr = QRCode()
    qr.add_data(qrcode)
    qr.print_ascii(invert=True)


@on('whatsapp_session_update')
def session_update(event, whatsapp, old_status, new_status):    
    conversion_table = {
        SessionStatus.WAITING_QR_CODE: "waiting log-in",
        SessionStatus.LOGGED_IN: "logged in",
        SessionStatus.LOADING: "loading"
    }
    
    logging.info(f"Session status changed to: {conversion_table[new_status]}")


if __name__ == "__main__":
    load_handlers()

    whats.start(args.skip_safeguards, args.skip_loop)

