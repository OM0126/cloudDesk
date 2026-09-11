CloudDesk

Unified Multi-Cloud Infrastructure Management Platform

CloudDesk is a web application built with Django for managing cloud infrastructure from one place.
The goal is to give users one dashboard where they can connect and manage their own cloud accounts.
CloudDesk follows a Bring Your Own Cloud (BYOC) approach. Users connect their own cloud accounts, while the infrastructure and billing stay in those accounts.

Our Vision

Cloud infrastructure is becoming increasingly multi-cloud. Developers and organizations may use AWS, Azure, and other cloud providers at the same time.
Managing each provider separately can be difficult because every provider has its own:

Management console

APIs

Authentication

Networking

Resource types

Monitoring systems

Billing systems

CloudDesk aims to solve this problem by providing a unified interface for cloud infrastructure management.

Why CloudDesk?

CloudDesk is not being built only for cloud administrators.

A major goal of the project is to make cloud infrastructure easier for developers, college students, and people who are learning cloud computing and DevOps.

Tools such as Terraform are very powerful, but they usually require users to understand Infrastructure as Code, providers, resources, variables, state files, modules, and configuration files before they can build a complete environment.

CloudDesk takes a more visual and practical approach.

Instead of starting with a Terraform script, a user can select what they need from the CloudDesk interface and let the platform handle the cloud API calls.

For example, imagine that you are building an application that needs:

10 Virtual Machines
5 instances on AWS
5 instances on Azure

3 object storage buckets
1 bucket on AWS
2 buckets on Azure

With CloudDesk, the user can connect both cloud accounts and create the required resources from one dashboard.

The user does not need to open the AWS Console, then open the Azure Portal, then manually repeat the same process.

CloudDesk can provide one workflow such as:

Application Deployment
        |
        +-- AWS
        |    +-- 5 EC2 Instances
        |    +-- 1 S3 Bucket
        |
        +-- Azure
             +-- 5 Virtual Machines
             +-- 2 Storage Accounts

The goal is to make this kind of multi-cloud setup easier to understand and easier to operate.

A Practical Example

Suppose a college student is building a web application as a final-year project.

The application needs:

Frontend servers
    5 AWS EC2 instances
    5 Azure Virtual Machines

Storage
    1 AWS S3 bucket
    2 Azure Storage resources

Database
    AWS RDS
    Azure SQL

Networking
    AWS VPC
    Azure Virtual Network

Normally, the student would need to:

Log in to AWS.

Create the AWS resources.

Configure AWS networking.

Log in to Azure.

Create the Azure resources.

Configure Azure networking.

Exchange networking information between both environments.

Keep track of all the created resources.

CloudDesk aims to bring these tasks into one application.

                         CloudDesk
                            |
             +--------------+--------------+
             |                             |
             v                             v
            AWS                           Azure
             |                             |
       5 EC2 Instances              5 Virtual Machines
       1 S3 Bucket                  2 Storage Resources
       RDS                          Azure SQL
       VPC                          Virtual Network

This makes CloudDesk useful as a learning platform as well as a practical infrastructure management tool.

Multi-Cloud Communication

Another important part of CloudDesk is communication between resources running in different cloud providers.

For example, imagine an application where:

AWS
5 EC2 Instances
       |
       |  Application Traffic
       |
       +-----------------------------+
                                     |
                                     v
                                 Azure
                            5 Virtual Machines

CloudDesk can help users prepare the networking configuration needed for communication between the two environments.

The long-term goal is to support use cases such as:

AWS EC2 Instance 1
        |
AWS EC2 Instance 2
        |
AWS EC2 Instance 3
        |
AWS EC2 Instance 4
        |
AWS EC2 Instance 5
        |
        |  Secure Multi-Cloud Network
        |
Azure VM 1
        |
Azure VM 2
        |
Azure VM 3
        |
Azure VM 4
        |
Azure VM 5

This can allow an application to use resources from both AWS and Azure instead of keeping the complete application inside one cloud provider.

For example:

