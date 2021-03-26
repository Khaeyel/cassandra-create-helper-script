#!/usr/bin/python3
import sys
import string
import random
import subprocess
import click

#Expected user input:
#   u - role name, eg. kgabrick
#   k - keyspaces to target
#   r - Read permissions, implicit?
#   w - Write permissions
#   e - Target environment
#   d - dry run

#Taken from https://stackoverflow.com/questions/19213232/python-v3-random-password-generator
def randompassword():
  chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
  size = random.randint(20, 28)
  return ''.join(random.choice(chars) for x in range(size))

#Need to set password for use in functions; can't call function multiple times
to_add_pw = randompassword() #String

#def usage():
#    argparser = argparse.ArgumentParser(description="This is a script that generates the CQLSH lines to create a new role, table, or keyspace. Each function has its own set of expected flags")
#    argparser.add_argument("fnc", help="Pick one: [role,table,keyspace]")

@click.group()
def ctl():
    #Debugging
    #print(sys.argv)
    #usage()
    pass

@ctl.command()
@click.option('--keyspacename','-k',required=True)
@click.option('--replication-factor','-rf',required=True)
@click.argument('datacenters',nargs=-1)
def keyspace(keyspacename,datacenters,replication_factor):
    dc_list = []
    for dc in datacenters:
        dc_list.append("'{0}': '{1}'".format(dc,replication_factor)) #'us-west4': '3'

    dc_string = ", ".join(dc_list)

    command = "CREATE KEYSPACE {0} WITH replication = {{'class': 'NetworkTopologyStrategy', {1} }}  AND durable_writes = true;".format(keyspacename, dc_string)

    print(command)
    return command

@ctl.command()
@click.option('--keyspace','-k',required=True)
@click.option('--table_file','-t',required=True)
def table(keyspace,table_file):
    #Devs to provide table and parameters as a paste-able block
    #Script just runs it in the requested keyspace

    #Sample input
    '''
    CREATE TABLE inbox_dev.inbox_entries (
       usr bigint,
       transaction_id text,
       date timestamp,
       entry_type text,
       entry_subtype text,
       entry_action text,
       external_id text,
       titles text,
       expiry timestamp,
       data blob,
       PRIMARY KEY ((usr), transaction_id, date, entry_type, entry_subtype)
    );
    '''

    with open(table_file,'r') as file:
        command = ' '.join(file.read().split())

    #CREATE TABLE {table} ...
    table = command.split()[2]

    #if table does not have ., keyspace is not included
    if "." not in table:
        print(command.replace(table,f'{keyspace}.{table}'))
        return command.replace(table,f'{keyspace}.{table}')
    #else table name contains ., keyspace is already included, don't do anything
    else:
        print(command)
        return command

@ctl.command()
@click.option('--rolename','-r',required=True)
@click.argument('keyspaces',nargs=-1)
@click.option('--write','-w',is_flag=True)
def role(rolename,keyspaces,write):
    command_list = []

    command_list.append("create role if not exists {0} with login = true and password = '{1}';".format(rolename,to_add_pw))
    command_list.append("grant execute on internal scheme to {0};".format(rolename))

    if write:
        for ks in keyspaces:
            for method in ["CREATE","DROP","MODIFY"]:
                command_list.append("grant {0} on keyspace {1} to {2};".format(method,ks,rolename))
    else:
        for ks in keyspaces:
            command_list.append("grant SELECT on keyspace {1} to {0};".format(rolename,ks))

    for cmd in command_list:
        print(cmd)

    return command_list

def usage():
    print("This is a helper script to generate output that is then piped into a Cassandra cluster as CQL commands")
    print("Required input is one of [role,table,keyspace] as the first argument. Use --help for more information")
    return True

if len(sys.argv) <= 1:
    usage()
    exit(1)

if __name__ == "__main__":
    ctl()