import pulumi_gcp as gcp


def enable_services():
    enabled_services = ('dns', 'run', 'domains', 'cloudbuild')

    for service in enabled_services:
        gcp.projects.Service(f"enable service {service.upper()}",
                             service=f"{service}.googleapis.com")


def create_dns_zones():
    gcp.dns.ManagedZone("wiki-zone", description="Zone of blame.wiki", dns_name="blame.wiki.")
    gcp.dns.ManagedZone("wikipedia-red", description="Zone of wikipedia.red", dns_name="wikipedia.red.")


def create_buckets():
    gcp.storage.Bucket("react static",
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

def create_appengine():
    gcp.appengine.StandardAppVersion('static nginx',
                                     version_id='v1',
                                     service='static_nginx',
                                     runtime='Docker',

                                     )

def create_cloudrun():
    # TODO: good example: https://github.com/pulumi/examples/blob/master/gcp-ts-cloudrun/index.ts
    pass