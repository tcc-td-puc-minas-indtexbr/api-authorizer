echo "AWS Account: $1"
echo "cloudformation deploy --template-file dynamodb.yml --stack-name api-authorizer-dynamodb --region sa-east-1 --profile tcc-td-puc-minas-admin"
aws cloudformation deploy --template-file dynamodb.yml --stack-name api-authorizer-dynamodb --region sa-east-1 --profile tcc-td-puc-minas-admin