AWS:
Application frontend
       |
       v
5 EC2 instances

       |
       | Multi-cloud communication
       |

Azure:
Application processing
       |
       v
5 Virtual Machines

CloudDesk can eventually help with the configuration needed for these connections, including cloud networking, routing, security rules, and resource discovery.

The exact networking method will depend on the cloud architecture and security requirements.

Why This Is Different From Just Writing Terraform

Terraform is an important Infrastructure as Code tool, and CloudDesk does not try to replace it.

Instead, CloudDesk focuses on a different experience.

Terraform is excellent when a developer already knows how to write infrastructure definitions and wants infrastructure to be reproducible through code.

CloudDesk is designed to make the same kind of infrastructure easier to understand and operate through a visual application.

A simple comparison is:

Terraform
    |
    +-- Write configuration
    +-- Define providers
    +-- Define resources
    +-- Manage variables
    +-- Manage state
    +-- Run Terraform commands

CloudDesk
    |
    +-- Connect cloud accounts
    +-- Select resources
    +-- Configure resources
    +-- Launch resources
    +-- View resources
    +-- Manage resources
    +-- See multiple clouds in one dashboard

CloudDesk can also use Terraform in the future.

Instead of choosing between the two, the long-term platform can support both:

                CloudDesk
                    |
          +---------+---------+
          |                   |
          v                   v
       Visual UI          Terraform
          |                   |
          +---------+---------+
                    |
                    v
            Cloud Infrastructure

This gives developers a choice between visual management and Infrastructure as Code.

Who Can Benefit From CloudDesk?

CloudDesk is intended to be useful for more than cloud administrators.

College Students

Students can use CloudDesk to learn:

Cloud computing

AWS

Azure

Networking

Virtual machines

Storage

Infrastructure

DevOps

Multi-cloud architecture

For a college project, a student can build and manage a realistic multi-cloud environment without manually switching between multiple provider consoles for every operation.

Developers

Developers can use CloudDesk when an application needs resources across more than one cloud provider.

For example:

Application
    |
    +-- AWS frontend
    |
    +-- Azure processing
    |
    +-- AWS storage
    |
    +-- Azure database

DevOps Learners

CloudDesk can provide a practical way to understand how different cloud resources, networks, and services work together.

Small Teams

A small development team can use a common dashboard to understand what infrastructure exists across different cloud accounts.

Cloud Engineers

Cloud engineers can use CloudDesk as a management layer for supported multi-cloud operations while still having the option to use Terraform and other Infrastructure as Code tools.

Learning Through CloudDesk

One of the goals of CloudDesk is to help people learn by doing.

Instead of only reading about:

EC2
VPC
Subnet
Security Group
Azure VM
Virtual Network
Storage
Routing

a student can create these resources and see how they are connected.

For example:

Create 5 AWS EC2 instances
          |
          v
Create AWS network
          |
          v
Create 5 Azure VMs
          |
          v
Create Azure network
          |
          v
Configure communication
          |
          v
Test application traffic

This creates a practical learning environment for cloud and DevOps students.

Multi-Cloud Application Example

A more complete example could look like this:

                         CloudDesk
                            |
              +-------------+-------------+
              |                           |
              v                           v
             AWS                         Azure
              |                           |
       +------+-------+             +-----+------+
       |              |             |            |
       v              v             v            v
   5 EC2 Instances   S3       5 Azure VMs    Storage
       |                            |
       |                            |
       +---------- Network ---------+
                    |
                    v
             Application Traffic

A project team could use this model to build an application where some services run on AWS and others run on Azure.

CloudDesk would provide one place to see and manage the infrastructure.

The Long-Term Idea

The long-term idea is not simply to create another cloud console.

CloudDesk is intended to become a practical platform for building and learning multi-cloud infrastructure.

The platform should help a user move from:

"I need 10 servers"

to:

5 servers on AWS
5 servers on Azure

and from:

"I need storage"

to:

1 AWS S3 bucket
2 Azure storage resources

and eventually from:

