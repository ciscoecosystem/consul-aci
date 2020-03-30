# AppDynamics mock-server

This is mock server which contains all the rest endpoint of AppDynamics. For the implementation we are using Prism (an Open Source HTTP Mock Server), with OpenAPI 3.0 documentation for API specification.

## How to use this ?
**Prerequisite:**
- npm
- [prism](https://stoplight.io/open-source/prism/)

**How to run this server?**
- run the following command to start prism mock server.
  - "prism mock -h 0.0.0.0 -p 4010 AppD.postman_collection.json-OpenApi3Json.json"

- Changes to be done in AppIQ code.
  - open Service/appd_utils.py and make following changes.
  - replace code in check_connection() functions
```python
        # Actual Code
        self.token = login.cookies['X-CSRF-TOKEN']
        if login.cookies.get('JSESSIONID'):
            self.JSessionId = login.cookies['JSESSIONID']
        # New Code
        self.token = "any value"
        self.JSessionId = "any value"
```

- Install the new bundle after changes, in APIC. In login screen, give details as following:
  - "Appdynamics Controller" - IP of the mock server
  - "Controller Port" - 4010
