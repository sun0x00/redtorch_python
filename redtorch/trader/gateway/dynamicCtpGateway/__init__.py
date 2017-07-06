# encoding: UTF-8

from redtorch.trader import vtConstant
from dynamicCtpGateway import DynamicCtpGateway

gatewayClass = DynamicCtpGateway
gatewayModelName = "DynamicCtpGateway"
gatewayType = vtConstant.GATEWAYTYPE_FUTURES
gatewayQryEnabled = True
