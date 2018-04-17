### Implementations details
The diagram below shows the overview for the application design in
general and shows relations between its main components.
![architecture](architecture.png)

#### Factory
Based on resources config file creates instances of grabbers that
will be responsible of handling particular resources. For each
resource instantiate all the needed classes to process one.

#### Grabber
An object corresponding to the resource. Holds all the components
needed to properly grab desired data from a remote resource.

#### Scheduler
Responsible for invoking grabbers for all resources within given
intervals or manually. Behaves as a supervisor to correctly invoke
and cleanup set of grabbers.
 

### Useful resouces
* [aiopg #1](https://github.com/aio-libs/aiopg/issues/128)
