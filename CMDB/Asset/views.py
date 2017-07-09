from django.shortcuts import render, HttpResponse
import json
from django.views import View
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from Asset import core
from Asset import models
from utils import api_token


@csrf_exempt
@api_token.token_required
def asset_with_no_asset_id(request):
    """
    客户端第一次汇报资产数据，会调用该接口；如果是新资产就会将资产信息保存到暂存审批表中，
    如果查询到是已有资产就返回asset_id给客户端。
    """
    if request.method == "POST":
        ass_handler = core.Assets(request)
        res = ass_handler.get_asset_id_by_sn()
        return HttpResponse(json.dumps(res))


@csrf_exempt
@api_token.token_required
def asset_report(request):
    """
    客户端拿到自己的资产ID以后，会调用该接口；并对数据更新比对并判断是否需要更新资产信息。
    """
    if request.method == "POST":
        ass_handler = core.Assets(request)
        if ass_handler.data_is_valid():
            ass_handler.data_inject()
        return HttpResponse(json.dumps(ass_handler.response))


class Index(View):
    @staticmethod
    def get(request):
        page = "index"
        # 柱状图数据
        server_count = models.Asset.objects.filter(asset_type="server").count()
        network_count = models.Asset.objects.filter(asset_type="network").count()
        storage_count = models.Asset.objects.filter(asset_type="storage").count()
        security_count = models.Asset.objects.filter(asset_type="security").count()
        software_count = models.Asset.objects.filter(asset_type="software").count()
        others_count = models.Asset.objects.filter(Q(asset_type="others") | Q(asset_type="machineroom")).count()

        # 饼状图数据
        online_count = models.Asset.objects.filter(status=1).count()
        offline_count = models.Asset.objects.filter(status=2).count()
        fault_count = models.Asset.objects.filter(status=3).count()
        unknown_count = models.Asset.objects.filter(status=4).count()
        other_status = models.Asset.objects.filter(status=5).count()

        return render(request, "index.html", locals())


class AssetList(View):
    """
    检索所有资产列表。
    """
    @staticmethod
    def get(request):
        page = "list"
        assets = models.Asset.objects.all()
        return render(request, "list.html", {"assets": assets, "page": page})


class AssetDetail(View):
    """
    根据get传递的asset_id，然后到数据库中查询相应的表。
    """
    @staticmethod
    def get(request, asset_id):
        asset_obj = models.Asset.objects.get(id=asset_id)
        server_obj = models.Server.objects.filter(asset_id=asset_id).first()
        cpu_obj = models.CPU.objects.filter(asset_id=asset_id).first()
        nic_obj = models.NIC.objects.filter(Q(asset_id=asset_id) & Q(ip_address__isnull=False)).first()
        ram_obj = models.RAM.objects.filter(asset_id=asset_id).first()
        disk_obj = models.Disk.objects.filter(asset_id=asset_id).first()
        return render(request, "detail.html", locals())
