from flask import render_template, url_for, Blueprint, request
from flask_socketio import emit, join_room, leave_room
from random import randint
from .extensions import socketio

WELCOME_MESSAGE = " has entered the room..."

views = Blueprint('index', __name__)

messages = {}
users = {}
usernames = [
    "TacoNinja42",
    "PixelPirate",
    "WaffleWizard",
    "BananaDrama",
    "CheeseChariot",
    "SockPhilosopher",
    "NapQueen",
    "PizzaWhisperer",
    "CloudPuncher",
    "DiscoPickle",
    "KoalaTea",
    "SnackAttack",
    "PajamaGuru",
    "BurritoBasher",
    "JellyJuggler",
    "CouchCommando",
    "PuddingPirate",
    "NoodleNinja",
    "QuackMaster",
    "ZombieZucchini"
]


def save_message(room: str, username: str, message: str, system_message: bool) -> str:
    """ takes message information and saves it to dictionary

    ARGS
    --------------------------------------------------------
    room: room message belongs in
    username: username of sender
    message: message sent by sender
    system_message: a T or F value to determine if message is user created

    RETURNS
    ---------------------------------------------------------
    no return
    """
    new_log = {"system-message": system_message, "username": username, "message": message}
    messages[room] = messages.get(room, [])
    messages[room].append(new_log)
    return new_log


def generate_message(room: str, username: str, message: str = WELCOME_MESSAGE, system_message: bool = False) -> str:
    """ takes message information and saves it to appropriate mapping in dictionary then returns a auto
    formatted message

    ARGS
    -------------------------------------------------------
    room: room message belongs in
    username: username of sender
    message: message sent by sender (default of WELCOME MESSAGE)
    system_message: A T or F value to determine if message is not user created

    RETURNS
    --------------------------------------------------------
    dictionary with three key value pairs
        server-message: boolean
        username: string username
        message: string message content
    """
    print(system_message)
    return save_message(room, username, message, system_message)


@views.route("/")
def index():
    return render_template('index.html')


@socketio.on("connect")
def connect():
    """ first event handler when client connects to server, generates a username and maps to session id,
    automatically places client in chat room 1, loads previous messages from chat room, sets client context to room
    '1', saves welcome message to cache and generates a formatted string to use for client-message.

    EVENTS
    ---------------------------------------------------------------------------
        1) join-room (sets room state to 1 on client side)
        2) load-messages (populates client document with previous messages)
        3) client-message (sends new message to all clients in room and populates their documents with it)
    """
    username = usernames[randint(0, len(usernames) - 1)]
    users[request.sid] = username

    room = "1"
    prev_messages = messages.get("1", None)

    join_room(room)

    emit("join-room", room, to=request.sid)
    emit("load-messages", prev_messages, to=request.sid)

    packaged_message = generate_message(room, users[request.sid], system_message=True)
    emit("client-message", packaged_message, to=room)


@socketio.on("change-room")
def change_room(change_room_data: dict):
    """ change room event handler, parses event data, loads previous messages from new chat room, removes old room
    from client context and sets new room, saves welcome message to cache and generates a formatted string to use
    for client-message.

    ARGS
    ----------------------------------------------------------
    change_room_data: a dictionary containing 2 key, value pairs
        old-room: clients old room
        new-room: clients new room

    EVENTS
    ------------------------------------------------------------
        1) join-room (sets room state to 1 on client side)
        2) load-messages (populates client document with previous messages)
        3) client-message (sends new message to all clients in room and populates their documents with it)
    """

    old_room = change_room_data["old-room"]
    new_room = change_room_data["new-room"]
    prev_messages = messages.get(new_room, None)

    leave_room(old_room)
    join_room(new_room)

    emit("join-room", new_room, to=request.sid)
    emit("load-messages", prev_messages, to=request.sid)

    packaged_message = generate_message(new_room, users[request.sid], system_message=True)
    emit("client-message", packaged_message, to=new_room)


@socketio.on("server-message")
def server_message(input_data):
    """ server message"""
    system_message = input_data["system-message"]
    room = input_data["room"]
    message = input_data["message"]

    packaged_message = generate_message(room, users[request.sid], message, system_message)

    socketio.emit('client-message', packaged_message, to=room)

