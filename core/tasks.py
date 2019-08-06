import socket
import netifaces
import ipaddress
import netaddr
from .models import Machine
import os
import nmap
from celery import shared_task
import  datetime
import platform
import boto
import boto.vpc
import boto.ec2

@shared_task
def roam(project):
    #  need to modify the code to enumerate the interfaces better
    returnList = []
    localinfo = getlocalinfo(project)
    inet_addrs = netifaces.ifaddresses(localinfo.split("$")[2])
    ips = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())
    print "IP Range: " + ips
    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    print "Gateway: " + gateway
    subnet = localinfo.split("$")[1] # will assume same subnet for all LAN IPs
    print "Subnet: " + subnet
    gatewaynewnode = makeanode(gateway, subnet,project,1,"SCAN","",True)
    returnList.append(gatewaynewnode)
    addaction(project,"ROAM",ips,gatewaynewnode)
    live_ip_nodes = networkscan(ips)

    for ip in live_ip_nodes:
        node = makeanode(ip,subnet,project,2,"SCAN","",True)
        returnList.append(node)
        gatewaynewnode.connected.connect(node)
        addaction(project, "ROAM", ips, node)
    return returnList

@shared_task
def traceroute(hostname, port, max_hops,project,doaddaction):
    returnList = []
    destination = socket.gethostbyname(hostname)
    print "Target: " + hostname

    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    nodes = ""
    edges = ""
    localinfo = getlocalinfo(project)
    localip = localinfo.split("$")[0]
    subnet = localinfo.split("$")[1]
    previousnode = makeanode(localip,subnet,project,0,"SEED","",True)
    returnList.append(previousnode)
    if doaddaction:
        addaction(project,"GOTO",hostname,previousnode)

    while True:
        recvsock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        recvsock.settimeout(5)
        sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        sendsock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recvsock.bind(("", port))
        sendsock.sendto("", (hostname, port))
        currentaddr = None
        currenthost = None
        try:
            _, currentaddr = recvsock.recvfrom(512)
            currentaddr = currentaddr[0]
            try:
                currenthost = socket.gethostbyaddr(currentaddr)[0]
            except socket.error:
                currenthost = currentaddr
        except socket.error:
            pass
        finally:
            sendsock.close()
            recvsock.close()

        if currentaddr is not None:
            currenthost = currentaddr
            nodes += "{ id : " + str(ttl + 1) + ", group : 'device', label : '" + currenthost + "'},"
            edges += "{ from: " + str(ttl) + ", to: " + str(ttl + 1) + " },"
            newnode = makeanode(currenthost,subnet,project,ttl,"TRACEROUTE","",True)
            returnList.append(newnode)
            previousnode.connected.connect(newnode)
            previousnode = newnode
            if doaddaction:
                addaction(project, "GOTO", hostname, newnode)
        ttl += 1
        if currentaddr == destination or ttl > max_hops:
            break
    return returnList

def makeanode(ip,subnet,project,distance,origin,enum,doenum):
    try:
        checknode = Machine.nodes.get(ip=ip,tag__startswith=project)
        print "Node exist: " + checknode.ip
        if doenum:
            nmapenumeration(checknode)
        else:
            checknode.enum = enum
            checknode.save()
    except Machine.DoesNotExist as ex:
        print "Exception: " + str(ex)
        try:
            hostname = socket.gethostbyaddr(ip.split("#")[0])[0]
        except Exception as ex:
            print "Exception: " + str(ex)
            hostname = ip
        print "Hostname: " + hostname

        count = len(Machine.nodes.filter(distance=distance).filter(tag__startswith=project))
        if ipaddress.ip_address(unicode(ip.split("#")[0])).is_private:
            tag = project + "#" + origin + "#INTERNAL#UP"
        else:
            tag = project + "#" + origin + "#EXTERNAL#UP"

        if origin == "SEED":
            findseed = project + "#SEED"
            try:
                seednode = Machine.nodes.get(tag__startswith=findseed)
                seednode.tag = str(seednode.tag).replace("SEED", "SCAN")
                seednode.save()
            except Exception as ex:
                print "Exception: " + str(ex)

        cloud = ""
        if origin == "AWS":
            print enum
            cloud = enum.split("$")[1]
            enum = enum.split("$")[0]

        newnode = Machine(ip=ip, hostname=hostname, subnet=subnet,tag=tag, distance=distance,queue=count,action="",enum=enum,cloud=cloud)
        newnode.save()
        print "New Node: " + newnode.ip
        if doenum:
            nmapenumeration(newnode)
        else:
            newnode.enum = enum
            newnode.save()
        return newnode

    return checknode

