"""
This file provide the data
lanqinglong@huawei.com
"""
import json


class NetworkData:

    def __init__(self):
        self.id = ''
        self.state = 'ACTIVE'
        self.name = 'onosfw-1'
        self.physicalNetwork = 'none'
        self.admin_state_up = True
        self.tenant_id = ''
        self.routerExternal = False
        self.type ='LOCAL'
        self.segmentationID = '6'
        self.shared = False

    def DictoJson(self):

        if self.id =='' or self.tenant_id == '':
            print 'Id and tenant id is necessary!'

        Dicdata = {}
        if self.id !='':
            Dicdata['id'] = self.id
        if self.state != '':
            Dicdata['status'] = self.state
        if self.name !='':
            Dicdata['name'] = self.name
        if self.physicalNetwork !='':
            Dicdata['provider:physical_network'] = self.physicalNetwork
        if self.admin_state_up !='':
            Dicdata['admin_state_up'] = self.admin_state_up
        if self.tenant_id !='':
            Dicdata['tenant_id'] = self.tenant_id
        if self.routerExternal !='':
            Dicdata['router:external'] = self.routerExternal
        if self.type !='':
            Dicdata['provider:network_type'] = self.type
        if self.segmentationID !='':
            Dicdata['provider:segmentation_id'] = self.segmentationID
        if self.shared !='':
            Dicdata['shared'] = self.shared

        Dicdata = {'network': Dicdata}

        return json.dumps(Dicdata,indent=4)

    def Ordered(self,obj):

        if isinstance(obj, dict):
            return sorted((k,self.Ordered(v)) for k,  v in obj.items())
        if isinstance(obj, list):
            return sorted(self.Ordered(x) for x in obj )
        else:
            return obj

    def JsonCompare(self,SourceData,DestiData,FirstPara,SecondPara):

        try:
            SourceCompareDataDic = json.loads(SourceData)
            DestiCompareDataDic = json.loads(DestiData)
        except ValueError:
            print "SourceData or DestData is not JSON Type!"
            return False

        try:
            Socom = SourceCompareDataDic[FirstPara][SecondPara]
            Decom = DestiCompareDataDic[FirstPara][SecondPara]
        except KeyError,error:
            print "Key error ,This key is not found:%s"%error
            return False

        if str(Socom).lower()== str(Decom).lower():
            return True
        else:
            print "Source Compare data:"+FirstPara+"."+SecondPara+"="+str(Socom)
            print "Dest Compare data: "+FirstPara+"."+SecondPara+"="+str(Decom)
            return False

    def GatewayCompare(self,SourceData,DestiData,FirstPara,SecondPara,ThirdPara):

        try:
            SourceCompareDataDic = json.loads(SourceData)
            DestiCompareDataDic = json.loads(DestiData)
        except ValueError:
            print "SourceData or DestData is not JSON Type!"
            return False

        try:
            Socom = SourceCompareDataDic[FirstPara][SecondPara][ThirdPara]
            Decom = DestiCompareDataDic[FirstPara][SecondPara][ThirdPara]
        except KeyError,error:
            print "Key error ,This key is not found:%s"%error
            return False

        if str(Socom).lower()== str(Decom).lower():
            return True
        else:
            print "Source Compare data:"+FirstPara+"."+SecondPara+"="+str(Socom)
            print "Dest Compare data: "+FirstPara+"."+SecondPara+"="+str(Decom)
            return False


