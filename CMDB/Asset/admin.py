from django.contrib import admin
from Asset import models
# Register your models here.
from Asset import core
from datetime import datetime


class AssetApprovalAdmin(admin.ModelAdmin):
    list_display = ('sn', 'asset_type', 'manufacturer', 'model', 'cpu_model', 'os_type', 'os_release', 'approved')
    list_filter = ('asset_type', 'os_type')
    search_fields = ('sn', 'os_type')
    list_editable = ('asset_type', 'approved')
    actions = ['asset_approval', ]

    def asset_approval(self, request, queryset):
        """
        :param request:  在admin页面操作AssetApprovalAdmin表的用户发现的request
        :param queryset: 在admin页面AssetApprovalAdmin表中的被选中的数据
        """

        for obj in queryset:
            asset_handler = core.Assets(request)
            if asset_handler.data_is_valid_without_id(obj):
                print("================>>>>", queryset)
                asset_handler.data_inject()
                obj.approved_by = request.user
                obj.approved = True
                obj.approved_date = datetime.now()
                obj.save()
    asset_approval.short_description = "新资产审批"


admin.site.register(models.Asset)
admin.site.register(models.Server)
admin.site.register(models.IDC)
admin.site.register(models.BusinessUnit)
admin.site.register(models.CPU)
admin.site.register(models.Disk)
admin.site.register(models.NIC)
admin.site.register(models.RAM)
admin.site.register(models.Manufacturer)
admin.site.register(models.Tag)
admin.site.register(models.NewAssetApprovalZone, AssetApprovalAdmin)
admin.site.register(models.UserProfile)
