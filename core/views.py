# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .forms import ProjectForm,GoToForm,ScanForm,NewProjectForm,CMDBScanForm,AWSForm,AzureForm
from django.shortcuts import render,redirect,render_to_response

from tasks import *
from celery.result import AsyncResult
import json
from django.http import HttpResponse
from django.template import RequestContext
from operator import itemgetter

def handler404(request):
    response = render_to_response('statistics.html', {},context=RequestContext(request))
    return response


def settings(request):
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    awsform = AWSForm()
    azureform = AzureForm()

    projectList = ["default"]
    for node in Machine.nodes:
        projectList.append(str(node.tag).split("#")[0])
    projectList = list(set(projectList))
    projectList.sort()

    context = {"awsform": awsform, "azureform": azureform, "projectList": projectList,
               "newprojectform": newprojectform, "gotoform": gotoform, "scanform": scanform,
               "projectform": projectform, "cmdbform": cmdbform}

    return render(request, 'settings.html', context)

def activities(request):
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    awsform = AWSForm()
    azureform = AzureForm()

    projectList = ["default"]
    for node in Machine.nodes:
        projectList.append(str(node.tag).split("#")[0])
    projectList = list(set(projectList))
    projectList.sort()

    all_seed_hosts = Machine.nodes.filter(tag__contains="SEED");
    activityList = []

    for node in all_seed_hosts:
        if str(node.action).startswith("$"):
            #print str(node.action)
            for activity in str(node.action).split("$"):
                try:
                    # format ID$Project$Activity$Time$Status
                    activityListElement = []
                    activityListElement.append(activity.split("@")[1])
                    activityListElement.append(node.tag.split("#")[0])
                    activityListElement.append(str(activity.split("@")[0]).replace("#"," -> "))
                    activityListElement.append(activity.split("@")[2])
                    activityList.append(activityListElement)

                    if len(activityList) > 8:
                        activityList = sorted(activityList, key=itemgetter(3), reverse=True)
                        context = {"awsform": awsform, "azureform": azureform, "projectList": projectList,
                                   "newprojectform": newprojectform, "gotoform": gotoform, "scanform": scanform,
                                   "projectform": projectform, "cmdbform": cmdbform, "activityList": activityList}
                        return render(request, 'activities.html', context)
                except Exception as ex:
                    print str(ex)

    context = {"awsform": awsform, "azureform": azureform, "projectList": projectList,
                "newprojectform": newprojectform, "gotoform": gotoform, "scanform": scanform,
               "projectform": projectform, "cmdbform": cmdbform,"activityList": activityList}

    return render(request, 'activities.html', context)

def statistics(request):
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    awsform = AWSForm()
    azureform = AzureForm()

    projectList = ["default"]
    for node in Machine.nodes:
        projectList.append(str(node.tag).split("#")[0])
    projectList = list(set(projectList))
    projectList.sort()

    all_hosts = Machine.nodes.filter(tag__ne="");
    host_count = 0;

    rogue_system_count = 0;
    down_host_count = 0;
    project_list = []

    for node in all_hosts:
        project_list.append(str(node.tag).split("#")[0])
        host_count += 1;
        if "discovered" in str(node.tag).lower():
            rogue_system_count += 1;
        if "down" in str(node.tag).lower():
            down_host_count += 1;

    project_count = len(list(set(project_list)))

    context = {"awsform": awsform, "azureform": azureform, "projectList": projectList,
               "newprojectform": newprojectform, "gotoform": gotoform, "scanform": scanform,
               "projectform": projectform, "cmdbform": cmdbform,"projectList":projectList,"host_count":host_count,"project_count":project_count,"rogue_system_count":rogue_system_count,"down_host_count":down_host_count}
    return render(request, 'statistics.html', context)

def index(request):
    return redirect("/core/statistics")


def clear(project_id):
    for allnodes in Machine.nodes.filter(tag__startswith=project_id):
        allnodes.delete()
    return "Info: all clear"


