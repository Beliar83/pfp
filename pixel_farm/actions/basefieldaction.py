"""This module contains the field action class.

.. module:: Field
    :synopsis: Field action

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife

import fife_rpg
from fife_rpg.actions.base import BaseAction
from pixel_farm.components.field import Field


class BaseFieldAction(BaseAction):
    """Base action for actions done to fields around a rectangle

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

    commands : list
        commands: List of additional commands to execute
    """

    dependencies = [Field]

    def __init__(self, application, origin, rect, direction, commands=None):
        super().__init__(application, commands)
        self.origin = origin
        self.rect = rect
        self.direction = direction
