# -*- coding:utf-8 -*-
# @Time     : 2017-06-30 11:27
# @Author   : gck1d6o
# @Site     : 
# @File     : sysinfo.py
# @Software : PyCharm

import platform
import wmi
from win32com.client import Dispatch
from pprint import pprint


class Win32Info(object):
    def __init__(self):
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer(".", "root\cimv2")

    def __get_cpu_info(self):
        """
        收集CPU信息
        :return:
        """
        data = {}
        cpu_list = self.wmi_obj.Win32_Processor()
        cpu_core_count = 0
        cpu_model = ""
        for cpu in cpu_list:
            cpu_core_count += cpu.NumberOfCores
            cpu_model = cpu.Name
        data["cpu_count"] = len(cpu_list)
        data["cpu_model"] = cpu_model
        data["cpu_core_count"] = cpu_core_count
        return data

    def __get_ram_info(self):
        """
        收集内存信息
        :return:
        """
        data= []
        ram_list = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        for item in ram_list:
            mb = int(1024 * 1024)
            ram_size = int(int(item.Capacity) / mb)
            item_data = {
                "slot": item.DeviceLocator.strip(),
                "capacity": ram_size,
                "model": item.Caption,
                "manufacturer": item.Manufacturer,
                "sn": item.SerialNumber,
            }
            data.append(item_data)
        return {"ram": data}

    def __get_server_info(self):
        """
        收集Server硬件信息
        :return:
        """
        computer_info = self.wmi_obj.Win32_ComputerSystem()[0]
        system_info = self.wmi_obj.Win32_OperatingSystem()[0]
        data = {
            "manufacturer": computer_info.Manufacturer,
            "model": computer_info.Model,
            "wake_up_type": computer_info.WakeUpType,
            "sn": system_info.SerialNumber
        }
        return data

    def __get_disk_info(self):
        """
        获取磁盘信息
        :return:
        """
        data = []
        disk_list = self.wmi_obj.Win32_DiskDrive()
        for item in disk_list:
            interface_choices = ["SAS", "SCSI", "SATA", "SSD", "PCI-E", "IDE"]
            interface_type = ""
            for interface in interface_choices:
                if interface in item.Model:
                    interface_type = interface
                    break
                else:
                    interface_type = "Other"
            item_data = {
                "interface_type": interface_type,
                "slot": str(item.Index),
                "sn": item.SerialNumber.strip(),
                "model": item.Model,
                "manufacturer": item.Manufacturer,
                "capacity": int(int(item.Size) / (1000*1000*1000))
            }
            data.append(item_data)
        return {"physical_disk_driver": data}

    def __get_nic_info(self):
        """
        收集网卡信息
        :return:
        """
        data = []
        nic_list = self.wmi_obj.Win32_NetworkAdapterConfiguration()
        for item in nic_list:
            if item.MACAddress is not None:
                if item.IPAddress is not None:
                    ip_address = item.IPAddress[0]
                    net_mask = item.IPSubnet[0]
                else:
                    ip_address = ""
                    net_mask = ""
                item_data = {
                    "ip_address": ip_address,
                    "net_mask": net_mask,
                    "mac_address": item.MACAddress,
                    "model": item.Caption,
                    "name": item.Description,
                }
                data.append(item_data)
        return {"nic": data}

    @property
    def collect(self):
        """
        收集系统信息
        :return:
        """
        data = {
            "os_type": platform.system(),
            "os_release": "%s %s %s" % (platform.release(), platform.architecture()[0], platform.version()),
            "os_distribution": "Microsoft",
            "asset_type": "server"
        }
        data.update(self.__get_cpu_info())
        data.update(self.__get_disk_info())
        data.update(self.__get_nic_info())
        data.update(self.__get_ram_info())
        data.update(self.__get_server_info())

        return data


if __name__ == '__main__':
    info = Win32Info()
    pprint(info.collect)