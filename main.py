from lib.whatsapp import Whatsapp, SessionStatus
from lib.utils import load_handlers
import logging
from pyding import on
from qrcode import QRCode

logging.basicConfig(level=logging.INFO)

whats = Whatsapp(headless=True)

@on("whatsapp_new_qr")
def new_qr(event, whatsapp: Whatsapp, qrcode):
    if whatsapp.headless:
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


load_handlers()

whats.start()

