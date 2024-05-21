# Mercaido

## AMQP server

Before continuing to the installation or development sections, make sure
an AMQP server is available.

Mercaido is tested with [RabbitMQ][] and [LavinMQ][].

A quick way to start a RabbitMQ server is with the `./do` script in this
repository. It'll use Podman or Docker to start a [rabbitmq:3-management][]
container. This container is *not* meant for production deployments,
only for evaluation and development of Mercaido.

Details:

- AMQP URL: `amqp://guest:guest@127.0.0.1:5672/%2F`
- Management web interface: `http://127.0.0.1:15672`
- Username / Password: `guest` / `guest`

Commands:

```
./do rabbitmq start
./do rabbitmq stop
```

[RabbitMQ]: https://www.rabbitmq.com
[LavinMQ]: https://lavinmq.com
[rabbitmq:3-management]: https://hub.docker.com/_/rabbitmq


## Installation

For this manual all instructions assume the Mercaido code is located
at `/home/example-user/src/mercaido` or `~/src/mercaido`.

Clone this repository:

```
git clone https://github.com/horus-view-and-explore/mercaido ~/src/mercaido
```

Install Mercaido Server:

```
pip install ~/src/mercaido/mercaido_server
```

Create or copy a configuration file from
`~/src/mercaido/mercaido_server/example_configurations`. For example:
`gunicorn-example.ini`.

NOTE: Depending on your configuration a specific WSGI server needs to be
installed. For the configuration in this example Gunicorn is needed:

```
pip install gunicorn[gevent]
```

Run the migration steps

```
python -m mercaido_server --config gunicorn-example.ini migrate
python -m mercaido_server --config gunicorn-example.ini message-queue-migrate
```

Mercaido Server consists of two services. A web application and a job
dispatcher. Both these command need to run in separate sessions:

Start the web application:

```
pserve gunicorn-example.ini
```

Or directly with Gunicorn:

```
gunicorn --paste gunicorn-example.ini --bind :8080 --workers 4 --worker-class gevent
```

Note: the `[server:main]` section in the configuration file is not
picked up when using Gunicorn directly. It's important that Gunicorn's
worker class is set to `gevent`. See [Gunicorn's documentation][gpd] on
Paste (pserve) deploments.

[gpd]: https://docs.gunicorn.org/en/stable/run.html#paste-deployment

Start the job dispatcher:

```
python -m mercaido_server --config gunicorn-example.ini dispatcher
```

To clarify, the dispatcher does not use Gunicorn, but poth programs
share the same configuration file.


## Example Services

There are two example services available in the `./examples` directory.

`mercaido_dummy_service` is a service that does nothing. It sleeps for
a bit while sending progress updates. And `mercaido_panorama` TODO.

These two can be installed with:

```
pip install ~/src/mercaido/examples/mercaido_dummy_service
pip install ~/src/mercaido/examples/mercaido_panorama
```

And started with:

```
mercaido_dummy_service --amqp 'amqp://guest:guest@127.0.0.1:5672/%2F'
mercaido_panorama_service --amqp 'amqp://guest:guest@127.0.0.1:5672/%2F'
```

The AMQP URL depends on your deployment of RabbitMQ.


## Development

There are a couple of packages within this repository. These are all
managed with [Poetry][].

- `examples/mercaido_dummy_service`
- `examples/mercaido_panorama`
- `mercaido_client` (used by services and server)
- `mercaido_server`

[Poetry]: https://python-poetry.org/

Go into the directories of the above packages and run the following
commands.

Create a virtual environment and install the current package and its
dependencies:

```
poetry install
```

Update dependencies:

```
poetry update
```

Run tests:

```
poetry run pytest ./tests
```

To run the server use the `example_config/development-example.ini`:

```
cd mercaido_server
poetry install
# and then finally...
poetry run pserve example_config/development-example.ini
```
