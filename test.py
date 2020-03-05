# -*- coding:utf-8 -*-

import unittest

from pyserialize import Serializable, JSON


class Point3D(Serializable):

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


class GeneralExample(Serializable):

    def __init__(self):
        # A built-in object like int, float, string, dict, array
        self.value = 0.0
        # An object inherited from Serializable
        self.object = None
        # An array of built-in objects
        self.pure_array = []
        # A dict of built-in objects
        self.pure_dict = {}
        # A array of objects inherited from Serializable
        self.object_array = []
        # A dict of objects inherited from Serializable
        self.object_dict = {}

    def __repr__(self):
        return str(self.__dict__)

    def attr_slots(self):
        return {'object': Point3D(), 'object_array': [[Point3D()]], 'object_dict': {'_': Point3D()}}


# test_data
TEST_DATA = {
    'Value': 102,
    'Object': {
        'X': 1,
        'Y': 2,
        'Z': 1
    },
    'PureArray': [1, 2, 3],
    'PureDict': {
        'X': 1,
        'Y': 2,
        'Z': 1
    },
    'ObjectArray': [[{
        'X': 1,
        'Y': 2,
        'Z': 1
    }]],
    'ObjectDict': {
        '1': {
            'X': 1,
            'Y': 2,
            'Z': 1
        }
    }
}


class TestSerializable(unittest.TestCase):

    def test_point3d_to_json_string(self):
        point = Point3D(1, 2, 3)
        point_dict = {'X': 1, 'Y': 2, 'Z': 3}
        json_str_1 = JSON.to_json_string(point, indent=4)
        json_str_2 = JSON.to_json_string(point_dict, indent=4)
        self.assertEqual(json_str_1, json_str_2, self.test_point3d_to_json_string.__name__)

    def test_parse_point3d(self):
        point_str = JSON.to_json_string({'X': 1, 'Y': 2, 'Z': 3})
        point = JSON.parse_object(point_str, Point3D)
        self.assertTrue(point.x == 1 and point.y == 2 and point.z == 3)

    def test_general_example_to_json_string(self):
        obj_str_1 = JSON.to_json_string(TEST_DATA, indent=4)
        obj = JSON.parse_object(obj_str_1, GeneralExample)
        obj_str_2 = JSON.to_json_string(obj, indent=4)
        self.assertTrue(obj_str_1 == obj_str_2, obj_str_1 + '\n' + obj_str_2)


if __name__ == '__main__':
    unittest.main()
