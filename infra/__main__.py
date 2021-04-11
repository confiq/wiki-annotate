from gcp import enable_services, create_dns_zones, create_buckets


enable_services()
create_dns_zones()
create_buckets()

# two things needs to be done!
# 1.1) create appengine for react static files

# 2.1) cloud run for API
# 2.2) continer registry

