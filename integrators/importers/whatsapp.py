# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/importers.WhatsAppImporter.ipynb (unless otherwise specified).

__all__ = ['get_g_attr', 'get_random_alphanumeric_string', 'MautrixWhatsapp', 'WhatsAppImporter']

# Cell
from hashlib import sha256
from ..data.schema import *
from ..imports import *
from .importer import ImporterBase
from .matrix import *
from ..pod.client import PodClient
from nbdev.showdoc import show_doc
import docker
import string
import subprocess
import sys
import time

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

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

# Cell
class MautrixWhatsapp:

    def __init__(self, hostname, bridge, user, data_dir, client, my_uid, my_gid):
        self.hostname = hostname # Matrix homeserver hostname
        self.bridge = bridge # bridge domain
        self.user = user # matrix username
        self.dir = data_dir # directory for configuration files
        self.client = client # docker client
        self.my_uid = my_uid # non-root user uid
        self.my_gid = my_gid # non-root user gid

        assert self.hostname is not None
        assert self.bridge is not None
        assert self.user is not None
        assert self.dir is not None
        assert self.client is not None
        assert self.my_uid is not None
        assert self.my_gid is not None

    def config_whatsapp_bridge(self):
        """Generate config files for whatsapp bridge"""
        AS_TOKEN = get_random_alphanumeric_string(64)
        HS_TOKEN = get_random_alphanumeric_string(64)
        SENDER_L = get_random_alphanumeric_string(32)

        find_replace = {
            "localhost": f"{self.bridge}",
            "example.com": f"{self.hostname}",
            "as_token:": f"as_token: {AS_TOKEN}",
            "hs_token:": f"hs_token: {HS_TOKEN}",
        }
        with open('../examples/whatsapp_bridge/example-config.yaml') as fin:
            with open(f"{self.dir}/config.yaml", 'w') as fout:
                for line in fin:
                    for key in find_replace:
                        if key in line:
                            line = line.replace(key, find_replace[key])
                    fout.write(line)
        find_replace = {
            "localhost": f"{self.hostname}",
            "example.com": f"{self.bridge}",
            "as_token:": f"as_token: {AS_TOKEN}",
            "hs_token:": f"hs_token: {HS_TOKEN}",
            "sender_localpart:": f"sender_localpart: {SENDER_L}"
        }
        with open('../examples/whatsapp_bridge/example-registration.yaml') as fin:
            with open(f"{self.dir}/registration.yaml", 'w') as fout:
                for line in fin:
                    for key in find_replace:
                        if key in line:
                            line = line.replace(key, find_replace[key])
                    fout.write(line)

    def run_bridge(self, networkname):
        """Launch whatsapp bridge"""
        self.client.containers.run(
            "dock.mau.dev/tulir/mautrix-whatsapp:latest",
            detach=True,
            network=networkname,
            restart_policy={'Name': 'on-failure'},
            ports={'29318': '29318'},
            volumes={self.dir: {'bind': '/data', 'mode': 'rw'}},
            environment=[f"UID={self.my_uid}", f"GID={self.my_gid}"],
            name=self.bridge
        )
        time.sleep(3)

