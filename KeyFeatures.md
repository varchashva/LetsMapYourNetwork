## Key Features

1. Project management
    - User can create and delete multiple projects to view same network from different perspective and/or to analyze mulitple networks at same time
    - Within a single project, result of all learning activities performed will be collated into a single view and thus provides a holistic perspective of network

2. Bulk load of existing CMDB
    - User can upload their existing CMDB file into the LMYN and it will provide the 'delta' with the actual network
    - So LMYN will provide the segregation between what's in their CMDB and not in network and vice-versa for user to take actions on rogue system
    - It uses different color-code scheme for different type of systems for e.g. systems which are live in network and not presented in CMDB will be shown as RED node

3. Ability to perform on-demand network activities
    - Other than uploading the CMDB file, user can perform below network activities to any project:
      - Traceroute to any destination host
      - Network scan to any IP and/or range (all well-known format of IP is accepted)
    - LMYN will incorporate the result of above actions into same project to build the network

4. Cloud (AWS) support 
    - LMYN fetches the topology information such as VPC, Subnets, Peering, Internet Gateway etc. from AWS APIs and represent it in form of graph
    - LMYN makes logical segregation of AWS network as "Regions > VPCs > Subnets > Instances" and groups them accordingly 

5. Enumeration
    - LMYN performs multiple enumeration probes to identify the operating system and type of device, as and when network is built
	  - For AWS, LMYN queries the AWS API to fetch the information of instances such as Platform, State, VPC, Subnet etc.
    - If enumeration is successful, then LMYN assigns a relevant icon for each node 

6. Ability to analyse 'interesting' network only
    - Now, once user builds the network using multiple activities (CMDB upload, ad-hoc network activities, cloud scan, enumeration), then user can filter only 'interesting' network out of the entire database on UI section
    - This filtering process can be performed on the basis of actions (for e.g. IP range, destination host) or enumeration details (Linux, Windows, Router, VPC, Subnet, State etc.)
    - Filtering process allows to perform 'AND' and 'OR' kind of operation for e.g. 'all IP in range 192.168.1.1/24 and Windows'
    - Filtering process gives ability to users to feed all the information in database but at the same time not overwhelming with the information in UI and make a run-time decision on what user wants to see

7. Continuous monitoring
    - Also, LMYN gives ability to monitor any existing network over the period of time
    - User can identify, in graph-form, that how their network is changing (which systems are disconnecting and connecting to network)
    - LMYN again utilises color-code scheme to segregate the different type of systems in network for e.g. all nodes which are not live will be shown as GREY

8. Segregation of backend activities and UI
    - LMYN segregates functionally of backend activities with UI
    - LMYN have implementation of Celery and RabbitMQ; thus, user have a seamless UI irrespective of background activities 
    - LMYN keeps track of status of all background activities and updates UI periodically

9. Docker support
    - All of these you can have in docker :)
