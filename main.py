from lib.patching import patch
# Path urlib stuff
patch()

from lib.whatsapp import Whatsapp, SessionStatus
from lib.database import setup_tables
from lib.utils import load_handlers
import logging
from pyding import on
from qrcode import QRCode
import argparse

parser = argparse.ArgumentParser(description='Whatsapp Automation Service.')

parser.add_argument('-f', '--headfull', action='store_true', help="Starts chrome on headfull mode")
parser.add_argument('-sd', '--setup-database', action='store_true', help="Setups database")
parser.add_argument('-sf', '--skip-safeguards', action='store_true', help="Skips the whatsapp waiting safeguard")
parser.add_argument('-sl', '--skip-loop', action='store_true', help="Skips the whatsapp waiting safeguard")
parser.add_argument('-t', '--threaded', action='store_true', help="Whatsapp main loop thread status")

args = parser.parse_args()
logging.basicConfig(level=logging.INFO)


if args.setup_database:
    setup_tables()

whats = Whatsapp(headless=not args.headfull, threaded=args.threaded)

@on("whatsapp_new_qr")
def new_qr(event, whatsapp: Whatsapp, qrcode):
    if not whatsapp.headless:
        logging.info("Please, log in using the following qr-code:")
        qr = QRCode()
        qr.add_data(qrcode)
        qr.print_ascii(invert=True)
    else:
        logging.info("Recieved the following log-in code: "+qrcode)


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

