import os
import string
from enum import IntEnum

from xml.dom.minidom import parseString

import numpy as np
import xmltodict
from dicttoxml import dicttoxml
from report import MyReport


class DataType(IntEnum):
    type_null = 0x00
    type_integer8 = 0x02
    type_integer16 = 0x03
    type_integer32 = 0x04
    type_unsigned8 = 0x05
    type_unsigned16 = 0x06
    type_unsigned32 = 0x07
    type_real32 = 0x08
    type_real64 = 0x11
    type_integer64 = 0x15


class ObjType(IntEnum):
    object_null = 0x00
    object_domain = 0x02
    object_var = 0x07
    object_array = 0x08
    object_record = 0x09

class DoItem:
    """ This class contains all data of a complete DO element in run time format """

    def __init__(self, do_data_, par_data_=None):
        self.parent = None
        self.xml_do_data = do_data_
        self.xml_do_pars = None
        self.onWrite = False
        self.onRead = False
        self.buff = 0
        self.new_buff = 0
        try:
            self.mux = int(do_data_["mux"], 16)
        except KeyError:
            pass

    def get_prop(self, name_):
        try:
            plist = self.xml_do_pars["property"]
            prop = list(filter(lambda x: x["@name"] == name_, plist))
            if len(prop) != 0:
                return prop[0]["@value"]
        except:
            return "0"
        return "0"

    @property
    def name(self):
        return self.xml_do_data["@name"]

    @property
    def data_type(self):
        return int(self.xml_do_data["@dataType"],16)

    @property
    def object_type(self):
        return int(self.xml_do_data["@objectType"])

    @property
    def cmd_w(self):
        return int(self.get_prop("sharc_cmd_w"))

    @property
    def cmd_w_par(self):
        return int(self.get_prop("sharc_cmd_w_par"))

    @property
    def cmd_r(self):
        return int(self.get_prop("sharc_cmd_r"))

    @property
    def cmd_r_par(self):
        return int(self.get_prop("sharc_cmd_r_par"))

    @property
    def on_read(self):
        return self.onRead

    @on_read.setter
    def on_read(self, value):
        self.onRead = value

    @property
    def on_write(self):
        return self.onWrite

    @on_write.setter
    def on_write(self, value):
        self.onWrite = value

    @property
    def value(self):
        return self.get_val()

    @value.setter
    def value(self, val_):
        self.set_val(val_)

    @property
    def default(self):
        try:
            tmp = self.xml_do_pars["defaultValue"]
            return tmp["@value"]
        except KeyError:
            return 0

    @property
    def min_value(self):
        try:
            return self.xml_do_pars["range"]["minValue"]["@value"]
        except KeyError:
            return 0

    @property
    def max_value(self):
        try:
            return self.xml_do_pars["range"]["maxValue"]["@value"]
        except KeyError:
            return 0

    def is_numeric(self) -> bool:
        if self.object_type == ObjType.object_var.value:
            match self.data_type:
                case DataType.type_integer8.value:
                    return True
                case DataType.type_integer16.value:
                    return True
                case DataType.type_integer32.value:
                    return True
                case DataType.type_unsigned8:
                    return True
                case DataType.type_unsigned16.value:
                    return True
                case DataType.type_unsigned32.value:
                    return True
                case DataType.type_integer64.value:
                    return True
                case DataType.type_unsigned8.value:
                    return True
                case DataType.type_unsigned16.value:
                    return True
                case DataType.type_unsigned32.value:
                    return True
                case DataType.type_real64.value:
                    return True
        return False

    def get_size_in_bytes(self):
        match self.data_type:
            case DataType.type_integer32.value:
                return 4
            case DataType.type_integer64.value:
                return 8
            case DataType.type_real32.value:
                return 4
            case DataType.type_real64.value:
                return 8

    def _get_val(self, new_):
        if self.is_numeric():
            match self.data_type:
                case DataType.type_integer8.value:
                    return np.int8(self.new_buff if new_ else self.buff)
                case DataType.type_integer16.value:
                    return np.int16(self.new_buff if new_ else self.buff)
                case DataType.type_integer32.value:
                    return np.int32(self.new_buff if new_ else self.buff)
                case DataType.type_unsigned8:
                    return np.uint8(self.new_buff if new_ else self.buff)
                case DataType.type_unsigned16.value:
                    return np.uint16(self.new_buff if new_ else self.buff)
                case DataType.type_unsigned32.value:
                    return np.uint32(self.new_buff if new_ else self.buff)
                case DataType.type_real32.value:
                    return np.float32(self.new_buff if new_ else self.buff)
                case DataType.type_real64.value:
                    return np.float64(self.new_buff if new_ else self.buff)
        else:
            return 0

    def get_val(self):
        return self._get_val(False)

    def get_new_val(self):
        return self._get_val(True)

    def _set_val(self, val_, new_) -> bool:
        if self.is_numeric():
            if new_:
                self.new_buff = val_
            else:
                self.buff = val_
            return True
        else:
            return False

    def set_val(self, val_) -> int:
        return self._set_val(val_, False)

    def set_new_val(self, val_) -> int:
        return self._set_val(val_, True)

    def to_xml(self):
        pass

    def set_val_ba(self, param: bytearray, len_: int):
        """ Set value of DO from the message byte array"""
        if self.data_type == DataType.type_integer32:
            tmp = int.from_bytes(param, "little")
            self.value = np.int32(tmp)
            MyReport().print("The value of DO is: " + str(self.value))


