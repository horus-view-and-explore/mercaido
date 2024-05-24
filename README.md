# Mercaido

The word mercaido is a blend of `mercado` and `AI`. Where the
first symbolizes a marketplace, the addition of `AI` transforms it into a `smart-marketplace`. The main trade here is that of georeferenced material and the ability to perform automated (the smart part) extraction, transformations and other high-level functions on it. A common product is the creation of maps (feature data) from spherical imagery.

How is this exchange of products and services between the different vendors achieved?

## The main Horus View & Explore stalls
`Mercaido server` (`MC`) is the central message broker. This means that all registration and configuration of the market services can be done here.

`Recording server` (`RS`) provides information on captured imagery and its time and location. One such single instance/record is often refereed to as a `frame`.

`Media server` (`MS`) has the ability to transform a `frame` into imagery, often referred to as rendering. A specific frame can be rendered into a multitude of image outputs (not to be confused with formats). These outputs closely resemble the concept of using different cameras to observe the scene. For example, one can change the `field of view`, `projection` (`spherical`, `orthographic`, ...), `resolution` and many more.
The server also performs `georeferencing` on rendered pixels, allowing one to create spatial information from imagery.

## Communication
As is true for all marketplaces, one needs to know their way around and speak the same language as the vendors. Horus provides two `python` libraries for this

1. `mercaido-client` (`mc`) is used to communicate with the `Mercaido server` (https://github.com/horus-view-and-explore/mercaido/tree/main/mercaido_client).

2. `horus-media-client` (`hmc`) allows one to communicate with both the `Media server` and the `Recording server`(https://github.com/horus-view-and-explore/horus-media-client).

```mermaid
graph TD;
    Customer-->mc;
    mc<-->MC;

    Customer-->hmc;
    hmc<-->MS;
    hmc<-->RS
```

## In a nutshell
A vendor has an AI service for extracting traffic signs from spherical imagery and would like be part of `Mercaido`.

Assuming a working mercaido environment, the vendor writes a python service that registers with `MC` using the `mc` library.
Typically this includes: name, required fields, and output format. Now this service is visible and available in the Mercaido marketplace.

A customer would like to purchase some traffic sign information for a specific region.

This customer fills in the required fields in the web interface and then the vendor's service does the following:

1. Query the `Recording server`, requesting all frames/recordings matching the customers criteria.
```mermaid
flowchart LR;
   Service-->|query frames|RS

```
2. Configure the camera/rendering settings and acquire imagery.
```mermaid
flowchart LR;
   Service-->|render imagery|MS

```
3. Use the vendor's proprietary algorithm for detecting traffic signs.
4. Request spatial coordinates for the detected objects/pixels.

```mermaid
flowchart LR;
   Service-->|detection|algorithm
   algorithm-->|geoposition|MS
```
5. After which the service can store the results on disk or WFS-T.
```mermaid
flowchart LR;
   Service-->|results|store
```
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
