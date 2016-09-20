"""This module contains the water action class.

.. module:: water
    :synopsis: Watering action.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

import fife_rpg
from pixel_farm.components.water_container import WaterContainer
from pixel_farm.helper import (sweep_yield, get_rotated_cell_offset_coord,
                               get_instances_at_offset)
from .basefieldaction import BaseFieldAction


class Water(BaseFieldAction):
    """Action to water fields in a rectangle around the origin

    Attributes
    ----------
    application : fife_rpg.RPGApplication
        The application in which the action was created

    origin : fife_rpg.RPGEntity
        The entity that is the origin point of the rectangle

    rect : fife.Rect
        The rectangle of the fields that should be watered.

    container : WaterContainer
        The container used for watering.

    direction : int
        The direction to which the player is facing. (0: Up, 1: Right, 2: Down,
        3: Left)

    commands : list
        commands: List of additional commands to execute

    Parameters
    ---------
    application : fife_rpg.RPGApplication
        The application in which the action was created

    origin : fife_rpg.RPGEntity
        The entity that is the origin point of the rectangle

    rect : fife.Rect
        The rectangle of the fields that should be watered.

    container : WaterContainer
        The container used for watering.
        
    direction : int
        The direction to which the player is facing. (0: Up, 1: Right, 2: Down, 
        3: Left)

    commands : list
        commands: List of additional commands to execute
    """

    dependencies = [WaterContainer]

    def __init__(self, application, origin, rect, container, direction,
                 commands=None):
        super().__init__(application, origin, rect, direction, commands)
        self.container = container

    def execute(self):
        """Execute the action

        Raises
        ------
        fife_rpg.exceptions.NoSuchCommandError
            If a command is detected that is not registered.
        """

        world = self.application.world
        origin_instance = self.origin.FifeAgent.instance
        if self.rect.getH() == 1 and self.rect.getW() == 1:
            fields = ((0, 0),)
        else:
            fields = sweep_yield(self.rect, False)
        for y, x in fields:
            if self.container.water == 0:
                break
            if self.container.water < -1:
                water = -1  # Just to be on the safe side
            y_pos, x_pos = get_rotated_cell_offset_coord(
                y, x, self.direction)
            world = self.application.world
            instances = get_instances_at_offset(
                self.application.current_map.camera,
                origin_instance, y_pos, x_pos)
            for instance in instances:
                entity = world.get_entity(instance.getId())
                if entity.Field:
                    entity.Field.water += 1
                    self.container.water -= 1
        super().execute()

    @classmethod
    def register(cls, name="Water"):
        """Registers the class as an action

        Parameters
        ----------
        name : str
            The name under which the class should be registered

        Returns
        -------
        bool
            True if the action was registered, False if not.
        """
        return super(Water, cls).register(name)
