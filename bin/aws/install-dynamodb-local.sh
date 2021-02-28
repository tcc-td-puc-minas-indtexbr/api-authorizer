mkdir ./target
mkdir ./target/dynamodb-local
curl -k -L -o ./target/dynamodb-local.tgz http://dynamodb-local.s3-website-us-west-2.amazonaws.com/dynamodb_local_latest.tar.gz
tar -xzf ./target/dynamodb-local.tgz --directory ./target/dynamodb-local