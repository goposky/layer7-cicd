# About
This is the repository that can be used to run the CA API Gateway locally.

A default example solution is present in a bundle at `build/gateway/gateway-developer-example.bundle`
A VodafoneZiggo solution is present in a bundle inside `gateway-config` together necessary encryption/password files.

## Running the Solution
In order to run the solution you need to do the following:

1) Put a valid gateway license in this folder. The license file should be called `license.xml`
3) Start the Gateway Container by running: `docker-compose up -d`

After the container is up and running you can connect the CA API Gateway Policy Manager to it and/or call the example API at `/example`

# About the Example Solution
The default example solution that is checked into this repository is contains a single folder and service. The service exposes `/example` and will respond with the following JSON for any HTTP(S) request:
```json
{
   "you-say": ["Hello", "Gateway"],
   "gateway-says": ["Hello", "User"]
}
```

