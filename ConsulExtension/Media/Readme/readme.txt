Monitor and Optimize Application Connectivity in Any Environment
The Consul Extension for ACI application enables greater control over Day 2+ operations and visibility into Layer 4/7 data of applications running in networks managed by Cisco APIC. Using the Consul Extension for ACI, network operators will be able to respond more quickly to connectivity issues and reduce the Mean-time-to-Resolution (MTTR). As the network topology becomes more dynamic and complex, Consul and ACI provide a consistent, automated workflow for gathering application information and health data.


ACI users should download the Consul Extension for ACI from the DC App Center. Once configured and a Consul Agent is added to the desired environments, ACI begins pulling information from Consul, including the number of agents running, services registered with those agents, nodes discovered by Consul, and any ACI endpoints with services that have been discovered by Consul.


Users can then use the Operations feature on the APIC Dashboard to get a list of existing services and create a visual map of the network topology. From here, operators can map each service to each ACI endpoint, drill down into specific service level data, and see if that service is actively reachable. In the future, Consul will be able to apply ACI policies directly to services.


Benefits of the Consul Extension for ACI:


End to End Service Visibility - Using the Consul Extension for ACI, network operators can retrieve Layer 4-7 service data for applications running at each ACI endpoint. This enables greater insights as to what services are currently running on the network.


Reduce Downtime & Failure Rates - Enable operators to trace connectivity issues at the service level and reduce the Mean-time-to-Resolution for network issues. Enable individuals to debug issues, rather as part of a broader, more time-intensive team effort.


Improve Productivity Across the Org - Develop stronger collaboration between application engineers and network operators by creating a single source of truth for information on applications. Enable ACI to provide a single pane of visibility for both developers and operators.


Features:
- Improved Visibility and Day 2+ automation of L4-L7 services registered with Consul.
- Self-Discovery of all services registered with Consul’s service catalog though a single agent.
- Automated correlation of L4-L7 service-to-ACI fabric and logical topology.
- Dynamic Service Dashboard to view L4-L7 service health.


Highlights:
- Enhanced L4-L7 service visibility for L2-L3 ACI infrastructure.
- Green field and brown field deployment supported.
- Saves data configured by the application.
- NO impact on ACI and Consul configurations if the application is deleted.
- Maintains organization operational model and ownership.


Pre-requisites:
- APIC version 3.2(1l) or above
- Consul version 1.6.3/1.6.3+ent or above
- In-band or Out-of-band connectivity between APIC and Consul seed agent (Consul server) on TCP port 8500 and 8501.


Before you begin:
User guide: tinyurl.com/y9ztt362
FAQs: tinyurl.com/ya8b95j2
Support: github.com/ciscoecosystem/consul-aci/issues


About HashiCorp Consul (www.consul.io/):
A service networking platform to connect and automate network configurations, discover services, and enable secure connectivity across any cloud or runtime.