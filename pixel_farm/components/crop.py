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

"""Crop component and functions

.. module:: crop
    :synopsis: Crop component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import

from fife_rpg.components.base import Base
from .field import Field


class Crop(Base):

    """Component that defines crop data

    Fields:

        fruit_id: The identifier of the fruit

        water: The amount of water the crop has received

        sun: The amount of sun the crop has received

        days: The number of days the crop has been in the current stage

        stage: The stage the crop is currently at.

        ripe: True if crop is ripe

        harvested: True if crop has been harvested

        field_id: The identifier of the field the crop is on.

    """

    dependencies = [Field]

    def __init__(self):
        Base.__init__(self, fruit_id=str, water=int, sun=int, days=int,
                      stage=int, ripe=bool, harvested=bool, field_id=str)

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        return fields

    @classmethod
    def register(cls, name="Crop", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered

            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return super(Crop, cls).register(name, auto_register)


def add_water(crop, water=1):
    """Adds the specified amount of water to the crop"""
    crop.water += water


def add_sun(crop, sun=1):
    """Adds the specified amount of sun to the crop"""
    crop.sun += sun


def add_days(crop, days=1):
    """Adds the specified amount of days to the crop"""
    crop.days += days
