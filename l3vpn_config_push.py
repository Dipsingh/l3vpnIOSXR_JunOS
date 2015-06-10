from pyIOSXR import IOSXR
from getpass import *
from pprint import pprint
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from jnpr.junos import Device
import argparse, sys, os, glob

defaults = {
    'port':'22',
    'user':'',
    'password':'',
    'ssh_key':''
}

def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description="utility to push configurations to JunOS or IOSXR devices")
    parser.add_argument("-u","--user",help="Username to login to device")
    parser.add_argument("-p","--password",action='store_true',help="Prompt for password to login to device")
    parser.add_argument("-c","--confirm",action='store_true',help="Auto Confirm configuration changes(No diff changes review)",required=False)
    parser.add_argument("-P","--port",required=False,help="Netconf port to connect on",)
    args=parser.parse_args()
    return args

args = parse_arguments(sys.argv)

if args.port:
    port = args.port
elif defaults['port'] != '':
    port = defaults['port']
else:
    port = '22'

if args.password is True:
    password = getpass('Password for %s :' % args.user)
elif defaults['password'] != '':
    password = defaults['password']
else:
    password=''


if os.path.exists('./configs'):
    for filename in glob.glob('./configs/*JunOS.txt'):
        with open(os.path.join(filename), 'r') as f:
            ipaddress = str(filename[10:-10])
            pprint('***Processing %s port %s ***' % (ipaddress, port))
            dev = Device(ipaddress,user=args.user,password=password,port=port,ssh_private_key_file=defaults['ssh_key'],gather_facts=False)

            dev.open()
            dev.bind(cfg=Config)
            pprint("Locking Configuration")

            try:
                dev.cfg.lock()
            except Exception as err:
                print ("Error occured during config lock ",err)
                continue

            try:
                dev.cfg.load(path=filename,format = 'set',merge=True)
            except Exception as err:
                print ("Error occured during config loading" , err)
                continue

            pprint("Verifying configuration")
            try:
                commit_check = dev.cfg.commit_check()
            except Exception as err:
                print ("Error occured during config check",err)
                continue

            if commit_check is True:
                if args.confirm is True:
                    pprint("Confirmation bypassed")
                    dev.cfg.commit()
                    dev.close()
                    continue
                else:
                    pprint("The following configs will be applied ")
                    diff = dev.cfg.pdiff()
                    commit_config = ''
                    while commit_config != 'YES' and commit_config != 'NO':
                        commit_config = raw_input('Apply configuration (YES/NO)')
                        if commit_config == 'YES':
                            pprint("Commiting")
                            rsp = dev.cfg.commit()
                            if rsp is True:
                                pprint ("Commit successful")
                                dev.close()
            elif commit_config == 'NO' :
                pprint("Rolling back")
                dev.cfg.rollback()
                dev.close()

    for xr_filename in glob.glob('./configs/*ios_xr.txt'):
        with open(os.path.join(xr_filename), 'r') as f:
            ipaddress = str(xr_filename[10:-11])
            pprint('***Processing %s port %s ***' % (ipaddress, port))
            xr_device = IOSXR(hostname='172.16.2.10',username='dipsingh',password='cisco123')
            xr_device.open()

            try:
                xr_device.load_candidate_config(filename=xr_filename)
            except Exception as err:
                print ('Error occured while loading candidate configs',err)
                continue

            if args.confirm is True:
                pprint("Confirmation bypassed")
                xr_device.commit_config()
                xr_device.close()
                continue
            else:
                pprint("The following configs will be applied ")
                diff = xr_device.compare_config()
                commit_config = ''
                while commit_config != 'YES' and commit_config != 'NO':
                    commit_config = raw_input('Apply configuration (YES/NO)')
                    if commit_config == 'YES':
                        pprint("Commiting")
                        rsp = xr_device.commit_config()
                        if rsp is True:
                            pprint ("Commit successful")
                            xr_device.close()
                    elif commit_config == 'NO' :
                        pprint("Rolling back")
                        xr_device.rollback()
                        xr_device.close()

else:
    print('Config Directory Not Found')
