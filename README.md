# AL Phonebook

`AL Phonebook` is a simple CLI application that can be used to record information about contacts.

`AL_Phonebook` uses `pydantic` for data validation! No more writing the wrong data!

## Installing

After cloning the repository, run:

```
poetry install
```

If `poetry` isn't available, run: 

```
pip install requirements.txt
```

### NOTE

On Linux it seems Poetry is having problem with Python 3.10.1. For me what worked was to install:


```
pip install cleo tomlkit poetry.core requests cachecontrol cachy html5lib pkginfo virtualenv lockfile  
```

from [this issue](https://github.com/python-poetry/poetry/issues/3071#issuecomment-1013591803).

## Using

`AL_Phonebook` is separated into two parts! `lib` if you want to use the backend alone and `cli` to use it as a CLI application. 

After installing the app, a new command `al_phonebook` should be available. Executing the command without any arguments will print the help prompt. Hopefully the help there is enough!

## Configuring

`AL Phonebook` saves its database and its configuration file in `$HOME/.al_phonebook`. To configure the app, change the `settings.yaml` file inside that folder. `

The settings available are the following:

```yaml
model:
  custom_model:
    path: "tests/resources/custom_model.py"
  custom_fields:
    age:
      type: integer 
    secondary_email:
      type: email 
      required: true 
      default: "foo@bar.com"

database:
  path: "tests/resources/.test_db.json"
```

| Setting           | What is does                                                                                                                                                                                        |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| custom_model      | Options related to the custom model. You can write a custom `Pydantic` model that will be used for contacts.                                                                                        |
| custom_model/path | A path to a single `.py` file containing a `Item` `pydantic` model. This model will be used for validating the contacts information. You can use most `pydantic` features **except nested models.** |
| custom_fields     | Besides defining a complete custom schema, you can also easily augment the default one using option.                                                                                                |
| database          | Options related to the database.                                                                                                                                                                    |
| database/path     | Path to where the database will be saved. You can use this to move the contact data.                                                                                                                |

### Custom Fields customization

In order to add a new field to your contacts simple add a new entry below `custom_fields`. 

For example, by default the `settings.yaml` looks like:

```yaml
database: {}
model: 
  custom_fields: {}
```

If you wanted to add a new field `rating` to be sure to remember who your favorite people are it would look like: 

```yaml
database: {}
model: 
  custom_fields: 
    rating:
        type: integer
        required: False
```

After this you can run: 

```bash
al_phonebook add
```

And the interactive prompt will ask for `rating`! 

## Formatting customization

`AL_Phonebook` comes with a plugin system to output your contact's information in any way you want. 

To add a new plugin: 

1. In `settings.yaml` add the following: 
```yaml
      display:
        paths: 
        - PATH_TO_FOLDER_WITH_PLUGIN
        formatters:
        - ClassName1
        - ClassName2
``` 
  The plug-in system will search `PATH_TO_FOLDER_WITH_PLUGIN` for valid formatters. A valid formatter a used defined class with a `format` method.

2. Execute 
```bash
  al_phonebook list-formatters
```

   to check if your formatter was sucessfully registered. If yes, it should print:

   ```bash
  📖 Starting AL Phonebook! 📖
  ClassName1, ClassName2
  ```
3. After that you can use a formatter with `search` and `list` commands:
```bash
al_phonebook list -f ClassName1
```

### Protip

The folder `$HOME/.al_phonebook/plugins` is automatically part of the plugins path. This means that if you go there and create, for example `json_formatter.py`:

```py
import json

class JsonFormatter:

    def format(d):
        return json.dumps(d, indent=4)
```

You'll automatically have a formatter that prints the contact's info in a json format. 

# Developing

To run tests: 

```bash
poetry run pytest tests
``` 

## Architecture

`AL_Phonebook` lib main class is `Model`. All testing is done in terms of `Model`. Using composition, `Model` abstracts the actual database interfaces and makes sure to establish a clean API between the database and any users.

By default, we use `TinyDB` as a backend. In order to extend the to another format, all you have to do is implement from the abstract class `AbcDatabase`. Since the tests are defined in terms of `Model`, honoring the `AbcDatabase` interface should mean your backend is working as intended. 








