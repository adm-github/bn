How to run the script:
- install all the dependencies: pip3 install -r requirements.txt
- ssh key must be loaded on the agent (i.e. ssh-add $pemfile)
- ./terminate_instances.py OR
- ./tree.py -s SERVER

Assumptions:
- the environment is on AWS
- An instance is considered to be terminated when all the following :
1. cpu is below X% (configurable)
2. memory usage is below X% (configurable)
3. no user logged in, in the last X hours (configurable)
4. ingress bandwidth usage is below X% (configurable)

Given the short amount of time that has to be dedicated to the task, this works more as a proof of concept than a production system.
A number of improvements are possible and desirable before this can be used in a real environment.
Improvements:
- single configuration file for all the options
- two steps termination: stop -> terminate
- distributed system to increase the power and minimize the time of execution
- introduce a process for defining how the instances are designed for termination rather than guessing (non technical)
- safe programming (exceptions, checks, etc.)
- improve the code to be vendor agnostic
