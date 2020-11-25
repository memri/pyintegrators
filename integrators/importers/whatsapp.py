# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/importers.WhatsAppImporter.ipynb (unless otherwise specified).

__all__ = ['MatrixClient', 'get_g_attr', 'WhatsAppImporter']

# Cell
from hashlib import sha256
from ..data.schema import *
from ..imports import *
from .importer import ImporterBase
from ..pod.client import PodClient
from nbdev.showdoc import show_doc
import json
import time

# Cell
class MatrixClient:

    def __init__(self, url, username, token):
        self.url = url # Matrix url
        self.username = username # username of Matrix account
        self.token = token # token of Matrix account

        assert self.url is not None
        assert self.username is not None
        assert self.token is not None

    def get_joined_rooms(self):
        """List all rooms the user joined"""
        try:
            result = requests.get(f"{self.url}/_matrix/client/r0/joined_rooms?access_token={self.token}")
            if result.status_code != 200:
                print(result, result.content)
                return False
            else:
                json = result.json()
                res = json["joined_rooms"] # only rooms with "joined" status
                return res
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_joined_members(self, room_id):
        """List all joined members in a room"""
        try:
            result = requests.get(f"{self.url}/_matrix/client/r0/rooms/{room_id}/joined_members?access_token={self.token}")
            if result.status_code != 200:
                print(result, result.content)
                return False
            else:
                json = result.json()
                res = json["joined"] # only members with "joined" status
                return res
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def send_messages(self, room_id, body):
        """Send a message to a joined room"""
        try:
            result = requests.post(f"{self.url}/_matrix/client/r0/rooms/{room_id}/send/m.room.message?access_token={self.token}", json=body)
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                event_id = json["event_id"]
                return event_id
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_event_context(self, room_id, event_id):
        """Fetch events after a certain event"""
        try:
            # limit to context event is set to 1
            result = requests.get(f"{self.url}/_matrix/client/r0/rooms/{room_id}/context/{event_id}?limit=1&access_token={self.token}")
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                res = json["events_after"] # only show events after the specific event
                return res
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def sync_events(self, next_batch):
        """Fetch all events in a room in a batch"""
        try:
            result = requests.get(f"{self.url}/_matrix/client/r0/sync?since={next_batch}&access_token={self.token}")
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                return json
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_profile(self, user_id):
        """Fetch profile of a specific user"""
        try:
            result = requests.get(f"{self.url}/_matrix/client/r0/profile/{user_id}")
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                return json
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def get_room_state(self, room_id):
        """Fetch status of a room"""
        try:
            result = requests.get(f"{self.url}/_matrix/client/r0/rooms/{room_id}/state?access_token={self.token}")
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                json = result.json()
                return json
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def download_file(self, uri):
        """Download media files"""
        try:
            result = requests.get(f"{self.url}/_matrix/media/r0/download/{HOSTNAME}/{uri}")
            if result.status_code != 200:
                print(result, result.content)
                return None
            else:
                file = result.content
                return file
        except requests.exceptions.RequestException as e:
            print(e)
            return None


# Cell

# TODO: remove after it is included in the util
def get_g_attr(item, name, data_type, default_value=None):
    # hide
    first_or_default = next((att for att in item.genericAttribute if att.name == name), None)
    if first_or_default == None:
        return default_value
    else:
        if data_type == 'int':
            return first_or_default.intValue
        elif data_type == 'bool':
            return first_or_default.boolValue
        elif data_type == 'float':
            return first_or_default.floatValue
        elif data_type == 'string':
            return first_or_default.stringValue
        elif data_type == 'datetime':
            return first_or_default.stringValue
        else:
            raise Exception(f"datatype {data_type} is not supported")


