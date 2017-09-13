- Word source: `owl3_relevant_fields.txt` needs to be tab delmited with the columns being word, alphagram, definition, probability, playability, front_hooks, back_hooks but with no headers.
- Download the .tar community neo4j version, not the pkg. https://neo4j.com/download/other-releases/#drivers

To set up neo4j:

Define in your terminal the directory path for `NEO4J_ROOT`.
```
NEO4J_ROOT=<path to /neo4j-enterprise-3.1.1/>
```

Then use this root to define the following directories:

```
CSV_DIR=$NEO4J_ROOT/import
DATABASE_DIR=$NEO4J_ROOT/data/databases/graph.db
IMPORT_COMMAND=$NEO4J_ROOT/bin/neo4j-import
```

And then define where you're storing your scripts (will probably be somewhere
in the Giraffe directory)
```
SCRIPTS_DIR=<path to script directory>
```

Run `one_edit_away.py`, then manually move the csv files that were created into `CSV_DIR`.

Now we just need to run the neo4j command and import into the database! Use the following command. It will take about 15 seconds. Make sure the `DATABASE_DIR` is completely empty, i.e., if you rerun the following command you'll first need to delete the contents of the directory.

```
time python "$SCRIPTS_DIR/neo4j_import_script.py" --csv_dir $CSV_DIR --database_dir $DATABASE_DIR  --import_command $IMPORT_COMMAND
```

Make sure to restart your server before trying to view the database from the console: `neo4j restart` or `neo4j stop` followed by `neo4j start`. Then view at in browser at `http://localhost:7474/browser/`.

And then you can create something pretty like this:

[[https://github.com/jwnorman/WordGraph/blob/master/images/two_to_thirteen.png]]
