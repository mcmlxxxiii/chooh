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

`chooh.yaml` is used for project configuration.

```yaml
servers:
    development: http://user:password@127.0.0.1:5984
    production: https://superuser:superpassword@production.com

deployments:
    development:
        pushes:
            - ddoc: site
              target_database: development/site
            - ddoc: data
              target_database: development/data
        config:
            debug: YES
    production:
        pushes:
            - ddoc: site
              target_database: production/site
            - ddoc: data
              target_database: production/data
        config:
            debug: NO
```

**(2)** Right in your project root, there needs to be a `ddocs/` folder.
That is where you would put the design documents.

**(3)** If you have a ddoc named **"bingo"** in `./ddocs/bingo/` directory you
may want to create `./ddocs/prepare_bingo.py` script to rule the ddoc
processing. On its execution, such a script would receive several global
variables:

- `deployment` with the name of the current deployment;
- `ddoc_assembly_dir` with the absolute path to the directory where ddoc is
  being assembled (yes, it is different from where it is being edited);
- `ddoc_support_dir` with the absolute path to the directory that does not get
  cleaned on every deployment as the ddoc assembly one does;
- `config` with the deployment config object taken from the `chooh.yaml` of your
  project;
- `changes` object describing the actual changes made to the ddoc (always `None`
  if the deployment is not continious as with `--auto` flag);
- `is_deployment_continuous` boolean telling if the deployment is run with the
  `--auto` flag;
- `context` object referencing all the above variables.

**(4)** Once application is ready to be deployed, run `chooh deploy development`.
You may also want to add `--auto` flag to make **chooh** watch your changes
and automatically push them according to your deployment setup.


A better documentation is to be written eventually. In meanwhile, please
refer to [the example application](https://github.com/mcmlxxxiii/chooh-demo)
and its README telling how to get started with **chooh**.


## TODOs

- [ ] Command for boilerplating projects.
- [ ] Pushing data documents.
- [x] ~~Pushing scenarios, like when several ddocs/data/databases involved.~~
