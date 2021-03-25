#!/usr/bin/python3
import sys
import argparse
import string
import random
import subprocess

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

def usage():
    argparser = argparse.ArgumentParser(description="This is a tool that generates the CQLSH lines to create a new role. And whatever other options you add to the call")
    argparser.add_argument("-u", help="Name of the role to generate lines for",required=True)
    argparser.add_argument("-k","--keyspaces",help="String of keyspaces to grant permissions to",required=True)
    argparser.add_argument("-e","--env",help="Environment to create role in. Either 'Stage' or 'Prod'",required=True)
    argparser.add_argument("-r","--read",help="Grant read-only permissions to the role",action="store_true")
    argparser.add_argument("-w","--write",help="Grant write permissions to the role, will grant read access also",action="store_true")
    argparser.add_argument("-d","--dry",help="Dry run, will print proposed output to console",action="store_true")
    argparser.parse_args()

def main():

    command_list = []

    try:

        argparser = argparse.ArgumentParser()
        argparser.add_argument("-u",required=True)
        argparser.add_argument("-k","--keyspaces",nargs='+',required=True)
        argparser.add_argument("-e","--env",required=True)
        argparser.add_argument("-r","--read",action="store_true")
        argparser.add_argument("-w","--write",action="store_true")
        argparser.add_argument("-d","--dry",action="store_true")
        args = argparser.parse_args()

    except Exception as err:
        # print help information and exit:
        print(err)
        usage()
        #sys.exit(2)
        return False

    """
    Sample output with input : -u testrole -k keyspace1 keyspace2 -rw

    create role if not exists testrole with login = true and password = 'aIPCX6sFvXybhlz1L8cy';
    grant execute on internal scheme to testrole;
    grant SELECT on keyspace keyspace1 to testrole
    grant SELECT on keyspace keyspace2 to testrole
    grant CREATE on keyspace keyspace1 to testrole
    grant DROP on keyspace keyspace1 to testrole
    grant MODIFY on keyspace keyspace1 to testrole
    grant CREATE on keyspace keyspace2 to testrole
    grant DROP on keyspace keyspace2 to testrole
    grant MODIFY on keyspace keyspace2 to testrole
    """

    to_add_rolename     = getattr(args,"u") #String
    to_add_keyspaces    = getattr(args,"keyspaces") #List
    to_add_read         = getattr(args, "read") #Boolean
    to_add_write        = getattr(args, "write") #Boolean
    to_add_env          = getattr(args, "env") #String

    command_list.append("create role if not exists {0} with login = true and password = '{1}';".format(to_add_rolename,to_add_pw))
    command_list.append("grant execute on internal scheme to {0};".format(to_add_rolename))

    if to_add_read or to_add_write:
        for ks in to_add_keyspaces:
            command_list.append("grant SELECT on keyspace {1} to {0};".format(to_add_rolename,ks))

    if to_add_write:
        for ks in to_add_keyspaces:
            for method in ["CREATE","DROP","MODIFY"]:
                command_list.append("grant {0} on keyspace {1} to {2};".format(method,ks,to_add_rolename))

    #Generate output in format of
    #cqlsh -u cassandra -p${PW} -e "command_list[i]"

    for cmd in command_list:
        #Debug
        if getattr(args,"dry"):
            print(cmd)
        #else:
        #    subprocess.run("echo cqlsh -u cassandra -p{0} -e \"{1}\"".format(${CASSANDRA_PW},cmd).split()) #,Shell=True)

    return True



if len(sys.argv) <= 1:
    usage()
    exit(1)

if __name__ == "__main__":
    main()
        