class DoSNode(DoItem):

    def __init__(self, parent_, do_data_, par_data_):
        super().__init__(do_data_, par_data_)
        self.xml_do_pars = par_data_
        self.parent = parent_
        self.subindex = int(do_data_["@subIndex"], 16)
        self.mux = (self.parent.index << 8) + int(do_data_["@subIndex"], 16)
        self.set_val = self.default

class DoNode(DoItem):

    def __init__(self, do_data_, par_data_):
        super().__init__(do_data_, par_data_)
        self.index = int(do_data_["@index"], 16)
        if par_data_ is not None:
            node_pars = list(filter(lambda x: x["@uniqueID"] == do_data_["@uniqueIDRef"], par_data_))
            self.xml_do_pars = par_data_[0]
            self.set_val(self.default)

        self.subdolist = list[DoSNode]()
        try:
            sub_items = do_data_["CANopenSubObject"]
            self.mux = int(do_data_["@index"], 16)
            for si in sub_items:
                node_pars = list(filter(lambda x: x["@uniqueID"] == si["@uniqueIDRef"], par_data_))
                self.subdolist.append(DoSNode(self, si, node_pars[0]))
        except:
            self.mux = int(do_data_["@index"], 16) << 8


class DmDictionary():

    def __init__(self):
        self.root = None
        self.parameterlist = None
        self.objectlist = None
        self.format = None
        self.version = None
        self.name = None
        self.xml_data: None

        self.treeItems = list[DoNode]()
        self.listItem = list[DoItem]()

    def from_xml(self,filen_):
        xmlfilen = filen_
        xmlfile = open(xmlfilen, "r")
        xmldata = xmlfile.read()
        xmlfile.close()
        self.root: dict = xmltodict.parse(xmldata)["dice_data"]
        try:
            # self.name = root["name"]
            self.version = self.root["@version"]
            self.format = self.root["@format"]

            self.parameterlist = (self.root["ISO15745ProfileContainer"]["ISO15745Profile"][0]
                                  ["ProfileBody"]["ApplicationProcess"]["parameterList"]["parameter"])
            self.objectlist = (self.root["ISO15745ProfileContainer"]["ISO15745Profile"][1]
                               ["ProfileBody"]["ApplicationLayers"]["CANopenObjectList"]["CANopenObject"])
            for xmldo in self.objectlist:
                id1 = xmldo["@uniqueIDRef"]
                try:
                    params = list(filter(lambda x: id1 in x["@uniqueID"], self.parameterlist))
                except KeyError:
                    MyReport().print("error loading unique id")
                    continue
                self.treeItems.append(DoNode(xmldo, params))

        except KeyError:
            pass

        for nd in self.treeItems:
            self.listItem.append(nd)
            for snd in nd.subdolist:
                self.listItem.append(snd)

    def find_do_by_mux(self, mux_) -> DoItem | None:
        temp_list = list(filter(lambda x: x.mux == mux_, self.listItem))
        if len(temp_list) == 0:
            return None
        elif len(temp_list) > 1:
            MyReport().error(-1, "Two dictionary elements with same mux: " + hex(mux_))
            MyReport().print(temp_list)
        return temp_list[0]

    def find_do_by_name(self, name_: string) -> DoItem | None:
        temp_list: list[DoItem] = list(filter(lambda x: x.name == name_, self.listItem))
        if len(temp_list) == 0:
            return None
        elif len(temp_list) > 1:
            MyReport().error(-1, "Two dictionary elements with same mux: " + name_)
            MyReport().print(vars(temp_list))
        return temp_list[0]

    def load_image(self, name_):
        xmlfilen = "data/" + name_ + ".xml"
        if not os.path.isfile(xmlfilen):
            return

        xmlfile = open(xmlfilen, "r")
        xml = xmlfile.read()
        xmlfile.close()
        image = xmltodict.parse(xml)["root"]
        imglist = image["do_list"]["item"]
        for do_img in imglist:
            do_it = self.find_do_by_mux(int(do_img["mux"], 16))
            if do_it:
                do_it.set_val(do_img["value"] if do_it else 0)

    def save_image(self, name_):
        xmlfilen = "data/" + name_ + ".xml"
        data = self._todict(name_)
        xml = dicttoxml(data, attr_type=False)
        xml_decode = xml.decode()
        xml_format = parseString(xml_decode).toprettyxml()
        xmlfile = open(xmlfilen, "w")
        xmlfile.write(xml_format)
        xmlfile.close()
