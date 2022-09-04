#!/usr/bin/env python3

import os
import json
import shutil
import telebot
import threading

BOT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
USERS_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "user_data/")
USERS_MEDIA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../media/users-media-files/")

class BotEngine:
    def __init__(self):
        self.bot_config = {}
        self.bot = None
        self.bot_config_path = BOT_CONFIG_PATH
        self.users_data_path = USERS_DATA_PATH

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
            "Step-Messaging": False,
            "Step-Name": None,
            "Step-Messaging-Title": None,
            "Start-Step-Message": None,
            "Send-Last-Step-Message": False,
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

        # Create user_media_directory if need
        if os.path.exists(USERS_MEDIA_PATH):
            if not os.path.exists(os.path.join(USERS_MEDIA_PATH, str(message.chat.id))):
                os.mkdir(os.path.join(USERS_MEDIA_PATH, str(message.chat.id)))
        else:
            os.mkdir(USERS_MEDIA_PATH)
            os.mkdir(os.path.join(USERS_MEDIA_PATH, str(message.chat.id)))

    def clean_user_media_directory(self, chat_id):
        shutil.rmtree(os.path.join(USERS_MEDIA_PATH, str(chat_id)))

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
                if text is not None and text.strip() != '' and text != '':
                    buttons_list.append(telebot.types.KeyboardButton(
                            text=text.strip(), 
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

        messages_for_admin = [
            f"<b>Attention!</b> A new user completed the step-messaging. \n<i>Title of Step-Messaging</i>: <b>{step_messaging_title}.</b> \n\n<i>Here's a user's replies:</i>",
        ]

        for step_name, user_msg in step_result[step_messaging_title].items():
            if type(user_msg) is dict:
                messages_for_admin.append({step_name: user_msg})
            else:
                messages_for_admin.append(f"\n<b>{step_name}</b>: {user_msg}")

        for admin_id in self.bot_config["Administrator-IDs"]:
            for message in messages_for_admin:
                if type(message) is dict:
                    for step_name, user_msg in message.items():
                        if "photo" in user_msg:
                            with open(user_msg["photo"], 'rb') as pic: 
                                self.bot.send_photo(chat_id=admin_id, photo=pic, caption=step_name)
                        elif "voice" in user_msg:
                            with open(user_msg["voice"], 'rb') as voice: 
                                self.bot.send_voice(chat_id=admin_id, voice=voice, caption=step_name)
                        elif "audio" in user_msg:
                            with open(user_msg["audio"], 'rb') as audio: 
                                self.bot.send_audio(chat_id=admin_id, audio=audio, caption=step_name)
                        elif "video" in user_msg:
                            with open(user_msg["video"], 'rb') as video: 
                                self.bot.send_video(chat_id=admin_id, video=video, caption=step_name)
                        elif "document" in user_msg:
                            with open(user_msg["document"], 'rb') as doc: 
                                self.bot.send_document(chat_id=admin_id, document=doc, caption=step_name)
                        elif "contact" in user_msg:
                            self.bot.send_message(
                                chat_id=admin_id, 
                                text=f"<b>{step_name}</b>: <i>{user_msg['contact']}</i>",
                                parse_mode="html"
                            )
                elif type(message) is str:
                    self.bot.send_message(chat_id=admin_id, text=message, parse_mode="html")

    def base_messaging_logic(self, message, specific_content):
        # Init user buttons markup
        markup = self.init_buttons_markup(specific_content["user_buttons"])
        if len(specific_content["bot_media"]) > 0:
            if not specific_content["media_first"]:
                
                # Send text if text is first
                if type(specific_content["bot_text"]) == list:
                    for text in specific_content["bot_text"]:
                        self.bot.send_message(message.chat.id, text, reply_markup=markup)
                else:
                    self.bot.send_message(message.chat.id, specific_content["bot_text"], reply_markup=markup)

                
            # Media files sending logic
            for media_file_path, caption in specific_content["bot_media"].items():
                media_file_extension = os.path.splitext(media_file_path)[-1]
                with open(media_file_path, "rb") as media_file_rb:
                    if media_file_extension in [".jpg", ".png", ".jpeg"]:
                        self.bot.send_photo(chat_id=message.chat.id, photo=media_file_rb, caption=caption, reply_markup=markup)
                    elif media_file_extension in [".mp4", ".mov", ".webm"]:
                        self.bot.send_video(chat_id=message.chat.id, video=media_file_rb, caption=caption, reply_markup=markup)
                    else:
                        self.bot.send_document(chat_id=message.chat.id, document=media_file_rb, caption=caption, reply_markup=markup)

            # Send text if it didn't sended, because media sended first   
            if specific_content["media_first"]:
                if type(specific_content["bot_text"]) == list:
                    for text in specific_content["bot_text"]:
                        self.bot.send_message(message.chat.id, text, reply_markup=markup)
                else:
                    self.bot.send_message(message.chat.id, specific_content["bot_text"], reply_markup=markup)
        else:
            # Send text if media list is empty
            if type(specific_content["bot_text"]) == list:
                for text in specific_content["bot_text"]:
                    self.bot.send_message(message.chat.id, text, reply_markup=markup)
            else:
                self.bot.send_message(message.chat.id, specific_content["bot_text"], reply_markup=markup)

    def step_messaging_logic(self, message, content={}):
        """This method has all logic for step messaging. Use it on bot.message_handler (s)"""

        title = self.show_user_data(message)["Step-Messaging-Title"]
        start_message = self.show_user_data(message)["Start-Step-Message"]
        

        for step_name in self.bot_config["Step-Messaging"][title][start_message]:

            # Check user active step
            if step_name == self.show_user_data(message)["Step-Name"]:
                
                # If this step messaging not finished
                if not self.show_user_data(message)["Send-Last-Step-Message"]:
                    
                    # Update information for administrators from user messages
                    if self.bot_config["Step-Messaging"][title][start_message][step_name]["send_to_admin"]:
                        
                        # If content from specific messages handlers exists, save it as result
                        user_data = self.show_user_data(message=message)
                        if content:
                            user_data["Step-Result"][title][step_name] = content
                            self.change_user_data(message, key_value=user_data)
                        # If not, save user message as result
                        else:
                            user_data["Step-Result"][title][step_name] = message.text.strip()
                            self.change_user_data(message, key_value=user_data)

                        # If it'a a last step - stop step messaging.If not, change step name in user data
                        if step_name == list(self.bot_config["Step-Messaging"][title][start_message].keys())[-1]:
                            self.change_user_data(message=message, key_value={
                                    "Send-Last-Step-Message": True
                                }
                            )
                        else:
                            if message is not None and content or message.text.strip() != start_message:
                                # Add next step into user-data
                                next_step = ""
                                step_list = list(self.bot_config["Step-Messaging"][title][start_message].keys())
                                for index, key in enumerate(step_list):
                                    if key == step_name:
                                        next_step = list(step_list)[int(index) + 1]
                                self.change_user_data(message=message, key_value={"Step-Name": next_step})
                                self.base_messaging_logic(message=message, specific_content=self.bot_config["Step-Messaging"][title][start_message][next_step])
                                break
                    
                    # If it's not a last step, continue chatting
                    if not self.show_user_data(message)["Send-Last-Step-Message"]:
                        self.base_messaging_logic(message=message, specific_content=self.bot_config["Step-Messaging"][title][start_message][step_name])
                    # If it's a last step - send every user answer to administrator's ID if need
                    else:
                        if self.bot_config["Step-Messaging"][title][start_message][step_name]["send_to_admin"]:
                            self.send_steps_to_admin(step_messaging_title=title, step_result=self.show_user_data(message)["Step-Result"])
                            self.clean_user_media_directory(chat_id=message.chat.id)

                        self.change_user_data(message=message, key_value={
                            "Send-Last-Step-Message": False,
                            "Step-Messaging": False,
                            "Step-Name": None,
                            "Step-Messaging-Title": None,
                            "Start-Step-Message": None,
                            "Step-Result": {
                                # Step Messaging Title: {
                                #   Step name: {user_answer: user_answer_type(text/media/etc...)}
                                # }
                            },
                        })
                        self.base_messaging_logic(message=message, specific_content=self.bot_config["Last-Step-Messages"][title])
                    
                else:
                    if self.bot_config["Step-Messaging"][title][start_message][step_name]["send_to_admin"]:
                        self.send_steps_to_admin(step_messaging_title=title, step_result=self.show_user_data(message)["Step-Result"])
                        self.clean_user_media_directory(chat_id=message.chat.id)

                    self.change_user_data(message=message, key_value={
                        "Send-Last-Step-Message": False,
                        "Step-Messaging": False,
                        "Step-Name": None,
                        "Step-Messaging-Title": None,
                        "Start-Step-Message": None,
                        "Step-Result": {
                            # Step Messaging Title: {
                            #   Step name: {user_answer: user_answer_type(text/media/etc...)}
                            # }
                        },
                    })
                    self.base_messaging_logic(message=message, specific_content=self.bot_config["Last-Step-Messages"][title])
                
                break

    def init_command_messaging_operations(self):
        """Init all commands messaging logic from base messaging logic method. Also update config and check user directories tree"""
        @self.bot.message_handler(commands=[command for command in self.bot_config["Commands"]])
        def command_handler(message):
            self.update_bot_config()
            self.check_user_directories(message=message)
            for command_name in self.bot_config["Commands"].keys():
                if message.text.strip().replace("/", "") == command_name:
                    self.base_messaging_logic(message=message, specific_content=self.bot_config["Commands"][command_name])

    def init_text_messaging_operations(self):
        "Init all messaging logic from base messaging logic method. For Step-Messaging it using another logic method."
        @self.bot.message_handler(content_types=['text'])
        def message_hadler(message):
            self.update_bot_config()
            self.check_user_directories(message=message)
            step_messaging_titles = [title for title in self.bot_config["Step-Messaging"]]

            # Turning on step mode in user data file if message from user exist in step-messaging-config
            for title in step_messaging_titles:
                if message.text.strip() in self.bot_config["Step-Messaging"][title] and not self.show_user_data(message)["Step-Messaging"]:
                    first_step_name = list(self.bot_config["Step-Messaging"][title][message.text.strip()].keys())[0]
                    self.change_user_data(message, {
                            "Step-Messaging": True, 
                            "Step-Messaging-Title": title,
                            "Start-Step-Message": message.text.strip(),
                            "Step-Name": first_step_name,
                            "Step-Result": {
                                title: {

                                }
                            }
                        }
                    )
                    
                    self.step_messaging_logic(message=message)
                    return True

            # Start step messaging if step-messaging mode is enabled
            if self.show_user_data(message)["Step-Messaging"]:
                self.step_messaging_logic(message=message)
            else:
                for msg_from_user in self.bot_config["Messaging"]:
                    if message.text.strip() == msg_from_user:
                        self.base_messaging_logic(message=message, specific_content=self.bot_config["Messaging"][msg_from_user])

    def init_photo_messaging_operations(self):
        "Init all messaging logic from base messaging logic method. For Step-Messaging it using another logic method."
        @self.bot.message_handler(content_types=['photo'])
        def message_hadler(message):
            self.update_bot_config()
            self.check_user_directories(message=message)

            file_path = self.bot.get_file(message.photo[-1].file_id).file_path
            media_file = self.bot.download_file(file_path)
            src = f"media/users-media-files/{message.chat.id}/" + file_path.split("/")[-1]
            with open(src, "wb") as new_file:
                new_file.write(media_file)

            if self.show_user_data(message)["Step-Messaging"]:
                self.step_messaging_logic(message=message, content={"photo": src})

    def init_voice_messaging_operations(self):
        "Init all messaging logic from base messaging logic method. For Step-Messaging it using another logic method."
        @self.bot.message_handler(content_types=['voice'])
        def message_hadler(message):
            self.update_bot_config()
            self.check_user_directories(message=message)


            file_path = self.bot.get_file(message.voice.file_id).file_path
            media_file = self.bot.download_file(file_path)
            src = f"media/users-media-files/{message.chat.id}/" + file_path.split("/")[-1]
            with open(src, "wb") as new_file:
                new_file.write(media_file)

            if self.show_user_data(message)["Step-Messaging"]:
                self.step_messaging_logic(message=message, content={"voice": src})

    def init_contact_messaging_operations(self):
        "Init all messaging logic from base messaging logic method. For Step-Messaging it using another logic method."
        @self.bot.message_handler(content_types=['contact'])
        def message_hadler(message):
            self.update_bot_config()
            self.check_user_directories(message=message)
            if self.show_user_data(message)["Step-Messaging"]:
                self.step_messaging_logic(message=message, content={"contact": message.contact.phone_number})

    def prepare(self):
        """Preparing config and messaging logic"""
        self.update_bot_config()
        self.init_command_messaging_operations()
        self.init_text_messaging_operations()
        self.init_photo_messaging_operations()
        self.init_contact_messaging_operations()
        self.init_voice_messaging_operations()

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
