# This Python file uses the following encoding: utf-8
# This file is part of gnome-tweak-tool.
#
# Copyright (c) 2011 John Stowers
#
# gnome-tweak-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gnome-tweak-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gnome-tweak-tool.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gio, GLib

import gtweak
from gtweak.tweakmodel import TWEAK_GROUP_POWER
from gtweak.widgets import ListBoxTweakGroup, GSettingsComboEnumTweak, GSettingsSwitchTweak, GetterSetterSwitchTweak, build_horizontal_sizegroup, Title, _GSettingsTweak
from gtweak.utils import AutostartFile

class IgnoreLidSwitchTweak(GetterSetterSwitchTweak):
    def __init__(self, **options):
        self._inhibitor_name = "gnome-tweak-tool-lid-inhibitor"
        self._inhibitor_path = "%s/%s" % (gtweak.LIBEXEC_DIR, self._inhibitor_name)

        self._dfile = AutostartFile(None,
                                    autostart_desktop_filename = "ignore-lid-switch-tweak.desktop",
                                    exec_cmd = self._inhibitor_path)

        GetterSetterSwitchTweak.__init__(self, _("Don’t suspend on lid close"), **options)

    def get_active(self):
        return self._sync_inhibitor()

    def set_active(self, v):
        self._dfile.update_start_at_login(v)
        self._sync_inhibitor()

    def _sync_inhibitor(self):
        if (self._dfile.is_start_at_login_enabled()):
            GLib.spawn_command_line_async(self._inhibitor_path)
            return True
        else:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            bus.call('org.gnome.tweak-tool.lid-inhibitor',
                     '/org/gnome/tweak_tool/lid_inhibitor',
                     'org.gtk.Actions',
                     'Activate',
                     GLib.Variant('(sava{sv})', ('quit', [], {})),
                     None, 0, -1, None)
            return False

sg = build_horizontal_sizegroup()

TWEAK_GROUPS = [
    ListBoxTweakGroup(TWEAK_GROUP_POWER,
        Title(_("When Power Button is Pressed"), "", uid="title-theme"),
        GSettingsComboEnumTweak(_("Action"), "org.gnome.settings-daemon.plugins.power", "power-button-action", size_group=sg),
        Title(_("When Laptop Lid is Closed"), "", uid="title-theme"),
        GSettingsComboEnumTweak(_("On Battery Power"),"org.gnome.settings-daemon.plugins.power", "lid-close-battery-action", size_group=sg),
        GSettingsComboEnumTweak(_("When plugged in"),"org.gnome.settings-daemon.plugins.power", "lid-close-ac-action", size_group=sg),
        GSettingsSwitchTweak(_("Suspend even if an external monitor is plugged in"),"org.gnome.settings-daemon.plugins.power", "lid-close-suspend-with-external-monitor", size_group=sg),
        IgnoreLidSwitchTweak(),
    )
]
