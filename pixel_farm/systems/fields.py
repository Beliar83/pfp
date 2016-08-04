# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#  This module is based on the character statistics system from PARPG

"""This system manages the fields.

.. module:: fields
    :synopsis: Manages the fields
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from __future__ import absolute_import

import yaml

from fife_rpg.systems import Base
from fife_rpg.components.agent import Agent

from pixel_farm.components.field import Field


class Fields(Base):

    "This system manages the fields."

    def __init__(self):
        self.map = None
        self.layer = None
        self.vert_start = None
        self.vert_size = None
        self.horz_start = None
        self.horz_size = None
        self.fields = {}

        # testing
        self.first = True
        field_1 = self.fields["field_1"] = {}
        field_1["map"] = "farm"
        field_1["layer"] = "fields"
        field_1["vert_start"] = -10
        field_1["vert_size"] = 15
        field_1["horz_start"] = -8
        field_1["horz_size"] = 15

    @classmethod
    def register(cls, name="fields"):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the system was registered, False if not.
        """
        return super(Fields, cls).register(name)

    def load_config(self, filepath="fields.yaml"):
        """Loads the config of this system from a yaml file

        Args:

            filepath: The path to the config file
        """
        stream = file(filepath, "r")
        self.fields = yaml.load(stream)["fields"]

    def setup_field(self, field_name, field_data):
        """Sets up a single field

        Args:

            field_name: The identifier of the field

            fields: The data of the field
        """
        agent_c_name = Agent.registered_as
        field_c_name = Field.registered_as
        if self.world.is_identifier_used("%s_0_0" % field_name):
            return

        for i in xrange(field_data["vert_size"]):
            identifier = "%s_border_left_%d" % (field_name, i)
            comp_data = {}
            agent_data = comp_data[agent_c_name] = {}
            agent_data["map"] = field_data["map"]
            agent_data["layer"] = field_data["layer"]
            agent_data["namespace"] = "LPC"
            agent_data["gfx"] = "grass/soil"
            agent_data["rotation"] = 270
            v_pos = field_data["vert_start"] + i
            h_pos = field_data["horz_start"] - 1
            agent_data["position"] = [h_pos, v_pos]
            agent_data["behaviour_type"] = "Base"
            self.world.get_or_create_entity(identifier, comp_data)
            h_pos = field_data["horz_start"] + field_data["horz_size"]
            agent_data["position"] = [h_pos, v_pos]
            agent_data["rotation"] = 90
            identifier = "%s_border_right_%d" % (field_name, i)
            self.world.get_or_create_entity(identifier, comp_data)

        comp_data = {}
        agent_data = comp_data[agent_c_name] = {}
        agent_data["map"] = field_data["map"]
        agent_data["layer"] = field_data["layer"]
        agent_data["namespace"] = "LPC"
        agent_data["gfx"] = "grass/soil"
        agent_data["behaviour_type"] = "Base"

        identifier = "%s_border_top_right" % (field_name)
        v_pos = field_data["vert_start"] - 1
        h_pos = field_data["horz_start"] + field_data["horz_size"]
        agent_data["position"] = [h_pos, v_pos]
        agent_data["rotation"] = 45
        self.world.get_or_create_entity(identifier, comp_data)

        identifier = "%s_border_bottom_right" % (field_name)
        v_pos = field_data["vert_start"] + field_data["vert_size"]
        h_pos = field_data["horz_start"] + field_data["horz_size"]
        agent_data["position"] = [h_pos, v_pos]
        agent_data["rotation"] = 135
        self.world.get_or_create_entity(identifier, comp_data)

        identifier = "%s_border_bottom_left" % (field_name)
        v_pos = field_data["vert_start"] + field_data["vert_size"]
        h_pos = field_data["horz_start"] - 1
        agent_data["position"] = [h_pos, v_pos]
        agent_data["rotation"] = 225
        self.world.get_or_create_entity(identifier, comp_data)

        identifier = "%s_border_top_left" % (field_name)
        v_pos = field_data["vert_start"] - 1
        h_pos = field_data["horz_start"] - 1
        agent_data["position"] = [h_pos, v_pos]
        agent_data["rotation"] = 315
        self.world.get_or_create_entity(identifier, comp_data)

        for i in xrange(field_data["horz_size"]):
            identifier = "%s_border_top_%d" % (field_name, i)
            comp_data = {}
            agent_data = comp_data[agent_c_name] = {}
            agent_data["map"] = field_data["map"]
            agent_data["layer"] = field_data["layer"]
            agent_data["namespace"] = "LPC"
            agent_data["gfx"] = "grass/soil"
            agent_data["rotation"] = 0
            v_pos = field_data["vert_start"] - 1
            h_pos = field_data["horz_start"] + i
            agent_data["position"] = [h_pos, v_pos]
            agent_data["behaviour_type"] = "Base"
            self.world.get_or_create_entity(identifier, comp_data)
            v_pos = field_data["vert_start"] + field_data["vert_size"]
            agent_data["position"] = [h_pos, v_pos]
            agent_data["rotation"] = 180
            identifier = "%s_border_bottom_%d" % (field_name, i)
            self.world.get_or_create_entity(identifier, comp_data)

        for i in xrange(field_data["vert_size"]):
            for j in xrange(field_data["horz_size"]):
                identifier = "%s_%d_%d" % (field_name, i, j)
                if self.world.is_identifier_used(identifier):
                    continue
                comp_data = {}
                agent_data = comp_data[agent_c_name] = {}
                agent_data["map"] = field_data["map"]
                agent_data["layer"] = field_data["layer"]
                agent_data["namespace"] = "LPC"
                agent_data["gfx"] = "soil:01"
                v_pos = field_data["vert_start"] + i
                h_pos = field_data["horz_start"] + j
                agent_data["position"] = [h_pos, v_pos]
                agent_data["behaviour_type"] = "Base"
                field_c_data = comp_data[field_c_name] = {}
                field_c_data["plowed"] = False
                self.world.get_or_create_entity(identifier, comp_data)
        self.world.application.update_agents(field_data["map"])

    def step(self, dt):
        Base.step(self, dt)
        for field_name in self.fields.iterkeys():
            field_data = self.fields[field_name]
            self.setup_field(field_name, field_data)
            for i in xrange(field_data["vert_size"]):
                for j in xrange(field_data["horz_size"]):
                    field_c_name = Field.registered_as
                    agent_c_name = Agent.registered_as
                    identifier = "%s_%d_%d" % (field_name, i, j)
                    entity = self.world.get_entity(identifier)
                    field = getattr(entity, field_c_name)
                    field_agent = getattr(entity, agent_c_name)
                    try:
                        is_plowed = field.plowed
                    except AttributeError:
                        print identifier
                    is_watered = field.water > 0
                    if is_plowed:
                        if is_watered:
                            field_agent.gfx = "plowed_soil_watered"
                        else:
                            field_agent.gfx = "plowed_soil"
                    else:
                        if is_watered:
                            field_agent.gfx = "soil_watered"
                        else:
                            field_agent.gfx = "soil:01"
