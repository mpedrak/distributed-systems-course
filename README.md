# Small projects for Distributed Systems Course

Small projects developed as part of the Distributed Systems course at AGH University of Krakow. Each folder contains a standalone application showcasing different middleware and distributed system concepts.

## Project descriptions

- [ice-smart-home](./ice-smart-home/) - distributed smart home simulation using the ZeroC Ice RPC framework, featuring a Java-based server that hosts multiple simulated devices like furnaces, sensors, and bulbulators. It includes an interactive Python command-line client that allows users to remotely control and monitor these devices using both synchronous and asynchronous remote procedure calls.

- [rabbitmq-messaging-system](./rabbitmq-messaging-system/) - RabbitMQ-based messaging system, written in C#, simulating a medical clinic, where Medics give examination requests to specialized Technicians (producer-consumer scenario). It also features an Admin client that monitors and logs all system traffic in real-time, and can broadcast targeted informational messages to specific groups of medical personnel using topic exchanges.

- [zookeeper-process-monitor](./zookeeper-process-monitor/) - Python-based ZooKeeper client that monitors a specific root znode to automatically launch an external program when the znode is created and terminate it when the znode is deleted. Additionally, it recursively watches for changes in the znode's children to print real-time count updates and provides a simple command-line interface to visualize the entire znode tree structure.

- [fastapi-tire-change-advisor](./fastapi-tire-change-advisor/) - FastAPI-based web application that determines whether it is time to switch between seasonal car tires based on daily average temperature trends. It integrates external geocoding and weather APIs (Geocode Maps and Open-Meteo) to fetch location coordinates and historical hourly temperatures, generates temperature graphs, and serves interactive HTML views with personalized recommendations.
