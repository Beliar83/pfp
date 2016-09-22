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

"""This system manages the crops on the fields.

.. module:: crop_growth
    :synopsis: Manages the crops on the fields
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife_rpg.components.agent import Agent
from fife_rpg.systems import Base
from pixel_farm.components.crop import Crop, add_days
from pixel_farm.components.field import Field


class Crops(Base):

    "This system manages the crops on the fields."

    def __init__(self):
        Base.__init__(self)
        self.fruits = {}
        # Just for testing
        tomato = {}
        stages = []
        stage = {}
        stage["min_days"] = 3
        stage["water"] = 4
        stage["sun"] = 4
        stage["gfx"] = "tomato_1"
        stage["namespace"] = "LPC"
        stages.append(stage)
        stage = {}
        stage["min_days"] = 2
        stage["water"] = 4
        stage["sun"] = 5
        stage["gfx"] = "tomato_2"
        stage["namespace"] = "LPC"
        stages.append(stage)
        stage = {}
        stage["min_days"] = 2
        stage["water"] = 3
        stage["sun"] = 6
        stage["gfx"] = "tomato_3"
        stage["namespace"] = "LPC"
        stages.append(stage)
        stage = {}
        stage["min_days"] = 2
        stage["water"] = 0
        stage["sun"] = 0
        stage["gfx"] = "tomato_4"
        stage["namespace"] = "LPC"
        stages.append(stage)
        stage = {}
        stage["min_days"] = 2
        stage["water"] = 0
        stage["sun"] = 0
        stage["gfx"] = "tomato_5"
        stage["namespace"] = "LPC"
        stages.append(stage)
        tomato["stages"] = stages
        tomato["ripe"] = 3
        tomato["harvested"] = 4
        tomato["regrows"] = 2
        self.fruits["tomato"] = tomato

    @classmethod
    def register(cls, name="Crops"):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered

        Returns:
            True if the system was registered, False if not.
        """
        return super(Crops, cls).register(name)

    def add_fruit(self, identifier, fruit_data):
        """Adds a fruit to the system"""
        if identifier not in self.fruits:
            self.fruits[identifier] = fruit_data

    def plant_crop(self, field, fruit):
        """pPant a crop on a field

        Args:

            field: Name of the field or an entity

            fruit: Name of the fruit
        """
        if isinstance(field, str):
            field = self.world.get_entity(field)
        field_comp = getattr(field, Field.registered_as)
        if field_comp.has_plant:
            return
        fruit_data = self.fruits[fruit]
        stage_data = fruit_data["stages"][0]
        comp_data = {}
        agent_data = comp_data["Agent"] = {}
        agent_data["gfx"] = stage_data["gfx"]
        if "namespace" in stage_data:
            agent_data["namespace"] = stage_data["namespace"]
        agent_data["map"] = field.Agent.map
        agent_data["layer"] = "crops"
        agent_data["position"] = field.Agent.position
        agent_data["behaviour_type"] = "Base"
        crop_data = comp_data["Crop"] = {}
        crop_data["fruit_id"] = "tomato"
        crop_data["field_id"] = field.identifier
        identifier = "%s_crop" % field.identifier
        self.world.get_or_create_entity(identifier, comp_data)
        field_comp.has_plant = True

    def advance_day(self):
        """Advance all crops by one day"""
        entities = getattr(self.world[...], Crop.registered_as)
        for entity in entities:
            crop = getattr(entity, Crop.registered_as)
            add_days(crop, 1)
            field_entity = self.world.get_entity(crop.field_id)
            field = getattr(field_entity,  Field.registered_as)
            crop.water += field.water
            field.water = 0
            crop.sun += field.sun
            field.sun = 0

    def step(self, dt):
        Base.step(self, dt)
        for agent, crop in self.world.components.join(Agent.registered_as,
                                                      Crop.registered_as):
            fruit_data = self.fruits[crop.fruit_id]
            stage_data = fruit_data["stages"][crop.stage]
            if crop.harvested:
                if crop.days > 0:
                    if "regrows" in fruit_data:
                        crop.harvested = False
                        regrows = fruit_data["regrows"]
                        crop.stage = regrows
                        stage_data = fruit_data["stages"][regrows]
                else:
                    harvested = fruit_data["harvested"]
                    crop.stage = harvested
                    stage_data = fruit_data["stages"][harvested]
            elif (crop.stage >= len(fruit_data["stages"]) - 1 or
                    crop.ripe):
                pass
            elif (crop.days >= stage_data["min_days"] and
                  crop.water >= stage_data["water"] and
                  crop.sun >= stage_data["sun"]):
                crop.sun = 0
                crop.water = 0
                crop.days = 0
                crop.stage += 1
                stage_data = fruit_data["stages"][crop.stage]
                if crop.stage == fruit_data["ripe"]:
                    crop.ripe = True
            agent.gfx = stage_data["gfx"]
            if "namespace" in stage_data:
                agent.namespace = stage_data["namespace"]
