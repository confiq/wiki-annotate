import pulumi_gcp as gcp

def enable_services():
    enabled_services = ['dns.googleapis.com','run.googleapis.com','domains.googleapis.com']

    for service in enabled_services:
        gcp.projects.Service(f"enable service {service.split('.')[0].upper()}",
            service=service)

def create_dns_zones():
    gcp.dns.ManagedZone("wiki-zone", description="Root of blame.wiki", dns_name="blame.wiki.")
