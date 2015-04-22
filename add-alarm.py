#!/usr/bin/python                                                                                                                                     

import os
import sys
import boto.ec2.cloudwatch
import boto.ec2
import datetime
import boto.rds
import boto.ec2.elb
import re

aws_akey=''                                       
aws_skey='' 

metrics=[]
alarms = [ 'ec2', 'rds',  'elb', 'CloudFront' ]
system = [ 'MemoryAvailable', 'DiskSpaceAvailable']
rds=[]
ec2=[]
cf=[]
elb=[]

ACTIONS =   [ 'None'] 
    
def get_ids(aws_akey,aws_skey,env,param):
    if param == 'ec2':
        conn = boto.ec2.connect_to_region("us-west-1",
                   aws_access_key_id=aws_akey,
                   aws_secret_access_key=aws_skey)
        res = conn.get_all_instances()
        instances = [i for r in res for i in r.instances]
        return [ ( i.id,i.ip_address,i.tags['Name'] )  for i in instances if i.tags.has_key('Name')
                 and re.search(r'%s' %
                               env, i.tags['Name'],re.IGNORECASE)  ]
      
    elif param == 'rds':
        ids = []
        conn = boto.rds.connect_to_region( "us-west-1",
        aws_access_key_id=aws_akey,aws_secret_access_key=aws_skey)
        rds = conn.get_all_dbinstances()
        return [ i.id  for i in rds if re.search(r'%s' % env,
                                                 i.id,re.IGNORECASE) ]
   
    elif param == 'CloudFront':
        conn = boto.connect_cloudfront( aws_access_key_id=aws_akey,
                                      aws_secret_access_key=aws_skey)
        ds = conn.get_all_distributions()
        return [ i.id for i in ds ]

    elif param == 'elb':
        ids = []
        elb = boto.ec2.elb.connect_to_region('us-west-1',
           aws_access_key_id=aws_akey,aws_secret_access_key=aws_skey )
        lbs = elb.get_all_load_balancers()
        return  [ lb.name for lb in lbs if re.search(r'%s' % env,
                                          lb.name, re.IGNORECASE) ]
        
    
def get_unit(metric):
     
    COUNT = [ 'DatabaseConnections', 'DiskQueueDepth',
              'READIOPS', 'WriteIOPS' ]
    PERCENT = [ 'CPUUtilization', '4xxErrorRate',
                '5xxErrorRate', 'TotalErrorRate'   ]
    BYTES = [ 'DiskReadBytes', 'DiskReadOps', 'DiskWriteBytes',
              'DiskWriteOps', 'NetworkIn',
              'NetworkOut', 'FreeStorageSpace',
              'FreeableMemory','NetworkReceiveThroughput' ]
    
    if metric in COUNT :
        return 'Count'
    elif metric in PERCENT:
        return 'Percent'
    elif metric in BYTES:
        return 'Bytes'
    else:
        return None




def add_metrics(instance_ids,metrics,tag,cw):

    print cw
    if tag == 'ec2':
        dim = 'InstanceId'
    elif tag == 'rds':
        dim  = 'DBInstanceIdentifier'
    elif tag == 'CloudFront':
        dim = 'DistributionId'
    elif tag == 'ELB':
        dim = 'LoadBalancerName'
    
    
    for ids in instance_ids:
        print ids[0]
        for mcs in metrics:
            if mcs.has_key(tag):
                metric =  mcs[tag][0]
                print metric
                check  =  mcs[tag][1]
                print check
                threshold = mcs[tag][2]
                print threshold
                if metric not in system:
                    namespace = tag.upper()
                    namespace = 'AWS/%s' % namespace
                    print namespace
                else:
                    namespace = 'System/Linux'
                    
                PERIOD  = int(mcs[tag][3])
                print PERIOD
                EVAL  = int(mcs[tag][4])
                print EVAL
                
                UNIT = get_unit(metric) 
                if re.match(r'^Free',metric,re.IGNORECASE):
                    comparison = '<='
                    print comparison
                elif   re.match(r'^Healthy',metric,re.IGNORECASE):
                    comparison = '<'
                    print comparison

                elif  re.search(r'Available',metric,re.IGNORECASE):
                    comparison = '<='
                    print comparison

                else:
                    comparison = '>='
                    print comparison
                
                if check == 'on':
                    name = ids[0] + "---" + ids[1] + "---" + ids[2] + "---" +  metric
                    print "Name:%s" % name
                    try:
                        alarm=boto.ec2.cloudwatch.alarm.MetricAlarm(
                            connection = cw,
                            name =    name,
                            metric =   metric,
                            namespace = namespace,
                            statistic = 'Average',
                            comparison = '%s' %  comparison,
                            description = '%s  check for %s--%s--ids[2]' %
                                             (mcs.keys(),ids[0],ids[1]),
                            threshold = int(threshold),
                            period = PERIOD,
                            evaluation_periods = EVAL,
                            unit = UNIT,
                            dimensions = { dim :ids[0]},
                            )
                    
                        cw.put_metric_alarm(alarm)
                             

                    except:
                        print "Couldn't add metric for %s-%s" % ( ids[0],metric)

if __name__ == "__main__" :


    if len(sys.argv) == 1:
        print "Usage %s env" %  sys.argv[0]
    else:
        env=sys.argv[1]


    conf_file = "/home/rihaz/cw.txt"
    if  not os.path.exists(conf_file):                                    
        print "Conf file does not exists"
        exit(0)
    
    fp = open(conf_file,'r')
    while 1:
        line = fp.readline().strip() 
        temp = line.split(':')
        if line:
            dict = { temp[0] : temp[1:]}
            metrics.append(dict)
        else:
            break
        
    cw = boto.ec2.cloudwatch.connect_to_region("us-west-1",
       aws_access_key_id=aws_akey,aws_secret_access_key=aws_skey)
    for alarm in alarms:
        abuf = get_ids(aws_akey,aws_skey,env,alarm)
        print abuf
        add_metrics(abuf,metrics,alarm,cw)





