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

from .forms import ProjectForm,GoToForm,ScanForm,NewProjectForm

from django import forms

from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Machine

import nmap

def index(request):
    return redirect("/core/default/action")


# def project(request,project_id):
#     # Removing everything as of now
#     for allnodes in Machine.nodes:
#         allnodes.delete()
#
#
#     print "All nodes deleted successfully"
#
# #     output = getlocalinfo()
# #
# #     localip = output.split("#")[0]
# #     localhostname = output.split("#")[1]
# #     subnet = output.split("#")[2]
# #
# #     gateway = output.split("#")[3]
# #     gatewayhostname = output.split("#")[4]
# # # { id : 0, group : 'source', label : '192.168.1.21'},{ id : 1, group : 'device', label : '192.168.1.1'},
# #     # #{ from: 1, to: 0 },
# #     localnode = Machine(ip=localip, subnet=subnet, hostname=localhostname)
# #     localnode.save()
# #
# #
# #     gatewaynode = Machine(ip=gateway, subnet=subnet, hostname=gatewayhostname)
# #     gatewaynode.save()
# #
# #     localnode.connected.connect(gatewaynode)
#
#     context = {"myinfo": "project", "project_id": project_id}
#     return render(request, 'project.html', context)


def action(request, project_id):

    print "Start Action"
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()

    # validation of project_id
    print "Current Project: " + project_id
    print "Project Count: " + str(len(projectform.PROJECT_CHOICES))

    projectAvailble = False
    for i in range(0, len(projectform.PROJECT_CHOICES)):
        key, value = projectform.PROJECT_CHOICES[i]
        if project_id == key:
            print "Got Project: " + project_id
            projectAvailble = True
            break

    if not projectAvailble:
        print "Info: Project Not Found. Returning to default..."
        return redirect("/core/default/action")

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
            # projectform = ProjectForm()
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

    else:
        action=request.GET.get("action","show")
        # scanform = ScanForm()
        # gotoform = GoToForm()
        # projectform = ProjectForm()
        # newprojectform = NewProjectForm()

    #
    # for allnodes in Machine.nodes:
    #     allnodes.delete()
    #
    # print "Delete successfully"
    print "Action is : " + action

    if "findme" in action:
        # project = request.GET.get("project","")
        # if project == "":
        #     project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        # print "Project in FindMe: "+ project
        output = getlocalinfo(project_id)
        context = {"project_id": project_id, "newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform}
        return render(request, 'project.html', context)
    elif "goto" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        gotocelery = traceroute(goto_target,33434,30,project_id)
        #output = gotocelery.get()
        context = {"project_id": project_id, "newprojectform":newprojectform,  "gotoform":gotoform,"scanform":scanform,"projectform":projectform}
        return render(request, 'project.html', context)
    elif "roam" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        myneighbour = roam(project_id)
        context = {"project_id": project_id, "newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform}
        return render(request, 'project.html', context)
    elif "clear" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        clear(project_id)
        context = {"project_id": project_id,"newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform}
        return render(request, 'project.html', context)
    elif "scan" in action:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        scancelery = networkscan(scanrange,project_id,-1)
        # output = scancelery.get()
        context = { "project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                   "projectform": projectform}
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
                   "projectform": projectform}
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
        # print "Project Count in Create: " + str(len(projectform.PROJECT_CHOICES))
        context = {"project_id": project_id, "newprojectform": newprojectform,
                   "gotoform": gotoform,
                   "scanform": scanform,
                   "projectform": projectform}
        # return render(request, 'project.html', context)
        return redirect("/core/" + str(project_id) + "/action")
    else:
        # project, test = projectform.PROJECT_CHOICES[int(project_id) - 1]
        context = {"project_id": project_id,"newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform}
        return render(request, 'project.html', context)



def save(request, project_id):
    return HttpResponse("save")

def clear(project_id):
    for allnodes in Machine.nodes.get(tag=project_id):
        allnodes.delete()
    return "Info: all clear"

def getlocalinfo(project):
    inet_addrs = netifaces.ifaddresses(netifaces.interfaces()[1])
    localip = inet_addrs[netifaces.AF_INET][0]['addr']
    print "Local IP: " + localip

    # localhostname = socket.gethostbyaddr(localip)
    # print localhostname[0]
    subnet = inet_addrs[netifaces.AF_INET][0]['netmask']
    print "Subnet: " + subnet

    localnode = makeanode(localip,subnet,project,0)

    gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
    print "Gateway: " + gateway

    gatewaynode =  makeanode(gateway,subnet,project,1)

    localnode.connected.connect(gatewaynode)
    # gatewayhostname = socket.gethostbyaddr(gateway)
    # print gatewayhostname[0]

    return localip + "#" + gateway
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

    gatewaynewnode = makeanode(gateway, subnet,project,1)

    live_ip_nodes = networkscan(ips,project, 2)

    for node in live_ip_nodes:
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
    return ip_list

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
        previousnode = Machine.nodes.get(ip=localip,tag=project)
    except Machine.DoesNotExist as ex:
        subnet = inet_addrs[netifaces.AF_INET][0]['netmask']
        previousnode = makeanode(localip,subnet,project,0)

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
                previousnode = makeanode(currenthost, subnet,project,ttl)
                # previousnode = Machine(ip=currenthost, hostname=currenthostname, subnet="255.255.255.0")
                # previousnode.save()
            else:
                newnode = makeanode(currenthost,subnet,project,ttl)
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


def makeanode(ip,subnet,project,distance):

    # jim = Person.nodes.get(name='Jim')
    # need to write a method to make an entry
    # perform the validation of existence of node

    try:
        checknode = Machine.nodes.get(ip=ip,tag=project)
        print "Node exist: " + checknode.ip
    except Machine.DoesNotExist as ex:
        print "Exception: " + str(ex)
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception as ex:
            print "Exception: " + str(ex)
            hostname = ip
        print "Hostname: " + hostname

        count = len(Machine.nodes.filter(distance=distance).filter(tag=project))
        newnode = Machine(ip=ip, hostname=hostname, subnet=subnet,tag=project, distance=distance,queue=count+1)
        newnode.save()
        print "New Node: " + newnode.ip
        return newnode

    return checknode


def networkscan(scanrange,project, distance):
    ip_list = []
    nm = nmap.PortScanner()

    nm.scan(scanrange,arguments="-PE -sn") # ping scan only - can be modified
    for host in nm.all_hosts():
        print "Live: " + host
        # traceroute(host, 33434, 30, project)
        hostnode = makeanode(host,"255.255.255.0",project,distance) # need to change the subnet ICMP Address Mask Ping (-PM)
        ip_list.append(host)
    return ip_list