from typing import Any
from math import cos, sin
import arcade
from arcade.types import Point2

class AnchorSprite(arcade.Sprite):

    __slots__ = (
        "_anchor",
        "_anchor_position",
    )

    def __init__(
            self,
            path_or_texture: str | bytes | arcade.Texture | None = None, anchor: Point2 | None = None, scale: float | tuple[float | int, float | int] | arcade.Vec2 = 1, center_x: float = 0, center_y: float = 0, angle: float = 0, **kwargs: Any) -> None:
        self._anchor_position: Point2 = (center_x, center_y)
        self._anchor: Point2 | None = anchor
        super().__init__(path_or_texture, scale, center_x, center_y, angle, **kwargs)
    
    @property
    def anchor(self):
        return self._anchor
    
    @anchor.setter
    def anchor(self, anchor: Point2 | None):
        if anchor == self._anchor:
            return
        
        self._anchor = anchor
        self._calculate_position()

    @property
    def position(self) -> Point2:
        """Get or set the center x and y position of the sprite."""
        return self._position

    @position.setter
    def position(self, new_value: Point2):
        if new_value == self._position:
            return
        self._calculate_position()

    def _calculate_position(self):
        anchor = self._anchor
        anchor_position = self._anchor_position
        if anchor is None:
            self._update_position(anchor_position)
            return
        
        dx = -anchor[0] * self.width * 0.5
        dy = -anchor[1] * self.height * 0.5
        c, s = cos(self.radians), sin(self.radians)
        position = (
            anchor_position[0] + c * dx - s * dy,
            anchor_position[1] + s * dx + c * dy
        )

        self._update_position(position)

    def _update_position(self, position: Point2):
        self._position = position
        self._hit_box.position = position

        self.update_spatial_hash()

        for sprite_list in self.sprite_lists:
            sprite_list._update_position(self)

    @property
    def width(self) -> float:
        """Get or set width or the sprite in pixels"""
        return self._width

    @width.setter
    def width(self, new_value: float):
        if new_value != self._width:
            self._scale = new_value / self._texture.width, self._scale[1]
            self._hit_box.scale = self._scale
            self._width = new_value

            self.update_spatial_hash()
            for sprite_list in self.sprite_lists:
                sprite_list._update_width(self)

    @property
    def height(self) -> float:
        """Get or set the height of the sprite in pixels."""
        return self._height

    @height.setter
    def height(self, new_value: float):
        if new_value != self._height:
            self._scale = self._scale[0], new_value / self._texture.height
            self._hit_box.scale = self._scale
            self._height = new_value

            self.update_spatial_hash()
            for sprite_list in self.sprite_lists:
                sprite_list._update_height(self)

    @property
    def size(self) -> Point:
        """
        Get or set the size of the sprite as a pair of values.

        This is faster than getting or setting width and height separately.
        """
        return self._width, self._height

    @size.setter
    def size(self, new_value: Point2):
        try:
            width, height = new_value
        except ValueError:
            raise ValueError(
                "size must be a tuple-like object which unpacks to exactly 2 coordinates"
            )
        except TypeError:
            raise TypeError(
                "size must be a tuple-like object which unpacks to exactly 2 coordinates"
            )

        if width != self._width or height != self._height:
            texture_width, texture_height = self._texture.size
            self._scale = width / texture_width, height / texture_height
            self._hit_box.scale = self._scale
            self._width = width
            self._height = height

            self.update_spatial_hash()

            for sprite_list in self.sprite_lists:
                sprite_list._update_size(self)

    @property
    def scale_x(self) -> float:
        """
        Get or set the sprite's x scale value.

        .. note:: Negative values are supported. They will flip &
                  mirror the sprite.
        """
        return self._scale[0]

    @scale_x.setter
    def scale_x(self, new_scale_x: AsFloat):
        old_scale_x, old_scale_y = self._scale
        if new_scale_x == old_scale_x:
            return

        new_scale = (new_scale_x, old_scale_y)

        # Apply scale to hitbox first to raise any exceptions quickly
        self._hit_box.scale = new_scale
        self._scale = new_scale
        self._width = self._texture.width * new_scale_x

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def scale_y(self) -> float:
        """
        Get or set the sprite's y scale value.

        .. note:: Negative values are supported. They will flip &
                  mirror the sprite.
        """
        return self._scale[1]

    @scale_y.setter
    def scale_y(self, new_scale_y: AsFloat):
        old_scale_x, old_scale_y = self._scale
        if new_scale_y == old_scale_y:
            return

        new_scale = (old_scale_x, new_scale_y)

        # Apply scale to hitbox first to raise any exceptions quickly
        self._hit_box.scale = new_scale
        self._scale = new_scale
        self._height = self._texture.height * new_scale_y

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def scale(self) -> Point2:
        """Get or set the x & y scale of the sprite as a pair of values.
        You may set both the x & y with a single scalar, but scale will always return
        a length 2 tuple of the x & y scale

        See :py:attr:`.scale_x` and :py:attr:`.scale_y` for individual access.

        See :py:meth:`.scale_multiply_uniform` for uniform scaling.

        .. note:: Negative scale values are supported.

            This applies to both single-axis and dual-axis.
            Negatives will flip & mirror the sprite, but the
            with will use :py:func:`abs` to report total width
            and height instead of negatives.

        """
        return self._scale

    @scale.setter
    def scale(self, new_scale: Point2 | AsFloat):
        if isinstance(new_scale, float | int):
            scale_x = new_scale
            scale_y = new_scale

        else:  # Treat it as some sort of iterable or sequence
            # Don't abstract this. Keep it here since it's a hot code path
            try:
                scale_x, scale_y = new_scale  # type / length implicit check
            except ValueError:
                raise ValueError(
                    "scale must be a tuple-like object which unpacks to exactly 2 coordinates"
                )
            except TypeError:
                raise TypeError(
                    "scale must be a tuple-like object which unpacks to exactly 2 coordinates"
                )

        new_scale = scale_x, scale_y
        if new_scale == self._scale:
            return

        self._hit_box.scale = new_scale
        tex_width, tex_height = self._texture.size
        self._scale = new_scale
        self._width = tex_width * scale_x
        self._height = tex_height * scale_y

        self.update_spatial_hash()
        for sprite_list in self.sprite_lists:
            sprite_list._update_size(self)

    @property
    def angle(self) -> float:
        """
        Get or set the rotation or the sprite.

        The value is in degrees and is clockwise.
        """
        return self._angle

    @angle.setter
    def angle(self, new_value: float) -> None:
        if new_value == self._angle:
            return

        self._angle = new_value
        self._hit_box.angle = new_value

        for sprite_list in self.sprite_lists:
            sprite_list._update_angle(self)

        self.update_spatial_hash()