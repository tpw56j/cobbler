"""
Copyright 2021 Yuriy Chelpanov
Yuriy Chelpanov <yuriy.chelpanov@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301  USA
"""
import uuid
from typing import List, Optional, Union

from cobbler.items import item
from cobbler.cexceptions import CX


class Menu(item.Item):
    """
    A Cobbler menu object.
    """

    COLLECTION_TYPE = "menu"

    def __init__(self, api, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self._display_name = ""

    #
    # override some base class methods first (item.Item)
    #

    def make_clone(self):
        """
        Clone this file object. Please manually adjust all value yourself to make the cloned object unique.

        :return: The cloned instance of this object.
        """
        _dict = self.to_dict()
        cloned = Menu(self.api)
        cloned.from_dict(_dict)
        cloned.uid = uuid.uuid4().hex
        return cloned

    def check_if_valid(self):
        """
        Check if the profile is valid. This checks for an existing name and a distro as a conceptual parent.
        """
        # name validation
        if not self.name:
            raise CX("Name is required")

    def from_dict(self, dictionary: dict):
        """
        Initializes the object with attributes from the dictionary.

        :param dictionary: The dictionary with values.
        """
        self._remove_depreacted_dict_keys(dictionary)
        super().from_dict(dictionary)

    @property
    def parent(self) -> Optional['Menu']:
        """
        Parent Menu of a menu instance.

        :return: The menu object or None
        """
        if not self._parent:
            return None
        return self.api.menus().find(name=self._parent)

    @parent.setter
    def parent(self, value: str):
        """
        Setter for the parent menu of a menu.

        :param value: The name of the parent to set.
        """
        old_parent = self._parent
        if isinstance(old_parent, item.Item):
            old_parent.children.remove(self.name)
        if not value:
            self._parent = ''
            return
        if value == self.name:
            # check must be done in two places as the parent setter could be called before/after setting the name...
            raise CX("self parentage is weird")
        found = self.api.menus().find(name=value)
        if found is None:
            raise CX("menu %s not found" % value)
        self._parent = value
        self.depth = found.depth + 1
        parent = self._parent
        if isinstance(parent, item.Item):
            parent.children.append(self.name)

    @property
    def children(self) -> list:
        """
        TODO

        :return:
        """
        return self._children

    @children.setter
    def children(self, value: List[str]):
        """
        TODO

        :param value:
        """
        if not isinstance(value, list):
            raise TypeError("Field children of object menu must be of type list.")
        if isinstance(value, list):
            if not all(isinstance(x, str) for x in value):
                raise TypeError("Field children of object menu must be of type list and all items need to be menu "
                                "names (str).")
            for name in value:
                menu = self.api.find_menu(name=name)
                if menu is not None:
                    self._children.update({name: menu})
                else:
                    self.logger.warning("Menu with the name \"%s\" did not exist. Skipping setting as a child!" % name)

    #
    # specific methods for item.Menu
    #

    @property
    def display_name(self) -> str:
        """
        TODO

        :return:
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name: str):
        """
        Setter for the display_name of the item.

        :param display_name: The new display_name. If ``None`` the comment will be set to an emtpy string.
        """
        self._display_name = display_name
