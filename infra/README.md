# deploy

## Prerequisites

To setup GCP credentials for this: 
`gcloud config configurations activate wiki-annotate` on my machine™️
### frontend

Go to folder `static_appengine` and deploy with `gcp app deploy`


### backend

go to root directly and type 
```
gcloud builds submit --tag gcr.io/wiki-annotate/api && gcloud run deploy --image gcr.io/wiki-annotate/api --platform managed --region europe-west1
```

## TODO

Normal CD/CI is required