# Cell
class WhatsAppImporter(ImporterBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matrix_client = None
        self.hostname = None
        self.matrix_address = None
        self.prefix_service = None
        self.bot_name = None
        self.username = None
        self.token = None
        self.acc_idx = {}
        self.msgchan_idx = {}
        self.msg_idx = {}

    def set_matrix_client(self, importer_run):
        """Set Matrix client instance and other parameters from importer_run"""
        self.hostname = get_g_attr(importer_run, 'host', 'string', None)
        self.matrix_address = get_g_attr(importer_run, 'address', 'string', None)
        self.prefix_service = get_g_attr(importer_run, 'prefix', 'string', None)
        self.bot_name = get_g_attr(importer_run, 'bot', 'string', None)
        self.username = importer_run.username
        self.token = importer_run.password

        assert self.hostname is not None
        assert self.matrix_address is not None
        assert self.prefix_service is not None
        assert self.bot_name is not None

        self.matrix_client = MatrixClient(self.matrix_address, self.username, self.token)

    def get_receivers(self, room):
        """Fetch message receivers of a room"""
        joined_members = self.matrix_client.get_joined_members(room)
        joined_members = list(joined_members.keys())
        joined_members.remove(self.username) # except the Matrix user
        # get associated Account item for each user
        receivers = [self.acc_idx[m] for m in joined_members]
        return receivers

    def get_bot_room_id(self, joined_rooms):
        """Get room_id of whatsappbot joined room"""
        for room in joined_rooms:
            joined_members = self.matrix_client.get_joined_members(room)
            # the room shared with whatsappbot has 2 members
            if len(joined_members) == 2 and self.bot_name in joined_members:
                return room

    def bot_list_contacts(self, room_id):
        """Create and send a messge, asking whatsappbot to list all contacts"""
        body = {"msgtype":"m.text", "body":"list contacts"}
        event_id = self.matrix_client.send_messages(room_id, body)
        return event_id

    def get_contacts(self, all_rooms):
        """Fetch a list of contacts from whatsappbot's response"""
        room_id = self.get_bot_room_id(all_rooms)
        event_id = self.bot_list_contacts(room_id)
        time.sleep(1) # wait for whatsappbot's reply
        contact_list = self.matrix_client.get_event_context(room_id, event_id)
        contacts = contact_list[0]["content"]["body"].split("\n")
        numbers = [self.get_phone_number(c) for c in contacts]
        numbers = [x for x in numbers if x is not None]
        users = [f"{self.prefix_service}{n}:{self.hostname}" for n in numbers]
        return users

    @staticmethod
    def get_phone_number(contact):
        """Get phone number from contact information"""
        if not contact.startswith(("#", "* /")):
            parts = contact.split(' - ')
            if len(parts) >= 2:
                phone_number = parts[1][1:-1]
                return phone_number

    def create_account(self, user_id):
        """Create Account item for each user_id"""
        profile = self.matrix_client.get_profile(user_id)
        avatar_url = None
        if "avatar_url" in profile:
            avatar_url = profile["avatar_url"]
        account = Account(externalId=user_id, displayName=profile["displayname"], avatarUrl=avatar_url, service="whatsapp")
        self.acc_idx[user_id] = account
        return account

    def create_message_channel(self, room_id, member_accounts):
        """Create MessageChannel item for each room, link with Account items"""
        room_state = self.matrix_client.get_room_state(room_id)
        room_name = None
        room_topic = None
        for s in room_state:
            if s["type"] == "m.room.name":
                room_name = s["content"]["name"]
            if s["type"] == "m.room.topic":
                room_topic == s["content"]["topic"]
        message_channel = MessageChannel(externalId=room_id, name=room_name, topic=room_topic)
        self.msgchan_idx[room_id] = message_channel
        for m in member_accounts:
            message_channel.add_edge("receiver", m) # link with Account
        return message_channel

    def create_message(self, event, room):
        """Create Message item for each event, link with MessageChannel and Account"""
        message = Message(externalId=event["event_id"], importJson=json.dumps(event["content"]), service="whatsapp")
        self.msg_idx[event["event_id"]] = message
        message.add_edge("messageChannel", self.msgchan_idx[room])
        message.add_edge("sender", self.acc_idx[event["sender"]])

        # Link with Message to create a thread
#         if "m.relates_to" in event["content"]:
#             message.add_edge("replyTo", self.msg_idx[event["content"]["m.relates_to"]["m.in_reply_to"]["event_id"]])

        # Create media item and link to Message
#         if "info" in event["content"]:
#             media = self.create_media(event["content"])
#             pod_client.create(media)

#             if event["content"]["msgtype"] == "m.video":
#                 message.add_edge("video", media)
#             elif event["content"]["msgtype"] == "m.image":
#                 message.add_edge("photo", media)
#             elif event["content"]["msgtype"] == "m.audio":
#                 message.add_edge("audio", media)
#             elif event["content"]["msgtype"] == "m.file":
#                 message.add_edge("document", media)
        return message

    def create_media(self, content):
        """Create media item in different types, link with File"""
        uri = content["url"].split('/')[3]
        binaries = self.matrix_client.download_file(uri)
        sha_file = sha256(binaries).hexdigest()
        # Create File item
        file = File(externalId=content["body"], sha256=sha_file)
        pod_client.create(file)
        # TODO: upload file

        if content["msgtype"] == "m.image":
            photo = Photo(externalId=content["url"])
            photo.add_edge("file", file)
            return photo
        elif content["msgtype"] == "m.video":
            video = Video(externalId=content["url"], duration=content["info"]["duration"])
            video.add_edge("file", file)
            return video
        elif content["msgtype"] == "m.audio":
            audio = Audio(externalId=content["url"], duration=content["info"]["duration"])
            audio.add_edge("file", file)
            return audio
        elif content["msgtype"] == "m.file":
            document = Document(externalId=content["url"], size=content["info"]["size"])
            document.add_edge("file", file)
            return document

    def import_all_accounts(self, all_rooms, users):
        """Import all created Account items to Pod"""
        for r in all_rooms:
            joined_members = self.matrix_client.get_joined_members(r)
            for m in joined_members:
                if not m in users:
                    users.append(m) # add whatsappbot, user
        for n in users:
            if not n in self.acc_idx:
                account = self.create_account(n)
                pod_client.create(account) # upload to Pod

    def import_all_messagechannels(self, all_rooms):
        """Import all created MessageChannel items to Pod"""
        for r in all_rooms:
            if not r in self.msgchan_idx:
                member_accounts = self.get_receivers(r)
                message_channel = self.create_message_channel(r, member_accounts)
                pod_client.create(message_channel) # upload to Pod
                pod_client.create_edges(message_channel.get_all_edges())

    def import_all_messages(self):
        """Import all created Message items to Pod"""
        batch = "s9_7_0_1_1_1"
        sync_events = self.matrix_client.sync_events(batch)
        joined_rooms = sync_events["rooms"]["join"]
        for r in joined_rooms:
            room_events = sync_events["rooms"]["join"][r]["timeline"]["events"]
            for e in room_events:
                if not e["event_id"] in self.msg_idx:
                    message = self.create_message(e, r)
                    pod_client.create(message) # upload to Pod
                    pod_client.create_edges(message.get_all_edges())

    def run(self, importer_run, pod_client=None, verbose=True):
        """This is the main function of WhatsAppImporter, which runs based on the information of importer_run."""
        self.set_matrix_client(importer_run)
        self.update_run_status(pod_client, importer_run, "running")

        all_rooms = self.matrix_client.get_joined_rooms()
        users = self.get_contacts(all_rooms)

        while True: # polling for chats and messages
            all_rooms = self.matrix_client.get_joined_rooms()

            self.update_progress_message(pod_client, importer_run, "importing contacts", verbose=verbose)
            self.import_all_accounts(all_rooms, users)

            self.update_progress_message(pod_client, importer_run, "importing chats", verbose=verbose)
            self.import_all_messagechannels(all_rooms)

            self.update_progress_message(pod_client, importer_run, "importing messages", verbose=verbose)
            self.import_all_messages()

            self.update_run_status(pod_client, importer_run, "polling")
            time.sleep(2)