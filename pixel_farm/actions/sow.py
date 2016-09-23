"""This module contains the sow action class.

.. module:: sow
    :synopsis: Sow action.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

import fife_rpg
from pixel_farm.components.field import Field
from pixel_farm.components.seed_container import SeedContainer
from .basefieldaction import BaseFieldAction


class Sow(BaseFieldAction):
    """Action to sow fields in a rectangle around the origin

    Attributes
    ----------
    application : fife_rpg.RPGApplication
        The application in which the action was created

    origin : fife_rpg.RPGEntity
        The entity that is the origin point of the rectangle

    rect : fife.Rect
        The rectangle of the fields that should be watered.

    direction : int
        The direction to which the player is facing. (0: Up, 1: Right, 2: Down,
        3: Left)

    seed_container : SeedContainer
        The container for the seeds to sow.

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

    direction : int
        The direction to which the player is facing. (0: Up, 1: Right, 2: Down,
        3: Left)

    seed_container : SeedContainer
        The container for the seeds to sow.

    commands : list
        commands: List of additional commands to execute
    """

    dependencies = [SeedContainer]

    def __init__(self, application, origin, rect, seed_container, direction,
                 commands=None):
        BaseFieldAction.__init__(self, application, origin, rect, direction,
                                 commands)
        self.seed_container = seed_container

    @property
    def can_continue(self):
        """Whether the field action can be continued or not

        Returns
        -------
        bool
        """
        return self.seed_container.seed > 0

    @classmethod
    def can_execute_on(cls, entity):
        """Whether the action can be used on an entity

        Parameters
        ----------
        entity : fife_rpg.RPGEntity
            The entity to check

        Returns
        -------
        bool
        """
        if super().can_execute_on(entity):
            field = getattr(entity, Field.registered_as)
            return field.plowed and not field.has_plant
        return False

    def on_cell_processed(self, cell_x, cell_y):
        """Called after a cell was processed during execution.

        Parameters
        ----------
        cell_x : int
            The x position of the cell

        cell_y : int
            The y position of the cell
        """
        self.seed_container.seed -= 1

    def do_field_action(self, entity):
        """Do an an action to a field

        Parameters
        ----------
        entity : fife_rpg.RPGEntity
            The field entity to do an action on
        """
        if not self.can_continue:
            return
        world = self.application.world
        world.systems.Crops.plant_crop(entity, self.seed_container.crop)

    @classmethod
    def register(cls, name="Sow"):
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
        return super(Sow, cls).register(name)
