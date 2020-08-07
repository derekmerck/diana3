![logo](resources/images/diana_logo_sm.png)DICOM Image Analysis and Archive
==================

Derek Merck  
<derek.merck@ufl.edu>  
University of Florida and Shands Hospital  
Gainesville, FL  

Source: <https://www.github.com/derekmerck/diana3>  
Image:  <https://cloud.docker.com/repository/docker/derekmerck/diana3>


Overview
----------------

Hospital picture archive and communications systems (PACS) are not well suited for "big data" analysis.  It is difficult to identify and extract datasets in bulk, and moreover, high resolution data is often not even stored in the clinical systems.

**DIANA** is a [DICOM][] imaging informatics platform that can be attached to the clinical systems with a very small footprint, and then tuned to support a range of tasks from high-resolution image archival to cohort discovery to radiation dose monitoring.  It provides DICOM services, image data indexing, REST endpoints for scripting, and user access control through an amalgamation of free and free and open source (FOSS) systems.

[DICOM]: http://www.dicomstandard.org/


Python-Diana
----------------

The Python-Diana package for Python >= 3.6 provides an api for a network of DICOM-file related services including PACS query, local archive, anonymization, file access, and study indexing.


### Installation

```bash
$ pip3 install git+https://github.com/derekmerck/diana3
```

Or install as locally editable:

```bash
$ git clone --recurse-submodules git+https://github.com/derekmerck/diana3
$ pip install -e diana3
```

`diana-cli`
-----------------

`diana-cli` provides command-line bindings for "service-level" tasks.  Specifically, given a service description file (endpoint kwargs as yaml), an endpoint can be created and methods (get, put, etc) called on it via command-line. 

```bash
$ diana-cli --version
3.2.x
```

Docker-Image
----------------

The docker directory includes a Dockerfile for a self-contained DIANA container based on Docker's current Python image.   Current builds of this images from ci are available on docker hub.

```bash
$ docker run -it derekmerck/diana3 diana-cli --version
3.2.x
```

License
-------

MIT
