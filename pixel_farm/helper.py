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
    start_pos_x = int(rect.getX() - mouse_pos.getX())
    start_pos_y = int(rect.getY() - mouse_pos.getY())
    ret_rect = fife.Rect(start_pos_x, start_pos_y, rect.getW(), rect.getH())
    return ret_rect


def get_instances_at_offset(camera, instance, y_pos, x_pos):
    """Returns all instances at the offset position from the instance

    Parameters
    ----------
    instance : fife.Instance
        The origin instance
    y_pos : int
        The y offset from the instance
    x_pos : int
        The x offseet from the instance

    Returns
    -------
    list[fife.Instance]
        The instances at the offset position
    """
    location = instance.getLocation()
    coords = location.getLayerCoordinates()
    coords.x += x_pos
    coords.y += y_pos
    location.setLayerCoordinates(coords)
    offset_instances = camera.getMatchingInstances(location)
    return offset_instances


def get_rotated_cell_offset_coord(y_pos, x_pos, direction):
    """Returns the cell offset coordinate rotated to match the direction.

    Parameters
    ----------
    y_pos : number
        The original y position.
    x_pos : number
        The original x position.
    direction : int
        The direction to rotate to. Origin position is 0 (north) and goes
        clockwise (east=1, south=2, west=3)

    Returns
    -------
    tuple of numbers
        The modified coordinates
    """
    if direction == 1:
        return x_pos, y_pos * -1
    elif direction == 2:
        return y_pos * -1, x_pos * -1
    elif direction == 3:
        return x_pos * -1, y_pos
    return y_pos, x_pos


def get_rotated_rect(self, rect, direction):
    """Calculates the rectangle rotated to the given direction.

    The original rectangle is assumed to be pointing up.

    Parameters
    ----------
    rect : fife.Rect
    direction : int
        The direction to be rotated to. (0: Up, 1: Right, 2: Down, 3: Left)

    Returns
    -------
    fife.Rect
        The rotated rectangle
    """
    if direction == 1:
        rect = fife.Rect((rect.bottom() - 1) * -1,
                         rect.getX(),
                         rect.getH(),
                         rect.getW())
    elif direction == 2:
        rect = fife.Rect((rect.right() - 1) * -1,
                         (rect.bottom() - 1) * -1,
                         rect.getW(),
                         rect.getH())
    elif direction == 3:
        rect = fife.Rect(rect.getY(),
                         (rect.right() - 1) * -1,
                         rect.getH(),
                         rect.getW())
    return rect


def sweep_yield(rect, yield_center=True):
    """Yields each coordinate in the rectangle starting from the leftmost
    centre column and goes around clockwise. The rectangle is processed
    per column and from left to right and bottom to top for the top half
    and from right to left and top to bottom for the bottom half of the
    rectangle.

    Parameters
    ----------
    rect : fife.Rect
        A rectangle with the coordinates to be yielded

    Yields
    ------
    y_pos : int
        The vertical position
    x_pos : int
        The horizontal position
    yield_center : bool
        Whether to include the center coordinates(0,0) or not.
    """
    x_start = rect.getX()
    x_end = rect.right()
    y_start = rect.bottom() - 1
    y_end = rect.getY() - 1
    if y_end < 0 and y_start > 0 or y_start < 0 and y_end > 0:
        for x in range(x_start, x_end, 1):
            for y in range(0, y_end, -1):
                if y == 0 and x == 0:
                    continue
                yield y, x
        for x in range(x_end - 1, x_start - 1, -1):
            for y in range(1, y_start + 1, 1):
                yield y, x
    else:
        for x in range(x_start, x_end, 1):
            for y in range(y_start, y_end, -1):
                if y == 0 and x == 0:
                    continue
                yield y, x
