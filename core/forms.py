from django import forms
from .models import Machine

class GoToForm(forms.Form):
    goto_target = forms.CharField(max_length=100,label="",initial="[Destination Host]")

class ProjectForm(forms.Form):
    PROJECT_CHOICES = [("default","default")]
    for node in Machine.nodes:
        tuple = (str(node.tag).split("#")[0],str(node.tag).split("#")[0])
        PROJECT_CHOICES.append(tuple)
        # print "Tag: " + node.tag
    PROJECT_CHOICES = list(set(PROJECT_CHOICES))
    print "Project List: " + str(PROJECT_CHOICES)
    project = forms.CharField(widget=forms.Select(choices=PROJECT_CHOICES),label="")


class NewProjectForm(forms.Form):
    newproject = forms.CharField(label="", initial="[Project Name]")

class ScanForm(forms.Form):
    scanrange = forms.CharField(label="", initial="[Target IP Range]")

class CMDBScanForm(forms.Form):
    cmdb_file = forms.FileField()