# Cell
class WhatsAppImporter(ImporterBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matrix = None
        self.matrix_client = None
        self.hostname = None
        self.matrix_address = None
        self.prefix_service = None
        self.bot_name = None
        self.username = None
        self.password = None
        self.dir = None
        self.matrix_acc = None
        self.matrix_token = None
        self.wa_network = None
        self.acc_idx = {} # helper dict for contacts
        self.msgchan_idx = {} # helper dict for chats
        self.msg_idx = {} # helper dict for messages

    def set_matrix_client(self, pod_client, importer_run, wa_network):
        """Set Matrix client instance and other parameters from importer_run"""
        self.hostname = get_g_attr(importer_run, 'host', 'string', None)
        self.bridgename = get_g_attr(importer_run, 'bridge', 'string', None)
        self.matrix_address = get_g_attr(importer_run, 'address', 'string', None)
        self.prefix_service = get_g_attr(importer_run, 'prefix', 'string', None)
        self.bot_name = get_g_attr(importer_run, 'bot', 'string', None)
        self.username = importer_run.username
        self.password = importer_run.password
        self.dir = f"{os.getcwd()}/../{self.username}_matrix_data"
        self.wa_network = wa_network

        assert self.hostname is not None
        assert self.bridgename is not None
        assert self.matrix_address is not None
        assert self.prefix_service is not None
        assert self.bot_name is not None
        assert self.username is not None
        assert self.password is not None
        assert self.dir is not None
        assert self.wa_network is not None

        # create docker network bridge
        client = docker.from_env()
        network_name = 'matrix-net'
        if not client.networks.list(network_name):
            client.networks.create(network_name, driver='bridge')

        # configure WhatsApp bridge
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        self.mautrix = MautrixWhatsapp(self.hostname, self.bridgename, self.username, self.dir, client, os.getuid(), os.getgid())
        self.mautrix.config_whatsapp_bridge()

        # check if matrix is already running
        if not client.containers.list(filters={'name': self.hostname}): # matrix is NOT running
            matrix_item = pod_client.search_by_fields({"externalId": self.hostname})
            self.matrix = Matrix(self.matrix_address, self.hostname, self.username, self.dir, client, os.getuid(), os.getgid())
            if len(matrix_item) == 0:
                self.matrix.config_matrix()
                self.matrix.upload_configs(pod_client)
            else:
                # TODO: find a way to download files
                print("Need to download config files")

            # run matrix and register
            self.matrix.run_matrix(network_name)
            self.matrix.register_user(self.password, pod_client)

        # retrieve matrix account and token
        items = pod_client.search_by_fields({"externalId": self.username})
        account_item = items[0]
        self.matrix_acc = account_item.displayName
        self.matrix_token = account_item.importJson

        # run whatsapp bridge
        self.mautrix.run_bridge(network_name)

        # create MatrixClient
        self.matrix_client = MatrixClient(self.matrix_address, self.matrix_token)

    def get_receivers(self, room):
        """Fetch message receivers of a room"""
        joined_members = self.matrix_client.get_joined_members(room)
        joined_members = list(joined_members.keys())
        if self.matrix_acc in joined_members: # except the Matrix user
            joined_members.remove(self.matrix_acc)
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
        time.sleep(2) # wait for whatsappbot's reply
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
        account = Account(externalId=user_id, displayName=profile["displayname"], service="whatsapp")
        person = Person(firstName=profile["displayname"])
        pod_client.create(person)
        account.add_edge("belongsTo", person)
        account.add_edge("organization", self.wa_network)
        return account

    def create_message_channel(self, room_id):
        """Create MessageChannel item for each room, link with Account items"""
        room_state = self.matrix_client.get_room_state(room_id)
        room_name = None
        room_topic = None
        for s in room_state:
            if s["type"] == "m.room.name":
                room_name = s["content"]["name"]
            if s["type"] == "m.room.topic":
                room_topic = s["content"]["topic"]
        message_channel = MessageChannel(externalId=room_id, name=room_name, topic=room_topic)
        member_accounts = self.get_receivers(room_id)
        for m in member_accounts:
            message_channel.add_edge("receiver", m) # link with Account
        return message_channel

    def create_message(self, event, room):
        """Create Message item for each event, link with MessageChannel and Account"""
        message = Message(externalId=event["event_id"], content=event["content"]["body"], dateSent=event["origin_server_ts"], service="whatsapp")
        if not event["sender"] in self.acc_idx:
            account = self.create_account(event["sender"])
            self.acc_idx[event["sender"]] = account
            pod_client.create(account)
            pod_client.create_edges(account.get_all_edges())
        if not room in self.msgchan_idx:
            msgchan = self.create_message_channel(room)
            self.msgchan_idx[room] = msgchan
            pod_client.create(msgchan)
        message.add_edge("messageChannel", self.msgchan_idx[room]) # link with MessageChannel
        message.add_edge("sender", self.acc_idx[event["sender"]]) # link with Account

        # Link with Message to create a thread
#         if "m.relates_to" in event["content"]:
#             message.add_edge("replyTo", self.msg_idx[event["content"]["m.relates_to"]["m.in_reply_to"]["event_id"]])

        # Create media item and link with Message
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
        pod_client.upload_file(binaries)

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
                self.acc_idx[n] = account
                pod_client.create(account) # upload to Pod
                pod_client.create_edges(account.get_all_edges())

    def import_all_messagechannels(self, all_rooms):
        """Import all created MessageChannel items to Pod"""
        for r in all_rooms:
            if not r in self.msgchan_idx:
                message_channel = self.create_message_channel(r)
                self.msgchan_idx[r] = message_channel
                pod_client.create(message_channel) # upload to Pod
                pod_client.create_edges(message_channel.get_all_edges())

    def import_all_messages(self, next_batch):
        """Import all created Message items to Pod"""
        sync_events = self.matrix_client.sync_events(next_batch)
        # messages from joined rooms
        joined_rooms = sync_events["rooms"]["join"]
        for r in joined_rooms:
            room_events = sync_events["rooms"]["join"][r]["timeline"]["events"]
            for e in room_events:
                if not e["event_id"] in self.msg_idx and e["type"] == "m.room.message":
                    message = self.create_message(e, r)
                    self.msg_idx[e["event_id"]] = message
                    pod_client.create(message) # upload to Pod
                    pod_client.create_edges(message.get_all_edges())
        return sync_events["next_batch"]

    def run(self, importer_run, pod_client=None, verbose=True):
        """This is the main function of WhatsAppImporter, which runs based on the information of importer_run."""
        wa_network = Network(name="WhatsApp")
        pod_client.create(wa_network)

        self.set_matrix_client(pod_client, importer_run, wa_network)
        self.update_run_status(pod_client, importer_run, "running")

        all_rooms = self.matrix_client.get_joined_rooms()
        notified = False
        while not len(all_rooms) > 1: # wait for web authentication
            if not notified:
                self.update_run_status(pod_client, importer_run, "waiting for web authentication")
                print(f"Please login to {self.matrix_address} with username {self.username} and password {self.password}, and invite {self.bot_name} to a new room.")
                notified = True
            time.sleep(10)
            all_rooms = self.matrix_client.get_joined_rooms()

        users = self.get_contacts(all_rooms)
        next_batch = "s9_7_0_1_1_1"
        time.sleep(5)

        while True: # polling for new contacts, chats and messages
            all_rooms = self.matrix_client.get_joined_rooms()

            self.update_progress_message(pod_client, importer_run, "importing contacts", verbose=verbose)
            self.import_all_accounts(all_rooms, users)

            self.update_progress_message(pod_client, importer_run, "importing chats", verbose=verbose)
            self.import_all_messagechannels(all_rooms)

            self.update_progress_message(pod_client, importer_run, "importing messages", verbose=verbose)
            next_batch = self.import_all_messages(next_batch)

            self.update_run_status(pod_client, importer_run, "polling")
            time.sleep(2)