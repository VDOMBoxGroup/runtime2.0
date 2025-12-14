# VDOM Runtime

## Installation

The first is needed to check that system meets all requirements:

* ply (pip install ply)
* pillow (pip install pillow)
* pycrypto (pip install pycrypto)
* sqlite (pip install pysqlite; copy dll for windows)
* sqlitebck (copy dll for windows)
* soappy (pip install soappy)
* pyScss[(docs)](https://pyscss.readthedocs.io/en/latest/index.html) (pip install pyScss) 
* WsgiDAV (pip install WsgiDAV==2.4.0)
* lxml (pip install lxml)
Optional, for some apps only:
* xapian (copy module for windows)
* xappy (copy module for windows)
* python-ldap (pip install python-ldap)

Then download latest runtime. Before first run is needed to build C extensions:

    python manage.py build

After that must be performed deploy action:

    python manage.py deploy

This action creates required directories and install all types from repository directory.

## Quick start

There are two executable files in the sources directory:

* server.py - main runtime server executable
* manage.py - auxiliary management utility

To install and select application you can use manage.py utility:

    python manage.py install <application XML file location>
    python manage.py select <application uuid or name>

For more detailed information see below.

## Starting runtime server

To start server just type:

    python server.py

Configuration can be found in the settings.py file, also server supports several command line arguments:

* -l, --listen - specify address to listen
* -p, --port - specify port
* -a, --applicaiton - specify application to serve
* -c, --configure - specify filename to load settings
* --preload - preload default application
* --profile - enable profiling

### Override settings

Command line:

    python server.py -c settings.ini

File contents:

    SERVER-ADDRESS = "gerg"
    SERVER-PORT = 4234

## Using manage utility

This utility can be used to perform several maintenance tasks, for example:

* install or uninstall application
* select default application
* list available applications and types
* query internal state from server
* show last stored profile

To perform action utility can be called from the command line as follow:

    python manage.py <action> <arguments>...

Or can work in interactive mode - just lunch manage.py without arguments.

Each action can have several arguments and/or keywords with shortcuts.
Shortcuts are generated automatically from first letters so please use full abbreviations when writing scripts.

### Build C extensions

This action can only be called from the command line.

Build server C extensions, show list of available extensions or clear temporary files.

Actions:

    build
    build <extension> ...
    build --list
    build --clean

Where *extension* is a specific extension to build.

Example:

    build

This command build all available extensions.

### Install application or type

Install application or type from desired location, install all types from repository or install appropriate type from repository.

Actions:

    install <location>
    install types
    install <type name>

Where *location* is the location of the application XML file.

Example:

    install x:\data\promail.xml

### Uninstall application or type

Uninstall application, type or all installed types.

Actions:

    uninstall <identifier>
    uninstall types

Where *identifier* is an application or type name or uuid.

Example:

    uninstall promail

### Delete application

Emergency delete application and cleanup infrastructure without proper uninstall procedure.

Actions:

    delete <identifier>

Where *identifier* is an application uuid.

Example:

    delete 7f459762-e1ba-42d3-a0e1-e74beda2eb85

### Select default application

Select default application or display current one.

Action:

    select
    select <identifier>

Where *identifier* is an application name or uuid.

Example:

    select promail

### Associate virtual host name with application

Associate virtual host name with application, display one or delete

Action:

    select --name <name>
    select <identifier> --name <name>
    select --name <name> --delete

Example:

    select promail --name mail
    select --name mail --delete

Where *identifier* is an application name or uuid and *name* is a virtual host name.

### List available applications and types

Action:

    list

### View log

Display actual server log and update it in the realtime.

Action:

    log

### Show application or type details

Show some information about available application or type like id, name, attributes and so on.

Action:

    show <identifier>

Where *identifier* is an application name or uuid.

Example:

    show form

## Debugging and profiling

Manage utility also have several actions to help with debugging and profiling.

### Show objects statistics

This action require enabled watcher.

Show objects statistics for all server objects or accumulated from the last snapshot.

Action:

    watch analyze

Example:

    watch analyze --all --limit 75 --sort counter

This command show 75 most common object types including built-in and sorted by count.

### Memorize objects state

This action require enabled watcher.

This action force watcher to memorize current object state and show further statistics on changes form this snapshot.

Action:

    watch memorize

### Query object graph

This action require enabled watcher.

Action:

    watch query graph <fully qualified type name>
    watch query graph <fully qualified type name> <location>

Where *fully qualified type name* is a full type name with module and *location* is the file name or directory for the resulting graph file.

Example:

    watch query graph memory.application.object.MemoryObject c:\temp --depth 5

There we request object graph for all (memory.application.object.)MemoryObject objects with depth of 5.

### Show profiling statistics

This command require enabled profiler.

Action:

    profile show
    profile show tasks

### Drop profiling statistics

This command require enabled profiler.

Action:

    profile drop
    profile drop tasks

### Query profiling statistics

This command require enabled profiler.

Action:

    watch query profile c:\temp
    watch query profile c:\temp tasks

### Query profiling callgraph

This command require enabled profiler.

Action:

    watch query callgraph c:\temp
    watch query callgraph c:\temp tasks

### Check profiling status

This command require enabled profiler.

Action:

    watch profiling

### Enable or disable profiling

This command require enabled profiler.

Action:

    watch profiling --enable
    watch profiling --disable

### Show or change log level

This command require enabled profiler.

Action:

    watch logging
    watch logging --level <log level>

Where *log level* is a one of *debug*, *message*, *warning* or *error*.

Example:

    watch logging --level warning

### Show or change show page debug

This command require enabled profiler.

Action:

    watch debugging
    watch debugging --showpagedebug enable
    watch debugging --showpagedebug disable

### Unload server resources

This command unloads resources copy to the destined folder from server. 

There are two switch keys, one responsible for outputting files with their real name 
(i.e. instead of `4968d3de-dc60-c927-365d-5b6c252d631c` there will be something like `logo.png`)
and the other will load all types resources from server.

Action:

    offload <appid> <location>
    offload <appid> <location> --by_name
    offload <appid> <location> --types
    offload <appid> <location> --by_name --types

Example:

    offload "4f498469-2e2b-45a8-b0ce-5619137c18e8" "path/to/output/folder"
    offload "4f498469-2e2b-45a8-b0ce-5619137c18e8" "path/to/output/folder" --by_name
    offload "4f498469-2e2b-45a8-b0ce-5619137c18e8" "path/to/output/folder" --types
    offload "4f498469-2e2b-45a8-b0ce-5619137c18e8" "path/to/output/folder" --by_name --types
    