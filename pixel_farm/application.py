# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The application for pixel-farm

.. module:: application
    :synopsis: Application for pixel-farm

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import

import PyCEGUI

from fife_rpg import RPGApplicationCEGUI
from fife_rpg import GameSceneView
from fife_rpg.game_scene import SimpleOutliner


class Application(RPGApplicationCEGUI):

    def __init__(self, TDS):
        RPGApplicationCEGUI.__init__(self, TDS)

        self._loadSchemes()

        root = PyCEGUI.WindowManager.getSingleton().createWindow(
            "DefaultWindow", "_MasterRoot")
        root.setMousePassThroughEnabled(True)
        PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(
            root)
        img_mgr = PyCEGUI.ImageManager.getSingleton()
        assert isinstance(img_mgr, PyCEGUI.ImageManager)
        img_mgr.addFromImageFile("images/1x1", "1x1.png")

    def _loadSchemes(self):
        PyCEGUI.SchemeManager.getSingleton().createFromFile(
            "TaharezLook.scheme")
        PyCEGUI.FontManager.getSingleton().createFromFile("DejaVuSans-10.font")
