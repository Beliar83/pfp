"""This module contains the field action class.

.. module:: Field
    :synopsis: Field action

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from abc import ABCMeta, abstractmethod

import six
from fife import fife

import fife_rpg
from fife_rpg.actions.base import BaseAction
from pixel_farm.components.field import Field
from pixel_farm.helper import (sweep_yield, get_rotated_cell_offset_coord,
                               get_instances_at_offset)


class BaseFieldAction(six.with_metaclass(ABCMeta, BaseAction)):
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

    @property
    @abstractmethod
    def can_continue(self):
        """Whether the field action can be continued or not

        Returns
        -------
        bool
        """

    @abstractmethod
    def do_field_action(self, entity):
        """Do an an action to a field

        Parameters
        ----------
        entity : fife_rpg.RPGEntity
            The field entity to do an action on
        """

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
            y_pos, x_pos = get_rotated_cell_offset_coord(
                y, x, self.direction)
            instances = get_instances_at_offset(
                self.application.current_map.camera,
                origin_instance, y_pos, x_pos)
            for instance in instances:
                entity = world.get_entity(instance.getId())
                if getattr(entity, Field.registered_as):
                    self.do_field_action(entity)
            if not self.can_continue:
                break
        super().execute()
