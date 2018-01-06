#!/usr/bin/env python3
from lib.instancemanager import InstanceManager


if __name__ == "__main__":
    aws_region = "us-east-1"

    mgr = InstanceManager(aws_region=aws_region)
    instances = mgr.get_all_instances()
    terminated_instances = []

    # Check each instance and terminate it if possible
    for instance in instances:
        print("Checking instance {}".format(instance["InstanceId"]))
        if mgr.is_instance_deletable(instance):
            mgr.terminate_instance(instance["InstanceId"])
            terminated_instances.append(instance["InstanceId"])

    # Report
    print("\n------------------------------")
    print("Report of terminated instances")
    print("------------------------------")
    if terminated_instances:
        for i in terminated_instances:
            print("Instance {} terminated".format(i))
    else:
        print("No instances were terminated")
