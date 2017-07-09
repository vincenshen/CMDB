# -*- coding:utf-8 -*-
# @Time     : 2017-07-03 14:06
# @Author   : gck1d6o
# @Site     : 
# @File     : core.py
# @Software : PyCharm

import json
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from Asset import models


class Assets(object):
    def __init__(self, request):
        self.request = request
        self.data = request.POST.get("asset_data", "")
        self.mandatory_field = ["sn", "asset_id", "asset_type"]  # 合法性检查客户端提交的数据中必须要有的字段
        self.response = {
            "error": [],
            "info": [],
            "warning": []
        }
        self.clean_data = None
        self.asset_obj = None
        self.waiting_approval = False

    def response_msg(self, msg_type, key, msg):
        """生成错误消息"""
        if msg_type in self.response:
            self.response[msg_type].append({key: msg})
        else:
            raise ValueError

    def mandatory_check(self, data, only_check_sn=False):
        """对客户端发送的资产信息做合法性检查，"""
        for field in self.mandatory_field:
            """检查必须字段"""
            if field not in data:
                self.response_msg("error", "MandatoryCheckFailed",
                                  "The filed [%s] is mandatory and not provided in you reporting data" % field)
        else:
            if self.response["error"]:
                print("==================>>>>> 合法性检查没通过")
                return False
        try:
            """
            到这里表示合法性检查通过，
            根据SN号或者asset_id在数据库中资产记录：
            1、如果能够查询到资产记录，就返回该资产obj。
            2、如果查找不到资产记录，就设置waiting_approval为True。
            """
            print("==================>>>>> 合法性检查通过")
            if not only_check_sn:
                self.asset_obj = models.Asset.objects.get(id=int(data["asset_id"]), sn=data["sn"])
            else:
                self.asset_obj = models.Asset.objects.get(sn=data["sn"])
            return True
        except ObjectDoesNotExist as e:  # 找不到该资产
            self.response_msg("error", "AssetDataInvalid",
                              "Can't find asset object in DB by using asset ID [%s] and SN [%s]" % (
                                  data["asset_id"], data["sn"]))
            self.waiting_approval = True
            print("==================>>>>> 找不到该资产信息，表明该资产是新资产。")
            return False

    def get_asset_id_by_sn(self):
        """
        客户端第一次汇报资产信息或没带asset_id时调用的接口。
        1、调用mandatory_check验证客户端数据合法性；
        2、在mandatory_check中判断是新资产还是旧资产；
            如果新资产就将资产信息存放到 待审批表；
            如果是旧资产就直接将asset_id返回给客户端。
        """
        if self.data is not None:
            try:
                data = json.loads(self.data)
                if self.mandatory_check(data, only_check_sn=True):
                    """这个资产已经存在DB中，仅仅返回资产ID给客户端"""
                    response = {"asset_id": self.asset_obj.id}
                else:
                    if self.waiting_approval is True:
                        """执行这一步，代表是新资产"""
                        print("==================>>>>> 执行这一步，代表是新资产")
                        response = {"needs_approval": "this is a new asset, needs IT admin's approval."}
                        self.clean_data = data
                        self.save_new_asset_to_approval_zone()
                    else:
                        response = self.response
            except ValueError as e:
                self.response_msg("error", "AssetDataInvalid", str(e))
                response = self.response
        else:
            self.response_msg("error", "AssetDataInvalid", "The reported asset data is not valid.")
            response = self.response
        return response

    def save_new_asset_to_approval_zone(self):
        """
        新资产将保存到待审批区，等待IT管理员审批
        """
        print("==================>>>>> 新资产将保存到待审批区，等待IT管理员审批")
        try:
            new_asset_obj = models.NewAssetApprovalZone.objects.get_or_create(
                sn=self.clean_data.get("sn"),
                data=json.dumps(self.clean_data),
                manufacturer=self.clean_data.get("manufacturer"),
                model=self.clean_data.get("model"),
                asset_type=self.clean_data.get("asset_type"),
                cpu_model=self.clean_data.get("cpu_model"),
                cpu_count=self.clean_data.get("cpu_count"),
                cpu_core_count=self.clean_data.get("cpu_core_count"),
                os_distribution=self.clean_data.get("os_distribution"),
                os_release=self.clean_data.get("os_release"),
                os_type=self.clean_data.get("os_type"),

            )
            print("==================>>>>>", new_asset_obj)
            return True
        except Exception as e:
            return False

    def data_is_valid(self):
        """数据有效性检查"""
        if self.data is not None:
            try:
                data = json.loads(self.data)
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response["error"]:
                    return True
            except ValueError as e:
                self.response_msg("error", "AssetDataInvalid", str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', "The reported asset data is not valid or provided")

    def __is_new_asset(self):
        """判断是否是新资产"""
        print("判断是否是新资产")
        if not hasattr(self.asset_obj, self.clean_data["asset_type"]):
            """没有反射中的属性代表新资产"""
            return True
        else:
            return False

    def data_is_valid_without_id(self, db_obj=None):
        """
        做数据合法性检查
        :param db_obj: 接收admin页面AssetApprovalAdmin表被选中数据的queryset
        """
        if db_obj.data is not None:
            self.data = db_obj.data
            try:
                data = json.loads(self.data)
                """在数据中通过sn去查询，如果查询到就获取asset_id,如果查询不到就新建一条记录，只包含sn和name"""
                """这里之所以用到get_or_create，就是让mandatory_check能够获取到asset_obj这个对象，以便后面的data_inject逻辑调用"""
                asset_obj = models.Asset.objects.get_or_create(sn=data.get("sn"))
                data["asset_id"] = asset_obj[0].id
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response["error"]:
                    return True
            except ValueError as e:
                self.response_msg("error", "AssetDataInvalid", str(e))
                return False
        else:
            self.response_msg("error", "AssetDataInvalid", "The reported asset data is not valid!")
            return False

    def data_inject(self):
        """保存数据到DB中"""
        if self.__is_new_asset():
            print("发现是新资产，进行资产创建。。。")
            self.create_asset()
        else:
            print("发现是旧资产，进行资产更新。。。")
            self.update_asset()

    def create_asset(self):
        """根据资产类型 反射到相应的Create func上"""
        func = getattr(self, "create_%s" % self.clean_data["asset_type"])
        func()

    def update_asset(self):
        """更新资产信息到DB中"""
        func = getattr(self, "update_%s" % self.clean_data["asset_type"])
        func()

    def create_server(self):
        """根据资产类型 反射到相应的Update func上"""
        self.create_or_update_manufacturer()
        self.create_server_info()
        self.create_ram_component()
        self.create_cpu_component()
        self.create_disk_component()
        self.create_nic_component()

        log_msg = "Asset %s %s has been created!" % (self.asset_obj.id, self.asset_obj)
        self.response_msg("info", "NewAssetOnline", log_msg)

    def verify_field(self, data_set, field_key, data_type, required=True):
        """数据类型验证及转换"""
        field_val = data_set.get(field_key, "")
        if field_val is not None:
            try:
                data_set[field_key] = data_type(field_val)
            except ValueError as e:
                self.response_msg("error", "InvalidField",
                                  "THe field [%s]'s data type is invalid, the correct data type should be [%s]" % (
                                      field_key, data_type))
        elif required is True:
            self.response_msg("error", "Lack of field",
                              "The field [%s] has no value provided in your reporting data [%s]" % (
                                  field_key, data_set))

    def create_server_info(self, ignore_errors=False):
        """将系统信息保存到DB"""
        try:
            self.verify_field(self.clean_data, "model", str)
            if not self.response["error"] or ignore_errors is True:
                data_set = {
                    "asset_id": self.asset_obj.id,
                    "raid_type": self.clean_data.get("raid_type"),
                    "model": self.clean_data.get("model"),
                    "os_type": self.clean_data.get("os_type"),
                    "os_distribution": self.clean_data.get("os_distribution"),
                    "os_release": self.clean_data.get("os_release"),
                }
                obj = models.Server(**data_set)
                obj.save()
                print("create_server_info执行成功")

        except Exception as e:
            self.response_msg("error", "ObjectCreationException", "Object [Server] %s" % str(e))
            print("create_server_info执行失败")

    def create_or_update_manufacturer(self, ignore_error=False):
        """获取或创建供应商"""
        try:
            self.verify_field(self.clean_data, "manufacturer", str)
            manufacturer = self.clean_data.get("manufacturer")
            if not self.response["error"] or ignore_error is True:
                obj = models.Manufacturer.objects.filter(name=manufacturer)
                if obj.exists():
                    obj = obj[0]
                else:
                    obj = models.Manufacturer.objects.create(name=manufacturer)
                self.asset_obj.manufacturer = obj
                self.asset_obj.save()
                print("create_or_update_manufacturer执行成功")
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [manufacturer] %s' % str(e))
            print("create_or_update_manufacturer执行失败", e)

    def create_cpu_component(self, ignore_error=False):
        """将CPU信息保存到DB"""
        try:
            self.verify_field(self.clean_data, "model", str)
            self.verify_field(self.clean_data, "cpu_count", int)
            self.verify_field(self.clean_data, "cpu_core_count", int)
            if not self.response["error"] or ignore_error is True:
                data_set = {
                    "asset_id": self.asset_obj.id,
                    "cpu_model": self.clean_data.get("cpu_model"),
                    "cpu_count": self.clean_data.get("cpu_count"),
                    "cpu_core_count": self.clean_data.get("cpu_core_count")
                }
                obj = models.CPU(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> has added new [cpu] component with data [%s]" % (self.asset_obj, data_set)
                self.response_msg('info', 'NewComponentAdded', log_msg)
                print("create_cpu_component执行成功")
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [cpu] %s' % str(e))
            print("create_cpu_component执行失败")

    def create_disk_component(self, ignore_error=False):
        """将磁盘信息保存到DB"""
        disk_data = self.clean_data.get("physical_disk_driver", "")
        if disk_data:
            for disk_item in disk_data:
                try:
                    self.verify_field(disk_item, "capacity", int)
                    self.verify_field(disk_item, "interface_type", str)
                    self.verify_field(disk_item, "model", str)
                    if not self.response["error"] or ignore_error is True:
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "sn": disk_item.get("sn", ""),
                            "slot": disk_item.get("slot", ""),
                            "capacity": disk_item.get("capacity", ""),
                            "model": disk_item.get("model"),
                            "interface_type": disk_item.get("interface_type", ""),
                        }
                        obj = models.Disk(**data_set)
                        obj.save()
                        log_msg = "Asset[%s] --> has added new [disk] component with data [%s]" % (
                            self.asset_obj, data_set)
                        self.response_msg('info', 'NewComponentAdded', log_msg)
                        print("create_disk_component执行成功")
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [Disk] %s' % str(e))
                    print("create_disk_component执行失败", e)
        else:
            self.response_msg('error', 'Lack of Data', 'Disk info is not provided in your reporting data')

    def create_nic_component(self, ignore_error=False):
        """将网卡信息保存到DB"""
        nic_data = self.clean_data.get("nic", "")
        if nic_data:
            for nic_item in nic_data:
                try:
                    self.verify_field(nic_item, "mac_address", str)
                    if not self.response["error"] or ignore_error is True:
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "name": nic_item.get("name", ""),
                            "model": nic_item.get("model", ""),
                            "ip_address": nic_item.get("ip_address", ""),
                            "mac_address": nic_item.get("mac_address", ""),
                            "net_mask": nic_item.get("net_mask", "")
                        }
                        obj = models.NIC(**data_set)
                        obj.save()
                        log_msg = "Asset[%s] --> has added new [disk] component with data [%s]" % (
                            self.asset_obj, data_set)
                        self.response_msg('info', 'NewComponentAdded', log_msg)
                        print("create_nic_component执行成功")
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [nic] %s' % str(e))
                    print("create_nic_component执行失败")
        else:
            self.response_msg('error', 'Lack of Data', 'NIC info is not provided in your reporting data')

    def create_ram_component(self, ignore_error=False):
        """将内存信息保存到DB"""
        ram_data = self.clean_data.get("ram", "")
        if ram_data:
            for ram_item in ram_data:
                print("create_ram_component执行.....")
                try:
                    self.verify_field(ram_item, "capacity", int)
                    if not self.response["error"] or ignore_error is True:
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "slot": ram_item.get("slot", ""),
                            "capacity": ram_item.get("capacity", ""),
                            "manufacturer": ram_item.get("manufacturer", ""),
                            "model": ram_item.get("model", ""),
                            "sn": ram_item.get("sn", "")
                        }
                        obj = models.RAM(**data_set)
                        obj.save()
                        log_msg = "Asset[%s] --> has added new [disk] component with data [%s]" % (
                            self.asset_obj, data_set)
                        self.response_msg('info', 'NewComponentAdded', log_msg)
                        print("create_ram_component执行成功")
                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [ram] %s' % str(e))
                    print("create_ram_component执行失败")
        else:
            self.response_msg('error', 'Lack of Data', 'RAM info is not provided in your reporting data')
            print("create_ram_component执行失败")

    def update_server(self):
        """更新服务器资产各组件"""
        self.update_asset_component(data_source=self.clean_data["nic"],
                                    fk="nic_set",
                                    update_fields=["name", "sn", "model", "mac_address", "ip_address", "net_mask"],
                                    identify_field="mac_address")
        self.update_asset_component(data_source=self.clean_data["physical_disk_driver"],
                                    fk="disk_set",
                                    update_fields=["slot", "sn", "model", "capacity", "interface_type"],
                                    identify_field="slot")
        self.update_asset_component(data_source=self.clean_data["ram"],
                                    fk="ram_set",
                                    update_fields=["slot", "sn", "model", "capacity"],
                                    identify_field="slot")
        self.update_cpu_component()
        self.update_server_component()
        self.update_manufacturer_component()

    def update_cpu_component(self):
        """
        更新DB中对应资产CPU信息
        """
        update_fields = ["cpu_model", "cpu_count", "cpu_core_count"]
        if hasattr(self.asset_obj, "cpu"):
            self.compare_save_component(model_obj=self.asset_obj.cpu,
                                        update_fields_in_db=update_fields,
                                        data_source=self.clean_data)
        else:
            self.create_cpu_component(ignore_error=True)

    def compare_save_component(self, model_obj=None, update_fields_in_db=None, data_source=None):
        """
        :param model_obj:  数据库中这个资产的对象
        :param update_fields_in_db: 需要比对的字段
        :param data_source:  客户端提交的这个资产的数据
        """
        for field in update_fields_in_db:
            """
            1.取出双方（数据库中资产信息，客户端提交的资产信息）的字段值
            2.统一数据类型
            3.数据比对
            4.根据比对结果，确定是否更新数据库中对应的资产信息
            """
            value_from_db = getattr(model_obj, field)
            value_from_client = data_source.get(field, "")
            if value_from_client:
                if type(value_from_db) is int:
                    value_from_client = int(value_from_client)
                elif type(value_from_db) is float:
                    value_from_client = float(value_from_client)
                elif type(value_from_db) is str:
                    value_from_client = str(value_from_client)

                if value_from_db == value_from_client:
                    """如果相等，表示没有变化，不需要更新"""
                    pass
                else:
                    db_field = model_obj._meta.get_field(field)
                    db_field.save_form_data(model_obj, value_from_client)
                    model_obj.update_date = datetime.now()
                    model_obj.save()
                    log_msg = "Asset[%s] --> component[%s] --> field[%s] has changed from [%s] to [%s]" % (
                        self.asset_obj, model_obj, field, value_from_db, value_from_client)
                    self.response_msg('info', 'FieldChanged', log_msg)
                    self.log_handler(self.asset_obj, 'FieldChanged', self.request.user, log_msg, model_obj)

            else:
                self.response_msg('warning', 'AssetUpdateWarning',
                                  "Asset component [%s]'s field [%s] is not provided in reporting data " % (
                                      model_obj, field))

    def update_server_component(self):
        update_fields = ["model", "os_type", "os_distribution", "os_release"]
        if hasattr(self.asset_obj, "server"):
            self.compare_save_component(model_obj=self.asset_obj.server,
                                        update_fields_in_db=update_fields,
                                        data_source=self.clean_data)
        else:
            self.create_server_info(ignore_errors=True)

    def update_manufacturer_component(self):
        self.create_or_update_manufacturer(ignore_error=True)

    def update_asset_component(self, data_source, fk, update_fields, identify_field=None):
        """
        :param data_source: 客户端汇报的资产数据
        :param fk: 表示哪一个组件的反向查询字符串
        :param update_fields: 需要比较并更新的字段
        :param identify_field: 通过该字段去数据库中获取资产信息, 如果为None表示仅仅使用资产ID进行识别
        :return:
        """
        try:
            component_obj = getattr(self.asset_obj, fk)  # fk=nic_set
            if hasattr(component_obj, "all"):  # this component is reverse m2m relation with Asset model
                objects_from_db = component_obj.all()  # 获取所有对象[nic_obj1, nic_obj2...]
                for obj in objects_from_db:
                    key_field_data = getattr(obj, identify_field)  # identify_field=mac_address, 获取实际的mac address
                    if type(data_source) is list:  # 确保data_source是一个list
                        for source_data_item in data_source:
                            key_field_data_from_data_source = source_data_item.get(identify_field, "")
                            if key_field_data == key_field_data_from_data_source:
                                self.compare_save_component(model_obj=obj,
                                                            update_fields_in_db=update_fields,
                                                            data_source=source_data_item)
                                break  # 已经根据identify_field匹配到客户端中对应的数据条目，并且进行比对和保存，因此也就没有必要继续循环。
                            else:
                                self.response_msg('warning', 'AssetUpdateWarning',
                                                  "Asset component [%s]'s key field [%s] is not provided in reporting "
                                                  "data " % (fk, identify_field))
                    else:
                        self.response_msg("error", "AssetUpdateWarning",
                                          "Cannot find any matches in source data by using key field val [%s],"
                                          "component data is missing in reporting data!"
                                          % key_field_data)
                self.filter_add_or_delete_components(model_obj_name=component_obj.model._meta.object_name,
                                                     data_from_db_obj=objects_from_db,
                                                     data_source=data_source,
                                                     identify_field=identify_field)
            else:
                pass
        except ValueError as e:
            print('\033[41;1m%s\033[0m' % str(e))

    def filter_add_or_delete_components(self, model_obj_name, data_from_db_obj, data_source, identify_field):
        """
        :param model_obj_name: NIC, DISK, RAM
        :param data_from_db_obj: [nic_obj1, nic_obj2...]
        :param data_source:  client report data
        :param identify_field: mac_address, slot
        :return:
        """
        if type(data_source) is list:
            data_source_value_list = set([data.get(identify_field) for data in data_source])    # [mac1, mac2 ...]
            data_identify_value_from_db = set([getattr(obj, identify_field) for obj in data_from_db_obj])

            print("data_source_value_list", data_source_value_list)
            print("data_identify_value_from_db", data_identify_value_from_db)
            # delete all this item from db
            data_only_in_db = data_identify_value_from_db - data_source_value_list
            print("data_only_in_db", data_only_in_db)
            if data_only_in_db:
                self.delete_component(all_components_obj=data_from_db_obj,
                                      delete_list=data_only_in_db,
                                      identify_field=identify_field)

            # add all this item to db
            data_only_in_data_source = data_source_value_list - data_identify_value_from_db
            print("data_only_in_data_source", data_only_in_data_source)
            if data_only_in_data_source:
                self.add_component(model_obj_name=model_obj_name,
                                   all_components=data_source,
                                   add_list=data_only_in_data_source,
                                   identify_field=identify_field)

    def delete_component(self, all_components_obj, delete_list, identify_field):
        """
        :param all_components_obj: data_from_db_obj
        :param delete_list: data_only_in_db
        :param identify_field: mac_address, slot
        :return:
        """
        delete_obj_list = []
        for obj in all_components_obj:
            value = getattr(obj, identify_field)    # get mac_address from db_obj
            if value in delete_list:
                delete_obj_list.append(obj)
        for item in delete_obj_list:
            item.delete()
            log_msg = "Asset[%s] --> component[%s] --> is lacking from reporting source data, assume it has been " \
                      "removed or replaced,will also delete it from DB" % (self.asset_obj, item)
            self.response_msg('info', 'HardwareChanges', log_msg)
            self.log_handler(self.asset_obj, 'HardwareChanges', self.request.user, log_msg, item)

    def add_component(self, model_obj_name, all_components, add_list, identify_field):
        """
        :param model_obj_name: NIC, DISK, RAM
        :param all_components: [{nic1:...}, {nic2:...} ...]
        :param add_list: [mac1, mac2, ...]
        :param identify_field: mac, slot
        :return:
        """
        model_class = getattr(models, model_obj_name)
        create_obj_list = []
        if type(all_components) is list:
            for data in all_components:
                if data[identify_field] in add_list:
                    create_obj_list.append(data)
        try:
            for component in create_obj_list:
                data_set = {}
                for field in model_class.auto_create_fields:
                    data_set[field] = component.get(field)
                data_set["asset_id"] = self.asset_obj.id
                obj = model_class(**data_set)
                obj.save()
                print('\033[32;1mCreated component with data:\033[0m', data_set)
                log_msg = "Asset[%s] --> component[%s] has just added a new item [%s]" % (
                    self.asset_obj, model_obj_name, data_set)
                self.response_msg('info', 'NewComponentAdded', log_msg)
                self.log_handler(self.asset_obj, 'NewComponentAdded', self.request.user, log_msg, model_obj_name)
        except Exception as e:
            print("\033[31;1m %s \033[0m" % e)
            log_msg = "Asset[%s] --> component[%s] has error: %s" % (self.asset_obj, model_obj_name, str(e))
            self.response_msg('error', "AddingComponentException", log_msg)

    @staticmethod
    def log_handler(asset_obj, event_name, user, detail, component=None):
        """
        日志功能，将日志信息保存的数据表中，方便今后调用。
        :param asset_obj:
        :param event_name:
        :param user:
        :param detail:
        :param component:
        :return:
        """
        log_catalog = {
            1: ['FieldChanged', 'HardwareChanges'],
            2: ['NewComponentAdded'],
        }

        if user.id:
            username = user.username
        else:
            username = "system"

        event_type = None
        for k, v in log_catalog.items():
            if event_name in v:
                event_type = k
                break
        log_obj = models.EventLog(
            name=event_name,
            event_type=event_type,
            asset_id=asset_obj.id,
            component=component,
            detail=detail,
            user=username
        )
        log_obj.save()
