# Guide line setting up an AWS environment

## Copyright and License
Copyright 2019 - 2020 © Badassops LLC - 😊  
License [BSD](http://www.freebsd.org/copyright/freebsd-license.html)  
Version 1.7, December 29, 2019

## The Basics

### Definiations
AWS == Amazon Web Services  
GCP == Google Cloud Platform  
K8 == Kubernetes  
As example we will be using `bao` as prefix and `bao.com` as domain and `prod` as the environment.

The scripts in this document are not optimal, they do not check for error (**none zero return of a command that should abort the rest of the script**), nor do they check whatever the script curretly running (**lock**) and not does it handles amy interrupt such as control-c. So use ar your own risk, 😈.


### 0 Cloud Provider

#### AWS
Remember AWS is an amazing cloud provider, but like other providers, it want to tide you to their service. If you OK with that then remember that to get best result you should use all AWS services instead build it your self, example database or ELK services.

#### GCP or AWS
In my opinion if your application is pure container base, then GCP might be a better solution, but if you need more very specific services, then AWS might be a better choice; do remember both cloud provider are still evolving, a service currently not available in GCP could change in the near future.
Most engineers are more familiar with AWS then GCP, but this is just part of the learning curve and
GCP is getting more traction with more companies adopting K8

**A very important note** is that AWS K8 is a slightly modified K8 in such that it will tide you to their solution, in the other hand GCP K8 solution in 99% vanilla, it means if on one day you want to host things your self, it would be easier.

### 1 Accounts
Create multiple accounts for each environment, such as development and production and have the production account the one that pays all the invoices (development and production) this will allow you to analyst the cost for development vs production: [AWS account](https://aws.amazon.com/answers/account-management/aws-multi-account-billing-strategy/) and [AWS billing](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/consolidated-billing.html)


### 2 TAG TAG TAG
The most important part of using AWS is tagging, so define a tag for each environment,
example:

```
bao-use1-prod == in AWS us-east-1 production
bao-usw2-dev  == in AWS us-west-1 development
```
then we need base tag for global and env such in IAM so in our case the base would be **bao-prod**

**Note:** use the shorter regions name instead of the full name, this due some of the AWS services have name length limitation.  
Info: [AWS regions end points](https://docs.aws.amazon.com/general/latest/gr/rande.html)

| Region                     | region-code    | zone-name | API            | ALB/NLB        | S3-WEB         |
|:-------------------------- |:-------------- |:----------|:---------------|:---------------|:---------------|
| US East (Ohio)             | us-east-2      | use2      | ZOJJZC49E0EPZ  | ZLMOA37VPKANP  | Z2O1EMRO9K5GLX |
| US East (N. Virginia)      | us-east-1      | use1      | Z1UJRXOUMOOFQ8 | Z26RNL4JYFTOTI | Z3AQBSTGFYJSTF |
| US West (N. California)    | us-west-1      | usw1      | Z2MUQ32089INYE | Z24FKFUX50B4VW | Z2F56UZL2M1ACD |
| US West (Oregon)           | us-west-2      | usw2      | Z2OJLYMUO9EFXC | Z18D5FSROUN65G | Z3BJ6K6RIION7M |
| Asia Pacific (Hong Kong)   | ap-east-1      | ape1      | Z3FD1VL90ND7K5 | Z12Y7K3UBGUAD1 | ZNB98KWMFR0R6  |
| Asia Pacific (Mumbai)      | ap-south-1     | aps1      | Z3VO1THU9YC4UR | ZVDDRBQ08TROAA | Z11RGJOFQNVJUP |
| Asia Pacific (Osaka-Local) | ap-northeast-3 | apne3     | None           | Z1GWIQ4HH19I5X | Z2YQB5RD63NC85 |
| Asia Pacific (Seoul)       | ap-northeast-2 | apne2     | Z20JF4UZKIW1U8 | ZIBE1TIR4HY56  | Z3W03O7B5YMIYP |
| Asia Pacific (Singapore)   | ap-southeast-1 | apse1     | ZL327KTPIQFUL  | ZKVM4W9LS7TM   | Z3O0J2DXBE1FTB |
| Asia Pacific (Sydney)      | ap-southeast-2 | apse2     | Z2RPCDW04V8134 | ZCT6FZBF4DROD  | Z1WCIGYICN2BYD |
| Asia Pacific (Tokyo)       | ap-northeast-1 | apne1     | Z1YSHQZHG15GKL | Z31USIVHYNEOWT | Z2M4EHUR26P7ZW |
| Canada (Central)           | ca-central-1   | cac1      | Z19DQILCV0OWEC | Z2EPGBW3API2WT | Z1QDHH18159H29 |
| China (Beijing)            | cn-north-1     | cnn1      | None           | None           | None           |
| China (Ningxia)            | cn-northwest-1 | cnnw1     | None           | None           | None           |
| EU (Frankfurt)             | eu-central-1   | euc1      | Z1U9ULNL0V5AJ3 | Z3F0SRJ5LGBH90 | Z21DNDUVLTQW6Q |
| EU (Ireland)               | eu-west-1      | euw1      | ZLY8HYME6SFDD  | Z2IFOLAFXWLO4F | Z1BKCTXD74EZPE |
| EU (London)                | eu-west-2      | euw3      | ZJ5UAJN8Y3Z2Q  | ZD4D7Y8KGAS4G  | Z3GKZC51ZF0DB4 |
| EU (Paris)                 | eu-west-3      | euw3      | Z3KY65QIEKYHQQ | Z1CMS0P5QUZ6D5 | Z3R1K369G5AVDG |
| EU (Stockholm)             | eu-north-1     | eun1      | Z3UWIKFBOOGXPP | Z1UDT6IFJ4EJM  | Z3BAZG2TWCNX0D |
| Middle East (Bahrain)      | me-south-1     | mes1      | Z20ZBPC0SS8806 | Z3QSRYVP46NYYV | Z1MPMWCPA7YB62 |
| South America (Sao Paulo)  | sa-east-1      | sae1      | ZCMLWB8V5SYIT  | ZTK26PT1VY4CU  | Z7KQH4QJS55SO  |

### 3 Application
Know your application, can it be containerized in K8? Or does it need separate instances? Whatever solution, also keep in mind to expose your application via a Load balancer, certainly if you plan to autoscale. Use DNS (AWS Route53) to point to your application and set the TTL to 5 mins (300 seconds), this will make thing easier if you have to change things.
When using the AWS load balancer solution setup your application as a CNAME of the load balancer, remember a AWS load balancer can have multiple IP's. Also note the GEO capability in Route53 that will send customer from a certain region to a load balancer in the same regions; think privacy laws.

### 4 Secrets
Avoid using AWS API key as mush as possible, instead use AWS IAM policies, roles and profiles.
Keep your secret in AWS Secret Manager and if possible either do a auto rotate or manually; example the AWS API is kept in AWS Secret Manager and is rotated

### 5 Regions, Traffic and Privacy Laws
Choose the AWS region that suite your expected traffic, the closer to your client the better, but do remember in special cases in EU (GDPR) and Canada (PIPEDA), data tagged private by the law must stay within the region. For the US regions, cost is also an important aspect, things such as 10x small instances vs 4 x big instance, remember the instance cost is not the same in each regions.
Use the AWS cost calculator: [AWS Calculator](https://calculator.s3.amazonaws.com/index.html). Once you have define the `prefect` instance type and instance count, this could be the moment you commit to at least 1 year No Upfront Revered, talk to a AWS representative, in some case startup companies get special discount.

### 6 Cost
Remember that storage and traffic can be your biggest cost, so make a decision on the followings:

- S3 create bucket as close as possible to the region of your application and setup a live cycle as how long data will be kept. In a K8 setting and < 30 days cycle, you might want to look at this solution [rook](https://rook.io/), this will keep traffic cost and storage as low as possible.
- S3 name are global which mean is an other AWS client create a S3 bucket called `momo-use1-prod`, then no other AWS client can use that bucket name!
- As much AWS Cloudtrail is useful, but it comes a steep price, so make sure to limit where and how to enable AWS Cloudtrail.
- the application should only logs as needed, over logging might drive the cost.

### 7 Network/VPC
Plan your network (VPC), chose a  network address (CIDR) that will work with your office(s) network(s), make sure that the CIDR (prefix) is big enough, I would suggest of a to use a /18 == his will allowed ~16K instance.
Remember AWS will require IPs for routing and load balancer. It cost nothing to use the private IPS in AWS

1. given the CIDR of the VPC, create a Front-End network subnet (public) and a Back-End network (private), each should have 4 subnets.
2. in both the FE-network and BE-network assign the 3 subnets to the availability zones (3), the 4th is for future use
3. make sure to not overlap your FE-network subnet with your BE-network subnet, this make setup later much easier. Example the FE-network with we the first part (/19) of the CIDR (/18) and the BE-network the second part (/19) of the CIDR (/18), this allow setting in AWS security group to use one rule to address subnets. Example VPC in several regions: in the example there is no collision in IP between the regions.

| Region     | Location   | CIDR            |
|:-----------|:-----------|:----------------|
| us-east-1  | Virginia   | 172.16.0.0/18   |
| us-east-2  | Ohio       | 172.16.64.0/18  |
| us-west-1  | California | 172.16.128.0/18 |
| us-west-2  | Oregon     | 172.16.192.0/18 |


### 8 Security
One of the most important is security, do not expose your application directly, instead use a load balancer, this means set your instance as mush as possible in the back-end network. Use HTTPS only make sure to use TLS 1.2 only and the highest encryption settings: [AWS TLS](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-security-policy-table.html) use the TLS-1-2-2017-01 policy.

Avoid SSH into any instance from the internet, instead specify the IPs that are allowed to SSH-in.
Using a bastion as jump-start server is highly recommend and optional a VPN to be even more secure, user will need to be VPN-ed to the bastion before they can ssh into any instance.
AWS has many good options to do SSO, one that is recommended if you use Google APP is to setup AWS console
access via the Google credentials, more here [AWS-GOOGLE-SSO](https://aws.amazon.com/blogs/security/how-to-set-up-federated-single-sign-on-to-aws-using-google-apps/)

Limit who has admin, setup a password policy such and length and rotation pf password, recommend to set password maximum age to 90 days. Setup the AWS EC2 security group as tide as possible.
An optional security setup, is to centralized login (user/password/ssh-key), AWS has this service but it come with a price tag, an other option would be setup your own LDAP solution such as OpenLDAP or FreeIPA

### 9 Instance image (AMI)
Creating your own instance image (AMI) should be only consider if a base image from AWS does not have the tools you need or you plan to make changes or read things such as in Route53, EC2 tags, AWS Secret Manager. Remember that using configuration systems such as Salttack, Ansible, Puppet to Chef, you can achieve the same, however it might delay when a new started instance is ready for usage. An other option would be to use of a script to be executed via the AWS EC2 `user-data` : think like the script would create Route53 record, adjust tag and more. In most cases you will need your own image. The tool recommended to create an IAM is [packer](https://www.packer.io/)
Here is an example configuration for packers (lets call it autoscale.json)

```
{
  "variables": {
    "aws_access_key": "",
    "aws_secret_key": "",
    "root_domain": "xxx" <--- change as needed
  },
  "provisioners": [
    {
      "type": "file",
      "source": "files",
      "destination": "/tmp"
    },
    {
      "execute_command": "echo 'xxxx' | {{ .Vars }} sudo -S -E bash '{{ .Path }}'", <--- the flavor of our distro
      "script": "autoscale.sh",
      "type": "shell"
    }
  ],
  "builders": [{
    "type": "amazon-ebs",
    "access_key": "{{user `aws_access_key`}}",
    "secret_key": "{{user `aws_secret_key`}}",
    "region": "xxxxx", <-- adjust to the correct region
    "source_ami": "ami-xxxx", <--- use correct AMI ID
    "instance_type": "t2.micro",
    "ssh_username": "xxxx", <--- use correct user name base on the source AMI
    "ssh_timeout": "5m",
    "ssh_pty" : "true",
    "vpc_id": "vpc-xxxx, <--- your VPC ID
    "subnet_id": "subnet-xxxx", <--- your **public* subnet
    "security_group_ids": [ "sg-xxxx" ], <--- correct EC2 security group, should allow SSH from any
    "associate_public_ip_address": true,
    "ami_name": "xxxx - {{isotime | clean_ami_name}}",
    "ami_block_device_mappings": [
      {
        "device_name": "/dev/sda1",
        "volume_size": 64, <--- 64GB, change as needed
        "delete_on_termination": true,
        "volume_type": "gp2" <--- change as needed
      }
    ]
  }]
}
```

And here is an example of the script `autoscale.sh` define above.


```
#!/usr/bin/env bash
# BSD 3-Clause License
#
# Copyright (c) 2019 - 2020, © Badassops LLC

# Fix ownership
chown -R root:root /tmp/files

# set the region from availability zone
export REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
REGION=${REGION%?}  # remove last char from az name to get region

# make sure all logs are delete
find /var/log -type f -exec rm {} \;
touch /var/log/utmp /var/log/wtmp /var/log/btmp
chmod 0664 /var/log/utmp /var/log/wtmp /var/log/btmp
chown root:utmp /var/log/utmp /var/log/wtmp /var/log/btmp

# install our script
# cp -arv /tmp/files/<our-scripts-location> /<our-scripts-location>
# find /<our-scripts-location> -type d -exec chmod 0755 {} \;
# chown -Rh root:root /<our-scripts-location>

# do something here
#

# for APT
# make sure we have latest
# apt-get -y update
# DEBIAN_FRONTEND=noninteractive \
#  apt-get -y \
#    -o DPkg::Options::="--force-confold" \
#    -o DPkg::Options::="--force-confdef" \
#    dist-upgrade
#
# remove packages
# apt-get -y purge package package package
#
# install packages
# apt-get -y \
# -o DPkg::Options::="--force-confold" \
# -o DPkg::Options::="--force-confdef" \
# install package package package

# For YUM
# make sure we have latest
# yum --assumeyes clean expire-cache
#
# remove packages
# yum --assumeyes --erase package package package
#
# install packages
# Yum base
# yum --assumeyes --install package package package

# do final something here
#
exit 0
```

Then create the ami with once you have downloaded packer. Do realized it **requires step 2 before you can create the AMI**

```
#!/usr/bin/env bash
# BSD 3-Clause License
#
# Copyright (c) 2019 - 2020, © Badassops LLC

export AWS_ACCESS_KEY_ID="" <--- insert your access key here
export AWS_SECRET_ACCESS_KEY="" <--- insert your secret key here
export AWS_DEFAULT_REGION="us-east-1" <--- adjust as needed
PACKER_LOG=1 packer build autoscale.json
```


For autoscale to work well, one need to read more here [Autoscale](https://aws.amazon.com/autoscaling/)
When using autoscale with Auto Scaling Group you want to create a launch template and make sure to use the AMI you created and assign a role profile (will be discussed later). We use this to avoid to put any secrets in the AMI and instead using the role profile to access any required services.
Launch Configuration or EC2 Fleet is outside the scope of this document

## The first step

Assume this is a Unix based laptop (OSX or Linux)
We want to automate all the task to build our AWS environment, however there is 1 step that need to be done manually, create the first AWS IAM user (we will call the user terraform)

For starter in your laptop : make sure you have python3 install and pip3 (for python 3)
install XCODE from Apple store to get python 3 and pip3

```
sudo pip3 install awscli
sudo pip3 install boto3
```

The command `aws` (after executing the above command is what we will use to do the IAM/S3 automation

### First IAM Account
	- in AWS IAM create user == hello-app-terraform
		Access type Programmatic access
		Attach existing policies directly : AdministratorAccess
		(we will adjust and tide-up the permissions later)
		Tag : key === Name and value == <your-base-tag>-terraform
		!!!!make sure do download the CSV! it has the secret-key and access-key!!!!

### AWS CLI setup
	- then open terminal on your laptop
	1. mkdir ~/.aws
	2. chmod 0700 ~/.aws
	3. vi ~/.aws/credentials
		add these lines and then save
		[default]
		aws_access_key_id = <XXX FROM THE downloaded CSV>
		aws_secret_access_key =  <XXX FROM THE downloaded CSV>
		region = <XXX-set correct-region-name>
	4. vi .aws/config
		add these lines and then save
		[default]
		output = json
	5. chmod 0400 ~/.aws/credentials ~/.aws/config
	6. test with : aws --profile default s3 ls
		since there is no bucket it will show nothing and there should be no errors
	We will need the AWS api information for the step later, creating the VPC and base security

### SSH key for EC2
	- still in terminal on your laptop
	Now we need to create a SSH key that will be use to access our instances, make sure to keep this secure, we will need the Public key later.
	- still in terminal on your laptop
	1. cd ~/.ssh (if it does not exist then do : mkdir ~/.ssh ; chmod 0700 ~/.ssh)
	2. ssh-keygen -t rsa -C "<your-base-tag>" -b 4096 -n "AWS" -P '' -f ./id_rsa-<your-base-tag>
	later we will need the content of the files ~/.ssh/id_rsa-<your-base-tag>.pub

## The Second step
This is the step that will create the network infrastrucrure such as VPC, subnets, Internet gateway, NAT gateways and for EC2 the security groups and SSH Key Pair.
We will be using [ops-aws](https://github.com/my10c/ops-aws)  
Once the repository has been cloned and you have read some of the documentation, is time to configure the yaml file under config
**NOTE**:
- currently IPV6 is only support on the public facing subnet, this is a AWS limitation. So make sure to be dual-stack.
- in the next release, I plan to add IPV6 support for the back-end.


### aws.yaml
Create the file aws.yaml under config directory with the following content

```
global:
  output: 'json'
  account: '{your aws account-#}'

credentials:
  aws_access_key_id: '{your aws api key}'
  aws_secret_access_key: '{your aws api secret}'
  region: '{your default regions}'

key:
    keyname: '{your key name, example bao-prod}'
    pubkey: '{your rsa public key, content of ~/.ssh/id_rsa-<your-base-tag>.pub}'
```

### dc.yaml
Create the file dc.yaml under the config directory with the following content,
Remember adjust for you need!

```
us-east-1:
  dc_region: 'Virginia'
  dc_endpoint: 'us-east-1'
  dc_isocode: 'us-va'
  dc_public_domain: 'bao.com'
  dc_domain: 'us-va.internal.bao.com' <--- internal domain
  dc_network: '172.16.0.0' <--- VPC network
  dc_cidr: '18' <--- VPC CIDR size, 18 is the recommended size
  dc_bastion: 'patriots' <--- any name you like for the bastion, see NOTES 2
  dc_ami: 'ami-01e24be29428c15b2' <--- the AMI you will be using, see NOTES 2
  dc_ipv6: True <--- set to False or True is you need IP6, recommended is True

```
NOTES
1. you can have multiple entries, one per region.
2. in the current version this is not use but need to set

### sec.yaml
Create the file sec.yaml here below is an example with explanation.
Some basic format of the sec.yaml file

```
Rule
  Protocol : start port : end port : destination
   - if start port == ALL then end port must be ALL : for TCP and UDP
     if start port == -1 then end port must be -1   : for ICMP
   - use the keyword 'none' for no in_rules or out_rules since
     the in_rules and out_rules must exist
   - make sure there is exactly 1 space between values!
   - other security group name can be used as destination
   Special identify names:
     Name:           info:
   - VPC_NET     vpc ipv4 cidr
   - VPC_FE      vpc (f)ront (e)nd network ipv4 cidr
   - VPC_BE      vpc (b)ack (e)nd network ipv4 cidr
   - VPC_NET_V6  vpc ipv6 cidr
   - VPC_FE_V6   vpc (f)ront (e)nd network ipv6 cidr
   - VPC_BE_V6   vpc (b)ack (e)nd network ipv6 cidr
```

Remember the 2 spaces as this must be a valid yaml file, below is a base example

```
# start with the security group names
security_groups:
  bao-prod-bastion:
  bao-prod-trusted:
  bao-prod-packer:
  bao-prod-all:
  bao-prod-rds:
  bao-prod-https:
  bat-prod-http:

# for each group define their rule
bao-prod-bastion:
  description: 'Allow 22/SSH only from known IPs'
  in_rules:
    - 'TCP 22 22 x.x.x.x/x'
    - 'TCP 22 22 y.y.y.y/y'
  out_rules:
    - 'ALL ALL ALL 0.0.0.0/0'
    - 'ALL ALL ALL ::/0'

bao-prod-trusted:
  description: 'Trusted from Bastion SSH and ICMP within VPC'
  in_rules:
    - 'TCP 22 22 bao-prod-bastion'
    - 'ICMP -1 -1 VPC_NET'
    - 'ICMP -1 -1 VPC_NET_V6'
  out_rules:
    - 'ALL ALL ALL VPC_NET'
    - 'ALL ALL ALL VPC_NET_V6'

bao-prod-packer:
  description: 'For AMI build, allow from VPC only'
  in_rules:
    - 'ALL ALL ALL VPC_NET'
    - 'ALL ALL ALL VPC_NET_V6'
  out_rules:
    - 'ALL ALL ALL 0.0.0.0/0'
    - 'ALL ALL ALLL ::/0'

bao-prod-all:
  description: 'Allow all TCP and ICMP only from known IPs'
  in_rules:
    - 'TCP ALL ALL x.x.x.x/x'
    - 'ICMP -1 -1 x.x.x.x/x'
  out_rules:
    - 'ALL ALL ALL 0.0.0.0/0'
    - 'ALL ALL ALL ::/0'

bao-prod-rds:
  description: 'Access to RDS, Mysql and Postgres only from Back-End'
  in_rules:
    - 'TCP 3306 3306 VPC_BE'
    - 'TCP 5432 5432 VPC_BE'
    - 'ICMP -1 -1 bao-prod-rds'
  out_rules:
    - 'TCP ALL ALL VPC_BE'
    - 'ICMP -1 -1 bao-prod-rds'

bao-prod-https:
  description: 'Allow HTTPS from anywhere'
  in_rules:
    - 'TCP 443 443 ALL'
  out_rules:
    - 'ALL ALL ALL 0.0.0.0/0'
    - 'ALL ALL ALL ::/0'

bao-prod-http:
  description: 'Allow HTTP only within the VCC'
  in_rules:
    - 'TCP 80 80 VPC_NET'
    - 'TCP 80 80 VPC_NET_V6'
  out_rules:
    - 'ALL ALL ALL 0.0.0.0/0'
    - 'ALL ALL ALL ::/0'
```

### ec2.yaml
For now the file is required but not in use, so create one under the director config with the following content

```

bastion:
  count: '1'
  tags:
    - Name: 'bastion'
    - component: 'Operations'
    - datacenter: 'us1'
    - environment: 'prod'
    - hostid: '01'
    - tld: 'example.com'
  sec_groups:
    - 'trusted'
    - 'bastion'
  type: 't2.small'
  create: True
  public_ip: True
  static_ip: True
  vpc_placement: 'fe'
  data_volume: '64'
```

### Create the infrastructure
Now is time to create the network with the python script

** TODO **

## The third step

Now that we have the AWS cli configure and working I time to create the base IAM objects and S3.

### IAM policies
In IAM we will create 12 policies, these are

1. route53_rw : allow read and write in AWS Route53

```
{
  "Sid": "Route53ReadWrite",
  "Version": "2012-10-17",
  "Statement":[{
    "Effect":"Allow",
    "Action":[
      "route53:*",
      "route53domains:*"
    ],
    "Resource":"*"
  }]
}
```

2. route53_ro : allow read only in AWS Route53

```
{
   "Sid": "Route53ReadOnly",
   "Version": "2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "route53:GetHostedZone",
            "route53:ListResourceRecordSets"
         ],
         "Resource":"*"
      },
      {
         "Effect":"Allow",
         "Action":["route53:ListHostedZones"],
         "Resource":"*"
      }
   ]
}
```

3. ec2_tag_rw : allow to create, modify to delete an EC2 tag

```
{
  "Sid": "Ec2TagReadWrite",
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:CreateTags",
      "ec2:DeleteTags",
    ],
    "Resource": "*"
  }]
}
```

4. ec2_tag_ro : allow to read all EC2 tags

```
{
  "Sid": "Ec2TagReadOnly",
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:DescribeTags"
    ],
    "Resource": "*"
  }]
}
```

5. ec2_instance_info_ro : allow to get an instance info

```
{
  "Sid": "Ec2InfoReadOnly",
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:Describe*",
    ],
    "Resource": "*"
  }]
}
```

6. s3_rw : allow to list buckets, get, put, list and delete objects in S3 buckets, we should one for specific bucket too! Use specific bucket(s) and add bucket-name to the policy so you can differentiate between policies

```
{
   "Sid": "S3ReadWrite",
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
           "s3:GetBucketLocation",
           "s3:ListAllMyBuckets"
          ],
        "Resource": [
            "arn:aws:s3:::*
        ]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:ListBucket"
        ],
        "Resource": [
          "arn:aws:s3:::*
        ]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ],
        "Resource": [
          "arn:aws:s3:::*",
          "arn:aws:s3:::*/*"
        ]
      }
    ]
}
```

7. s3_ro : allow to list buckets, get and list objects in S3 buckets, we should one for specific bucket too! Use specific bucket(s) and add bucket-name to the policy so you can differentiate between policies


```
{
   "Sid": "S3ReadOnly",
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:ListBucket"
        ],
        "Resource": [
            "arn:aws:s3:::*
        ]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:List*",
          "s3:Get*",
          "s3:HeadBucket"
        ],
        "Resource": [
          "arn:aws:s3:::*",
          "arn:aws:s3:::*/*"
        ]
      }
    ]
}
```

8. asm_rw : add, modify or delete a secret in AWS Secret Manager, refined to specific secrets should be considert (use specific ARN(s) and add secret-name to the policy so you can differentiate between policies


```
{
  "Sid": "ASMReadWrite",
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["secretsmanager:*"],
    "Resource": ["*"]
  }]
}
```

9. asm_ro : read a secret in AWS Secret Manager, refined to specific secret should be consider (use specific ARN(s)) and add secret-name to the policy so you can differentiate between policies


```
{
  "Sid": "ASMReadOnly",
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
        "secretsmanager:GetResourcePolicy",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:ListSecretVersionIds"
    ],
    "Resource": ["*"]
  }]
}
```

10. acm_rw : add, modify or delete a certificate in AWS Certificate Manager, refined to specific certificate should be consider (use specific ARN(s)) and add certificate-name to the policy so you can differentiate between policies


```
{
  "Sid": "ACMReadWrite",
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["acm:*"],
    "Resource": "*"
  }]
}
```

11. acm_ro : add, modify or delete a certificate in AWS Certificate Manager, refined to specific certificate should be consider (use specific ARN(s)) and add certificate-name to the policy so you can differentiate between policies

```
{
  "Sid": "ACMReadOnly",
  "Version": "2012-10-17",
  "Statement": {
    "Effect": "Allow",
    "Action": [
      "acm:DescribeCertificate",
      "acm:ListCertificates",
      "acm:GetCertificate",
      "acm:ListTagsForCertificate"
    ],
    "Resource": "*"
  }
}
```
12. autoscale : will be use for autoscaling and instance profile, allow to update Route53 record and EC2 tags

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AutoScale",
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "route53:Get*",
                "route53:List*",
                "route53:TestDNSAnswer",
                "route53:ChangeResourceRecordSets"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
Extra policy: full admin but requires 2fa

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        },
        {
            "Sid": "DenyAllExceptListedIfNoMFA",
            "Effect": "Deny",
            "NotAction": [
                "iam:CreateVirtualMFADevice",
                "iam:EnableMFADevice",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ListVirtualMFADevices",
                "iam:ResyncMFADevice",
                "sts:GetSessionToken"
            ],
            "Resource": "*",
            "Condition": {
                "BoolIfExists": {
                    "aws:MultiFactorAuthPresent": "false"
                }
            }
        }
    ]
}
```

Here is an example of script to create the above policies, it assumed that the json files are extension to `iam_policy`

```
#!/usr/bin/env bash
# BSD 3-Clause License
#
# Copyright (c) 2019 - 2020, © Badassops LLC

_debug=echo # <-- set to nothing for real executing of the script to create the policies
_env="prod"
_prefix="bao-$_env-"

# ROUTE53   == dns
# EC2       == compute
# S3        == storage
# ASM       == secret manager
# ACM       == certificate manager

_policies="
route53_rw
route53_ro
ec2_tag_rw
ec2_tag_ro
ec2_instance_info_ro
s3_rw
s3_ro
asm_rw
asm_ro
acm_rw
acm_ro
"

for _policy in $_policies
do
    _name=$_prefix$_policy
    echo "creating iam policy $_name ..."
    $_debug aws --profile default iam create-policy \
        --policy-name "$_name"  \
        --description "$_name"  \
        --policy-document file://"$_policy".iam_policy
    echo -e "\n"
done
```

For more information over [IAM policy](https://docs.aws.amazon.com/iam/index.html)

### Role for autoscale
Next we will create a role and profile that will be able to be use for autoscaling, the one is a bit tricky. First we create a role configuration json file, this role allows to use the AWS EC2 service. We want to limit what service a role can have, but if necessary, more than one service can be assigned.

```
{
  "Version": "2012-10-17",
  "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }]
}
```

Now we have the role so best here below is a script to create the autoscale role

```
#!/usr/bin/env bash
# BSD 3-Clause License
#
# Copyright (c) 2019 - 2020, © Badassops LLC

_debug=echo # <-- set to nothing for real executing of the script to create the role
_env="prod"
_prefix="bao-$_env-"
_aws_account="xxxxx" # <-- adjust with your AWS account-#

# make sure the policy was created first
_roles="
autoscale
"

for _role in $_roles
do
    _name=$_prefix$_role
    echo "creating iam role $_name ..."
    # Create the role and attach the trust policy that allows EC2 to assume this role.
    $_debug aws --profile default iam create-role \
        --role-name "$_name"    \
        --description "$_name"  \
        --assume-role-policy-document file://$_role.role

    # Embed the permissions policy (in this example an inline policy) to the role to specify what it is allowed to do.
    $_debug aws --profile default iam create-instance-profile   \
        --instance-profile-name "$_name"

    $_debug aws --profile default iam add-role-to-instance-profile  \
        --instance-profile-name "$_name" \
        --role-name "$_name"

    $_debug aws --profile default iam attach-role-policy    \
        --role-name "$_name" \
        --policy-arn arn:aws:iam::$_aws_account:policy/"$_name"

    echo -e "\n"
done
```

For more information over [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html)

### IAM Users
Next creating IAM users, at this point we assume you are familiar with he IAM policy and for this we will be using this script below, it will create the user, assign the policy and then create the user AWS API key, saved in the fly <user-name>.aws. Make sure to save the .AWS file securely!

```
#!/usr/bin/env bash
# BSD 3-Clause License
#
# Copyright (c) 2019 - 2020, © Badassops LLC

_debug=echo # <-- set to nothing for real executing of the script to create the users
_aws_account=xxxx # <--- put your AWS account-#

_users="
luc:policy-name <--- format is username:policy-name, the policy name should be the one that we created above. We assume we do not give admin
"

for _user in $_users
do

    _user_name=${_user%:*}
    _user_policy=${_user#*:}
    echo "creating user $_user_name with policy $_user_policy attached ..."
    $_debug aws --profile default iam create-user   \
        --user-name "$_user_name"   \
        --tag "Key=Name,Value=$_user_name"

    $_debug aws --profile default iam attach-user-policy    \
        --user-name "$_user_name"   \
        --policy-arn "arn:aws:iam::$_aws_account:policy/$_user_policy"

    $_debug aws --profile default iam create-access-key \
        --user-name "$_user_name" | $_debug tee -a "$_user_name".aws

    echo -e "\n"
done
[[ -f *.aws ]] && chmod 0400 *.aws
```

### Create S3 buckets
And finally create the S3 buckets, but before that we need to create a lifecycle configuration files, you will need to adjust to match your need, how many days you need (want) to keep the objects in the S3 bucket. We name the file `template.s3_lifecycle`
The values of `%%DAYS%%` will be modified by the script we will be using, so no need to adjust the value here.

```
{
    "Rules": [
        {
            "Expiration": {
                "Days": %%DAYS%%
            },
            "ID": "objects-cleaner",
            "Filter": {
                "Prefix": ""
            },
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": %%DAYS%%
            },
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": %%DAYS%%
            }
        }
    ]
}
```

Here is an example for a S3 bucket access policy, allowing access from certain VPC and/or certain IPs only. The script only support single entry in he format of IP or NETWORK and the CDIR mask. In the json file the the %% S3_BUCKET%%, %%ALLOW_VPC_ID%%, %% ALLOW_IP_OR_NETWORK%% and %%CIDR_MASK%% will be replaced by the create script

```
{
  "Sid": "S3AllowOnlyFromVPCAndSourceIP",
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "S3AllowOnlyFromVPCAndSourceIP",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::%% S3_BUCKET%%",
      "arn:aws:s3:::%%S3_BUCKET%%/*"
    ],
    "Condition": {
      "StringNotLike": {
        "aws:sourceVpc": [
          "%%ALLOW_VPC_ID%%"
        ]
      },
      "NotIpAddress": {
        "aws:SourceIp": [
          "%%ALLOW_IP_OR_NETWORK%%/%%CIDR_MASK%%"
        ]
      }
    }
  }]
}
```

The create buckets script

```
#!/usr/bin/env bash
# BSD 3-Clause License
#
# Copyright (c) 2019 - 2020, © Badassops LLC

_debug=echo # <-- set to nothing for real executing of the script to create the S# buckets
_env="prod"
_prefix="bao-${_env}-"

# <bucket name>, adding the S3 regions to make it easier to track in which region the bucket was created
# <region> use correct AWS region preferable location for the bucket, keep GDPR in mind
# <lifecycle day> use disable for no lifecycle, otherwise days to expired the objects
# <bucket policy> use disable for no policy other wise use enable
# <vpc allowed> the VPC allowed to access he bucket, for now it only support 1 VPC
# <ip/net allowed> the IP or network addres allowed to access he bucket, for now it only 1 entry
# <cidr mask> the mask of the allowed ip or network
#
# example : momo:us-east-1:30:enable:vpc-xxx:6.6.6.0:16

_s3_buckets="
momo-use1:us-east-1:30:enable:vpc-xxx:6.6.6.0:16
"

for _s3_bucket in $_s3_buckets
do
	_s3_bucket_name=$_prefix"$(echo $_s3_bucket | cut -d: -f1)"
	_s3_bucket_region="$(echo $_s3_bucket 		| cut -d: -f2)"
	_s3_bucket_lifecycle="$(echo $_s3_bucket 	| cut -d: -f3)"
	_s3_bucket_policy="$(echo $_s3_bucket 		| cut -d: -f4)"
	_s3_bucket_vpc_acl="$(echo $_s3_bucket 		| cut -d: -f5)"
	_s3_bucket_ip_acl="$(echo $_s3_bucket 		| cut -d: -f6)"
	_s3_bucket_cidr_mask="$(echo $_s3_bucket 	| cut -d: -f7)"

	echo "Creating S3 bucket $_s3_bucket_name"
	if [[ "$_s3_bucket_region" != "us-east-1" ]] ; then
		$_debug aws --profile default s3api create-bucket \
			--create-bucket-configuration LocationConstraint=$_s3_bucket_region \
			--acl private \
			--no-object-lock-enabled-for-bucket \
			--bucket "$_s3_bucket_name" \
			--region "$_s3_bucket_region"
	else
		$_debug aws --profile default s3api create-bucket \
			--acl private \
			--no-object-lock-enabled-for-bucket \
			--bucket "$_s3_bucket_name" \
			--region "$_s3_bucket_region"
	fi
	if [[ "$_s3_bucket_policy" != disable ]] ; then
		echo "Adding Bucket policy to the S3 bucket $_s3_bucket_name"
		cat template.s3_policy |sed -e "s/%%S3_BUCKET%%/$_s3_bucket_name/g;"				|\
								sed -e "s/%%ALLOW_VPC_ID%%/$_s3_bucket_vpc_acl/g;"			|\
								sed -e "s/%%ALLOW_IP_OR_NETWORK%%/$_s3_bucket_ip_acl/g;"	|\
								sed -e "s/%%CIDR_MASK%%/$_s3_bucket_cidr_mask/g;" > "$_s3_bucket_name".s3_policy
		$_debug aws --profile default	\
			--region $_s3_bucket_region		\
			s3api put-bucket-policy 		\
			--cli-input-json file://"$_s3_bucket_name".s3_policy \
			--bucket "$_s3_bucket_name"
		#cat "$_s3_bucket_name".s3_policy
		rm "$_s3_bucket_name".s3_policy
	fi

	if [[ "$_s3_bucket_lifecycle" != "disable" ]] ; then
		echo "Adding Bucket lifecycle of $_s3_bucket_lifecycle days to the S3 bucket $_s3_bucket_name"
		cat template.s3_lifecycle | sed -e "s/%%DAYS%%/$_s3_bucket_lifecycle/g;" > "$_s3_bucket_name".s3_lifecycle
		$_debug aws --profile default	\
			--region $_s3_bucket_region		\
			s3api put-bucket-lifecycle-configuration \
			--lifecycle-configuration file://"$_s3_bucket_name".s3_lifecycle \
			--bucket "$_s3_bucket_name"
		#cat "$_s3_bucket_name".s3_lifecycle
		rm "$_s3_bucket_name".s3_lifecycle
	fi
		echo -e "\n"
done
```

# Hello world
This document is work in progress!  
Comment/help/suggestion welcome  
momo 👋
