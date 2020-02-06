"""
EDMC Discord Rich Presence Plugin
:author: 147loch
:date: 06.02.2020
:version: 2.1.20
"""

from os.path import dirname, join
from sys import platform
import sys
import time
import ctypes
if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk
import myNotebook as nb
from config import config
import l10n
import functools
import release

_ = functools.partial(l10n.Translations.translate, context=__file__)

CLIENT_ID = b'522871175420837901'

VERSION = '2.1.20'

this = sys.modules[__name__]

# Add global var for Planet name (landing + around)
planet = '<Hidden>'
landingPad = '2'
#
# From discord-rpc.h
#


class DiscordRichPresence(ctypes.Structure):
    _fields_ = [
        ('state', ctypes.c_char_p),  # max 128 bytes
        ('details', ctypes.c_char_p),  # max 128 bytes
        ('startTimestamp', ctypes.c_int64),
        ('endTimestamp', ctypes.c_int64),
        ('largeImageKey', ctypes.c_char_p),  # max 32 bytes
        ('largeImageText', ctypes.c_char_p),  # max 128 bytes
        ('smallImageKey', ctypes.c_char_p),  # max 32 bytes
        ('smallImageText', ctypes.c_char_p),  # max 128 bytes
        ('partyId', ctypes.c_char_p),  # max 128 bytes
        ('partySize', ctypes.c_int),
        ('partyMax', ctypes.c_int),
        ('matchSecret', ctypes.c_char_p),  # max 128 bytes
        ('joinSecret', ctypes.c_char_p),  # max 128 bytes
        ('spectateSecret', ctypes.c_char_p),  # max 128 bytes
        ('instance', ctypes.c_int8)
    ]


class DiscordJoinRequest(ctypes.Structure):
    _fields_ = [
        ('userId', ctypes.c_char_p),
        ('username', ctypes.c_char_p),
        ('avatar', ctypes.c_char_p)
    ]


def init_discord_rpc():
    discord_rpc_lib = 'discord-rpc.dll'
    if platform == 'darwin':
        discord_rpc_lib = 'libdiscord-rpc.dylib'
    elif platform == 'linux' or platform == 'linux2':
        discord_rpc_lib = 'libdiscord-rpc.so'
    this.discord_rpc = ctypes.cdll.LoadLibrary(join(dirname(__file__), discord_rpc_lib))

    this.ReadyProc = ctypes.CFUNCTYPE(None)
    this.DisconnectedProc = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)  # errorCode, message
    this.ErroredProc = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)  # errorCode, message
    this.JoinGameProc = ctypes.CFUNCTYPE(None, ctypes.c_char_p)  # joinSecret
    this.SpectateGameProc = ctypes.CFUNCTYPE(None, ctypes.c_char_p)  # spectateSecret
    this.JoinRequestProc = ctypes.CFUNCTYPE(None, ctypes.POINTER(DiscordJoinRequest))

    class DiscordEventHandlers(ctypes.Structure):
        _fields_ = [
            ('ready', this.ReadyProc),
            ('disconnected', this.DisconnectedProc),
            ('errored', this.ErroredProc),
            ('joinGame', this.JoinGameProc),
            ('spectateGame', this.SpectateGameProc),
            ('joinRequest', this.JoinRequestProc)
        ]

    this.Discord_Initialize = this.discord_rpc.Discord_Initialize
    this.Discord_Initialize.argtypes = [ctypes.c_char_p, ctypes.POINTER(DiscordEventHandlers), ctypes.c_int,
                                   ctypes.c_char_p]  # applicationId, handlers, autoRegister, optionalSteamId
    this.Discord_Shutdown = this.discord_rpc.Discord_Shutdown
    this.Discord_Shutdown.argtypes = None
    this.Discord_UpdatePresence = this.discord_rpc.Discord_UpdatePresence
    this.Discord_UpdatePresence.argtypes = [ctypes.POINTER(DiscordRichPresence)]
    this.Discord_Respond = this.discord_rpc.Discord_Respond
    this.Discord_Respond.argtypes = [ctypes.c_char_p, ctypes.c_int]  # userid, reply

    this.event_handlers = DiscordEventHandlers(this.ReadyProc(ready),
                                               this.DisconnectedProc(disconnected),
                                               this.ErroredProc(errored),
                                               this.JoinGameProc(joinGame),
                                               this.SpectateGameProc(spectateGame),
                                               this.JoinRequestProc(joinRequest))


#
# Callback handlers
#


def ready():
    print('ready')


def disconnected(errorCode, message):
    print('disconnected', errorCode, message)


def errored(errorCode, message):
    print('errored', errorCode, message)


def joinGame(joinSecret):
    print('joinGame', joinSecret)


def spectateGame(spectateSecret):
    print('spectateGame', spectateSecret)


def joinRequest(request):
    print('joinRequest', request.userId, request.username, request.avatar)


this.presence_state = _('Connecting CMDR Interface').encode('utf-8')
this.presence_details = b''
this.time_start = time.time()


