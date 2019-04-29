from django import forms
from .models import Machine

class GoToForm(forms.Form):
    goto_target = forms.CharField(max_length=100,label="",initial="[Destination Host]")

class ProjectForm(forms.Form):
    PROJECT_CHOICES = [("default","default")]
    for node in Machine.nodes:
        tuple = (str(node.tag).split("#")[0],str(node.tag).split("#")[0])
        PROJECT_CHOICES.append(tuple)
    PROJECT_CHOICES = list(set(PROJECT_CHOICES))
    PROJECT_CHOICES.sort()
    project = forms.CharField(widget=forms.Select(choices=PROJECT_CHOICES),label="")


class NewProjectForm(forms.Form):
    newproject = forms.CharField(label="", initial="[Project Name]")

class ScanForm(forms.Form):
    scanrange = forms.CharField(label="", initial="[Target IP Range]")

class CMDBScanForm(forms.Form):
    cmdb_file = forms.FileField()


class AWSForm(forms.Form):
    access_key = forms.CharField(label="",widget=forms.PasswordInput())
    access_id = forms.CharField(label="",widget=forms.PasswordInput())
    regionlist = [("us-east-1", "us-east-1"),
               ("us-east-2","us-east-2"),
               ("us-west-1","us-west-1"),
               ("us-west-2","us-west-2"),
               ("ap-south-1", "ap-south-1"),
               ("ap-northeast-3", "ap-northeast-3"),
               ("ap-northeast-2", "ap-northeast-2"),
               ("ap-southeast-1", "ap-southeast-1"),
               ("ap-southeast-2", "ap-southeast-2"),
               ("ap-northeast-1", "ap-northeast-1"),
               ("ca-central-1", "ca-central-1"),
               ("cn-north-1", "cn-north-1"),
               ("cn-northwest-1", "cn-northwest-1"),
               ("eu-central-1", "eu-central-1"),
               ("eu-west-1", "eu-west-1"),
               ("eu-west-2", "eu-west-2"),
               ("eu-west-3", "eu-west-3"),
               ("eu-north-1", "eu-north-1"),
               ("sa-east-1", "sa-east-1"),
               ("us-gov-east-1", "us-gov-east-1"),
               ("us-gov-west-1]", "us-gov-west-1]")]
    regions = forms.CharField(widget=forms.Select(choices=regionlist), label="")


class AzureForm(forms.Form):
    access_key = forms.CharField(label="", initial="[Azure Access Key]")
    access_id = forms.CharField(label="", initial="[Azure Access ID]")