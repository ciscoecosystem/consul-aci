The Consul Extension for ACI application provides ACI administrators L4-L7 Service Mesh visibility and an automated way to manage L2-L3 infrastructure based on L4-L7 service requirements.

This application offers enhanced Consul-to-ACI L4-L7 service visibility including dynamic service health, enabling faster mean-time-to-resolution (MTTR); and L4-L7 service mesh intention driven dynamic Network Middleware Automation.

Service visibility and faster Mean-time-to-Resolution (MTTR):
- Real-time visibility into dynamic L4-L7 services, service health and service-to-service communication on virtual, container and bare-metal workloads connected by the ACI multi-cloud network.
- Faster identification of issues based on service health and network data correlation.

Network Middleware Automation:
- Consistent L4-L7 service mesh driven network policy (contracts and filters) automation for virtual, bare-metal and container workloads across private and public cloud for your ACI multi-cloud network.
- Easier transition to a secure service mesh based deployments for Applications teams and DevOps operators with the ACI multi-cloud network.

Features:
- Supports Consul Enterprise and Consul open-source deployments.
- Visibility into L4-L7 services running on multiple Consul Datacenters.
- Self-Discovery of an entire Consul Datacenter service catalog though a single seed agent(Consul Server).
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

GA-1.0 release limitations:
- Supported on Chrome, Mozilla and Safari web-browsers only.
- Supported for on-premise APIC only.


Before you begin:
User guide: https://tinyurl.com/y9ztt362
FAQs: https://tinyurl.com/ya8b95j2
Support: https://github.com/ciscoecosystem/consul-aci/issues

About Consul (https://www.consul.io/):
- Consul is a highly distributed service mesh solution by HashiCorp for providing a full featured control plane with service discovery, configuration, and segmentation functionality at L4-L7.