"I need two cloud environments to communicate"

to:

AWS Network
       |
       | Secure Connection
       |
Azure Network

all from one platform.

This is where CloudDesk can become useful for students, developers, DevOps learners, and teams that want a simpler way to understand and manage multi-cloud infrastructure.

                    CloudDesk
                       |
          +------------+------------+
          |                         |
          v                         v
         AWS                      Azure
          |                         |
          v                         v
     AWS Resources            Azure Resources

Our long-term goal is to make CloudDesk a single place to manage infrastructure across multiple clouds.

Main Objectives

The main goals of CloudDesk are:

Provide a unified multi-cloud dashboard

Allow users to connect their own cloud accounts

Manage cloud resources through official cloud APIs

Provide secure authentication

Protect sensitive infrastructure operations

Provide cloud resource information in a simple interface

Support multiple cloud providers

Simplify common infrastructure operations

Build a foundation for cloud automation and DevOps

Bring Your Own Cloud (BYOC)

CloudDesk uses a Bring Your Own Cloud (BYOC) approach.
The user owns the cloud account and infrastructure.
CloudDesk acts as a management layer between the user and the cloud provider.

                 User
                  |
                  v
              CloudDesk
                  |
          +-------+-------+
          |               |
          v               v
         AWS             Azure
          |               |
          v               v
    User Resources   User Resources

The user still pays the cloud provider directly.
CloudDesk does not own the user's cloud resources.

AWS Integration

AWS is the first cloud provider implemented in CloudDesk.
CloudDesk communicates with AWS using AWS APIs and Boto3.

AWS Services

EC2

CloudDesk supports or is being extended to support:

View EC2 instances

Create EC2 instances

Create multiple EC2 instances

Start instances

Stop instances

Reboot instances

Terminate instances

View instance state

View instance type

View private IP

View public IP when available

View VPC

View subnet

View security group

View availability zone

View key pair

Provide basic connection information

S3

View buckets

Create buckets

Delete buckets

RDS

View database instances

Start databases

Stop databases

Delete databases

Lambda

View Lambda functions

Delete Lambda functions

VPC

View VPC resources

Create VPCs

Delete VPCs

IAM

View IAM users

Create IAM users

Delete IAM users

CloudWatch

View CloudWatch alarms

Delete CloudWatch alarms

EC2 Launch Experience

One of the major goals of CloudDesk is to provide an EC2 launch experience similar to the AWS console.
The planned launch workflow includes:

EC2 Launch
   |
   +-- Name / Tags
   |
   +-- Application / OS Image
   |
   +-- Instance Type
   |
   +-- Key Pair
   |
   +-- Network Settings
   |
   +-- Storage
   |
   +-- Advanced Settings
   |
   +-- Number of Instances
   |
   +-- Launch

CloudDesk is designed to make the launch process easier by showing the available options instead of making users enter every AWS resource ID manually.
After launching an instance, CloudDesk can display information such as:

Instance ID
Instance State
Instance Type
Private IP
Public IP
Availability Zone
VPC
Subnet
Security Group
Key Pair

For instances with a reachable public address, CloudDesk can also provide basic connection guidance.

Security

Security is a major part of CloudDesk because the application can perform operations on real cloud infrastructure.

User Authentication

CloudDesk uses Django authentication.
Google OAuth is also supported through Django Allauth.

OTP Protection

Sensitive cloud operations can be protected using email OTP verification.
The general workflow is:

User
  |
  v
Select Infrastructure Action
  |
  v
Request OTP
  |
  v
OTP Sent Through Email
  |
  v
Verify OTP
  |
  v
Execute Cloud Operation

This adds another layer of protection before a sensitive cloud action is run.

Credential Management

CloudDesk is designed to keep sensitive credentials outside the source code.
Credentials should be stored using environment variables.
Example:

SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

Cloud credentials and application secrets must never be hardcoded into the source code.
They must also never be committed to GitHub.

Azure Integration

