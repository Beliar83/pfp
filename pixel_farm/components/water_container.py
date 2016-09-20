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

"""Water container component and functions

.. module:: water_container
    :synopsis: Water container component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base


class WaterContainer(Base):
    """Component for storing water

    Attributes
    ----------
    max_water : int
        How much water the container can hold.

    water : int
        The amount of water left in the container.
    """

    def __init__(self):
        Base.__init__(self, max_water=int, water=int)

    @classmethod
    def register(cls, name="WaterContainer", auto_register=True):
        """Registers the class as a component

        Parameters
        ----------
        name : str
            The name under which the class should be registered

        auto_register : bool
            This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns
        -------
        bool
            True if the component was registered, False if not.
        """
        return super(WaterContainer, cls).register(name, auto_register)
