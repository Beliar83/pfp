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

"""The model, view and controller classes for pixel-farm

.. module:: application
    :synopsis:  model, view and controller classes

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import

import PyCEGUI
from fife import fife
import fife_rpg
from fife_rpg.game_scene import (GameSceneController, GameSceneView,
                                 GameSceneListener)
from .gui.selection_grid import SelectionGrid

from .components.field import Field
from .helper import get_offset_rect


class Listener(GameSceneListener, fife.IKeyListener):

    def __init__(self, engine, gamecontroller=None):
        GameSceneListener.__init__(self, engine, gamecontroller)
        fife.IKeyListener.__init__(self)

    def activate(self):
        """Makes the listener receive events"""
        GameSceneListener.activate(self)
        self.eventmanager.addKeyListener(self)

    def deactivate(self):
        """Makes the listener receive events"""
        GameSceneListener.deactivate(self)
        self.eventmanager.removeKeyListener(self)

    def mouseMoved(self, event):  # pylint: disable=W0221
        GameSceneListener.mouseMoved(self, event)
        application = self.gamecontroller.application
        point = fife.ScreenPoint(event.getX(), event.getY())
        game_map = application.current_map
        instances = game_map.get_instances_at(
            point,
            game_map.get_layer("fields"))
        self.gamecontroller.selected = None
        if instances:
            instance = instances[0]
            entity = application.world.get_entity(instance.getId())
            if entity.Field:
                self.gamecontroller.selected = entity
                self.gamecontroller.update_selector(instance)

    def keyPressed(self, event):
        pass

    def keyReleased(self, event):
        assert isinstance(event, fife.KeyEvent)
        key = event.getKey().getValue()
        selecteed = self.gamecontroller.selected
        if key == fife.Key.P:
            if selecteed:
                selecteed.Field.plowed = True
        elif key == fife.Key.C:
            if selecteed:
                if not selecteed.Crop and selecteed.Field.plowed:
                    application = self.gamecontroller.application
                    application.world.systems.Crops.plant_crop(selecteed,
                                                               "tomato")
        elif key == fife.Key.W:
            if selecteed:
                selecteed.Field.water += 1
                print selecteed.Field.water
        elif key == fife.Key.S:
            if selecteed:
                selecteed.Field.sun += 1
                print selecteed.Field.sun
        elif key == fife.Key.D:
            if selecteed:
                application = self.gamecontroller.application
                world = application.world
                world.systems.Crops.advance_day()
                identifier = "%s_crop" % selecteed.identifier
                crop = world.get_entity(identifier)
                if crop:
                    print "water %d. sun %d, days %d" % (crop.Crop.water,
                                                         crop.Crop.sun,
                                                         crop.Crop.days)
                    print crop.Crop.stage
        elif key == fife.Key.H:
            if selecteed:
                application = self.gamecontroller.application
                world = application.world
                identifier = "%s_crop" % selecteed.identifier
                crop = world.get_entity(identifier)
                if crop.Crop.ripe:
                    crop.Crop.ripe = False
                    crop.Crop.harvested = True
                    crop.Crop.days = 0
                    crop.Crop.water = 0
                    crop.Crop.sun = 0
        elif key == fife.Key.R:
            self.gamecontroller.rotate_selection(True)


class Controller(GameSceneController):

    def __init__(self, view, application, outliner=None, listener=None):
        listener = listener or Listener(application.engine, self)
        GameSceneController.__init__(
            self, view, application, outliner, listener)
        self.selected = None
        self.selection_direction = 0

    def pump(self, time_delta):
        GameSceneController.pump(self, time_delta)
        self.update_selector()
        self.view.select_grid.update_grid()

    def on_activate(self):
        super(Controller, self).on_activate()
        PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(
            self.view.ingame)
        self.view.select_grid.recreate_grid(3, 3, True)

    def rotate_selection(self, right):
        """Rotate the selection in the given direction

        right : bool
            True to rotate right, False to roate left
        """
        if right:
            if self.selection_direction < 3:
                self.selection_direction += 1
            else:
                self.selection_direction = 0
        else:
            if self.selection_direction > 0:
                self.selection_direction -= 1
            else:
                self.selection_direction = 3

    def update_selector(self, instance=None):
        application = self.application
        game_map = application.current_map
        #: :type game_map: fife_rpg.Map
        camera = game_map.camera
        #: :type camera: fife.Camera
        generic = fife.GenericRenderer.getInstance(camera)
        inst_renderer = fife.InstanceRenderer.getInstance(camera)

        generic.setPipelinePosition(inst_renderer.getPipelinePosition() + 1)
        generic.removeAll("Selector")
        generic.setEnabled(True)
        generic.activateAllLayers(game_map.fife_map)
        if instance is None:
            if self.selected:
                instance = self.selected.FifeAgent.instance
            else:
                return
        #: :type instance: fife.Instance
        mouse_cell = self.view.select_grid.mouse_cell
        cell_rect = self.view.select_grid.cell_rect
        #: :type cell_rect: PyCEGUI.Rectf
        mouse_pos = fife.Point(*mouse_cell)
        rect = fife.Rect(int(cell_rect.d_min.d_x),
                         int(cell_rect.d_min.d_y),
                         int(cell_rect.getWidth()),
                         int(cell_rect.getHeight()))
        rect = get_offset_rect(rect, mouse_pos)
        if self.selection_direction == 1:
            rect = fife.Rect(rect.bottom() * -1,
                             rect.getX(),
                             rect.getH(),
                             rect.getW())
        elif self.selection_direction == 2:
            rect = fife.Rect(rect.right() * -1,
                             rect.bottom() * -1,
                             rect.getW(),
                             rect.getH())
        elif self.selection_direction == 3:
            rect = fife.Rect(rect.getY(),
                             rect.right() * -1,
                             rect.getH(),
                             rect.getW())
        start_row = rect.getY()
        start_col = rect.getX()
        width = rect.getW() + 1
        height = rect.getH() + 1

        world = application.world
        #: :type world: fife_rpg.RPGWorld
        for row in xrange(start_row, start_row + height):
            for col in xrange(start_col, start_col + width):
                location = instance.getLocation()
                #: :type location: fife.Location
                coords = location.getLayerCoordinates()
                #: :type coords: fife.Point3D
                coords.x += col
                coords.y += row
                location.setLayerCoordinates(coords)
                offset_instances = camera.getMatchingInstances(location)
                if len(offset_instances) == 0:
                    continue
                offset_instance = offset_instances[0]
                entity = world.get_entity(offset_instance.getId())
                if not entity or not getattr(entity, Field.registered_as):
                    continue
                quad_node1 = fife.RendererNode(offset_instance)
                quad_node1.setRelative(fife.Point(-16, -16))
                quad_node2 = fife.RendererNode(offset_instance)
                quad_node2.setRelative(fife.Point(-16, 16))
                quad_node3 = fife.RendererNode(offset_instance)
                quad_node3.setRelative(fife.Point(16, 16))
                quad_node4 = fife.RendererNode(offset_instance)
                quad_node4.setRelative(fife.Point(16, -16))
                generic.addLine("Selector", quad_node1, quad_node2,
                                255, 255, 255)
                generic.addLine("Selector", quad_node2, quad_node3,
                                255, 255, 255)
                generic.addLine("Selector", quad_node3, quad_node4,
                                255, 255, 255)
                generic.addLine("Selector", quad_node4, quad_node1,
                                255, 255, 255)


class View(GameSceneView):

    def __init__(self, application):
        super(View, self).__init__(application)
        #: :type ingame: PyCEGUI.DefaultWindow
        ingame = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
            "ingame.layout")
        self.ingame = ingame
        #: :type select_grid: PyCEGUI.GridLayoutContainer
        select_grid = ingame.getChild("SelectGrid")
        self.select_grid = SelectionGrid(select_grid)