Azure is the next major cloud provider that will be integrated into CloudDesk.
The Azure implementation will follow the same overall multi-cloud architecture used for AWS.
The planned Azure connection uses service-principal authentication.
Required configuration includes:

Subscription ID
Tenant ID
Client ID
Client Secret

The long-term architecture will look like:

                    CloudDesk
                       |
          +------------+------------+
          |                         |
          v                         v
         AWS                      Azure
          |                         |
          v                         v
      AWS APIs                 Azure APIs

Planned Azure Services

Azure Virtual Machines

Planned operations:

List VMs

Create VMs

Start VMs

Stop VMs

Restart VMs

Delete VMs

View networking information

Azure Storage

Planned operations:

List storage accounts

View storage information

Create supported storage resources

Delete supported resources

Azure SQL

Planned operations:

List databases

View database information

Manage supported operations

Azure Functions

Planned operations:

List functions

View function information

Manage supported operations

Azure Virtual Network

Planned operations:

View virtual networks

View subnets

Manage supported networking resources

Azure Monitor

Planned operations:

View monitoring information

View alerts

Manage supported monitoring operations

Multi-Cloud Architecture

CloudDesk uses a provider-based architecture.
Each cloud provider has its own API and implementation, while the user interacts with a unified interface.

                         CloudDesk
                            |
              +-------------+-------------+
              |                           |
              v                           v
         AWS Provider                Azure Provider
              |                           |
              v                           v
          AWS APIs                    Azure APIs
              |                           |
              v                           v
        AWS Resources                Azure Resources

This makes it easier to add more cloud providers later.

Unified Dashboard

One of the main goals is to show all connected cloud accounts in one dashboard.
The dashboard will eventually provide:

Connected cloud accounts

Cloud resources

Resource status

Infrastructure information

Networking information

Monitoring information

Cloud actions

Multi-cloud search

Instead of switching between different provider consoles, the user can manage supported infrastructure from CloudDesk.

Future Multi-Cloud Resource Search

A future version will allow users to search for resources across multiple cloud providers.
For example:

Search: production

Could return:

AWS
 ├── EC2
 ├── RDS
 └── S3

Azure
 ├── Virtual Machine
 ├── Azure SQL
 └── Storage Account

Future Cost Management

Future versions of CloudDesk may include cloud cost-management features such as:

Cost visibility

Resource cost analysis

AWS vs Azure cost comparison

Cost optimization recommendations

Resource-based cost analysis

Future Monitoring

CloudDesk may provide unified monitoring across cloud providers.
Possible information includes:

Running resources

Stopped resources

Failed resources

Alerts

Resource health

Infrastructure status

Future Automation

CloudDesk will eventually move beyond manual cloud management.
Potential automation features include:

Automated provisioning

Scheduled infrastructure actions

Infrastructure workflows

Resource templates

Automation jobs

Infrastructure lifecycle management

DevOps Integration

Later, CloudDesk will also connect with DevOps and Infrastructure as Code tools.

Potential integrations include:

Terraform

Docker

Kubernetes

GitHub Actions

CI/CD pipelines

Infrastructure as Code

Automated deployments

Terraform will be an integration, not a replacement for CloudDesk. CloudDesk is focused on giving developers and students a visual way to create, understand, and manage multi-cloud infrastructure, while still allowing experienced users to use Terraform when they prefer Infrastructure as Code.

Project Architecture

The project is built as a Django application.

multi_cloud_desk/
│
├── manage.py
│
├── multi_cloud_desk/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── cloud_desk/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── aws.py
│   ├── adapter.py
│   └── migrations/
│
├── templates/
│   ├── dashboard.html
│   ├── aws_account.html
│   └── ...
│
├── static/
│
├── .gitignore
│
└── README.md

Technology Stack

Backend

Python

Django

Boto3

Django Allauth

Frontend

HTML

CSS

JavaScript

Django Templates

Database

SQLite for local development

Cloud Providers

Amazon Web Services (AWS)

Microsoft Azure

CloudDesk Workflow

The basic CloudDesk workflow is:

