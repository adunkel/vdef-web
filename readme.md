# vDef-Web

## Getting Started

Instructions to run the web application.

### Get an account
To use vDef-Web you need a TACC account. Get an account at https://portal.tacc.utexas.edu.

### Running the web application

Run the web application using docker-compose

```sh
$ docker-compose up
```
You can now access the web-application at http://localhost:8000/ and log in with you TACC credentials.

## How to add systems and applications to Agave
Here we describe briefly how to add systems and applications to Agave. For more details see the [Agave documentation](http://developer.agaveapi.co).

### Install the command line utility
```sh
$ git clone https://bitbucket.org/agaveapi/cli.git
$ export PATH=$PATH:your/path/cli/bin
```

### Authenticate with Agave
Ensure you have jq installed:
For mac users:
```sh
$ brew install jq
```
Set environment variables
```sh
$ export AGAVE_TENANTS_API_BASEURL=https://api.tacc.utexas.edu/tenants
$ export AGAVE_JSON_PARSER=jq
```
Initialize the tenant, create a client, and create an access token.
```sh
$ tenants-init -t tacc.prod
$ clients-create -S -N client_name
API username : your_tacc_username
API password: your_tacc_password
$ auth-tokens-create
API password: your_tacc_password
```
The token you receive is stored locally in `~/.agave/current` and is valid for 4 hours. If you need to refresh the token, type the following command and you receive a new access token for 4 hours.
```sh
$ auth-tokens-refresh
```

### Add a system to Agave
To add a system to Agave, we need to define the system in a JSON file. Here is an example file for schur as an [execution](example_files/schur-execution-example.json) and [storage](example_files/schur-storage-example.json) system. Let Agave know about your system:
```sh
$ systems-addupdate -F your_system_file.json
```

### Add an application to Agave
To add an application to Agave, we need to define the application in a JSON file and create a wrapper. Here is an example [application](example_files/quenching-application.json) and [wrapper](quenching-wrapper.txt). Upload your application to Agave:
```sh
$ apps-addupdate -F your_app_file.json
```
Upload the wrapper to the location on your deploymentSystem you have set in your application file (~/deploymentSystem/deploymentPath)