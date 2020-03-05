# -*- coding:utf-8 -*-
"""
It is a external library for parsing json string to python object.

TODO: It also need some improvement.

@author: Zeng Xiangkuo
"""
import json
import logging

# GLOBAL LOGGER INSTANCE
LOG = logging.getLogger(__name__)


class Serializable(object):
    """
        # Serializable
        It used for parsing json string to python object.

        Ex.
        ```
        class Point3D(Serializable):

            def __init__(self):
                self.x = 1
                self.y = 2
                self.z = 3

        class Example(Serializable):

            def __init__(self):

                self.value = 1
                self.object = None
                self.object_array = None
                self.object_dict = None

            def __repr__(self):
                return str(self.__dict__)

            def attr_slots(self):
                return {'object': Point3D(),
                        'object_array': [[Point3D()]],
                        'object_dict': {'_': Point3D()}}


        # test_data
        TEST_DATA = {
            'Value': 102,
            'Object': {
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

        ex = Example()
        ex.load(TEST_DATA)
        print(ex.dump())
        ```
    """

    def attr_slots(self):
        """
            Return attr-type pairs.
        """
        return {}

    def __convert_attr(self, attr):
        words = attr.split('_')
        return ''.join([word[0].upper() + word[1::] for word in words])

    def __find_attr(self, attr, dict_data):
        for k in dict_data.keys():
            if -1 != k.find('__'):
                continue
            if attr.lower() == self.__convert_attr(k).lower():
                return k
        return None

    def __load_array(self, arr_data, value, attrs):
        if not attrs or attrs[0] is None:
            arr_data.extend(value)
            return
        tp = attrs[0]
        if isinstance(tp, Serializable):
            for item in value:
                temp = tp.__class__()
                temp.load(item)
                arr_data.append(temp)
        elif isinstance(tp, list):
            for item in value:
                arr_data.append([])
                self.__load_array(arr_data[-1], item, tp)
        elif isinstance(tp, dict):
            for item in value:
                arr_data.append({})
                self.__load_dict(arr_data[-1], item, tp)
        else:
            arr_data.extend(value)

    def __load_dict(self, dict_data, value, attrs):
        if not attrs or list(attrs.values())[0] is None:
            dict_data.update(value)
            return
        tp = list(attrs.values())[0]
        if isinstance(tp, Serializable):
            for key, item in value.items():
                temp = tp.__class__()
                temp.load(item)
                dict_data[key] = temp
        elif isinstance(tp, list):
            for key, item in value.items():
                dict_data[key] = []
                self.__load_array(dict_data[key], item, tp)
        elif isinstance(tp, dict):
            for item in value:
                dict_data[key] = {}
                self.__load_dict(dict_data[key], item, tp)
        else:
            dict_data.update(value)

    def __dump_array(self, arr_data, attrs):
        if not attrs or attrs[0] is None:
            return []
        tp = attrs[0]
        data = [None] * len(arr_data)
        for i in range(len(arr_data)):
            if isinstance(tp, Serializable):
                data[i] = arr_data[i].dump()
            elif isinstance(tp, list):
                data[i] = self.__dump_array(arr_data[i], tp)
            elif isinstance(tp, dict):
                data[i] = self.__dump_dict(arr_data[i], tp)
            else:
                data[i] = arr_data[i]
        return data

    def __dump_dict(self, dict_data, attrs):
        if not attrs or list(attrs.values())[0] is None:
            return {}
        tp = list(attrs.values())[0]
        data = {}
        for k, v in dict_data.items():
            if -1 != k.find('__'):
                continue
            if isinstance(tp, Serializable):
                data[self.__convert_attr(k)] = v.dump()
            elif isinstance(tp, list):
                data[self.__convert_attr(k)] = self.__dump_array(v, tp)
            elif isinstance(tp, dict):
                data[self.__convert_attr(k)] = self.__dump_dict(v, tp)
            else:
                data[self.__convert_attr(k)] = v
        return data

    def load(self, data):
        """
            Load the dictionary object.
        """
        for key, value in data.items():
            attr = self.__find_attr(key, self.__dict__)
            if not attr:
                continue
            tp = self.attr_slots().get(attr)
            if tp is None:
                self.__dict__[attr] = value
                continue
            if value is None:
                continue
            if isinstance(tp, Serializable):
                temp = tp.__class__()
                temp.load(value)
                self.__dict__[attr] = temp
            elif isinstance(tp, list):
                self.__dict__[attr] = []
                self.__load_array(self.__dict__[attr], value, tp)
            elif isinstance(tp, dict):
                self.__dict__[attr] = {}
                self.__load_dict(self.__dict__[attr], value, tp)
            else:
                self.__dict__[attr] = value

    def dump(self):
        """
            Dump as a dictionary object.
        """
        data = {}
        for attr, value in self.__dict__.items():
            if -1 != attr.find('__'):
                continue
            tp = self.attr_slots().get(attr)
            key = self.__convert_attr(attr)
            if tp is None:
                data[key] = value
                continue
            if isinstance(tp, Serializable):
                data[key] = value.dump()
            elif isinstance(tp, list):
                data[key] = self.__dump_array(value, tp)
            elif isinstance(tp, dict):
                data[key] = self.__dump_dict(value, tp)
            else:
                data[key] = value
        return data


class JSON(object):
    """
        # JSON
        It used for extending standard json library.
    """

    @staticmethod
    def parse_object(jsonstr, cls):
        """
            Parse the json string as a serializable Python object.
        """
        if not isinstance(cls(), Serializable):
            raise TypeError('Only support serializable Python object.')
        data = json.loads(jsonstr)
        obj = cls()
        obj.load(data)
        return obj

    @staticmethod
    def parse_array(jsonstr, cls):
        """
            Parse the json string as a serializable Python object array.
        """
        if not isinstance(cls(), Serializable):
            raise TypeError('Only support serializable Python object.')
        data = json.loads(jsonstr)
        arr = [None] * len(data)
        for i in range(len(data)):
            arr[i] = cls()
            arr[i].load(data[i])
        return arr

    @staticmethod
    def to_json_string(obj, **kwargs):
        """
            Convert the serializable Python object to a json string.
        """
        if isinstance(obj, Serializable):
            return json.dumps(obj.dump(), **kwargs)
        elif isinstance(obj, list):
            if obj and isinstance(obj[0], Serializable):
                arr = [v.dump() for v in obj]
                return json.dumps(arr, **kwargs)
        else:
            return json.dumps(obj, **kwargs)
