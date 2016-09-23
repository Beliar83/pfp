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

import PyCEGUI
from fife import fife

from fife_rpg.game_scene import (GameSceneController, GameSceneView,
                                 GameSceneListener)
from fife_rpg.helpers import Enum
from pixel_farm.actions.plow import Plow
from pixel_farm.actions.sow import Sow
from .actions.water import Water
from .components.field import Field
from .components.tool import Tool
from .gui.selection_grid import SelectionGrid
from .helper import get_offset_rect, get_rotated_cell_offset_coord

TOOLS = Enum(("WateringCan", "Plow", "Seed"))


class Listener(GameSceneListener, fife.IKeyListener):
    """Listener for the Controller

    Attributes
    ----------
    gamecontroller : Controller
        The controller for this listener
    """

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
            self.gamecontroller.selected = entity
            self.gamecontroller.update_selector(instance)

    def mousePressed(self, event):
        GameSceneListener.mousePressed(self, event)
        selected = self.gamecontroller.selected
        if selected:
            mouse_cell = self.gamecontroller.view.select_grid.mouse_cell
            cell_rect = self.gamecontroller.view.select_grid.cell_rect
            #: :type cell_rect: PyCEGUI.Rectf
            mouse_pos = fife.Point(*mouse_cell)
            rect = fife.Rect(int(cell_rect.d_min.d_x),
                             int(cell_rect.d_min.d_y),
                             int(cell_rect.getWidth()) + 1,
                             int(cell_rect.getHeight() + 1))
            rect = get_offset_rect(rect, mouse_pos)

            if self.gamecontroller.tool.tool_type == TOOLS.WateringCan:
                world = self.gamecontroller.application.world
                watering_can = world.get_entity("WateringCan")
                water_action = Water(self.gamecontroller.application,
                                     selected, rect,
                                     watering_can.WaterContainer,
                                     self.gamecontroller.selection_direction)
                water_action.execute()
            elif self.gamecontroller.tool.tool_type == TOOLS.Seed:
                world = self.gamecontroller.application.world
                seed_bag = world.get_entity("SeedBag")
                sow_action = Sow(self.gamecontroller.application,
                                 selected, rect, seed_bag.SeedContainer,
                                 self.gamecontroller.selection_direction)
                sow_action.execute()
            elif self.gamecontroller.tool.tool_type == TOOLS.Plow:
                plow_action = Plow(self.gamecontroller.application, selected,
                                   rect,
                                   self.gamecontroller.selection_direction)
                plow_action.execute()

    def keyPressed(self, event):
        pass

    def keyReleased(self, event):
        assert isinstance(event, fife.KeyEvent)
        key = event.getKey().getValue()
        selected = self.gamecontroller.selected
        world = self.gamecontroller.application.world
        if key == fife.Key.P:
            plow = world.get_entity("Plow").Tool
            self.gamecontroller.tool = plow
        elif key == fife.Key.C:
            seed_bag = world.get_entity("SeedBag").Tool
            self.gamecontroller.tool = seed_bag
        elif key == fife.Key.W:
            watering_can = world.get_entity("WateringCan").Tool
            self.gamecontroller.tool = watering_can
        elif key == fife.Key.S:
            if selected:
                selected.Field.sun += 1
                print(selected.Field.sun)
        elif key == fife.Key.D:
            if selected:
                application = self.gamecontroller.application
                world = application.world
                world.systems.Crops.advance_day()
                identifier = "%s_crop" % selected.identifier
                crop = world.get_entity(identifier)
                if crop:
                    print("water %d. sun %d, days %d" % (crop.Crop.water,
                                                         crop.Crop.sun,
                                                         crop.Crop.days))
                    print(crop.Crop.stage)
        elif key == fife.Key.H:
            if selected:
                application = self.gamecontroller.application
                world = application.world
                identifier = "%s_crop" % selected.identifier
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
        self.__tool = None
        self.tool = None

    @property
    def tool(self):
        """The current tool

        Returns
        -------
        Tool
        """
        return self.__tool

    @tool.setter
    def tool(self, tool):
        self.__tool = tool
        if tool is not None:
            self.view.select_grid.recreate_grid(tool.h_reach, tool.v_reach,
                                                tool.reach_behind)
        else:
            self.view.select_grid.recreate_grid(1, 1, False)

    def step(self, time_delta):
        GameSceneController.step(self, time_delta)
        self.update_selector()
        self.view.select_grid.update_grid()

    def on_activate(self):
        super(Controller, self).on_activate()
        # noinspection PyArgumentList
        PyCEGUI.System.getSingleton().getDefaultGUIContext().setRootWindow(
            self.view.ingame)
        if self.tool is None:
            self.tool = self.application.world.get_entity("Plow").Tool

    def rotate_selection(self, right):
        """Rotate the selection in the given direction


        Parameters
        ----------
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

    def get_instances_at_offset(self, instance, y_pos, x_pos):
        """Returns all instances at the offset position from the instance

        Parameters
        ----------
        instance : fife.Instance
            The origin instance
        y_pos : int
            The y offset from the instance
        x_pos : int
            The x offseet from the instance

        Returns
        -------
        list of fife.Instance
            The instances at the offset position
        """
        camera = self.application.current_map.camera

        location = instance.getLocation()
        #: :type location: fife.Location
        coords = location.getLayerCoordinates()
        #: :type coords: fife.Point3D
        coords.x += x_pos
        coords.y += y_pos
        location.setLayerCoordinates(coords)
        offset_instances = camera.getMatchingInstances(location)
        return offset_instances

    def get_instances(self, instance, rect):
        """Returns all the instances near the instance in the given rectangle.

        The (0, 0) position of the rectangle. is where the instance is. It does
        not need to be inside the rectangle.

        Parameters
        ----------
        instance : fife.Instance
            The instance which is the origin point of the rectangle.
        rect : fife.Rect
            The rectangle inside which the instances should be.

        Returns
        -------
        list of fife.Instance
            The instances inside the rectangle
        """

        application = self.application
        start_row = rect.getY()
        start_col = rect.getX()
        width = rect.getW()
        height = rect.getH()
        world = application.world
        #: :type world: fife_rpg.RPGWorld
        instances = []
        for row in range(start_row, start_row + height):
            for col in range(start_col, start_col + width):
                y_pos, x_pos = get_rotated_cell_offset_coord(
                    row, col, self.selection_direction)
                offset_instances = self.get_instances_at_offset(
                    instance, y_pos, x_pos)
                if len(offset_instances) == 0:
                    continue
                offset_instance = offset_instances[0]
                entity = world.get_entity(offset_instance.getId())
                if not entity or not getattr(entity, Field.registered_as):
                    continue
                instances.append(offset_instance)

        return instances

    def update_selector(self, instance=None):
        application = self.application
        game_map = application.current_map
        #: :type game_map: fife_rpg.Map
        camera = game_map.camera
        #: :type camera: fife.Camera

        if instance is None:
            if self.selected:
                instance = self.selected.FifeAgent.instance
            else:
                return
        #: :type instance: fife.Instance
        generic = fife.GenericRenderer.getInstance(camera)
        inst_renderer = fife.InstanceRenderer.getInstance(camera)

        generic.setPipelinePosition(inst_renderer.getPipelinePosition() + 1)
        generic.removeAll("Selector")
        generic.setEnabled(True)
        generic.activateAllLayers(game_map.fife_map)

        mouse_cell = self.view.select_grid.mouse_cell
        cell_rect = self.view.select_grid.cell_rect
        #: :type cell_rect: PyCEGUI.Rectf
        mouse_pos = fife.Point(*mouse_cell)
        rect = fife.Rect(int(cell_rect.d_min.d_x),
                         int(cell_rect.d_min.d_y),
                         int(cell_rect.getWidth()) + 1,
                         int(cell_rect.getHeight() + 1))
        rect = get_offset_rect(rect, mouse_pos)
        width = rect.getW()
        height = rect.getH()

        instances = self.get_instances(instance, rect)
        if len(instances) == 0:
            color = [255, 0, 0]
            if not self.selected.Field:
                return
        elif len(instances) < height * width:
            color = [255, 255, 0]
        else:
            color = [255, 255, 255]
        for offset_instance in instances:
            quad_node1 = fife.RendererNode(offset_instance)
            quad_node1.setRelative(fife.Point(-16, -16))
            quad_node2 = fife.RendererNode(offset_instance)
            quad_node2.setRelative(fife.Point(-16, 16))
            quad_node3 = fife.RendererNode(offset_instance)
            quad_node3.setRelative(fife.Point(16, 16))
            quad_node4 = fife.RendererNode(offset_instance)
            quad_node4.setRelative(fife.Point(16, -16))
            generic.addLine("Selector", quad_node1, quad_node2,
                            *color)
            generic.addLine("Selector", quad_node2, quad_node3,
                            *color)
            generic.addLine("Selector", quad_node3, quad_node4,
                            *color)
            generic.addLine("Selector", quad_node4, quad_node1,
                            *color)

        quad_node1 = fife.RendererNode(instance)
        quad_node1.setRelative(fife.Point(-16, -16))
        quad_node2 = fife.RendererNode(instance)
        quad_node2.setRelative(fife.Point(-16, 16))
        quad_node3 = fife.RendererNode(instance)
        quad_node3.setRelative(fife.Point(16, 16))
        quad_node4 = fife.RendererNode(instance)
        quad_node4.setRelative(fife.Point(16, -16))
        color.append(128)
        generic.addQuad("Selector", quad_node1, quad_node2, quad_node3,
                        quad_node4, *color)


class View(GameSceneView):
    def __init__(self, application):
        super(View, self).__init__(application)
        #: :type ingame: PyCEGUI.DefaultWindow
        # noinspection PyArgumentList
        ingame = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile(
            "ingame.layout")
        self.ingame = ingame
        #: :type select_grid: PyCEGUI.GridLayoutContainer
        select_grid = ingame.getChild("SelectGrid")
        self.select_grid = SelectionGrid(select_grid)
