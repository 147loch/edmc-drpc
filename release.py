if sys.version_info[0] == 3:
    import tkinter as tk
else:
    import Tkinter as tk
from config import config
import requests
import os
import zipfile
import StringIO
import shutil


class Release:

    plugin_dir = None

    def __init__(self, version):
        self.__version = version
        self.__disable_auto_updates = tk.IntVar(value=config.getint("edmcdrpc__disable_auto_update"))
        self.__plugin_prefs_text = None
        self.__latest = None
        self.release_pull()
        self.release_update()
        pass

    def release_pull(self):
        r = requests.get("https://api.github.com/repos/147loch/edmc-drpc/releases/latest")
        if r.status_code == requests.codes.ok:
            self.__latest = r.json()

    def release_update(self):
        if self.__latest is not None:
            current = Release.version2number(self.__version)
            release = Release.version2number(self.__latest.get('tag_name'))

            if current < release:
                if self.__disable_auto_updates.get() == 0:
                    self.installer()
                else:
                    self.__plugin_prefs_text = "New version available: {}. Please update now.".format(
                        self.__latest.get('tag_name')
                    )

    def plugin_prefs(self, frame):
        if self.__plugin_prefs_text is not None:
            nb.Label(frame, text=self.__plugin_prefs_text).grid(padx=10, pady=10, sticky=tk.W)

    def prefs_changed(self):
        self.release_pull()
        self.release_update()

    def installer(self):
        tag_name = self.__latest.get('tag_name')
        new_plugin_dir = os.path.join(os.path.dirname(Release.plugin_dir), "edmc-sagi-{}".format(tag_name))

        if not os.path.isdir(new_plugin_dir):
            try:
                download = requests.get("https://github.com/147loch/edmc-drpc/archive/{}.zip".format(tag_name),
                                        stream=True)
                z = zipfile.ZipFile(StringIO.StringIO(download.content))
                z.extractall(os.path.dirname(Release.plugin_dir))
            except:
                self.__plugin_prefs_text = "Plugin update failed, please do it manually"

            try:
                shutil.rmtree(Release.plugin_dir)
            except:
                self.__plugin_prefs_text = "Could not delete the old version, deleting the new one"
                shutil.rmtree(new_plugin_dir)

            self.__plugin_prefs_text = "Update installed, please restart the app now."
            Release.plugin_dir = new_plugin_dir
        else:
            self.__plugin_prefs_text = "Plugin update failed, please do it manually"

    @staticmethod
    def version2number(version):
        major, minor, patch = version.split('.')
        return (int(major) * 1000000) + (int(minor) * 1000) + int(patch)

    @classmethod
    def plugin_start(cls, plugin_dir):
        cls.plugin_dir = plugin_dir