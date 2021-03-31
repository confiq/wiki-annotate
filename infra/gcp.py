import pulumi_gcp as gcp

def enable_services():
    gcp.projects.Service("enableDNS",
        disable_dependent_services=True,
        service="dns.googleapis.com")
        
    gcp.projects.Service('Enable Cloud Run',
        service='run.googleapis.com'
    )

def create_dns_zones():
    gcp.dns.ManagedZone("wiki-zone", description="Root of blame.wiki", dns_name="blame.wiki.")
