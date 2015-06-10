__author__ = 'dipsingh'

import os
from jinja2 import Template,Environment,FileSystemLoader
import csv

L3VPN_TEMPLATE_FILENAME = 'IOSXR_TEMPLATE.jinja2'
JunOS_Template_Filename = 'JunOS_Template.jinja2'
L3VPN_DATA_FILENAME = 'L3VPN_Details.csv'


def transform_cust(row):
    vrf_interface_fields = { csv_field_name: csv_field_value
                    for csv_field_name,csv_field_value in row.items()
                    if csv_field_value != '0'
                    if csv_field_name.startswith('VRF_Interface')
    }
    row ['vrf_interface'] = vrf_interface_fields
    vrf_name_fields = { csv_field_name: csv_field_value
                        for csv_field_name,csv_field_value in row.items()
                        if csv_field_value != '0'
                        if csv_field_name.startswith('VRF_NAME')
                        }
    row ['cust_vrf_name'] = vrf_name_fields
    ip_address_fields = { csv_field_name: csv_field_value
                        for csv_field_name,csv_field_value in row.items()
                        if csv_field_value != '0'
                        if csv_field_name.startswith('IP_interface')
                        }
    row ['ip_address_interface'] = ip_address_fields
    int_to_ipmap_fields = {}
    for csv_field_name,csv_field_value in vrf_interface_fields.items():
        for csv_intf_name,csv_intf_value in ip_address_fields.items():
            if csv_field_name.lstrip('VRF_Interface_') == csv_intf_name.lstrip('IP_interface_'):
                int_to_ipmap_fields[csv_field_value] = csv_intf_value
    row['int_to_ipmap'] = int_to_ipmap_fields


env = Environment(loader=FileSystemLoader(os.getcwd()),trim_blocks=True, lstrip_blocks = True )
template = env.get_template(L3VPN_TEMPLATE_FILENAME)
junostemplate = env.get_template(JunOS_Template_Filename)

if os.path.exists('./configs'):
    pass
else:
    os.mkdir('./configs')
path = os.getcwd() + '/configs'

for row in csv.DictReader(open(L3VPN_DATA_FILENAME)):
    transform_cust(row)
    filename = row['IP_Address']+'_'+row['Device_Type']+'.txt'
    with open(os.path.join(path,filename),'a') as f:
        if row['Device_Type'] == 'ios_xr':
            f.write(template.render(row))
        else:
            f.write(junostemplate.render(row))
