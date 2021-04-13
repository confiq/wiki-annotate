import pulumi_gcp as gcp


def enable_services():
    enabled_services = ('dns', 'run', 'domains', 'cloudbuild', 'appengineflex')
    for service in enabled_services:
        gcp.projects.Service(f"enable service {service.upper()}",
                             service=f"{service}.googleapis.com")


def create_dns_zones():
    blame_wiki = gcp.dns.ManagedZone("wiki-zone", description="Zone of blame.wiki", dns_name="blame.wiki.")
    wikipedia_red = gcp.dns.ManagedZone("wikipedia-red", description="Zone of wikipedia.red", dns_name="wikipedia.red.")
    return {
        'blame.wiki': blame_wiki,
        'wikipedia.red': wikipedia_red,
    }


def create_buckets():
    react_bucket = gcp.storage.Bucket("react static",
                       name='wiki-react-app',
                       cors=[gcp.storage.BucketCorArgs(
                           max_age_seconds=3600,
                           methods=[
                               "GET",
                               "HEAD",
                           ],
                           # origins=["http://image-store.com"],
                           # response_headers=["*"],
                       )],
                       force_destroy=True,
                       location="EU",
                       uniform_bucket_level_access=True,
                       website=gcp.storage.BucketWebsiteArgs(
                           main_page_suffix="index.html",
                           not_found_page="404.html",
                       ))
    gcp.storage.BucketIAMBinding("publicRule",
                                 bucket=react_bucket.name,
                                 role="roles/storage.objectViewer",
                                 members=["allUsers"]
                                 )


def create_dns_appengine_domain_map(wikipedias: dict) -> dict:
    dns = {}
    for wiki, langs in wikipedias.items():
        domain_mapping = gcp.appengine.DomainMapping(f"top domain {wiki}",
                                                 domain_name=wiki,
                                                 ssl_settings=gcp.appengine.DomainMappingSslSettingsArgs(
                                                     ssl_management_type="AUTOMATIC",
                                                 ))
        dns[wiki] = {'resource_records': domain_mapping.resource_records}
        for lang in langs:
            gcp.appengine.DomainMapping(f"subdomain for {lang}.{wiki}",
                                        domain_name=f"{lang}.{wiki}",
                                        ssl_settings=gcp.appengine.DomainMappingSslSettingsArgs(
                                            ssl_management_type="AUTOMATIC",
                                        ))
    return dns


def create_dns_records(wikipedias):
    for wiki, data in wikipedias.items():
        type_dns = {'A': ['216.239.32.21', '216.239.34.21', '216.239.36.21', '216.239.38.21'],  # manual for now
                    'AAAA': ['2001:4860:4802:32::15', '2001:4860:4802:34::15', '2001:4860:4802:36::15', '2001:4860:4802:38::15']
                    }

        #  This can't work, for some reason I can't iterate with DomainMapping we'll do it manually
        # type_dns = {'A': [], 'AAAA': []}
        # for top_domain_record in data['top_domain_records']:
        #     type_dns[top_domain_record['type']].append(top_domain_record['rrdata'])

        # for dns_type, values in type_dns.items():
        #     gcp.dns.RecordSet(f"top domain record {dns_type}", name=f'{wiki}.', managed_zone=data['dns_zone'].name, rrdatas=values, ttl=300, type=type)
        for lang in data['wiki_family_langs']:
            gcp.dns.RecordSet(f"subdomain record for {lang}", name=f'{lang}.{wiki}.', managed_zone=data['dns_zone'].name,
                              rrdatas=['ghs.googlehosted.com.'], ttl=300, type='CNAME')


def create_cloudrun():
    # TODO: good example: https://github.com/pulumi/examples/blob/master/gcp-ts-cloudrun/index.ts
    pass
