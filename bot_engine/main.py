#!/usr/bin/env python3

from ast import Index
import os
import json
import telebot
import threading

BOT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
USERS_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "user_data/")

class BotEngine:
    def __init__(self):
        self.bot_config = {}
        self.bot = None

    def show_user_data(self, message):
        """Return specific user data, depending on chat_id"""
        with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'rb') as user_data_rb:
            return json.load(user_data_rb)

    def change_user_data(self, message, key_value={}):
        """Change specific key in user data, depending on chat id, using json"""
            
        if len(key_value) > 0:
            with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'rb') as user_data_rb:
                user_data = json.load(user_data_rb)
            for key, value in key_value.items():
                user_data[key] = value
            with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'w') as user_data_w:
                json.dump(user_data, user_data_w)

    def check_user_directories(self, message):
        """Create user-data directory if it doesn't exist and init base data-file, using json"""
        # Init base user data object
        user_base_data = {
            "First-Name": message.from_user.first_name if message.from_user.first_name else "",
            "Last-Name": message.from_user.last_name if message.from_user.last_name else "",
            "Username": message.from_user.username if message.from_user.username else "",
            "Phone-Number": None,
            "Location": None,
            "Step-Enabled": False,
            "Step-Name": None,
            "Start-Step-Message": None,
            "Last-Step": False,
            "Step-Result": {
                # Step Messaging Title: {
                #   Step name: {user_answer: user_answer_type(text/media/etc...)}
                # }
            },
            "Cart": {},
        }
        # Write into file if need
        if os.path.exists(os.path.join(USERS_DATA_PATH, str(message.chat.id))):
            if not os.path.exists(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json")):
                with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'w') as user_data_w:
                    json.dump(user_base_data, user_data_w)
        else:
            os.mkdir(os.path.join(USERS_DATA_PATH, str(message.chat.id)))
            with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'w') as user_data_w:
                json.dump(user_base_data, user_data_w)
        

    def update_bot_config(self, key_value={}):
        """Update bot configuration file, using json"""
        with open(BOT_CONFIG_PATH, 'rb') as config_file_rb:
            self.bot_config = json.load(config_file_rb)
        self.bot = telebot.TeleBot(self.bot_config["API"])

        if len(key_value) > 0:
            for key, value in key_value.items():
                self.bot_config[key] = value
            with open(BOT_CONFIG_PATH, 'w') as config_file_w:
                json.dump(self.bot_config, config_file_w)

    def init_buttons_markup(self, buttons_config):
        """Return created markup with buttons, if buttons config from argument has buttons. Else, return markup remover"""
        if buttons_config:
            buttons_config = buttons_config[0]
            buttons_list = []

            # Initialisation list of buttons
            for text, type in buttons_config.items():
                if text != "" or text is not None:
                    buttons_list.append(telebot.types.KeyboardButton(
                            text=text, 
                            request_contact=True if type == "phone" else False, 
                            request_location=True if type == "location" else False
                        )
                    )

            # Create markup if buttons exists
            if len(buttons_list) > 0:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                try:
                    markup.add(buttons_list[0], buttons_list[1], buttons_list[2])
                except IndexError:
                    try:
                        markup.add(buttons_list[0], buttons_list[1])
                    except IndexError:
                        markup.add(buttons_list[0])

                return markup
            else:
                return telebot.types.ReplyKeyboardRemove()
                
        else:
            return telebot.types.ReplyKeyboardRemove()

    def send_steps_to_admin(self, step_messaging_title, step_result):
        """Sending step data from user to the administrator IDs"""

        text = f"<b>Attention!</b> A new user completed the step-messaging. <i>Title of Step-Messaging</i>: <b>{step_messaging_title}.</b> \n<i>Here's a user messages:</i>\n"
        for step_name, user_msg in step_result[step_messaging_title].items():
            text += f"\n{step_name}: {user_msg}"

        for admin_id in self.bot_config["Administrator-IDs"]:
            self.bot.send_message(chat_id=admin_id, text=text, parse_mode="html")

        pass

    def update_step_results(self, message, step_messaging_title, step_data):
        """This method will update a new values into user data files, contains step-result information"""
        with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'rb') as user_data_rb:
            user_data = json.load(user_data_rb)

        for step_name, user_answer in step_data.items():
            user_data["Step-Result"][step_messaging_title][step_name] = user_answer
        with open(os.path.join(USERS_DATA_PATH, f"{message.chat.id}/{message.chat.id}_data.json"), 'w') as user_data_w:
            json.dump(user_data, user_data_w)

    def messaging_logic(self, message, config_key, user_message):
        """Base messaging logic, using in telebot handlers."""
        for obj in self.bot_config[config_key]:
            # If user message exists in bot config file
            if obj == user_message:
                
                markup = self.init_buttons_markup(self.bot_config[config_key][obj]["user_buttons"])
                
                # Check bot steps by order depending on sending message type
                if len(self.bot_config[config_key][obj]["bot_media"]) > 0:
                    if not self.bot_config[config_key][obj]["media_first"]:
                        
                        # Send text if text is first
                        self.bot.reply_to(message, self.bot_config[config_key][obj]["bot_text"], reply_markup=markup)

                        if self.bot_config[config_key][obj]["bot_additional_text"]:
                            for msg in self.bot_config[config_key][obj]["bot_additional_text"]:
                                self.bot.send_message(chat_id=message.chat.id, text=msg, reply_markup=markup)
                    
                    # Media files sending logic
                    for media_file_path, caption in self.bot_config[config_key][obj]["bot_media"].items():
                        media_file_extension = os.path.splitext(media_file_path)[-1]
                        with open(media_file_path, "rb") as media_file_rb:
                            if media_file_extension in [".jpg", ".png", ".jpeg"]:
                                self.bot.send_photo(chat_id=message.chat.id, photo=media_file_rb, caption=caption)
                            elif media_file_extension in [".mp4", ".mov", ".webm"]:
                                self.bot.send_video(chat_id=message.chat.id, video=media_file_rb, caption=caption)
                            else:
                                self.bot.send_document(chat_id=message.chat.id, document=media_file_rb, caption=caption)

                    # Send text if it didn't sended, because media sended first   
                    if self.bot_config[config_key][obj]["media_first"]:
                        self.bot.reply_to(message, self.bot_config[config_key][obj]["bot_text"], reply_markup=markup)

                        if self.bot_config[config_key][obj]["bot_additional_text"]:
                            for msg in self.bot_config[config_key][obj]["bot_additional_text"]:
                                self.bot.send_message(chat_id=message.chat.id, text=msg, reply_markup=markup)
                else:
                    # Send text if media list is empty
                    self.bot.reply_to(message, self.bot_config[config_key][obj]["bot_text"], reply_markup=markup)

                    if self.bot_config[config_key][obj]["bot_additional_text"]:
                        for msg in self.bot_config[config_key][obj]["bot_additional_text"]:
                            self.bot.send_message(chat_id=message.chat.id, text=msg, reply_markup=markup)

    def step_messaging_logic(self, message):
        """This method has all logic for step messaging. Use it on bot.message_handler (s)"""
        start_message = self.show_user_data(message)["Step-Start-Message"]
                
        # Creating first step if need
        if self.show_user_data(message)["Step-Name"] is None:
            first_step_name = list(self.bot_config["Step-Messaging"][start_message].keys())[0]
            for start_message in self.bot_config["Step-Messaging"]:
                if start_message == message.text.strip():
                    print(first_step_name)
                    self.change_user_data(message, key_value={
                            "Step-Result": {
                                self.bot_config["Step-Messaging"][start_message][first_step_name]["step_messaging_title"]: {} 
                            },
                            "Step-Name": first_step_name
                        }
                    )

        for step_name in self.bot_config["Step-Messaging"][start_message]:

            # Check user active step
            if step_name == self.show_user_data(message)["Step-Name"]:
                step_messaging_title = self.bot_config["Step-Messaging"][start_message][step_name]["step_messaging_title"]

                # Init user buttons markup
                markup = self.init_buttons_markup(self.bot_config["Step-Messaging"][start_message][step_name]["user_buttons"])
                
                # Check bot steps by order depending on sending message type
                if len(self.bot_config["Step-Messaging"][start_message][step_name]["bot_media"]) > 0:
                    
                    if not self.bot_config["Step-Messaging"][start_message][step_name]["media_first"]:
                        
                        # Send text if text is first
                        for text in self.bot_config["Step-Messaging"][start_message][step_name]["bot_text"]:
                            self.bot.send_message(message.chat.id, text, reply_markup=markup)
                    
                    # Media files sending logic
                    for media_file_path, caption in self.bot_config["Step-Messaging"][start_message][step_name]["bot_media"].items():
                        media_file_extension = os.path.splitext(media_file_path)[-1]
                        with open(media_file_path, "rb") as media_file_rb:
                            if media_file_extension in [".jpg", ".png", ".jpeg"]:
                                self.bot.send_photo(chat_id=message.chat.id, photo=media_file_rb, caption=caption)
                            elif media_file_extension in [".mp4", ".mov", ".webm"]:
                                self.bot.send_video(chat_id=message.chat.id, video=media_file_rb, caption=caption)
                            else:
                                self.bot.send_document(chat_id=message.chat.id, document=media_file_rb, caption=caption)

                    # Send text if it didn't sended, because media sended first   
                    if self.bot_config["Step-Messaging"][start_message][step_name]["media_first"]:
                        for text in self.bot_config["Step-Messaging"][start_message][step_name]["bot_text"]:
                            self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)

                else:
                    # Send text if media list is empty
                    for text in self.bot_config["Step-Messaging"][start_message][step_name]["bot_text"]:
                        self.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=markup)

                
                # Update information for administrators from user messages
                if message.text.strip() != start_message:
                    self.update_step_results(message=message, step_messaging_title=step_messaging_title, step_data={step_name: message.text.strip()})

                # If it'a a last step - stop step messaging, if not, change step name in user data and send result to administrators
                if step_name == list(self.bot_config["Step-Messaging"][start_message])[-1]:
                    self.change_user_data(message=message, key_value={
                            "Last-Step": True,
                        }
                    )
                    break

                else:
                    # Add second step into user-data
                    next_step = ""
                    step_list = self.bot_config["Step-Messaging"][start_message].keys()
                    for index, key in enumerate(step_list):
                        if key == step_name:
                            next_step = list(step_list)[int(index) + 1]
                    self.change_user_data(message=message, key_value={"Step-Name": next_step})


                if self.show_user_data(message=message)["Last-Step"]:
                    self.change_user_data(message=message, key_value={
                            "Step-Enabled": False,
                            "Step-Name": None,
                            "Start-Step-Message": None,
                            "Last-Step": False
                        }
                    )
                    self.send_steps_to_admin(step_result=self.show_user_data(message=message)["Step-Result"], step_messaging_title=step_messaging_title)    
                
                break



    def init_command_operations(self):
        """Init all commands messaging logic from base messaging logic method. Also update config and check user directories tree"""
        @self.bot.message_handler(commands=[command for command in self.bot_config["Commands"]])
        def command_handler(message):
            self.update_bot_config()
            self.check_user_directories(message=message)
            self.messaging_logic(message=message, config_key="Commands", user_message=message.text.strip().replace('/', ''))


    def init_message_operations(self):
        "Init all messaging logic from base messaging logic method. For Step-Messaging it using another logic method."
        @self.bot.message_handler(content_types=['text'])
        def message_hadler(message):

            self.update_bot_config()
            self.check_user_directories(message=message)

            # Turning on step mode in user data file if message from user exist in step-messaging-config
            if message.text.strip() in self.bot_config["Step-Messaging"] and not self.show_user_data(message)["Step-Enabled"]:
                
                self.change_user_data(message=message, key_value={"Step-Enabled": True, "Step-Start-Message": message.text.strip()})

            # Start step messaging if step-messaging mode is enabled
            if self.show_user_data(message)["Step-Enabled"]:
                self.step_messaging_logic(message=message)
            else:
                self.update_bot_config()
                self.check_user_directories(message=message)
                self.messaging_logic(message=message, config_key="Messaging", user_message=message.text.strip())
                
    def prepare(self):
        """Preparing config and messaging logic"""
        self.update_bot_config()
        self.init_command_operations()
        self.init_message_operations()

    def start_bot_in_thread(self):
        """Preparing everything what program need and start bot in thread (self.bot_thread) for manipulation"""

        self.prepare()

        # To resolve pyTelegramBotAPI bug with launching, steal this part of code
        try:
            self.bot_thread
        except AttributeError:
            self.bot_thread = threading.Thread(target=self.bot.polling, args=())

        if self.bot_thread.is_alive():
            print("\n[!] Telegram Bot already stared!\n")
        else:
            self.bot_thread.start()
            print("\n[+] Telegram Bot successfully started!\n")

    def start_bot(self):
        """Preparing everything what program need and start bot"""

        self.prepare()
        self.bot.polling(non_stop=True)


BotEngine().start_bot_in_thread()












# Создай код, с проверкой на "Последнее сообщение" - избавишься от бага.