## WORK IN PROGRESS!

### major refactoring:
	python3
	adjusted for new aws stuff/api
	nothing work yet! execpt: help, version and action regions

### current refactoring:
Check the file **refactoring_update** file for which one Im working on. Assume nothing is working until released :)

Note:
```
the files: bin/awsbuild.py will need be adjusted as I hardcoded
		the sys.path.append to my project directory on my Mac
```

# ops-aws : my aws terraform script written in python3

## Background

### History
Orignally it was written in bash using the AWS java api, then once boto and awscli came, it was rewrite in bash
and making use of the awscli command. Later with boto2 it was rewrite again, this time in python2, quick and dirty.
So I decided to refactor and write the script properly in python3 and using the new resource now available in AWS.

### What can it do, at least once the refactorting is completed
The script is expecting that every single resouce is tagged with the same name.
Given couple simple configuration, the script will do the following
1. create/destory VPC
2. stop/start/terminate instances in the VPC
3. get status of the instances in the VPC
4. add/delete instances in the VPC

When a VPC is created, it will create 2 networks, Front End, which is public facing and Back End, which is
private. Ipv6 is disabled by default and a NAT gateway is created so the instance in the BE-network can reach
the NET (think of patching). And finally one instance will be created (bastion/jump/vpn box) in the FE-network
with a static IP (AWS's EIP) and you now have a AWS infrastrure ready for use.

Some note how the network and subnets are created:
1. given the CIDR of the VPC the FE-network will be same size of the BE-network
2. in both the FE-network and BE-network four subnet will be created and assigned to the availability zones, mind you some regions has only 3 zones and other have more then 4, but I decided to use only the first 4, so in 3 zone one subnet is not created, this something one day I like to fix...
3. make sure that the CIDR (prefix) is big enough, I would suggest of a /18, this will allowed ~2000 instance in each zones, remember that load balancer, route and gateways all needs an IP in the network

#### Prefix sizes
```
 /17  255.255.128.0   128 Cs : ~ 4000 instance / zone
 /18  255.255.192.0    64 Cs : ~ 2000 instance / zone
 /19  255.255.224.0    32 Cs : ~ 1000 instance / zone
 /20  255.255.240.0    16 Cs : ~  500 instance / zone
 /21  255.255.248.0     8 Cs : ~  200 instance / zone  the script minimum prefix size
```

### IPv6
If IPv6 is enabledd, this means the VPC will get a /56 assigned by AWS, it a live public IP space
From here the /56 is devided into 2x /57 : first will be use for the FE-network and the second to the BE-network.
Then the FE-subnets and the BE-subnets gets a /64 from the their respective network /57. The /64 assigment
is due to the AWS requirement that the CDIR size must be a /64.

```
 /56 == 256 x /64 ==  4,722,366,482,869,645,213,696 == IPv6 addresses
 /57 == 128 x /64 ==  2,361,183,241,434,822,606,848 == IPv6 addresses
 /64              ==     18,446,744,073,709,551,616 == IPv6 addresses
```

### The script usage
```
usage: [-action=<action>] [-cfgdir=<directory>] [-config=<config file>] [-tag=<tag name>] [-region=<AWS region name>] [-help] [-version]

script to create/destory VPC and to stop/start/erminate/status/add/terminate instances in the VPC

optional arguments:
  -h, --help            show this help message and exit
  -version              show program's version number and exit
  -config CONFIG        yaml file containt the instances information that need
                        to be added or terminated, used by the actions 'add'
                        or 'terminate', default to config/ec2.yaml
  -cfgdir CFGDIR        directory where to find the configuration files; names
                        are hardcoded, these are files name aws.yaml - dc.yaml
                        - sec.yaml, by default the files are under the
                        directory config/
  -action {create,destroy,start,stop,status,add,terminate,regions,key,explain}
                        action to be preformed to the selected AWS region, use
                        action 'regions' to show availabe regions.
  -region REGION        the AWS region of the VPC
  -tag TAG              the tag name of the VPC
  -log LOGFILE          log file to be used, default to awsbuild.log in
                        current directory
```

### Hello world
Comment/help/suggestion welcome

- momo