1. User creates an account
          |
          v
2. User logs in
          |
          v
3. User connects a cloud account
          |
          v
4. CloudDesk authenticates the connection
          |
          v
5. CloudDesk retrieves cloud resources
          |
          v
6. User views resources
          |
          v
7. User selects an operation
          |
          v
8. Security verification
          |
          v
9. Cloud provider API executes the operation
          |
          v
10. CloudDesk displays the updated state

Development Roadmap

Phase 1 — Django Foundation

Django project

User authentication

User profiles

Google OAuth

Database models

Status:  Completed

Phase 2 — AWS Integration

AWS account connection

AWS dashboard

AWS resource retrieval

AWS resource operations

EC2 management

S3 management

RDS management

Lambda management

VPC management

IAM management

CloudWatch management

Status:  Core implementation completed

Phase 3 — AWS Improvements

Better AWS console-style interface

Advanced EC2 launch workflow

Multiple instance creation

Networking improvements

Public/private IP information

Better connection guidance

Improved infrastructure management

Status:  In Progress

Phase 4 — Azure Integration

Azure authentication

Azure account connection

Azure Virtual Machine management

Azure Storage management

Azure SQL management

Azure networking

Azure monitoring

Status:  Planned

Phase 5 — Unified Multi-Cloud Platform

AWS + Azure unified dashboard

Cross-cloud resource search

Unified monitoring

Cost management

Cloud optimization

Automation

Status:  Planned

Phase 6 — DevOps Platform

Terraform

Kubernetes

CI/CD

Infrastructure as Code

Automated deployments

Infrastructure automation

Status:  Future

Current Development Status

Completed

Django project foundation

User registration

User login

User logout

User profiles

Google OAuth

AWS account connection

AWS dashboard

AWS resource retrieval

AWS infrastructure actions

EC2 management

EC2 instance creation

Multiple EC2 instance creation

EC2 networking information

Email configuration

OTP verification

Protected AWS actions

GitHub repository setup

Currently Developing

Improved AWS console-style UI

Advanced EC2 launch experience

AWS networking management

Azure integration

Planned

Azure cloud management

Unified AWS + Azure dashboard

Cross-cloud resource search

Cloud monitoring

Cost management

Infrastructure automation

Terraform integration

Kubernetes integration

CI/CD integration

Installation

Clone the repository:

git clone https://github.com/OM0126/cloudDesk.git
cd cloudDesk

Create a virtual environment:

python -m venv venv

Activate the environment on Linux/macOS:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run database migrations:

python manage.py migrate

Create a Django superuser:

python manage.py createsuperuser

Start the development server:

python manage.py runserver

Open the application:

http://127.0.0.1:8000/

Environment Configuration

CloudDesk should use environment variables for sensitive configuration.
Example:

SECRET_KEY=your-secret-key

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

Never commit:

.env

Cloud credentials

OAuth secrets

API keys

Passwords

Private keys

Database files containing sensitive credentials

to GitHub.

Security Warning

CloudDesk interacts with real cloud infrastructure.
Incorrect operations can result in:

Resource deletion

Service interruption

Unexpected cloud charges

Security exposure

Always use appropriate permissions and carefully test infrastructure operations.

Long-Term Vision

Our long-term vision is for CloudDesk to become a single management platform for multi-cloud infrastructure.

                         CLOUDDESK
                  Multi-Cloud Control Plane
                              |
              +---------------+---------------+
              |                               |
              v                               v
         +---------+                     +---------+
         |   AWS   |                     |  Azure  |
         +---------+                     +---------+
              |                               |
              v                               v
      Cloud Infrastructure            Cloud Infrastructure

Over time, CloudDesk will grow from basic cloud management into a broader multi-cloud and DevOps platform.

Project

CloudDesk

Unified Multi-Cloud Infrastructure Management Platform
Built with:

Python

Django

AWS

Azure

Boto3

Django Allauth

HTML

CSS

JavaScript

One Platform. Multiple Clouds. One Unified Experience.
