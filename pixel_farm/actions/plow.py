"""This module contains the plow action class.

.. module:: plow
    :synopsis: Plow action.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

import fife_rpg
from pixel_farm.components.field import Field
from .basefieldaction import BaseFieldAction


class Plow(BaseFieldAction):
    """Action to plow fields in a rectangle around the origin

    Attributes
    ----------
    application : fife_rpg.RPGApplication
        The application in which the action was created

    origin : fife_rpg.RPGEntity
        The entity that is the origin point of the rectangle

    rect : fife.Rect
        The rectangle of the fields that should be plowed.

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
        The rectangle of the fields that should be plowed.

    direction : int
        The direction to which the player is facing. (0: Up, 1: Right, 2: Down,
        3: Left)

    commands : list
        commands: List of additional commands to execute
    """

    def __init__(self, application, origin, rect, direction, commands=None):
        BaseFieldAction.__init__(self, application, origin, rect, direction,
                                 commands)

    @property
    def can_continue(self):
        """Whether the field action can be continued or not

        Returns
        -------
        bool
        """
        return True

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
        if super().can_execute_on(entity):
            field = getattr(entity, Field.registered_as)
            return not field.plowed
        return False

    def do_field_action(self, entity):
        """Do an an action to a field

        Parameters
        ----------
        entity : fife_rpg.RPGEntity
            The field entity to do an action on
        """
        field = getattr(entity, Field.registered_as)
        field.plowed = True

    @classmethod
    def register(cls, name="Plow"):
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
        return super(Plow, cls).register(name)
