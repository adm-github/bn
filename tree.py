#!/usr/bin/env python3
from lib.instancemanager import InstanceManager
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", help="Instance ID for which to show the process tree")
    args = parser.parse_args()

    aws_region = "us-east-1"

    mgr = InstanceManager(aws_region=aws_region)
    print(mgr.run_ssh_command(args.server, "sudo pstree"))