class RouterData(NetworkData):

    def __init__(self):
        self.id = '00001'
        self.tenant_id = '00002'
        self.state = 'ACTIVE'
        self.external_gateway_info = None
        self.name = 'router'
        self.gw_port_id = None
        self.admin_state_up = True
        self.routes = []
        
        self.network_id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        self.enable_snat = True 
        self.subnet_id = ''
        #self.ip_address = ''
        self.ip_address = '192.168.212.3'
        
        
    def DictoJson(self):
        if self.id == '' or self.tenant_id == '':
            print 'Id and tenant id is necessary!'
            
        Dicdata = {}
        
        external_fixed_ips = []
        external_fixed_ips.append({'subnet_id':self.subnet_id,'ip_address':self.ip_address})
        Dicdata1 = {} 
        if self.network_id != '':
            Dicdata1['network_id'] = self.network_id
        if self.enable_snat != '':
            Dicdata1['enable_snat'] = self.enable_snat
            Dicdata1['external_fixed_ips'] = external_fixed_ips 
            
        #external_gateway_info.append('network_id':self.network_id,'enable_snat':self.enable_snat,'external_fixed_ips':external_fixed_ips)           
         
        if self.id != '':
            Dicdata['id'] = self.id
        if self.tenant_id != '':
            Dicdata['tenant_id'] = self.tenant_id
        if self.state != '':
            Dicdata['status'] = self.state
        if self.subnet_id != '':
            Dicdata['external_gateway_info'] = Dicdata1
        if self.name != '':
            Dicdata['name'] = self.name
        if self.gw_port_id != '':
            Dicdata['gw_port_id'] = self.gw_port_id
        if self.admin_state_up != '':
            Dicdata['admin_state_up'] = self.admin_state_up
        if self.routes != '':
            Dicdata['routes'] = self.routes
            
        Dicdata = {'router': Dicdata}

        return json.dumps(Dicdata,indent=4)        

    def NoneGateway(self,SourceData):

        try:
            SourceDataDic = json.loads(SourceData)
        except ValueError:
            print "SourceData is not JSON Type!"
            return False
        DetinaDataDic = {}
        SourceDataDic['router']['external_gateway_info'] = None
        DetinaDataDic = SourceDataDic
        
        return json.dumps(DetinaDataDic,indent=4)
        
    
class RouterInterfaceData(NetworkData):
    
    def __init__(self):
        self.id = ''
        self.subnet_id = ''
        self.tenant_id = ''
        self.port_id = ''
        
    def DictoJson(self):
        if self.id == '' or self.subnet_id == '' or self.tenant_id == '' or self.port_id == '':
            print 'Id and tenant id and subnet id and port id is necessary!'
        
        Dicdata = {}
        if self.id != '':
            Dicdata['id'] = self.id
        if self.subnet_id != '':
            Dicdata['subnet_id'] = self.subnet_id
        if self.tenant_id != '':
            Dicdata['tenant_id'] = self.tenant_id
        if self.port_id != '':
            Dicdata['port_id'] = self.port_id
        
        return json.dumps(Dicdata,indent=4)

class FloatingIpData(NetworkData):
    
    def __init__(self):
        self.id = ''
        self.tenant_id = ''
        self.router_id = ''
        self.port_id = ''
        self.floating_network_id = ''
        self.fixed_ip_address = ''
        self.floating_ip_address = ''
        self.status = 'ACTIVE'
    
    def DictoJson(self):
        if self.id == '' or self.tenant_id == '' or self.router_id == '' or self.port_id == '':
            print 'Id and tenant id and router id and port id is necessary!'
        
        Dicdata = {}
        if self.id != '':
            Dicdata['id'] = self.id
        if self.tenant_id != '':
            Dicdata['tenant_id'] = self.tenant_id
        if self.router_id != '':
            Dicdata['router_id'] = self.router_id
        if self.port_id != '':
            Dicdata['port_id'] = self.port_id
        if self.floating_network_id != '':
	    Dicdata['floating_network_id'] = self.floating_network_id
        if self.floating_network_id != '':
            Dicdata['floating_ip_address'] = self.floating_network_id
        if self.fixed_ip_address != '':
            Dicdata['fixed_ip_address'] = self.fixed_ip_address
        if self.floating_ip_address != '':
            Dicdata['floating_ip_address'] = self.floating_ip_address
        if self.status != '':
            Dicdata['status'] = self.status
            
        Dicdata = {'floatingip': Dicdata}

        return json.dumps(Dicdata,indent=4)    
    
