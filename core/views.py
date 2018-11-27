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

    if request.method == "POST":
        print "Info: Request is POST"
        print "Debug: "+ str(request.POST)
        if "goto_target" in request.POST:
            gotoform = GoToForm(request.POST)
            if gotoform.is_valid():
                action = "goto"
                goto_target = gotoform.cleaned_data["goto_target"]
        elif "scanrange" in request.POST:
            scanform = ScanForm(request.POST)
            if scanform.is_valid():
                action = "scan"
                scanrange = scanform.cleaned_data["scanrange"]
        elif "newproject" in request.POST:
            newprojectform = NewProjectForm(request.POST)
            print "In new project create block"
            if newprojectform.is_valid():
                project_id = str(newprojectform.cleaned_data["newproject"])
                action = "create"
                print "New Project: " + project_id
        elif "project" in request.POST:
            projectform = ProjectForm(request.POST)
            if projectform.is_valid():
                action="select"
                project_id = str(projectform.cleaned_data["project"])
                print "Project: " + project_id
        elif request.FILES['cmdbfilepath']:
            print "CMDB file: " + str(request.FILES['cmdbfilepath'].name)
            action = "cmdb"
            print "Project: " + project_id
    else:
        action=request.GET.get("action","show")
    print "Action is : " + action

    if "findme" in action:
        output = getlocalinfo(project_id)
        print "Local Info: " + str(output)
        context = {"project_id": project_id, "newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "goto" in action:
        output = traceroute(goto_target,33434,30,project_id)
        print "Traceroute result: " + str(output)
        context = {"project_id": project_id, "newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "roam" in action:
        myneighbours = roam(project_id)
        print "My neighbours: " + str(myneighbours)
        context = {"project_id": project_id, "newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "clear" in action:
        clear(project_id)
        print "All clear..."
        context = {"project_id": project_id,"newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "scan" in action:
        scanresult = networkscan(scanrange)
        print "Scan results: " + str(scanresult)

        localinfo = getlocalinfo(project_id)
        inet_addrs = netifaces.ifaddresses(localinfo.split("$")[2])  # need to modify the code to enumerate the interfaces propoerly
        local_ip_range = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(
            netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())
        print "Local IP range " + local_ip_range

        gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        subnet = inet_addrs[netifaces.AF_INET][0]['netmask']  # will assume same subnet for all LAN IPs
        gatewaynewnode = makeanode(gateway, subnet, project_id,1,"SCAN")

        for ip in scanresult:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(local_ip_range):
                print "In local range: " + ip
                node = makeanode(ip,subnet,project_id,2,"SCAN")
                gatewaynewnode.connected.connect(node)
            else:
                print "Performing traceroute to " + ip
                traceroute(ip,33434,30,project_id)
        context = { "project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                    "projectform": projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "select" in action:
        print "Project List in Select: " + str(projectform.PROJECT_CHOICES)
        context = {"project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                   "projectform": projectform}
        return redirect("/core/" + str(project_id) + "/action")
    elif "create" in action:
        output = getlocalinfo(project_id)
        print "Project created: " + output
        # neomodel.db.set_connection('bolt://neo4j:Neo4j@localhost:7687')
        # neomodel.Database.__init__()
        print "Reinitialized DB"
        context = {"project_id": project_id, "newprojectform": newprojectform,
                   "gotoform": gotoform,
                   "scanform": scanform,
                   "projectform": projectform,"cmdbform":cmdbform}
        return redirect("/core/" + str(project_id) + "/action")
    elif "cmdb" in action:
        localipstring = getlocalinfo(project_id)
        localip = str(localipstring).split("$")[0]
        subnet = str(localipstring).split("$")[1]
        interface = str(localipstring).split("$")[2]
        print "processing "+ str(len(localip)) + "local interfaces " + interface
        cmdb_file_ips = []

        gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
        print "Gateway: " + gateway

        gatewaynewnode = makeanode(gateway, subnet, project_id, 1, "SCAN")
        localnode = makeanode(localip,subnet,project_id,0,"SCAN")
        gatewaynewnode.connected.connect(localnode)

        for line in request.FILES['cmdbfilepath']:
            cmdb_file_ips.append(line)
            print "scanning IP " + line
            scanresult = networkscan(line)
            for ip in scanresult:
                local_ip_range = localip+"/"+str(netaddr.IPAddress(subnet).netmask_bits())
                if netaddr.IPAddress(ip) in netaddr.IPNetwork(local_ip_range):
                    print "in local range"
                    node = makeanode(ip, subnet, project_id, 2,"CMDB")
                    gatewaynewnode.connected.connect(node)
                else:
                    print "performing traceroute to " + ip
                    traceroute(ip, 33434, 30, project_id)

        print "You want to be intrusive: " + str(request.POST.get("beintrusive", None))
        if str(request.POST.get("beintrusive", None)) == "on":
            traceroute("google.com", 33434, 30, project_id)  # perform traceroute to (multiple?)google.com
            local_ip_range = localip + "/" + str(netaddr.IPAddress(subnet).netmask_bits())
            scanresult = networkscan(local_ip_range )# Scan all live LOCAL IPs
            for ip in scanresult:
                origin = "DISCOVERED"
                for cmdb_file_ip in cmdb_file_ips:
                    if netaddr.IPAddress(ip) in netaddr.IPNetwork(cmdb_file_ip):
                        origin = "CMDB"
                        break
                node = makeanode(ip,subnet,project_id,2,origin)
                gatewaynewnode.connected.connect(node)
        return redirect("/core/" + str(project_id) + "/action")
    else:
        context = {"project_id": project_id,"newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)

def clear(project_id):
    for allnodes in Machine.nodes.filter(tag__startswith=project_id):
        allnodes.delete()
    return "Info: all clear"

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
    makeanode(localip, subnet, project, 0, "SEED")
    return localip + "$" + subnet + "$" + localinterface

def roam(project):
    #  need to modify the code to enumerate the interfaces better
    localinfo = getlocalinfo(project)
    inet_addrs = netifaces.ifaddresses(localinfo.split("$")[2])
    ips = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())

    print "IP Range: " + ips

    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    print "Gateway: " + gateway

    subnet = localinfo.split("$")[1] # will assume same subnet for all LAN IPs

    print "Subnet: " + subnet

    gatewaynewnode = makeanode(gateway, subnet,project,1,"SCAN")
    live_ip_nodes = networkscan(ips)

    for ip in live_ip_nodes:
        node = makeanode(ip,subnet,project,2,"SCAN")  # need to change the subnet ICMP Address Mask Ping (-PM)
        gatewaynewnode.connected.connect(node)

    return live_ip_nodes


def traceroute(hostname, port, max_hops,project):
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
    try:
        previousnode = Machine.nodes.get(ip=localip,tag__startswith=project)
    except Machine.DoesNotExist as ex:
        previousnode = makeanode(localip,subnet,project,0,"SEED")

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

            if ttl<2:
                previousnode = makeanode(currenthost, subnet,project,ttl,"TRACEROUTE")
            else:
                newnode = makeanode(currenthost,subnet,project,ttl,"TRACEROUTE")
                newnode.connected.connect(previousnode)
                previousnode = newnode

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
        if ipaddress.ip_address(unicode(ip.split("#")[0])).is_private:
            tag = project + "#" + origin + "#INTERNAL"
        else:
            tag = project + "#" + origin + "#EXTERNAL"

        newnode = Machine(ip=ip, hostname=hostname, subnet=subnet,tag=tag, distance=distance,queue=count)
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