def refresh(request,project_id):
    # 1. Save state
    prevstate = Machine.nodes.filter(tag__startswith=project_id)
    print "Before refresh:"
    print len(prevstate)
    for node in prevstate:
        print node.ip

    # 2. Identify current state
    currentstate = []
    findseed = project_id + "#SEED"
    node = Machine.nodes.get(tag__startswith=findseed)
    actions = node.action.split("$")
    for action in actions:
        if str(action).startswith("GOTO"):
            print str(action).split("#")[0] + "@" + str(action).split("#")[1]
            path = traceroute(str(action).split("#")[1].split("@")[0], 33434, 30, project_id, False)
            currentstate += path
            print "Traceroute result: " + str(path)
        elif str(action).startswith("ROAM"):
            print str(action).split("#")[0]
            myneighbours = roam(project_id)
            currentstate += myneighbours
            print "My neighbours: " + str(myneighbours)
        elif str(action).startswith("SCAN"):
            print str(action).split("#")[0] + "@" + str(action).split("#")[1]
            scanresult = scan(str(action).split("#")[1].split("@")[0], project_id, False)
            print "Scan results: " + str(scanresult)
            currentstate += scanresult

    print "Current state:"
    print len(currentstate)
    for node in currentstate:
        print node.ip

    # 3. Compare
    for pnode in prevstate:
        isavailable = False
        for cnode in currentstate:
            if pnode.ip == cnode.ip:
                pnode.tag = str(pnode.tag).replace("DOWN","UP")
                pnode.save()
                isavailable = True
                break
        if isavailable == False:
            print "Not available: " + pnode.ip
            pnode.tag = str(pnode.tag).replace("UP","DOWN")
            pnode.save()

    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    awsform = AWSForm()
    azureform = AzureForm()

    actionList = []
    findseed = project_id + "#SEED"
    node = Machine.nodes.get(tag__startswith=findseed)
    actions = node.action.split("$")

    for action in actions:
        actionList.append(action)

    for node in Machine.nodes.filter(tag__startswith=project_id):
        actionList.append(node.enum)

    actionList = list(set(actionList))

    projectList = ["default"]
    for node in Machine.nodes:
        projectList.append(str(node.tag).split("#")[0])
        projectList = list(set(projectList))
        projectList.sort()


    context = {"awsform":awsform,"azureform":azureform,"projectList": projectList, "actionList": actionList, "project_id": project_id, "newprojectform": newprojectform, "gotoform": gotoform, "scanform": scanform,
               "projectform": projectform, "cmdbform": cmdbform}
    return render(request, 'project.html', context)

def create(request):
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    awsform = AWSForm()
    azureform = AzureForm()

    projectList = ["default"]
    for node in Machine.nodes:
        projectList.append(str(node.tag).split("#")[0])
    projectList = list(set(projectList))
    projectList.sort()

    newprojectform = NewProjectForm(request.POST)
    print "In new project create block"
    if newprojectform.is_valid():
        project_id = str(newprojectform.cleaned_data["newproject"])
        action = "create"
        print "New Project: " + project_id

    output = getlocalinfo(project_id)
    print "Project created: " + output
    print "Reinitialized DB"
    actionList = listActions(project_id)
    historyList = listHistory(project_id)
    enumList = listEnums(project_id)
    cloudList = listCloud(project_id)
    context = {"cloudList": cloudList, "awsform": awsform, "azureform": azureform, "actionList": actionList,
               "historyList": historyList, "enumList": enumList, "projectList": projectList, "project_id": project_id,
               "newprojectform": newprojectform,
               "gotoform": gotoform,
               "scanform": scanform,
               "projectform": projectform, "cmdbform": cmdbform}
    return redirect("/core/" + str(project_id) + "/action")

