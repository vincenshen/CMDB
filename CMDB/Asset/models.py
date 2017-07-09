from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

asset_type_choices = (
    ("server", "服务器"),
    ("network", "网络设备"),
    ("storage", "存储设备"),
    ("security", "安全设备"),
    ("machineroom", "机房设备"),
    ("software", "软件资产"),
    ("others", "其他设备"),
)
status_choices = (
    (1, "在线"),
    (2, "下线"),
    (3, "故障"),
    (4, "未知"),
    (5, "其他"),
)


class Asset(models.Model):
    """
    资产总表
    """
    asset_type = models.CharField(max_length=128, choices=asset_type_choices, default="server", verbose_name="资产类型")
    name = models.CharField(max_length=128, unique=True, verbose_name="资产名称")
    sn = models.CharField(max_length=128, unique=True, verbose_name="资产序列号")
    manufacturer = models.ForeignKey("Manufacturer", verbose_name="制造商", null=True, blank=True)
    management_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="管理IP")
    trade_date = models.DateField(null=True, blank=True, verbose_name="购买时间")
    expire_date = models.DateField(null=True, blank=True, verbose_name="过保时间")
    price = models.FloatField(null=True, blank=True, verbose_name="价格")
    business_unit = models.ForeignKey("BusinessUnit", verbose_name="业务线", null=True, blank=True)
    tags = models.ForeignKey("Tag", null=True, blank=True)
    owner = models.ForeignKey("UserProfile", null=True, blank=True, verbose_name="资产所有者")
    cabinet = models.ForeignKey("Cabinet", null=True, blank=True, verbose_name="机房机柜")
    status = models.SmallIntegerField(choices=status_choices, default=1)
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "资产总表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "<id:%s name:%s>" % (self.id, self.name)


class Server(models.Model):
    """
    服务器子表
    """
    sub_asset_type_choices = (
        (1, "PC Server"),
        (2, "Blade Server"),
        (3, "Mini Computer"),
        (4, "Other"),
    )
    created_by_choices = (
        ("auto", "Auto"),
        ("manual", "Manual")
    )
    asset = models.OneToOneField("Asset")
    sub_asset_type = models.SmallIntegerField(choices=sub_asset_type_choices, verbose_name="服务器类型", default=1)
    created_by = models.CharField(choices=created_by_choices, max_length=6, default="auto")
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    raid_type = models.CharField(max_length=128, blank=True, null=True, verbose_name="Raid卡型号")
    os_type = models.CharField(max_length=128, null=True, blank=True)
    os_distribution = models.CharField(max_length=128, null=True, blank=True)
    os_release = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "服务器"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s sn:%s" % (self.asset.name, self.asset.sn)


class CPU(models.Model):
    """
    CPU组件
    """
    asset = models.OneToOneField("Asset")
    cpu_model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    cpu_count = models.SmallIntegerField(verbose_name="物理CPU个数")
    cpu_core_count = models.SmallIntegerField(verbose_name="CPU核数")
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.cpu_model


class RAM(models.Model):
    """
    内存组件
    """
    asset = models.ForeignKey("Asset")
    sn = models.CharField(max_length=128, null=True, blank=True, verbose_name="SN号")
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    slot = models.CharField(max_length=128, verbose_name="插槽")
    manufacturer = models.CharField(max_length=128, null=True, blank=True)
    capacity = models.IntegerField(verbose_name="内存大小MB")
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RAM"
        verbose_name_plural = verbose_name
        unique_together = ("asset", "slot")

    def __str__(self):
        return '%s:%s:%s' % (self.asset_id, self.slot, self.capacity)

    auto_create_fields = ['sn', 'slot', 'model', 'capacity']