@shared_task
def scan(scanrange,project_id,doaddaction):
    print "Starting scan: " + str(scanrange)
    returnlist = []
    localinfo = getlocalinfo(project_id)
    inet_addrs = netifaces.ifaddresses(
        localinfo.split("$")[2])  # need to modify the code to enumerate the interfaces properly
    local_ip_range = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(
        netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())
    print "Local IP range " + local_ip_range

    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    subnet = inet_addrs[netifaces.AF_INET][0]['netmask']  # will assume same subnet for all LAN IPs
    gatewaynewnode = makeanode(gateway, subnet, project_id, 1, "SCAN", "",True)
    returnlist.append(gatewaynewnode)
    localnode = makeanode(localinfo.split("$")[0],localinfo.split("$")[1],project_id,0,"SEED","",True)
    returnlist.append(localnode)
    localnode.connected.connect(gatewaynewnode)

    if doaddaction:
        addaction(project_id, "SCAN", scanrange, gatewaynewnode)
        addaction(project_id,"SCAN",scanrange,localnode)

    try:
        if netaddr.IPNetwork(scanrange).is_private():
            scanresult = networkscan(scanrange)
            for ip in scanresult:
                try:
                    if netaddr.IPAddress(ip) in netaddr.IPNetwork(local_ip_range):
                        print "In local range: " + ip
                        node = makeanode(ip, subnet, project_id, 2, "SCAN", "",True)
                        returnlist.append(node)
                        gatewaynewnode.connected.connect(node)
                        if doaddaction:
                            addaction(project_id,"SCAN",scanrange,node)
                    else:
                        print "Not in local range " + ip
                        print "Performing traceroute to " + ip
                        print traceroute(ip,33434, 30, project_id,False)
                except Exception as ex:
                    print str(ex)
                    print ip
                    print str(node)
                    print returnlist
    except Exception as ex:
        try:
            print str(ex)
            socket.gethostbyname(scanrange)
            print "Not an internal IP " + scanrange
            print "Performing traceroute to " + scanrange
            path = traceroute(scanrange, 33434, 30, project_id,False)
            print path
        except Exception as ex:
            print "Invalid input " + scanrange
            print str(ex)

    return returnlist

def networkscan(scanrange):
    nm = nmap.PortScanner()
    if os.path.exists(os.path.dirname(scanrange)):
        nm.scan(scanrange,arguments="-PE -sn -iL")
    else:
        nm.scan(scanrange,arguments="-PE -sn") # ping scan only - can be modified
    return nm.all_hosts()

