# python script to auto create neo4j_import_script.sh
# run within the directory that has all the csvs to import

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--csv_dir', nargs=1, required=True, help='the directory where the csvs are stored')
parser.add_argument('--database_dir', nargs='+', required=True,
                    help='the directory in which to store the neo4j database.')
parser.add_argument('--import_command', nargs=1, required=True, help='the path to the neo4j script to import.')
args = parser.parse_args()
csv_dir = args.csv_dir[0]
database_dir = args.database_dir[0]
import_command = args.import_command[0]

command = import_command + ' --into ' + database_dir
command += ' --skip-duplicate-nodes true'
command += ' --skip-bad-relationships true'
command += ' --bad-tolerance 100000000'

for filename in os.listdir(csv_dir):
    if 'edges' in filename:
        command += ' --relationships'
    elif 'nodes' in filename:
        command += ' --nodes'
    else:
        continue

    command += ' ' + os.path.join(csv_dir, filename)

print 'running neo4j command now: ' + command
print ''
print ''
os.system(command)
