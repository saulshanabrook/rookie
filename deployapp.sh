aws s3 cp index.html s3://rookielens --acl public-read
aws s3 cp keys.csv.gz s3://rookielens/data/ --acl public-read --content-type text/plain --content-encoding gzip