## How to use Lets Map Your Network

> Honestly, there is no _'correct'_ way of using LMYN. It solely depends on what you want to acheive using it. Having said that, I am jotting down some _'good'_ practices, which will help you to start with and later feel free to explore it as per your requirement. Do provide your inputs with use-cases in comments and I shall update this document.

1. Create a new project using _Project Management_ module, this will help you to segregate the information about the network.
2. Upload the CMBD (configuration management database) file, if applicable, to build the initial network. This will quickly give you idea about what it is in paper and what is in network.
    > Tip: Use _'Stealth'_ mode while uploading the CMDB file, this will discover the surprisingly _**hidden assets**_ in your network
3. Now you can perform multiple network such as traceroute, scanning to build your network and/or validate the 'actual' network against the desired state of network
4. For cloud (AWS) network, you just have to provide the access_key & access_id and select a region. LMYN will build the network automatically
5. Once you build the network, now you can inspect the interesting part of entire network. Few examples:
    - All Windows systems with specific IP range
    - All Linux systems for a certain VPC
    - All intermediate hops to reach google.com 
    - All local subnet IPs with no definite operating system details 
    - All internet gateways for a particular region
 6. Now you can use LMYN to monitor the changes in network. Use the refresh button on top right corner.
    > All GREY nodes represent the systems which are not live at this point, but were detected live previously
