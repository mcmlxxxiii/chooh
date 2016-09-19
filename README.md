**chooh** is an utility to assist with development and deployment
of so called couchapps, web applications engineered to be served from CouchDB
design documents.

It provides some features, such as ddoc prepare scripts, custom asset
bundling and support for multiple databases, that the creator was missing
in those already existing great tools.

**A word of warning though.** Some of those features can be leveraged only
with writing Python scripts. Thus, if you're uncomfortable with Python,
**chooh** may not be a good choice for your project.


## Installation

Just run `pip install chooh`. Though **chooh** may be installed globally,
the general recommendation is to have a separate _virtualenv_ for each of your
projects so that no other pips installed for the purpose of enhancing things
locally would ever popute the system-wide python installation.


## Usage

**(1)** There has to be a `chooh.yaml` file in the root directory of your
project. That is how `chooh` command would determine the root directory so that
it can be run from any directory under it.

So far, `chooh.yaml` is also used for configuring databases.

```yaml
databases:
    development:
        server: http://user:password@127.0.0.1:5984
        db_name: dummy

    production:
        server: http://user:password@production.com:5984
        db_name: genius
```

**(2)** Right in your project root, there should be a `ddocs/` folder.
That is where you would put the design documents.

**(3)** If you have a ddoc named _"bingo"_ in _./ddocs/bingo/_ directory you
may want to create _./ddocs/prepare\_bingo.py_ script to rule the ddoc
processing.

**(4)** Once application is ready to be deployed, run `chooh push ddoc DDOC_NAME TARGET_DB_NAME`.
You may also want to add `--auto` flag to make **chooh** watch your changes
and automatically push them right where you'd like to observe them.


A better documentation is to be written eventually. In meanwhile, please
refer to [the example application](https://github.com/mcmlxxxiii/chooh-demo)
and its README telling how to get started with **chooh**.


## TODOs

- Command for boilerplating the project.
- Pushing data documents.
- Pushing scenarios, like when several ddocs/data/databases involved.
