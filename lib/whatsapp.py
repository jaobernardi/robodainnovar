import logging
import pyding

from .structures import Message
from . import config

from threading import Thread
from enum import Enum, auto
from typing import Any
from os import path
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


class SessionStatus(Enum):
    LOGGED_IN = auto()
    WAITING_QR_CODE = auto()
    LOADING = auto()


class Whatsapp():
    def __init__(self, threaded=False, headless=True):
        # Setup drivers
        options = Options()
        options.add_argument(f"--user-data-dir={path.abspath(config.get_session_path())}")
        options.add_argument(f"--no-sandbox")
        if headless:
            options.add_argument("--headless")
            options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36")

        # Open chrome
        self.webdriver = webdriver.Chrome(
            executable_path=config.get_chrome_path(),
            chrome_options=options
        )

        # Do changes
        self.webdriver.set_script_timeout(float("100000000"))

        # Save tags
        self.threaded = threaded
        self.headless = headless
        self.activities_queue = []
        self.running = False

    # Properties

    @property
    def current_status(self):
        if self.is_waiting_qrcode:
            return SessionStatus.WAITING_QR_CODE
        elif self.is_logged:
            return SessionStatus.LOGGED_IN
        else:
            return SessionStatus.LOADING

    @property
    def is_loading(self):
        return not self.is_waiting_qrcode and not self.is_logged

    @property
    def is_waiting_qrcode(self):
        return self.element_presence("div", attributes={"data-ref": Any})

    @property
    def is_logged(self):
        return self.element_presence("div", role="textbox")
    
    # Get methods

    def get_qr_code(self):
        if not self.element_presence("div", attributes={"data-ref": Any}):
            return
        qr_code = self.find_element("div", attributes={"data-ref": Any})
        try:
            return qr_code.get_attribute('data-ref') if qr_code else None
        except StaleElementReferenceException:
            return
    
    def focus_on_user(self, user):
        return

    # Action methods

    def send_message(self, chat_id, msg, options = None):
        self.load_js_from_file("bin/js/sendMessage.js", False, chat_id, msg, options or {})

    def seen_message(self, msg_id):
        self.load_js_from_file("bin/js/sendSeen.js", False, msg_id)

    # Selenium interfacing methods

    def element_presence(self, *args, **kwargs):
        return self.find_element(*args, **kwargs) != None

    def find_element(self, element, eclass = None, id = None, attributes = None, position=None, search_scope = None, avoid_mark=False, return_all=False, **kwargs) -> WebElement:
        extras = []
        if not attributes:
            attributes = {}
        attributes.update(kwargs)

        if not search_scope:
            search_scope = self.webdriver

        if avoid_mark:
            attributes['controller-mark'] = {'function': 'not'}

        if eclass:
            attributes['class'] = {"value": eclass, "function": "contains"}
        if id:
            attributes['id'] = id

        # Fire up events
        event = pyding.call("whatsapp_elementquery", cancellable=True, element=element, attributes=attributes, search_scope=search_scope)
        if event.cancelled:
            return 

        # Create the attributes part of the selector
        for attr, value in attributes.items():
            match value:
                case {"value": value, "function": function}:
                    extras.append(f"{function}(@{attr}, '{value}')")

                case {"value": value, "operator": operator}:
                    extras.append(f"@{attr}{operator}'{value}'")
                
                case {"function": function}:
                    extras.append(f"{function}(@{attr})")

                case {"attr_function": True}:
                    extras.append(f"{attr}()")

                case {"attr_function": True, "value": value}:
                    extras.append(f"{attr}() = '{value}'")
               
                case {"attr_function": True, "value": value, "operator": operator}:
                    extras.append(f"{attr}() {operator} '{value}'")

                case value if value in [Any, None]:
                    extras.append(f"@{attr}")
        
                case value:
                    extras.append(f"@{attr}='{value}'")


        # Build the selector
        selector = ("//" if not element.startswith("/") else '') + f"{element}" + (f"[{' and '.join(extras)}]" if extras else '') + (f'[{position}]' if position else '')       
        logging.debug(f"Performing element search with the following selector: {selector}")
        try:
            found = search_scope.find_elements(By.XPATH, selector)
            if not return_all:
                found = found[-1] if len(found) > 0 else None
            return found
        except NoSuchElementException:
            return

    def mark_element_from_find(self, *args, **kwargs):
        if element := self.find_element(*args, **kwargs):
            self.mark_element(element)

    def mark_element(self, element):
        self.edit_attribute(element, "controller-mark", "")

    def edit_attribute(self, element, attribute, value):
        try:
            self.webdriver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);", element, attribute, value)
        except StaleElementReferenceException:
            return
    # Logic

    def message_loop(self):
        last_msg = None
        print("loop")
        # Wait for message
        message = self.load_js_from_file("bin/js/waitMessage.js", asyncronos=True)
        msg = Message(self, message)
        # Prevent duplicate readings
        if msg.id == last_msg:
            return
        last_msg = msg.id
        pyding.call("whatsapp_new_message", whatsapp=self, message=msg)
        

    def loop(self):
 
        latest_qr = None
        latest_status = self.current_status
        while True:
            # Split commands per session status
            match self.current_status:
                # Landing page
                case SessionStatus.WAITING_QR_CODE:
                    qr_code = self.get_qr_code()
                    if qr_code and qr_code != latest_qr:
                        pyding.call("whatsapp_new_qr", whatsapp=self, qrcode=qr_code)
                        latest_qr = qr_code
                case SessionStatus.LOGGED_IN:
                    self.message_loop()

    # Driving the webdriver

    def execute_js(self, js, *arguments):
        return self.webdriver.execute_script(js, *arguments) 
    

    def execute_async_js(self, js, *arguments):
        return self.webdriver.execute_async_script(js, *arguments)
        

    def load_js_from_file(self, path, asyncronos=False, *arguments):
        with open(path, "r") as r:
            contents = r.read()
        if asyncronos:
            return self.execute_async_js(contents, *arguments)
        return self.execute_js(contents, *arguments)
        

    def expose_store(self):
        # This bit was made using code written by https://github.com/pedroslopez
        # <3 pedroslopez
        self.load_js_from_file("bin/js/moduleRaid.js")
        self.load_js_from_file("bin/js/exposeStore.js")
        self.load_js_from_file("bin/js/loadUtils.js")


    def die(self):
        self.webdriver.quit()


    def start(self, skip_safeguards=False, skip_loop=False):
        # Go to the website
        event = pyding.call("whatsapp_warmup", blocking=False, cancellable=True, whatsapp=self)
        if event.cancelled:
            logging.info("WhatsApp startup cancelled due to event cancel.")
            return

        self.webdriver.get("https://web.whatsapp.com/")

        if not skip_safeguards:
            logging.info("Waiting for whatsapp to load.")
            while self.is_loading:
                pass
            logging.info("Whatsapp loaded.")
        
        self.expose_store()

        if not skip_loop:
            self.running = True
            if self.threaded:
                self.main_thread = Thread(target=self.loop, daemon=True)
                self.main_thread.start()
                return
            self.loop()