def nmapenumeration(node):
    if "SEED" in str(node.tag):
        node.enum = platform.system() + "#" + platform.platform()
        node.save()
        print "Update for SEED " + node.enum
        return {"Status",True}
    if ipaddress.ip_address(unicode(node.ip)).is_private:
        print "Enumeration started " + node.ip
        nm = nmap.PortScanner()
        nm.scan(str(node.ip), arguments="--top-ports 5 -O")
        try:
            osidentified = False
            if "osmatch" in nm[str(node.ip)].keys():
                for osmatch in nm[str(node.ip)]['osmatch']:
                    if int(osmatch['accuracy']) > 90:
                        if "linux" in str(osmatch['name'] + osmatch['osclass'][0]['type']).lower():
                            node.enum = "Linux#" + osmatch['name'] + "#" + osmatch['osclass'][0]['type']
                        elif "switch" in str(osmatch['name'] + osmatch['osclass'][0]['type']).lower():
                            node.enum = "Switch#" + osmatch['name'] + "#" + osmatch['osclass'][0]['type']
                        elif "windows" in str(osmatch['name'] + osmatch['osclass'][0]['type']).lower():
                            node.enum = "Windows#" + osmatch['name'] + "#" + osmatch['osclass'][0]['type']
                        elif "voip" in str(osmatch['name'] + osmatch['osclass'][0]['type']).lower():
                            node.enum = "VoIP#" + osmatch['name'] + "#" + osmatch['osclass'][0]['type']
                        elif "router" in str(osmatch['name'] + osmatch['osclass'][0]['type']).lower():
                            node.enum = "Router#" + osmatch['name'] + "#" + osmatch['osclass'][0]['type']
                        node.save()
                        print "Updated for " + node.ip + " with " + node.enum
                        osidentified = True
                        break
            if not osidentified:
                nm.scan(str(node.ip), ports='445', arguments="--script smb-os-discovery")
                if "hostscript" in nm[str(node.ip)].keys():
                    if "linux" in str(nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[1].split(":")[1].strip() + "#" + nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[2].split(":")[1].strip()).lower():
                        node.enum = "Linux#" + nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[1].split(":")[1].strip() + "#" + nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[2].split(":")[1].strip()
                    elif "windows" in str(nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[1].split(":")[1].strip() + "#" + nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[2].split(":")[1].strip()).lower():
                        node.enum = "Windows#" + nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[1].split(":")[1].strip() + "#" + nm[str(node.ip)]['hostscript'][0]['output'].splitlines()[2].split(":")[1].strip()
                    print "Updated for " + node.ip + " with " + node.enum
                    node.save()
                    # below code is for banner grabbing for top10 ports
                    # else:
                    #     node = makeanode(ip, subnet, project_id, 2, "SCAN", "")
                    #     # need to add below in logic
                    # nm = nmapenumeration(ip,"--top-ports 10 --script banner")
                    # for port in nm[ip]['tcp'].keys():
                    #     if nm[ip]['tcp'][port]['state'] == 'open':
                    #         node = makeanode(ip, subnet, project_id, 2, "SCAN", nm[ip]['tcp'][port]['script']['banner'])
                    #     else:
                    #         node = makeanode(ip, subnet, project_id, 2, "SCAN", "")
        except Exception as ex:
            print "Exception " + str(ex)
            return {"Status":str(ex)}
        return {"Status":str(nm)}
    else:
        print "Not a private IP, skipping it " + node.ip
        return {"Status":False}

def getlocalinfo(project):
    localip = ""
    subnet = ""
    localinterface = ""
    for interface in netifaces.interfaces():
        print "Processing: " + interface
        try:
            inet_addrs = netifaces.ifaddresses(interface)
            currentip = ipaddress.ip_address(unicode(inet_addrs[netifaces.AF_INET][0]['addr']))
            currentsubnet = inet_addrs[netifaces.AF_INET][0]['netmask']
            print "current ip: " + str(currentip) + " " + currentsubnet
            if (not currentip.is_loopback and currentip.version == 4):
                localip = str(currentip)
                subnet = str(currentsubnet)
                localinterface = interface
                break #picking only first valid IP, as of now
        except Exception as ex:
            print ex
    makeanode(localip, subnet, project, 0, "SEED","",True)
    return localip + "$" + subnet + "$" + localinterface

def listCloud(project_id):
    cloudList = []
    for node in Machine.nodes.filter(tag__startswith=project_id):
        if node.cloud != "":
            cloudList.append(str(node.cloud).split("#")[0])

    cloudList = list(set(cloudList)).sort()
    return cloudList

