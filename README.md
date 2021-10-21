How to start the computing server with docker
---------------------------------------------
The computing server is composed of a RabbitMQ broker and one or more worker (by default only one worker is started).

To start the server:
1. Be sure that your computer has docker and docker-compose.
2. Obtain a copy of this repository and save it in your computer (we will refer to your local folder as `${Fusion-Driver-Host}`)
3. Open a terminal and go to the folder `${Fusion-Driver-Host}/docker/`.
4. Run the following command:
```
docker-compose up
```

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
