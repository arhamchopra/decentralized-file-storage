import os
import argparse

from handlers import handler

SERVER_IP = "172.24.1.107"
SERVER_PORT = 10000
AUTH = "default"
DIRPATH = "./maidsafe"
MAX_RETRIES = 10

parser = argparse.ArgumentParser()

parser.add_argument('--auth', required=True, 
        help='Authentication details of the user')
parser.add_argument('--server_ip', type=str, 
        default=SERVER_IP, help='IP for the server')
parser.add_argument('--server_port', type=int, 
        default=SERVER_PORT, help='Port for the server')
parser.add_argument('--max_retries', type=int, default=MAX_RETRIES, 
        help='The number of attempts for upload before failing')
parser.add_argument('--dirpath', type=str, default=DIRPATH, 
        help='Path to the maidsafe directory')
parser.add_argument('--command', type=str, required=True,
        help='The command you want to run: (upload | download | list)')
parser.add_argument('--filename', type=str, default = "",
        help='The file being requested')

args = parser.parse_args()
args_dict = vars(args)

if not os.path.isdir(args.dirpath):
    os.mkdir(args.dirpath)

if(args.command == 'upload' or args.command == 'download'):
    if args.filename is "":
        print("Incorrect usage: Need the filename")
        os._exit(0)

handler(args_dict)