def listActions(project_id):
    actionList = []
    findseed = project_id + "#SEED"
    node = Machine.nodes.get(tag__startswith=findseed)
    actions = node.action.split("$")

    for action in actions:
        if "#" in action:
            actionList.append(str(action).split("#")[1].split('@')[0])
    actionList = list(set(actionList))
    return actionList

def listHistory(project_id):
    historyList = []
    findseed = project_id + "#SEED"
    node = Machine.nodes.get(tag__startswith=findseed)
    actions = node.action.split("$")

    for action in actions:
        if "#" in action:
            historyList.append(str(action))

    historyList = list(set(historyList))
    return historyList

def listEnums(project_id):
    enumList = ["Unknown"]

    for node in Machine.nodes.filter(tag__startswith=project_id):
        if "#" in node.enum:
            enumList.append(str(node.enum).split("#")[0])

    enumList = list(set(enumList)).sort()
    return enumList

def addaction(project_id,action, param, node):
    if str(action + "#" + param) in node.action:
        print "Action already added"
    else:
        node.action = node.action + "$" + action + "#" + param
        node.save()
        print "Action updated: " + node.action


@shared_task
def cmdbprocess(scanrange,beintrusive,filename,project_id):
    localipstring = getlocalinfo(project_id)
    localip = str(localipstring).split("$")[0]
    subnet = str(localipstring).split("$")[1]
    interface = str(localipstring).split("$")[2]
    print "processing " + str(len(localip)) + "local interfaces " + interface
    cmdb_file_ips = []

    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    print "Gateway: " + gateway

    gatewaynewnode = makeanode(gateway, subnet, project_id, 1, "CMDB", "",True)
    localnode = makeanode(localip, subnet, project_id, 0, "CMDB", "",True)
    gatewaynewnode.connected.connect(localnode)
    addaction(project_id, "CMDB", filename, gatewaynewnode)
    addaction(project_id, "CMDB", filename, localnode)

    for line in scanrange:
        try:
            ipaddress.ip_address(line)
            cmdb_file_ips.append(line)
            print "scanning IP " + line
            scanresult = networkscan(line)
            print "Scan results " + str(scanresult)
            for ip in scanresult:
                local_ip_range = localip + "/" + str(netaddr.IPAddress(subnet).netmask_bits())
                if netaddr.IPAddress(ip) in netaddr.IPNetwork(local_ip_range):
                    print "in local range"
                    node = makeanode(ip, subnet, project_id, 2,"CMDB","",True)
                    gatewaynewnode.connected.connect(node)
                    addaction(project_id,"CMDB",filename,node)
                else:
                    print "performing traceroute to " + ip
                    output = traceroute.delay(ip, 33434, 30, project_id,True)
                    findseed = project_id + "#SEED"
                    seednode = Machine.nodes.get(tag__startswith=findseed)
                    addaction(project_id, "GOTO",ip + "@" + str(output) + "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode)
        except Exception as ex:
            print str(ex)
            print "Not a valid IP. Ignoring " + line

    if str(beintrusive) == "on":
        local_ip_range = gateway + "/" + str(netaddr.IPAddress(subnet).netmask_bits())
        output = cmdbanalysis.delay(local_ip_range,cmdb_file_ips,project_id,filename)
        findseed = project_id + "#SEED"
        seednode = Machine.nodes.get(tag__startswith=findseed)
        addaction(project_id, "CMDB", str(local_ip_range) + "@" + str(output) + "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode)
        output = traceroute.delay("google.com", 33434, 30, project_id,True)  # perform traceroute to (multiple?)google.com
        seednode = Machine.nodes.get(tag__startswith=findseed)
        addaction(project_id, "GOTO","google.com" + "@" + str(output) + "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode)
    return {"Status":True}

@shared_task
def cmdbanalysis(localrange,cmdb_file_ips,project_id,filename):
    localipstring = getlocalinfo(project_id)
    localip = str(localipstring).split("$")[0]
    subnet = str(localipstring).split("$")[1]
    interface = str(localipstring).split("$")[2]
    print "processing " + str(len(localip)) + "local interfaces " + interface
    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    print "Gateway: " + gateway
    gatewaynewnode = makeanode(gateway, subnet, project_id, 1, "CMDB", "",True)
    addaction(project_id, "CMDB", localrange, gatewaynewnode)
    scanresult = networkscan(localrange)
    print str(scanresult)
    for ip in scanresult:
        origin = "DISCOVERED"
        for cmdb_file_ip in cmdb_file_ips:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(cmdb_file_ip):
                origin = "CMDB"
                break
        node = makeanode(ip, subnet, project_id, 2, origin, "",True)
        addaction(project_id, "CMDB", localrange, node)
        addaction(project_id, "CMDB", filename, node)
        gatewaynewnode.connected.connect(node)

@shared_task
def aws_processing(access_key,access_id,region,project_id):
    try:
        vpcconn = boto.vpc.connect_to_region(region,aws_access_key_id=access_id,aws_secret_access_key=access_key)
    except Exception as ex:
        print str(ex)
    vpcs = vpcconn.get_all_vpcs()
    for vpc in vpcs:
        print "Processing instances..."
        subnets = vpcconn.get_all_subnets(filters={'vpc-id': vpc.id})
        for subnet in subnets:
            ec2conn = boto.ec2.connect_to_region(region)
            instances = ec2conn.get_only_instances(filters={'vpc-id': vpc.id, 'subnet-id': subnet.id})
            enum = "InlineRouter#" + subnet.id + "$" + vpc.id
            routernode = makeanode(str(ipaddress.IPv4Network(subnet.cidr_block)[1]),str(ipaddress.IPv4Network(subnet.cidr_block).netmask), project_id, 2, "AWS", enum,False)
            routernode.save()
            addaction(project_id,"AWS",region,routernode)
            if len(instances) <= 0:
                routernode.tag = str(routernode.tag).replace("#UP","#DOWN")
                routernode.distance = -1
                routernode.save()
            for instance in instances:
                try:
                    if "windows" in str(instance.platform).lower():
                        enum = str(instance.platform).capitalize() + "#" + subnet.id + "#" + instance.state + "#" + instance.placement + "$" + vpc.id
                    else:
                        enum = "Linux#" + subnet.id + "#" + instance.state + "#" + instance.placement + "$" + vpc.id
                    instancenode = makeanode(instance.private_ip_address,str(ipaddress.IPv4Network(subnet.cidr_block).netmask),project_id,1,"AWS",enum,False)
                    instancenode.connected.connect(routernode)
                    instancenode.save()
                    addaction(project_id, "AWS", region, instancenode)
                    if "ec2" in instance.public_dns_name:
                        print "Making it PUBLIC " + instance.public_dns_name
                        instancenode.ip = parsepublicip(instance.public_dns_name)
                        instancenode.hostname = instance.public_dns_name
                        instancenode.tag = str(instancenode.tag).replace("INTERNAL","EXTERNAL")
                        instancenode.save()

                except Exception as ex:
                    print str(ex)

        print "Processing routes..."
        route_tables = vpcconn.get_all_route_tables(filters={'vpc-id': vpc.id})
        for route_table in route_tables:
            for association in route_table.associations:
                if not (association.subnet_id is None):
                    subnet = vpcconn.get_all_subnets(filters={'vpc-id': vpc.id,"subnet-id":association.subnet_id})
                    enum = "InlineRouter#" + "#" + subnet[0].id + "$" + vpc.id
                    subnetnode = makeanode(str(ipaddress.IPv4Network(subnet[0].cidr_block)[1]),str(ipaddress.IPv4Network(subnet[0].cidr_block).netmask), project_id, 2, "AWS",enum, False)
                    addaction(project_id, "AWS", region, subnetnode)
                    for route in route_table.routes:
                        if str(route.state).startswith("active"):
                            if not (route.destination_cidr_block is None):
                                if not (route.gateway_id is None or route.gateway_id in "local"):
                                    if str(route.gateway_id).startswith("igw"):
                                        enum = "InternetGateway#" + str(route.gateway_id) + "$" + vpc.id
                                        igw = vpcconn.get_all_internet_gateways(internet_gateway_ids=route.gateway_id)
                                        igwnode = makeanode("1.1.1.1","255.255.255.255",project_id, 3, "AWS", enum, False) # need to check for node which don't have IP
                                        subnetnode.connected.connect(igwnode)
                                        addaction(project_id, "AWS", region, igwnode)
                                        igwnode.save()
                                        subnetnode.save()
                                    elif str(route.gateway_id).startswith("vgw"):
                                        enum = "VPNGateway#" + str(route.gateway_id) + "$" + vpc.id
                                        vpngw = vpcconn.get_all_vpn_gateways(vpn_gateway_ids=route.gateway_id)
                                        vpngwnode = makeanode("1.1.1.1", "255.255.255.255", project_id, 3, "AWS", enum,
                                                            False)  # need to check for node which don't have IP
                                        subnetnode.connected.connect(vpngwnode)
                                        addaction(project_id, "AWS", region, vpngwnode)
                                        vpngwnode.save()
                                        subnetnode.save()
                                elif not (route.vpc_peering_connection_id is None):
                                    peer = vpcconn.get_all_vpc_peering_connections(vpc_peering_connection_ids=[route.vpc_peering_connection_id])
                                    if str(peer[0].accepter_vpc_info.vpc_id) in str(vpc.id):
                                        enum = "VPCPeer#" + peer[0].requester_vpc_info.vpc_id + "$" + vpc.id
                                        peernode = makeanode(str(ipaddress.IPv4Network(peer[0].requester_vpc_info.cidr_block)[1]),str(ipaddress.IPv4Network(peer[0].requester_vpc_info.cidr_block).netmask),project_id, 4, "AWS", enum, False)
                                    else:
                                        enum = "VPCPeer#" + peer[0].accepter_vpc_info.vpc_id + "$" + vpc.id
                                        peernode = makeanode(
                                            str(ipaddress.IPv4Network(peer[0].accepter_vpc_info.cidr_block)[1]),
                                            str(ipaddress.IPv4Network(peer[0].accepter_vpc_info.cidr_block).netmask),
                                            project_id, 4, "AWS", enum, False)
                                    peernode.save()
                                    addaction(project_id, "AWS", region, peernode)
                                    subnetnode.connected.connect(peernode)
                                    subnetnode.save()
                                elif not (route.interface_id is None):
                                    instance = ec2conn.get_only_instances(filters={'instance-id': route.instance_id})
                                    if "windows" in str(instance[0].platform).lower():
                                        enum = str(instance[0].platform).capitalize() + "#" + subnet[0].id + "#" + instance[0].state + "#" + instance[0].placement + "$" + vpc.id
                                    else:
                                        enum = "Linux#" + "#" + subnet[0].id + "#" + instance[0].state + "#" + instance[0].placement + "$" + vpc.id
                                    instancenode = makeanode(instance[0].private_ip_address,str(ipaddress.IPv4Network(subnet[0].cidr_block).netmask), project_id,1, "AWS", enum, False)
                                    subnetnode.connected.connect(instancenode)
                                    addaction(project_id, "AWS", region, instancenode)
                                    subnetnode.save()
                                    instancenode.save()
                                else:
                                    print "Unprocessed route " + str(route.gateway_id)
                        else:
                            print "Route is not processed for " + str(route.destination_cidr_block) + " (" + str(route.state) + ")"

def parsepublicip(hostname):
    splits = hostname.split("-")
    return splits[1] + "." + splits[2] + "." + splits[3] + "." + splits[4].split(".")[0]