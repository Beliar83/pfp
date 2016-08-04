"""Various functions and classes

.. module:: helpers
    :synopsis: Various functions and classes

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""

from fife import fife


def get_offset_rect(rect, mouse_pos):
    """Offset the rect so the boundaries are relative to the mouse_pos

    Parameters
    ----------
    rect : fife.Rect
        The original rect
    mouse_pos : fife.Point
        The mouse position
    """
    #: :type rect: fife.Rect
    #: :type mouse_pos: fife.Point
    start_pos_x = int(rect.getX() - mouse_pos.getX())
    start_pos_y = int(rect.getY() - mouse_pos.getY())
    ret_rect = fife.Rect(start_pos_x, start_pos_y, rect.getW(), rect.getH())
    return ret_rect