def update_presence():
    presence = DiscordRichPresence()
    if config.getint("disable_presence") == 0:
        presence.state = this.presence_state
        presence.details = this.presence_details
    presence.startTimestamp = int(this.time_start)
    presence.largeImageKey = "ed-logo"
    presence.largeImageText = "Elite Dangerous"
    presence.smallImageKey = "lch-logo"
    presence.smallImageText = "Made by 147loch"
    this.Discord_UpdatePresence(presence)


this.disablePresence = None


def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    this.disablePresence = tk.IntVar(value=config.getint("disable_presence"))
    this.disable_auto_update = tk.IntVar(value=config.getint("edmcdrpc__disable_auto_update"))
    frame = nb.Frame(parent)
    nb.Checkbutton(frame, text="Disable Presence", variable=this.disablePresence).grid(padx=10, sticky=tk.W)
    nb.Checkbutton(frame, text="Disable Auto Updates", variable=this.disable_auto_update).grid(padx=10, pady=5,
                                                                                               sticky=tk.W)
    nb.Label(frame, text='Version %s' % VERSION).grid(padx=10, pady=10, sticky=tk.W)

    this.Release.plugin_prefs(frame)

    return frame


def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('disable_presence', this.disablePresence.get())
    config.set('edmcdrpc__disable_auto_update', this.disable_auto_update.get())
    update_presence()


def plugin_start3(plugin_dir):
    release.Release.plugin_start(plugin_dir)
    return 'dRPC'


def plugin_start(plugin_dir):
    release.Release.plugin_start(plugin_dir)
    return 'dRPC'


def init():
    init_discord_rpc()
    this.Discord_Initialize(CLIENT_ID, this.event_handlers, True, None)
    update_presence()


def plugin_app(parent):
    this.Release = release.Release(VERSION, init)
    return


def plugin_stop():
    this.Discord_Shutdown()


def journal_entry(cmdr, is_beta, system, station, entry, state):
    global planet
    global landingPad
    if entry['event'] == 'StartUp':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        if station is None:
            this.presence_details = _('Flying in normal space').encode('utf-8')
        else:
            this.presence_details = _('Docked at {station}').format(station=station).encode('utf-8')
    elif entry['event'] == 'Location':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        if station is None:
            this.presence_details = _('Flying in normal space').encode('utf-8')
        else:
            this.presence_details = _('Docked at {station}').format(station=station).encode('utf-8')
    elif entry['event'] == 'StartJump':
        this.presence_state = _('Jumping').encode('utf-8')
        if entry['JumpType'] == 'Hyperspace':
            this.presence_details = _('Jumping to system {system}').format(system=entry['StarSystem']).encode('utf-8')
        elif entry['JumpType'] == 'Supercruise':
            this.presence_details = _('Preparing for supercruise').encode('utf-8')
    elif entry['event'] == 'SupercruiseEntry':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        this.presence_details = _('Supercruising').encode('utf-8')
    elif entry['event'] == 'SupercruiseExit':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        this.presence_details = _('Flying in normal space').encode('utf-8')
    elif entry['event'] == 'FSDJump':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        this.presence_details = _('Supercruising').encode('utf-8')
    elif entry['event'] == 'Docked':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        this.presence_details = _('Docked at {station}').format(station=station).encode('utf-8')
    elif entry['event'] == 'Undocked':
        this.presence_state = _('In system {system}').format(system=system).encode('utf-8')
        this.presence_details = _('Flying in normal space').encode('utf-8')
    elif entry['event'] == 'ShutDown':
        this.presence_state = _('Connecting CMDR Interface').encode('utf-8')
        this.presence_details = b''
    elif entry['event'] == 'DockingGranted':
        landingPad = entry['LandingPad']
    elif entry['event'] == 'Music':
        if entry['MusicTrack'] == 'MainMenu':
            this.presence_state = _('Connecting CMDR Interface').encode('utf-8')
            this.presence_details = b''
    # Todo: This elif might not be executed on undocked. Functionality can be improved
    elif entry['event'] == 'Undocked' or entry['event'] == 'DockingCancelled' or entry['event'] == 'DockingTimeout':
        this.presence_details = _('Flying near {station}').format(station=entry['StationName']).encode('utf-8')
    # Planetary events
    elif entry['event'] == 'ApproachBody':
        this.presence_details = _('Approaching {body}').format(body=entry['Body']).encode('utf-8')
        planet = entry['Body']
    elif entry['event'] == 'Touchdown' and entry['PlayerControlled']:
        this.presence_details = _('Landed on {body}').format(body=planet).encode('utf-8')
    elif entry['event'] == 'Liftoff' and entry['PlayerControlled']:
        if entry['PlayerControlled']:
            this.presence_details = _('Flying around {body}').format(body=planet).encode('utf-8')
        else:
            this.presence_details = _('In SRV on {body}, ship in orbit').format(body=planet).encode('utf-8')
    elif entry['event'] == 'LeaveBody':
        this.presence_details = _('Supercruising').encode('utf-8')

    # EXTERNAL VEHICLE EVENTS
    elif entry['event'] == 'LaunchSRV':
        this.presence_details = _('In SRV on {body}').format(body=planet).encode('utf-8')
    elif entry['event'] == 'DockSRV':
        this.presence_details = _('Landed on {body}').format(body=planet).encode('utf-8')
    update_presence()
