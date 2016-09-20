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

"""Tool component and functions

.. module:: tool
    :synopsis: Tool container component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.base import Base


class Tool(Base):
    """A component for tools

    Attributes
    ----------
    v_reach : int
        The vertical reach of the tool.
    h_reach : int
        The horizontal reach of the tool.
    reach_behind : bool
        If the tool can reach behind the user during using it.
    tool_type : str
        The type of the tool.
    """

    def __init__(self):
        Base.__init__(self, v_reach=int, h_reach=int, reach_behind=bool,
                      tool_type=str)

    @classmethod
    def register(cls, name="Tool", auto_register=True):
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
        return super(Tool, cls).register(name, auto_register)
