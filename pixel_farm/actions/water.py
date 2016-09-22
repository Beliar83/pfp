"""This module contains the water action class.

.. module:: water
    :synopsis: Watering action.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

import fife_rpg
from pixel_farm.components.field import Field
from pixel_farm.components.water_container import WaterContainer
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

    @property
    def can_continue(self):
        """Whether the field action can be continued or not

        Returns
        -------
        bool
        """
        return self.container.water != 0

    def can_execute_on(self, entity):
        """Whether the action can be used on an entity

        Parameters
        ----------
        entity : fife_rpg.RPGEntity
            The entity to check

        Returns
        -------
        bool
        """
        return super().can_execute_on(entity)

    def on_cell_processed(self, cell_x, cell_y):
        """Called after a cell was processed during execution.

        Parameters
        ----------
        cell_x : int
            The x position of the cell

        cell_y : int
            The y position of the cell
        """
        self.container.water -= 1
        if self.container.water < -1:
            water = -1  # Just to be on the safe side

    def do_field_action(self, entity):
        """Do an an action to a field

        Parameters
        ----------
        entity : fife_rpg.RPGEntity
            The field entity to do an action on
        """
        field = getattr(entity, Field.registered_as)
        if not self.can_continue:
            return
        field.water += 1

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
