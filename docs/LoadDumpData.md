### Load & Dump Data into/From JSON Algorithms
- `flask dumpdata` dumps DB data into JSON
- `flask loaddata` loads data from JSON
- `flask dumpcache` dumps cached changes into the proper JSON file(s)

###### Dump

 >  `flask dumpdata`

- Only Root models are dumped, A DIR with the model class name is created

    > We've 7 Root models/DIRs
            - Company
            - Contact
            - Deal
            - Sprint
            - Project
            - Organization
            - User
- In each Dir, all records in a Root model are dumped into files, where each file represents one record.
Each file name starts with the `id` of the object

- Dumped data **must be Sorted** so if these data is saved into a [Git](https://git-scm.com/) repo, only there's a change
in Data if it's actually changed.

- Each file in Dumped data may contain a duplicate data that may exist elsewhere
This is because we only dump Root models, and each dumped record should contain
all its data.Duplication is handled throug the process of loading data using command
`flask loaddata`

- Each model object has `as_dict` method, that returns object as dict and we can dump it into JSON
    - adds extra `model` field with the model name of the converted object
    - It uses the following conversion scheme (according to field type)

        | Actual ObjectField Type   | Conversion Type             | Description |
        | ------------------------  |:---------------------------:|-------------|
        | string                    |      -                      |     No change
        | numeric                   |      -                      |     No change
        | datetime                  |      -                      |     No change
        | enum                      |      String                 | field_value.name is the string representing the enum value
        | Foreign Key               |      dict                   | we convert the referenced object .as_dict()
        |Backref i.e `contact.tasks`|      list of dicts          | we get all object referencing current object and we call their as_dict()

    - **backrefs that involve a many To Many relationship with many to many tables involved**
        > some backrefs involve Many to Many relationship i.e `company.tags`
        > In this case, we serialize them as normal backrefs (explained in table above)
        > , but we also get the related records out of the many to many table involved i.e `companytags`
        > insert them as list of dicts in a newly created field called 'CompanyTags'.
        > Then later on when loading data, we check if field name doesn't exist in the model object we're trying to load we assume it
        > belongs to many to many model object and we load that object too.

     - **Important**
        > `as_dict()` takes an argument `resolve_refs` which is False by default
        > if set to True, it means don't resolve (backrefs)
        > To understand **`Why is this important`** please consider the following scenario

        > `contact.tasks` is a backref/one to many relationship means a `task` has a F.K relationship to `contact`
        > If we're calling `contact.as_dict()` then to get all tasks as dicts embeded in the `contact` dictionary then
        > for each task we call `task.as_dict(resolve_refs=False)` otherwise if `resolve_refs` is True
        > `task.as_dict()` will try to resolve the F.K `contact.as_dict()` and we end up a dead lock / Stack error
        > where a contact tries to get `task_as_dict()` but task tries to get the same `contact.as_dict()`



- We use [ujosn](https://pypi.python.org/pypi/ujson) for fast dump of data. but with only one problem that it
dumps datetime fields into epoch so you'll have to reverse epoch into datetime when loading object from JSON
and you can easily determine that a decimal number is epoch if the dumped data has the exact model
then you can get the model class and determine if the field name is datetime field or not and if so, you can
convert epoch into datetime. This is what `obj.from_dict()` method used by `flask loaddata` is doing

**Limitations**
- We dump only Root models, so if there's a non-Root model record created like a `task` that is not referring to another Root model record
i.e not assigned to any user, and not referring to any other contact. It will not be dumped

###### Load

 >  `flask loaddata`

- Root models :

    > We've 7 Root models/DIRs
            - Company
            - Contact
            - Deal
            - Sprint
            - Project
            - Organization
            - User

- Each root model has a directory with each file inside, representing a record

- All records in DB except for Many To Many Tables have 2 fields :
    - `author_last_id`, Last User ID to make modifications to record
    - `author_original_id` Orginal User ID to create the record

    > This means we need to load and save `Users` first before trying to save other records otherwise
    > `author_last_id` & `author_original_id` will be referencing non existing records and we get ORM Error

    > Same thing goes for `Users`, we Save them without `author_last_id` & `author_original_id`
    > Then update these fields for all saved users

- We loop over all over each record/file and load the dumped json file into a dictionary
- we determine record model class by a field called `model` in the dumped JSON of that object/record
- we create an empty object of a the same type determined by `model` field then call `obj.from_dict(loaded_dict)`
- `obj.from_dict()`
    - It loads the parent root object and any nested objects inside
    - The way it works is as follows

        - Create a list to put any nested dictionary we encounter so we can load later
        - Create a list to put all processd/loaded objects inside
        - Load Root object as follows:

        | Dictionary value type     | object field type           | Description |
        | ------------------------  |:---------------------------:|-------------|
        | string                    |      string                 |     No change
        | numeric                   |      numeric                |     No change
        | epoch                     |      datetime               |If dictionary key representing model field of type timestamp, we assume numeric value is epoch and we convert into datetime
        | dict                      |      -                      |a F.K of another object. add it to a list we'll process later
        | list                      |      -                      |Backref objects, add them to the list of un processed dicts for now

        **Dict keys that doesn't exist in model object**
            > we assume they belong to Many to many tables, we add them to the list of unprocessed dicts
            > Their values will be a dictionary any ways

        - Put the loaded root model in the list of loaded objects
        - For each non processed dictionary load it the same way as above and put any nested dicts `Foreginkeys & Backrefs` into
         list of un-processed dictionaries
        - Continue until list of unprocessed objects is empty

    - Return all loaded objects

- Now we save objects into DB

**Warning**

- When you invoke `flask loaddata` the `crm.events` package is disabled by default
so we don't invoke ORM events when loading data because we don't need to alter the inserted records, we want a typical mirror

- Many to Many fields have a primary key with auto increment constrains, but since we load them with old
IDs exactly as in the dump, this causes a problem in `postgresql` DB as it looses track of the latest max ID inserted for many to many tables
we fix this by issuing
    ```
            for table in m2m_tables:
                db.engine.execute("SELECT setval('%s_id_seq', (SELECT MAX(id) FROM %s)+1);" % (table, table))`

    ```