class Disk(models.Model):
    """
    硬盘组件
    """
    disk_interface_choice = (
        ('SATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
        ('IDE', "IDE"),
        ("PCI-E", "PCI-E"),
    )
    asset = models.ForeignKey("Asset")
    sn = models.CharField(max_length=128, null=True, blank=True, verbose_name="SN号")
    slot = models.CharField(max_length=10, verbose_name="插槽")
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    capacity = models.IntegerField(verbose_name="磁盘容量GB")
    interface_type = models.CharField(choices=disk_interface_choice, max_length=128, verbose_name="接口类型")
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("asset", "slot")
        verbose_name = "硬盘"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s:slot:%s capacity:%s' % (self.asset_id, self.slot, self.capacity)

    auto_create_fields = ['sn', 'slot', 'model', 'capacity', 'interface_type']


class NIC(models.Model):
    """
    网卡组件
    """
    asset = models.ForeignKey("Asset")
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name="网卡名称")
    sn = models.CharField(max_length=128, null=True, blank=True, verbose_name="SN号")
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    mac_address = models.CharField(max_length=128, unique=True, verbose_name="MAC地址")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    net_mask = models.CharField(max_length=128, null=True, blank=True)
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "网卡"
        verbose_name_plural = verbose_name
        # unique_together = ("asset", "mac_address")

    def __str__(self):
        return '%s:%s' % (self.asset_id, self.mac_address)

    auto_create_fields = ["name", "sn", "model", "mac_address", "ip_address", "net_mask"]


class RaidAdaptor(models.Model):
    """
    Raid卡
    """
    asset = models.ForeignKey('Asset')
    sn = models.CharField(max_length=128, null=True, blank=True, verbose_name="SN号")
    slot = models.CharField(max_length=10, verbose_name="插槽")
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("asset", "slot")


class Manufacturer(models.Model):
    """
    厂商
    """
    name = models.CharField(max_length=128, unique=True, verbose_name="厂商")
    support_phone = models.CharField(max_length=128, null=True, blank=True, verbose_name="支持电话")
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "厂商"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BusinessUnit(models.Model):
    """
    业务线
    """
    name = models.CharField(max_length=128, unique=True, verbose_name="业务线")
    parent_unit_id = models.ForeignKey("BusinessUnit", related_name="parent_id", blank=True, null=True)
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Cabinet(models.Model):
    """
    机柜
    """
    idc = models.ForeignKey("IDC")
    number = models.CharField(max_length=128)

    class Meta:
        unique_together = ("idc", "number")

    def __str__(self):
        return self.number


class IDC(models.Model):
    """
    机房
    """
    name = models.CharField(max_length=128, unique=True, verbose_name="机房名称")
    notes = models.TextField(null=True, blank=True, verbose_name="备注")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    资产标签
    """
    name = models.CharField(max_length=128, unique=True, verbose_name="Tag name")
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserProfile(AbstractUser):
    """
    用户表
    """
    phone = models.CharField(max_length=11, null=True, blank=True)
    token_id = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.username


class NewAssetApprovalZone(models.Model):
    """
    待审批新资产缓存区
    """
    sn = models.CharField(max_length=128, unique=True, verbose_name="SN号")
    manufacturer = models.CharField(max_length=128, verbose_name="制造商", null=True, blank=True)
    asset_type = models.CharField(max_length=128, choices=asset_type_choices, null=True, blank=True)
    model = models.CharField(max_length=128, null=True, blank=True, verbose_name="型号")
    cpu_model = models.CharField(max_length=128, blank=True, null=True)
    cpu_count = models.IntegerField(null=True, blank=True)
    cpu_core_count = models.IntegerField(null=True, blank=True)
    os_distribution = models.CharField(max_length=128, null=True, blank=True)
    os_type = models.CharField(max_length=128, null=True, blank=True)
    os_release = models.CharField(max_length=128, null=True, blank=True)
    data = models.TextField(verbose_name="资产数据")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="汇报日期")
    approved = models.BooleanField(default=False, verbose_name="已批准")
    approved_by = models.ForeignKey("UserProfile", verbose_name="审批人", null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="审批日期")

    class Meta:
        verbose_name = "待审批新资产"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sn


class EventLog(models.Model):
    """记录事件日志"""
    event_type_choices = (
        (1, u'硬件变更'),
        (2, u'新增配件'),
        (3, u'设备下线'),
        (4, u'设备上线'),
        (5, u'定期维护'),
        (6, u'业务上线\更新\变更'),
        (7, u'其它'),
    )
    name = models.CharField(max_length=128, verbose_name="事件名称")
    event_type = models.SmallIntegerField(choices=event_type_choices, verbose_name="事件类型")
    asset = models.ForeignKey("Asset")
    component = models.CharField(max_length=128, blank=True, null=True, verbose_name="事件子项")
    detail = models.TextField(verbose_name="事件详情")
    user = models.CharField(max_length=32, blank=True, null=True, verbose_name="事件处理人")
    create_data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "事件日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
