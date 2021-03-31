import pulumi_gcp as gcp

def enable_services():
    gcp.projects.Service("enable DNS",
        service="dns.googleapis.com")
