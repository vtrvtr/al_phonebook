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

# Developing

To run tests: 

```bash
poetry run pytest tests
``` 

## Architecture

`AL_Phonebook` lib main class is `Model`. All testing is done in terms of `Model`. Using composition, `Model` abstracts the actual database interfaces and makes sure to establish a clean API between the database and any users.

By default, we use `TinyDB` as a backend. In order to extend the to another format, all you have to do is implement from the abstract class `AbcDatabase`. Since the tests are defined in terms of `Model`, honoring the `AbcDatabase` interface should mean your backend is working as intended. 








