"""A Python Pulumi program"""
from gcp import enable_services, create_dns_zones
import pulumi_gcp as gcp
import pulumi


enable_services()
create_dns_zones()


# current = gcp.organizations.get_client_config()
# pulumi.export("project", current.access_token)
