## Installation Guidelines ##

### Short version ###

#### Using DockerHub - Linux only ####
1. Install [docker & docker-compose](https://docs.docker.com/install/linux/docker-ce/debian/#install-using-the-repository)
   - sudo apt-get update
   - sudo apt-get install docker-ce docker-compose
2. wget https://raw.githubusercontent.com/varchashva/LetsMapYourNetwork/master/docker-compose.yml
3. docker-compose up
4. Browse to http://localhost:9999/core and you are set to explore the tool :)

### Long version ###
#### For Linux User (Note - Below commands have been provided for Debian-based linux. For other versions of Linux change all commands accordingly) #### 

1. Download LMYN from GitHub and extract all to a directory like /opt/LMYN ($LMYN_HOME)
2. Install python: sudo apt-get install python2.7
3. Install nmap: sudo apt-get install nmap 
4. Install rabbitmq-server: sudo apt-get install rabbitmq-server
5. Install Java Development Kit
   - Install Oracle JDK 8 (it’s a prerequisite for Neo4j database)
   - Run command java -version on terminal
   - If output with version details then jump to Neo4j installation or else continue with Java installation 
   - Run below commands to install Java
     - sudo add-apt-repository ppa:webupd8team/java -y
     - sudo apt-get update 
     - sudo apt-get install oracle-java8-installer
6. Go to Neo4j [download](https://neo4j.com/download-center/#releases) section
   - Select ‘Community Server’ section and [download Linux version of Neo4j](https://go.neo4j.com/download-thanks.html?edition=community&release=3.3.6&flavour=unix&_ga=2.217214878.946316120.1534600164-1297405808.1534400604)
   - Extract the downloaded file with command sudo tar -xzf neo4j-community-3.3.6-unix.tar.gz -C /opt/neo4j
   - Change to neo4j directory cd /opt/neo4j
   - Run command ./bin/neo4j console to start the neo4j server
   - Browse to Neo4j web console (http://localhost:7474) to change the default password from neo4j to Neo4j
   - Please refer [Neo4j Installation Guide](https://neo4j.com/docs/operations-manual/current/installation) for any troubleshooting, if required 
7. Run command sudo pip install --trusted-host pypi.python.org -r $LMYN/LetsMapYourNetwork/requirements.txt
8. Run command sudo python $LMYN_HOME/LetsMapYourNetwork/manage.py runserver 0.0.0.0:9999 --insecure
9. Open http://localhost:9999/core in browser and explore the tool

#### For Windows User #### 

1. Download LMYN from GitHub and extract all. It is recommended to extract within Python home directory for e.g. C:\python\LMYN ($LMYN_HOME)
2. Install python 
   - Go to python [download](https://www.python.org/downloads/release/python-2715) section and click on [Windows x86 MSI installer for 32-bit](https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi) user OR [Windows x86-64 MSI installer](https://www.python.org/ftp/python/2.7.15/python-2.7.15.amd64.msi) for 64-bit user 
   - Install the downloaded python file with all default settings
3. Download [nmap](https://nmap.org/dist/nmap-7.70-setup.exe) from here and install with all default settings
4. Download [RabbitMQ-Server](https://www.rabbitmq.com/install-windows.html) and install with all default settings
5. Install Microsoft Visual Studio C++
   - 32-bit user install [VC setup](http://download.microsoft.com/download/A/5/4/A54BADB6-9C3F-478D-8657-93B3FC9FE62D/vcsetup.exe) only with all optional product UNCHECKED
   - 64-bit users install [Windows SDK and .NET Framework](https://www.microsoft.com/en-us/Download/confirmation.aspx?id=8442) with default settings  
6. Install Oracle JDK 8 (it’s a prerequisite for Neo4j database)
   - Run command java -version on command prompt
   - If output with version details then jump to Neo4j installation or else continue with Java installation 
   - Go to Oracle [download](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) section and install JDK 8 with all default settings
   - Go to JRE installation directory like C:/Program files/java/jre7/bin and create a folder ‘server’ and copy all content of folder ‘client’ to folder ‘server’
7. Go to Neo4j [download](https://neo4j.com/download-center/#releases) section
   - Select ‘Community Server’ section and [download Windows version](https://go.neo4j.com/download-thanks.html?edition=community&release=3.4.6&flavour=winzip&_ga=2.141706682.946316120.1534600164-1297405808.1534400604)
   - Right click on downloaded file and click extract all to a directory like C:\neo4j
   - Open the command prompt with administrative privileges and change to extracted directory like cd C:\neo4j 
   - Run command bin\neo4j console to start the neo4j server
   - Browse to Neo4j web console (http://localhost:7474) to change the default password from neo4j to Neo4j
   - Please refer [Neo4j Installation Guide](https://neo4j.com/docs/operations-manual/current/installation/) for any troubleshooting, if required 
8. Open command prompt with Administrative privilegs and browse to Python home directory for e.g. cd C:\python
   - Run command python -m pip install --trusted-host pypi.python.org -r $LMYN/LetsMapYourNetwork/requirements.txt
9. Use same command prompt with Administrative privileges and from Python home directory
   - Run command python $LMYN_HOME\LetsMapYourNetwork\manage.py runserver 0.0.0.0:9999 --insecure
10. Open http://localhost:9999/core in browser and explore the tool
