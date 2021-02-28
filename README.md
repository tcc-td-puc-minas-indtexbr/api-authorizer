# api-authorizer
Micro serviço em Lambda responsável por filtrar as requisições para outras APIs no serviço API Gateway.
Sendo um Gateway Authorizer.
faz parte do nosso TCC do curso Especialização em Arquitetura de Software Distribuído da PUC Minas.


<!-- badges -->
[![Open Source Love](https://badges.frapsoft.com/os/mit/mit.svg?v=102)]()

## Prerequisites
- Python 3.6
- Chalice
- python-dotenv
- pytz

## Features
- Docker-compose 
- Chalice  

## Installation
Follow the next steps

### Running Locally
You will need the aws credentials for the profile `sigo-lambdas`:
```
cat ~/.aws/credentials
[sigo-lambdas]
aws_access_key_id=*********************
aws_secret_access_key=*********************
region=sa-east-1
```


To create the `venv` and install the modules execute:
```
./bin/venv.sh
```
If you don't want to create the venv, execute the follow commands:
```
./bin/install.sh
./bin/install-vendor.sh
```
#### Running the chalice
Execute the follow command:
```
./bin/chalice/run-local.sh
```
### Running via docker
You will need the aws credentials for the profile `sigo-lambdas`:
Create a copy of `docker/aws/credentials.example` to `docker/aws/credentials`;
Edit the file with the credentiais.
```
cat ./docker/aws/credentials
[sigo-lambdas]
aws_access_key_id=*********************
aws_secret_access_key=*********************
region=sa-east-1
```

To execute the build
```
./bin/runenv.sh --build
```

Execute the follow command:
```
./bin/runenv.sh
```

## Samples
See the project samples in this folder [here](samples).

## Running tests
To run the unit tests of the project you can execute the follow command:

First you need install the tests requirements:
 ```
 ./bin/venv-exec.sh ./bin/tests/install-tests.sh 
 ```

 
### Unit tests:
 ```
./bin/venv-exec.sh ./bin/tests/unit-tests.sh
 ``` 
### Functional tests:
Executing the tests:
 ```
./bin/venv-exec.sh ./bin/tests/functional-tests.sh
```

### All tests: 
Executing the tests:
```
 ./bin/venv-exec.sh ./bin/tests/tests.sh 
 ```

## Generating coverage reports
To execute coverage tests you can execute the follow commands:

Unit test coverage:
``` 
./bin/venv-exec.sh ./bin/tests/unit-coverage.sh
``` 
Functional test coverage:

``` 
./bin/venv-exec.sh ./bin/tests/functional-coverage.sh
``` 
> Observation:

The result can be found in the folder `target/functional` and `target/unit`.


## License
See the license [LICENSE.md](LICENSE.md).

## Contributions
* Anderson de Oliveira Contreira [andersoncontreira](https://github.com/andersoncontreira)
* Allysson Santos [allyssonm](https://github.com/allyssonm)