How to start the computing server with docker
---------------------------------------------
The computing server is composed of a RabbitMQ broker and one or more workers (by default only one worker is started).

To start the server:
1. Be sure that your computer has docker and docker-compose.
2. Obtain a copy of this repository and save it in your computer (we will refer to your local folder as `${Fusion-Driver-Host}`)
3. Open a terminal and go to the folder `${Fusion-Driver-Host}/docker/`.
4. Run the following command:
```
docker-compose up
```

Setting the RabbitMQ server
---------------------------
The communication between the IODA Fusion server and the IODA computing nodes relies on a RabbitMQ broker. Since that connection is usually protected and needs users' credentials, it must be configured by the user. The default configuration only works for local testing.

Edit the environment variable ```BROKER_URL``` in the ```docker-compose.yml```:
```
BROKER_URL=amqp://user:password@host/vhost
```
- ```amqp``` is the protocol used by default. 
- ```user:password``` are the users' credentials.
- ```host``` is the ip or domain name of the machine that is running the broker. 
- ```vhost``` (optional, depending on the configuration) is the virtual host provided by the RabbitMQ broker.  

If you are using an external broker that is not under your control, then ask the administrator. 

How to create a custom task
---------------------------
IODA computing node can run a custom task which is some code that can be interpreted (MATLAB, Python) or more generally any binary that complies with a few format requirements (see below).

To configure a new task, (e.g. a binary file):
1. Put your files inside the `${Fusion-Driver-Host}/code/` folder. 
2. Create the files `inputFormat.txt` and `outputFormat.txt` that defines the input and output format (open `${Fusion-Driver-Host}/code/basicOps/` for an example).

The input data will be forwarded to your application as input arguments, and the output will be captured either directly from the standard output (stdout) or as a file.


Testing workers can run tasks
------------------------------
With the default configuration, a worker should be able to run Python tasks (that are stored in the folder `${Fusion-Driver-Host}/code/`).

To test the worker (of course, the server must be previously started), run the following command:
```
docker-compose exec worker python tests/test_task_python.py
```
The output should be something like this:
``` 
{
    "data": {
        "error": null,
        "output": 5.0
    },
    "format": "json",
    "info": {
        "duration": 0.002869129180908203,
        "generatedFiles": {
            "names": [
                "/code/var/results/ciemat17/out.txt",
                "/code/var/results/ciemat17/Script stdout.txt"
            ],
            "sizes": [
                30,
                0
            ]
        },
        "startTime": 1634807225.1875727,
        "stdout": "",
        "stopTime": 1634807225.1904418
    },
    "name": ""
}
```
