import paramiko
import datetime
import boto3 as boto


class InstanceManager():
    def __init__(self, aws_region):
        '''
        :param aws_region: AWS Region
        :param type: string
        '''
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.aws_region = aws_region

        self.check_time_hours = 24
        self.cpu_threshold = 10  # 10% CPU
        self.network_threshold = 10000  # 10 Bytes

    def get_all_instances(self):
        '''
        :returns: List of instances and info
        :return type: dict
        '''
        boto_client = boto.client("ec2", region_name=self.aws_region)
        describe_instances = boto_client.describe_instances()
        return describe_instances["Reservations"][0]["Instances"]

    def run_ssh_command(self, instance, command):
        """
        :param instance: server name, ip or fqdn
        :param type: str
        :param command: Command to execute
        :param type: str
        :return: command output
        :return type: str
        """
        self.ssh_client.connect(instance, 22, "ec2-user")

        output = ""
        (stdin, stdout, stderr) = self.ssh_client.exec_command(command)
        for line in stdout.readlines():
            output += line

        self.ssh_client.close()
        return output

    def check_cpu_status(self, instance):
        """
        :param instance: instance dictionary as returned by the AWS API
        :param type: dict
        :return: value of the CPU Utilization in cloudwatch
        :return type: float
        """
        now = datetime.datetime.utcnow()
        end_time = datetime.timedelta(hours=self.check_time_hours)

        boto_client = boto.client("cloudwatch", region_name=self.aws_region)

        response = boto_client.get_metric_statistics(
            Period=self.check_time_hours*3600,
            StartTime=now - end_time,
            EndTime=now,
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Statistics=['Average'],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance["InstanceId"]}]
        )
        return response['Datapoints'][0]['Average']

    def check_networking_usage(self, instance):
        """
        :param instance: instance dictionary as returned by the AWS API
        :param type: dict
        :return: value of the NetworkIn in cloudwatch
        :return type: float
        """
        now = datetime.datetime.utcnow()
        end_time = datetime.timedelta(hours=self.check_time_hours)

        boto_client = boto.client("cloudwatch", region_name=self.aws_region)
        response = boto_client.get_metric_statistics(
            Period=self.check_time_hours * 3600,
            StartTime=now - end_time,
            EndTime=now,
            MetricName='NetworkIn',
            Namespace='AWS/EC2',
            Statistics=['Average'],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance["InstanceId"]}]
        )
        return response['Datapoints'][0]['Average']

    def did_users_login(self, instance, days=1):
        """
        :param instance: instance dictionary as returned by the AWS API
        :param type: dict
        :return: True if users logged in in the last x days, false elsewhere
        :return type: bool
        """
        lastlog = self.run_ssh_command(instance["PublicDnsName"], "lastlog -t{}".format(days))

        # One line is used for the column names, removing it with the -1
        if len(lastlog.strip().split("\n")) - 1:
            return True

        return False

    def terminate_instance(self, instance_id):
        """
        :param instance_id: ID of the instance to terminate
        :param type: str
        """
        boto_client = boto.client("ec2", region_name=self.aws_region)
        boto_client.terminate_instances(
            InstanceIds=[instance_id],
            DryRun=False
        )

    def is_instance_deletable(self, instance):
        """
        :param instance: instance dictionary as returned by the AWS API
        :param type: dict
        :return: True if instance can be deleted, false elsewhere
        :return type: bool
        """
        terminate = False

        if not self.did_users_login(instance) and \
                        self.check_cpu_status(instance) < self.cpu_threshold and \
                        self.check_networking_usage(instance) < self.network_threshold:
            terminate = True

        return terminate