def action(request, project_id):
    print "Current Project: " + project_id
    print "Start Action"
    gotoform = GoToForm()
    scanform = ScanForm()
    projectform = ProjectForm()
    newprojectform = NewProjectForm()
    cmdbform = CMDBScanForm()
    awsform = AWSForm()
    azureform = AzureForm()

    projectList = ["default"]
    for node in Machine.nodes:
        projectList.append(str(node.tag).split("#")[0])
    projectList = list(set(projectList))
    projectList.sort()
    action = "show"
    if request.method == "POST":
        print "Info: Request is POST"
        print "Debug: "+ str(request.POST)
        if "goto_target" in request.POST:
            gotoform = GoToForm(request.POST)
            if gotoform.is_valid():
                action = "goto"
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
        elif "access_key" in request.POST and "access_id" in request.POST:
                awsform = AWSForm(request.POST)
                if awsform.is_valid():
                    action = "aws"
                    access_key = str(awsform.cleaned_data["access_key"])
                    access_id = str(awsform.cleaned_data["access_id"])
                    region = str(awsform.cleaned_data["regions"])
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
        actionList = listActions(project_id)
        enumList = listEnums(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList":cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"enumList":enumList, "projectList":projectList, "project_id": project_id, "newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return redirect("/core/" + str(project_id) + "/action")
    elif "goto" in action:
        output = traceroute.delay(goto_target,33434,30,project_id,True)
        print "Traceroute result: " + str(output)

        findseed = project_id + "#SEED"
        seednode = Machine.nodes.get(tag__startswith=findseed)

        addaction(project_id, "GOTO", goto_target+"@"+ str(output)+ "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode )

        actionList = listActions(project_id)
        enumList = listEnums(project_id)
        historyList = listHistory(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"historyList":historyList, "enumList": enumList,"projectList":projectList, "project_id": project_id, "newprojectform":newprojectform, "gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "roam" in action:
        myneighbours = roam.delay(project_id)
        print "My neighbours: " + str(myneighbours)
        localinfo = getlocalinfo(project_id)
        inet_addrs = netifaces.ifaddresses(localinfo.split("$")[2])
        mylocalrange = netifaces.gateways()['default'][netifaces.AF_INET][0] + "/" + str(
            netaddr.IPAddress(inet_addrs[netifaces.AF_INET][0]['netmask']).netmask_bits())

        findseed = project_id + "#SEED"
        seednode = Machine.nodes.get(tag__startswith=findseed)

        addaction(project_id, "ROAM", mylocalrange+"@"+str(myneighbours)+ "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode )

        actionList = listActions(project_id)
        enumList = listEnums(project_id)
        historyList = listHistory(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"historyList":historyList, "enumList": enumList,"projectList":projectList, "project_id": project_id, "newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return redirect("/core/" + str(project_id) + "/action")
    elif "clear" in action:
        clear(project_id)
        print "All clear..."
        return redirect("/core/statistics")
    elif "scan" in action:
        scanresult = scan.delay(scanrange,project_id,True)
        print "Scan results: " + str(scanresult)
        findseed = project_id + "#SEED"
        seednode = Machine.nodes.get(tag__startswith=findseed)

        addaction(project_id, "SCAN", scanrange+"@"+str(scanresult)+ "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode )

        actionList = listActions(project_id)
        enumList = listEnums(project_id)
        historyList = listHistory(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"historyList":historyList, "enumList": enumList, "projectList":projectList, "project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                    "projectform": projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)
    elif "select" in action:
        actionList = listActions(project_id)
        enumList = listEnums(project_id)
        historyList = listHistory(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"historyList":historyList, "enumList": enumList,"projectList":projectList, "project_id": project_id, "newprojectform":newprojectform,"gotoform": gotoform, "scanform": scanform,
                   "projectform": projectform}
        return redirect("/core/" + str(project_id) + "/action")
    elif "create" in action:
        output = getlocalinfo(project_id)
        print "Project created: " + output
        print "Reinitialized DB"
        actionList = listActions(project_id)
        historyList = listHistory(project_id)
        enumList = listEnums(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"historyList":historyList, "enumList": enumList,"projectList":projectList, "project_id": project_id, "newprojectform": newprojectform,
                   "gotoform": gotoform,
                   "scanform": scanform,
                   "projectform": projectform,"cmdbform":cmdbform}
        return redirect("/core/" + str(project_id) + "/action")
    elif "aws" in action:
        findseed = project_id + "#SEED"
        seednode = Machine.nodes.get(tag__startswith=findseed)
        output = aws_processing.delay(access_key,access_id,region,project_id)
        addaction(project_id, "AWS", region+"@"+str(output)+ "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), seednode)

        actionList = listActions(project_id)
        historyList = listHistory(project_id)
        enumList = listEnums(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform": awsform, "azureform": azureform, "actionList": actionList, "historyList": historyList,
                   "enumList": enumList, "projectList": projectList, "project_id": project_id,
                   "newprojectform": newprojectform, "gotoform": gotoform, "scanform": scanform,
                   "projectform": projectform, "cmdbform": cmdbform}
        return render(request, 'project.html', context)
    elif "cmdb" in action:
        scanrange = []
        for line in request.FILES['cmdbfilepath']:
            scanrange.append(str(line).strip())
        scanrange = list(set(scanrange))
        print request.POST.get("beintrusive", None)
        output = cmdbprocess.delay(scanrange,request.POST.get("beintrusive", None),request.FILES['cmdbfilepath'].name,project_id)
        print "Process started " + str(output)
        findseed = project_id + "#SEED"
        seednode = Machine.nodes.get(tag__startswith=findseed)
        addaction(project_id, "CMDB",str(request.FILES['cmdbfilepath']) + "@" + str(output) + "@" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),seednode)
        return redirect("/core/" + str(project_id) + "/action")
    else:
        if "default" in str(project_id):
            output = getlocalinfo(project_id)
            print "Project created: " + output
            print "Reinitialized DB"
        actionList = listActions(project_id)
        enumList = listEnums(project_id)
        historyList = listHistory(project_id)
        cloudList = listCloud(project_id)
        context = {"cloudList": cloudList,"awsform":awsform,"azureform":azureform,"actionList": actionList,"historyList":historyList, "enumList": enumList,"projectList":projectList, "project_id": project_id,"newprojectform":newprojectform,"gotoform":gotoform,"scanform":scanform,"projectform":projectform,"cmdbform":cmdbform}
        return render(request, 'project.html', context)


def task_state(request):
    if request.is_ajax():
        try:
            if "project_id" in str(request.POST.get("task","Invalid")):
                project_id = str(request.POST.get("task","Invalid")).split("#")[1]
                findseed = project_id + "#SEED"
                seednode = Machine.nodes.get(tag__startswith=findseed)
                tasklist = str(seednode.action).split("$")
                for taskstring in tasklist:
                    print "Taskstring " + taskstring
                    try:
                        now = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"%Y-%m-%d %H:%M")
                        tasktime = datetime.datetime.strptime(taskstring.split("@")[2], "%Y-%m-%d %H:%M")
                        if int(str(now - tasktime).split(":")[1]) < 5:
                            task_id = taskstring.split("@")[1]
                            print "task id " + task_id
                            task = AsyncResult(task_id)
                            print str(task.result) + "#" + str(task.state)
                            if "pending" in str(str(task.result) + "#" + str(task.state)).lower():
                                status = "Pending"
                                status = json.dumps(status)
                                print "Returning pending..."
                                return HttpResponse(status, content_type='application/json')
                    except Exception as ex:
                        print str(ex)
                status = "Success"
                print "returning success..."
            else:
                task = AsyncResult(request.POST.get("task","Invalid"))
                #print str(task.result) + "#" + str(task.state)
                if "pending" in str(str(task.result) + "#" + str(task.state)).lower():
                    status = "Pending"
                    status = json.dumps(status)
                    print "Returning pending..."
                    return HttpResponse(status, content_type='application/json')
        except Exception as ex:
            print str(ex)
        status = "Success"
        print "returning success..."
    else:
        status = 'This is not an ajax request'

    status = json.dumps(status)
    return HttpResponse(status, content_type='application/json')