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

"""Seed container component and functions

.. module:: seed_container
    :synopsis: Seed container component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base


class SeedContainer(Base):
    """Component for storing seed

    Attributes
    ----------
    max_seed : int
        How much seed the container can hold.

    seed : int
        The amount of seed left in the container.

    crop : str
        The crop that the seed grows into.
    """

    def __init__(self):
        super().__init__(max_seed=int, seed=int, crop=str)

    @classmethod
    def register(cls, name="SeedContainer", auto_register=True):
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
        return super(SeedContainer, cls).register(name, auto_register)
