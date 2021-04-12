from functions import get_wikipedia_langs
from gcp import enable_services, create_dns_zones, create_buckets, create_dns_appengine_domain_map, create_dns_records


enable_services()
# dns
dns_zones = create_dns_zones()
dns_records = create_dns_appengine_domain_map({'wikipedia.red': get_wikipedia_langs()})
create_dns_records(
    {'wikipedia.red': {
        'top_domain_records': dns_records['wikipedia.red']['resource_records'],
        'wiki_family_langs': get_wikipedia_langs(),
        'dns_zone': dns_zones['wikipedia.red'],
    }
    })

create_buckets()