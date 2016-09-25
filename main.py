# pylint: disable=unused-import
# pylint: enable=unused-import

from fife.extensions.fife_settings import Setting

from pixel_farm.application import Application
from pixel_farm.mvc import Controller, View

TDS = Setting(app_name="Pixel Farm", settings_file="./settings.xml")


def main():
    app = Application(TDS)
    app.load_components("combined.yaml")
    app.register_components()
    app.load_actions("combined.yaml")
    app.register_actions()
    app.load_systems("combined.yaml")
    app.register_systems()
    app.load_behaviours("combined.yaml")
    app.register_behaviours()
    app.create_world()
    world = app.world
    view = View(app)
    controller = Controller(view, app)
    app.load_maps()
    # world.read_object_db()
    world.import_agent_objects()
    world.load_and_create_entities()
    app.switch_map("farm")
    app.push_mode(controller)
    app.run()

if __name__ == '__main__':
    main()
