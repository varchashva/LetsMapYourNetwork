# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from scapy.all import *
from platform import system as system_name # Returns the system/OS name
from os import system as system_call       # Execute a shell command -> Replace with subprocess
import socket
import netifaces
import ipaddress
import netaddr
import sys

from .forms import ProjectForm,GoToForm,ScanForm,NewProjectForm,CMDBScanForm

from django import forms

from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Machine
from django.core.files.storage import FileSystemStorage
import neomodel
import os



import nmap

def index(request):
    return redirect("/core/default/action")

def action(request, project_id):

    print "Start Action"
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    action = "show"

    # validation of project_id
    print "Current Project: " + project_id
    print "Project Count: " + str(len(projectform.PROJECT_CHOICES))


    # projectAvailble = False
    # for i in range(0, len(projectform.PROJECT_CHOICES)):
    #     key, value = projectform.PROJECT_CHOICES[i]
    #     if project_id == key:
    #         print "Got Project: " + project_id
    #         projectAvailble = True
    #         break
    #
    # if not projectAvailble:
    #     print "Info: Project Not Found. Returning to default..."
    #     return redirect("/core/default/action")

    if request.method == "POST":
        print "Info: Request is POST"
        print "Debug: "+ str(request.POST)
        if "goto_target" in request.POST:
            gotoform = GoToForm(request.POST)
            # scanform = ScanForm()
            # projectform = ProjectForm()
            # newprojectform = NewProjectForm()
            if gotoform.is_valid():
                action = "goto"
                goto_target = gotoform.cleaned_data["goto_target"]
        elif "scanrange" in request.POST:
            scanform = ScanForm(request.POST)
            # gotoform = GoToForm()
            # projectform = ProjectForm()
            # newprojectform = NewProjectForm()
            if scanform.is_valid():
                action = "scan"
                scanrange = scanform.cleaned_data["scanrange"]
        elif "newproject" in request.POST:
            newprojectform = NewProjectForm(request.POST)
            # scanform = ScanForm()
            # gotoform = GoToForm()
            # projectform = ProjectForm(request.POST)
            print "In new project create block"
            if newprojectform.is_valid():
                project_id = str(newprojectform.cleaned_data["newproject"])
                action = "create"
                print "New Project: " + project_id
        elif "project" in request.POST:
            projectform = ProjectForm(request.POST)
            # scanform = ScanForm()
            # gotoform = GoToForm()
            # newprojectform = NewProjectForm()
            if projectform.is_valid():
                action="select"
                project_id = str(projectform.cleaned_data["project"])
                print "Project: " + project_id
        elif request.FILES['cmdbfilepath']:
            print "IN CMDB"
            print "Files: " + str(request.FILES['cmdbfilepath'].name)
            action = "cmdb"
            print "Action in CMDB " + action
            print "Project: " + project_id
    else:
        action=request.GET.get("action","show")
        # scanform = ScanForm()
        # gotoform = GoToForm()
        # projectform = ProjectForm()
        # newprojectform = NewProjectForm()
    print "Action is : " + action

    if "findme" in action:
        # project = request.GET.get("project","")
        # if project == "":
        #     project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        # print "Project in FindMe: "+ project
        output = getlocalinfo(project_id)
        context = {"project_id": project_id, "newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "goto" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        gotocelery = traceroute(goto_target,33434,30,project_id)
        #output = gotocelery.get()
        context = {"project_id": project_id, "newprojectform":newprojectform,  "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "roam" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        myneighbours = roam(project_id)
        context = {"project_id": project_id, "newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "clear" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        clear(project_id)
        context = {"project_id": project_id,"newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "scan" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        scanresult = networkscan(scanrange)

        interface = netifaces.interfaces()[1]
        inet_addrs = netifaces.ifaddresses(netifaces.interfaces()[1])  # need to modify the code to enumerate the interfaces propoerly
        local_ip_range = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(
            netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())
        # ips = netifaces.gateways()['default'][netifaces.AF_INET][0]
        print "Local IP range " + local_ip_range

        gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        subnet = inet_addrs[netifaces.AF_INET][0]['netmask']  # will assume same subnet for all LAN IPs
        gatewaynewnode = makeanode(gateway, subnet, project_id, 1,"SCAN")

        for ip in scanresult:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(local_ip_range):
                print "in local range"
                node = makeanode(ip,subnet,project_id,2,"SCAN")
                gatewaynewnode.connected.connect(node)
            else:
                print "performing traceroute to " + ip
                traceroute(ip,33434,30,project_id)
        context = { "project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                    "projectform": projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "select" in action:
        # print "In Select: " + str(projectform.PROJECT_CHOICES)
        # print "Len: "+ str(len(projectform.PROJECT_CHOICES))
        print "Project List in Select: " + str(projectform.PROJECT_CHOICES)
        # for i in range(0, len(projectform.PROJECT_CHOICES)):
        #     key, value = projectform.PROJECT_CHOICES[i]
        #     if project in key:
        #         project_id = i + 1
        #         break
        # project, test = projectform.PROJECT_CHOICES[project_id-1]
        # project_id = projectform.PROJECT_CHOICES.index(projectform.PROJECT_CHOICES[str(project)])
        # print "Project and ID: " + project + str(project_id)
        context = {"project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                   "projectform": projectform,"cmdbform":cmdbform}
        return redirect("/core/" + str(project_id) + "/action")
        # return render(request, 'project.html', context)
    elif "create" in action:
        # tuple = (project_id,project_id)
        # projectform.PROJECT_CHOICES.append(tuple)
        # # print "Project Form: " + str(projectform)
        # print "Project List in create: " + str(projectform.PROJECT_CHOICES)
        # projectform.fields["project"] = forms.CharField(widget=forms.Select(choices=projectform.PROJECT_CHOICES),label="")
        # project_id = len(projectform.PROJECT_CHOICES) + 1
        # print "Project ID in Create: " + str(project_id)

        # project, test = projectform.PROJECT_CHOICES[project_id-1]
        output = getlocalinfo(project_id)
        # neomodel.db.set_connection('bolt://neo4j:Neo4j@localhost:7687')
        # neomodel.Database.__init__()
        print "Reinitialized DB"
        # print "Project Count in Create: " + str(len(projectform.PROJECT_CHOICES))
        context = {"project_id": project_id, "newprojectform": newprojectform,
                   "gotoform": gotoform,
                   "scanform": scanform,
                   "projectform": projectform,"cmdbform":cmdbform}
        # return render(request, 'project.html', context)
        return redirect("/core/" + str(project_id) + "/action")
    elif "cmdb" in action:
        # for interface in netifaces.interfaces():
        #     inet_addrs = netifaces.ifaddresses(interface)  # need to modify the code to enumerate the interfaces propoerly
        #
             # local_ip_range = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(
             #     netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())
        #
        #     local_ip_range = "10.20.11.1/24"
        #     # ips = netifaces.gateways()['default'][netifaces.AF_INET][0]
        # print "Local IP range " + local_ip_range
        #
        # gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        # subnet = inet_addrs[netifaces.AF_INET][0]['netmask']  # will assume same subnet for all LAN IPs
        # gatewaynewnode = makeanode(gateway, subnet, project_id, 1,"CMDB")

        localipstring = getlocalinfo(project_id) # form: ip1#ip2#ip3$subnet1#subnet2#ip3
        ip_ranges = str(localipstring).split("$")[0].split("#")
        subnet_ranges = str(localipstring).split("$")[1].split("#")
        print "processing "+ str(len(ip_ranges)) + "local interfaces"
        cmdb_file_ips = []

        localnode = makeanode(ip_ranges[0],subnet_ranges[0],project_id,0,"CMDB")

        for line in request.FILES['cmdbfilepath']:
            cmdb_file_ips.append(line)
            print "scanning IP " + line
            scanresult = networkscan(line)
            for ip in scanresult:
                for i in range(0,len(ip_ranges)):
                    local_ip_range = ip_ranges[i]+"/"+str(netaddr.IPAddress(subnet_ranges[i]).netmask_bits())
                    if netaddr.IPAddress(ip) in netaddr.IPNetwork(local_ip_range):
                        print "in local range"
                        node = makeanode(ip, subnet_ranges[i], project_id, 2,"CMDB")
                        localnode.connected.connect(node)
                    else:
                        print "performing traceroute to " + ip
                        traceroute(ip, 33434, 30, project_id)

        print "Here it is " + str(request.POST.get("beintrusive", None))
        if str(request.POST.get("beintrusive", None)) == "on":
            for i in range(0,len(ip_ranges)):
                local_ip_range = ip_ranges[i] + "/" + str(netaddr.IPAddress(subnet_ranges[i]).netmask_bits())
                scanresult = networkscan(local_ip_range )# Scan all live LOCAL IPs
                for ip in scanresult:
                    origin = "DISCOVERED"
                    for cmdb_file_ip in cmdb_file_ips:
                        if netaddr.IPAddress(ip) in netaddr.IPNetwork(cmdb_file_ip):
                            origin = "CMDB"
                            break
                    node = makeanode(ip,subnet_ranges[i],project_id,2,origin)
                    localnode.connected.connect(node)
                # gatewaynewnode.connected.connect(node)
            traceroute("google.com",33434,30,project_id) # perform traceroute to google.com
        return redirect("/core/" + str(project_id) + "/action")
    else:
        context = {"project_id": project_id,"newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)

def clear(project_id):
    for allnodes in Machine.nodes.get(tag__startswith=project_id):
        allnodes.delete()
    return "Info: all clear"

def getlocalinfo(project):
    localip = ""
    subnet = ""
    for interface in netifaces.interfaces():
        print "processing: " + interface
        try:
            inet_addrs = netifaces.ifaddresses(interface)
            currentip = ipaddress.ip_address(unicode(inet_addrs[netifaces.AF_INET][0]['addr']))
            currentsubnet = inet_addrs[netifaces.AF_INET][0]['netmask']
            print "current ip: " + str(currentip) + " " + currentsubnet
            if (not currentip.is_loopback and currentip.version == 4):
                localip = str(localip) + "#" + str(currentip)
                subnet = subnet + "#" + currentsubnet
                break #picking only first valid IP as of now
        except Exception as ex:
            print ex
    makeanode(localip.strip("#"), subnet.strip("#"), project, 0, "SEED")
    return localip.strip("#") + "$" + subnet.strip("#")

    # localhostname = socket.gethostbyaddr(localip)
    # print localhostname[0]


    # gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    # print "Gateway: " + gateway
    #
    # gatewaynode =  makeanode(gateway,subnet,project,1,"FINDME")
    #
    # localnode.connected.connect(gatewaynode)
    # # gatewayhostname = socket.gethostbyaddr(gateway)
    # print gatewayhostname[0]

    # return localip
    # return localip + "#" +localhostname[0] +"#" + subnet + "#" + gateway + "#" + gatewayhostname[0]

def roam(project):

    ip_list = []

    # Code for ARP Scanning
    interface = netifaces.interfaces()[1]
    inet_addrs = netifaces.ifaddresses(netifaces.interfaces()[1]) # need to modify the code to enumerate the interfaces propoerly
    ips = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())
    # ips = netifaces.gateways()['default'][netifaces.AF_INET][0]

    print "Interface: " + interface
    print "IP Range: " + ips

    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    print "Gateway: " + gateway

    subnet = inet_addrs[netifaces.AF_INET][0]['netmask'] # will assume same subnet for all LAN IPs
    print "Subnet: " + subnet

    gatewaynewnode = makeanode(gateway, subnet,project,1,"SCAN")
    ip = "10.20.11.1/24"
    live_ip_nodes = networkscan(ips)

    for ip in live_ip_nodes:
        node = makeanode(ip,"255.255.255.255",project,2,"SCAN")  # need to change the subnet ICMP Address Mask Ping (-PM)
        gatewaynewnode.connected.connect(node)

    # print "Starting ARP Scanning" # changing with nmap ping scan
    # conf.verb = 0
    # for ip in netaddr.IPNetwork(ips):
    #     ip = str(ip)
    #     # print ip
    #     if ip == gateway:
    #         continue
    #     ans, unans = srp(Ether(dst="FF:FF:FF:FF:FF:FF")/ARP(pdst=ip), timeout=2, iface=interface, inter=0.1)
    #     for src, rcv in ans:
    #         print "Live Host: " + rcv.sprintf("%ARP.psrc%")
    #         newnode = makeanode(rcv.sprintf("%ARP.psrc%"),subnet)
    #         # newnode = Machine(ip=rcv.sprintf("%ARP.psrc%"), hostname=socket.gethostbyaddr(rcv.sprintf("%ARP.psrc%"))[0], subnet="255.255.255.0") # need to include the correct subnet mask
    #         # newnode.save()
    #         newnode.connected.connect(gatewaynewnode)
    #         ip_list.append(rcv.sprintf("%ARP.psrc%"))
    # print ip_list
    return live_ip_nodes

    # Code for ARP Scanning


def traceroute(hostname, port, max_hops,project):
    destination = socket.gethostbyname(hostname)
    print "Target: " + hostname

    # ip_packet = IP(dst=hostname, ttl=10)
    # https://jvns.ca/blog/2013/10/31/day-20-scapy-and-traceroute/
    # udp_packet = UDP(dport=33434)

    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    nodes = ""
    edges = ""
    inet_addrs = netifaces.ifaddresses(netifaces.interfaces()[1])
    localip = inet_addrs[netifaces.AF_INET][0]['addr']
    try:
        previousnode = Machine.nodes.get(ip=localip,tag__startswith=project)
    except Machine.DoesNotExist as ex:
        subnet = inet_addrs[netifaces.AF_INET][0]['netmask']
        previousnode = makeanode(localip,subnet,project,0,"SEED")

    inet_addrs = netifaces.ifaddresses(netifaces.interfaces()[1])
    subnet = inet_addrs[netifaces.AF_INET][0]['netmask']

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
            # currenthost = "%s (%s)" % (currenthostname, currentaddr)
            currenthost = currentaddr
            nodes += "{ id : " + str(ttl + 1) + ", group : 'device', label : '" + currenthost + "'},"
            edges += "{ from: " + str(ttl) + ", to: " + str(ttl + 1) + " },"

            if ttl<2:
                previousnode = makeanode(currenthost, subnet,project,ttl,"TRACEROUTE")
                # previousnode = Machine(ip=currenthost, hostname=currenthostname, subnet="255.255.255.0")
                # previousnode.save()
            else:
                newnode = makeanode(currenthost,subnet,project,ttl,"TRACEROUTE")
                # newnode = Machine(ip=currenthost, hostname=currenthostname, subnet= "255.255.255.0")
                # newnode.save()
                newnode.connected.connect(previousnode)
                previousnode = newnode

                # previousnode = Machine(ip=currenthost, hostname=currenthostname, subnet="255.255.255.0")
        # else:
        #     currenthost = "*"
        #     newnode = makeanode("*","*",project,ttl)
        #     newnode.connected.connect(previousnode)
        #     previousnode = newnode
        #

        # print "%dt%s" % (ttl, currenthost)

        ttl += 1
        if currentaddr == destination or ttl > max_hops:
            break
    return nodes + "#" + edges


def makeanode(ip,subnet,project,distance,origin):
    try:
        checknode = Machine.nodes.get(ip=ip,tag__startswith=project)
        print "Node exist: " + checknode.ip
    except Machine.DoesNotExist as ex:
        print "Exception: " + str(ex)
        try:
            hostname = socket.gethostbyaddr(ip.split("#")[0])[0]
        except Exception as ex:
            print "Exception: " + str(ex)
            hostname = ip
        print "Hostname: " + hostname

        count = len(Machine.nodes.filter(distance=distance).filter(tag__startswith=project))
        if count % 2 == 0:
            queue = (count/2)*(-1)
        else:
            queue = (count + 1)/2

        if ipaddress.ip_address(unicode(ip.split("#")[0])).is_private:
            tag = project + "#" + origin + "#INTERNAL"
        else:
            tag = project + "#" + origin + "#EXTERNAL"
        newnode = Machine(ip=ip, hostname=hostname, subnet=subnet,tag=tag, distance=distance,queue=queue)
        newnode.save()
        print "New Node: " + newnode.ip
        return newnode

    return checknode


def networkscan(scanrange):
    nm = nmap.PortScanner()
    if os.path.exists(os.path.dirname(scanrange)):
        nm.scan(scanrange,arguments="-PE -sn -iL")
    else:
        nm.scan(scanrange,arguments="-PE -sn") # ping scan only - can be modified
    return nm.all_hosts()