class SubnetData(NetworkData):

    def __init__(self):
        self.id = ''
        self.tenant_id = ''
        self.network_id = ''
        self.nexthop = '192.168.1.1'
        self.destination = '192.168.1.1/24'
        self.start = '192.168.2.2'
        self.end = '192.168.2.254'
        self.ipv6_address_mode = 'DHCPV6_STATELESS'
        self.ipv6_ra_mode = 'DHCPV6_STATELESS'
        self.cidr = '192.168.1.1/24'
        self.enable_dhcp = True
        self.dns_nameservers = 'aaa'
        self.gateway_ip = '192.168.2.1'
        self.ip_version = '4'
        self.shared = False
        self.name = 'demo-subnet'

    def DictoJson(self):
        if self.id =='' or self.tenant_id == '':
            print 'Id and tenant id is necessary!'

        Dicdata = {}
        host_routesdata = []
        host_routesdata.append({'nexthop': self.nexthop,'destination': self.destination})
        allocation_pools = []
        allocation_pools.append({'start': self.start,'end':self.end})

        if self.id != '':
            Dicdata['id'] = self.id
        if self.network_id != '':
            Dicdata['network_id'] = self.network_id
        if self.name != '':
            Dicdata['name'] = self.name
        if self.nexthop != '':
            Dicdata['host_routes'] = host_routesdata
        if self.tenant_id != '':
            Dicdata['tenant_id'] = self.tenant_id
        if self.start != '':
            Dicdata['allocation_pools'] = allocation_pools
        if self.shared != '':
            Dicdata['shared'] = self.shared
        if self.ipv6_address_mode != '':
            Dicdata['ipv6_address_mode'] = self.ipv6_address_mode
        if self.ipv6_ra_mode != '':
            Dicdata['ipv6_ra_mode'] = self.ipv6_ra_mode
        if self.cidr != '':
            Dicdata['cidr'] = self.cidr
        if self.enable_dhcp != '':
            Dicdata['enable_dhcp'] = self.enable_dhcp
        if self.dns_nameservers != '':
            Dicdata['dns_nameservers'] = self.dns_nameservers
        if self.gateway_ip != '':
            Dicdata['gateway_ip'] = self.gateway_ip
        if self.ip_version != '':
            Dicdata['ip_version'] = self.ip_version

        Dicdata = {'subnet': Dicdata}

        return json.dumps(Dicdata,indent=4)

class VirtualPortData(NetworkData):

    def __init__(self):
        self.id = ''
        self.state = 'ACTIVE'
        self.bindingHostId = 'fa:16:3e:76:8e:88'
        self.allowedAddressPairs = [{'mac_address':'fa:16:3e:76:8e:88','ip_address':'192.168.1.1'}]
        self.deviceOwner = 'none'
        self.fixedIp = []
        self.ip_address = '192.168.1.4'
        self.securityGroups = [{'securityGroup':'asd'}]
        self.adminStateUp = True
        self.network_id = ''
        self.tenant_id = ''
        self.subnet_id = ''
        self.bindingvifDetails = 'port_filter'
        self.bindingvnicType = 'normal'
        self.bindingvifType = 'ovs'
        self.macAddress = 'fa:16:3e:76:8e:88'
        self.deviceId = 'a08aa'
        self.name = 'u'

    def DictoJson(self):
        if self.id == '' or self.tenant_id == ' ' or \
           self.network_id == '' or self.subnet_id == '':
            print 'Id/tenant id/networkid/subnetId is necessary!'

        Dicdata = {}
        fixedIp =[]
        fixedIp.append({'subnet_id':self.subnet_id,'ip_address':self.ip_address})
        allocation_pools = []

        if self.id != '':
            Dicdata['id'] = self.id
        if self.state != '':
            Dicdata['status'] = self.state
        if self.bindingHostId != '':
            Dicdata['binding:host_id'] = self.bindingHostId
        if self.allowedAddressPairs != '':
            Dicdata['allowed_address_pairs'] = self.allowedAddressPairs
        if self.deviceOwner != '':
            Dicdata['device_owner'] = self.deviceOwner
        if self.securityGroups != '':
            Dicdata['security_groups'] = self.securityGroups
        if self.adminStateUp != '':
            Dicdata['admin_state_up'] = self.adminStateUp
        if self.network_id != '':
            Dicdata['network_id'] = self.network_id
        if self.tenant_id != '':
            Dicdata['tenant_id'] = self.tenant_id
        if self.bindingvifDetails != '':
            Dicdata['binding:vif_details'] = self.bindingvifDetails
        if self.bindingvnicType != '':
            Dicdata['binding:vnic_type'] = self.bindingvnicType
        if self.bindingvifType != '':
            Dicdata['binding:vif_type'] = self.bindingvifType
        if self.macAddress != '':
            Dicdata['mac_address'] = self.macAddress
        if self.deviceId != '':
            Dicdata['device_id'] = self.deviceId
        if self.name != '':
            Dicdata['name'] = self.name

        Dicdata['fixed_ips'] = fixedIp
        Dicdata = {'port': Dicdata}

        return json.dumps(Dicdata,indent=4)
