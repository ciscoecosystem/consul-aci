Cisco AppIQ is a stateful app.

AppIQ stateful application correlates the APM construct and metrics seen by AppDynamics Core APM in terms of Application Tiers, Nodes and ServiceEndpoints with the corresponding ACI constructs of Tenant, Application Profile, EPG, Contracts, etc.
This Application provides ACI operators almost real-time visibility of the performance and the health of the application as it relates to ACI applicationa dn fabric topology.

PREREQUISITE:
ACI version 3.2 or above
AppDynamics Controller version 4.4 or above (on-prem and SaaS supported)
Application monitored by AppDynamics Controller should be running on ACI fabric managed by the APIC cluster on which AppIQ is installed


HOWTO:
Login
Once the AppIQ has been enabled, Navigate to the tenant in which the application Endpoints are present. AppIQ will show up as a tab on the far right of the menu bar.
To login Enter the following information:

Property 			Description
AppDynamics 		Controller The AppDynamics controller IP address.
Controller Port 	The running port identifier.
User 				The controller user name.
Account 			The tenant user account name.
Password 			The tenant user account password.

Once the credentials are input correctly, you will see a list of applications on the AppDynamics controller available to view for the above user.
Each application will have "Details", "Mapping" and "View"

Details:
Clicking this gives the information about the ACI endpoints in this application along with the health of the tier the endpoint is a part of and the health of the EPG that the application is a part of.

Mapping:
Clicking this gives the user the ability to select application endpoints that they would like to view in the "Details" and "View" tabs.
tag (R) next to endpoints indicates that this is the recommended endpoint to be viewed.

View:
Please refer to the screenshots for more information this.

RESTRICTIONS:
AppIQ is supported for upto 250 application endpoints on ACI fabric.
AppIQ is tested to support 1 AppDynamics controller per APIC cluster.
Application "Details", "View" and "Mapping" will be empty if there are no application endpoints for a given Application in the Tenant on which AppIQ is viewed.
ACI should be setup in Learning mode and not flooding.