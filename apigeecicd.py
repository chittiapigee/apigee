import argparse
import base64
import json
import requests
import os
import yaml
from zipfile import  ZipFile


def read_config_from_yml(yamfile):
    filename = os.getcwd()+os.sep+yamfile
    with open(filename) as file:
        return  yaml.load(file,Loader=yaml.FullLoader)


def get_base64(mgmt_username, mgmt_password):
    return base64.b64encode(bytes(mgmt_username.strip()+':'+mgmt_password.strip(),'utf-8')).decode('utf-8')


def make_get_call(url, mgmt_username, mgmt_password):
    headers = {
        'authorization': "Basic " + get_base64(mgmt_username, mgmt_password)
    }

    return requests.request("GET", url, headers=headers, verify=False)


def get_highest_revnum(mgmt_url, mgmt_username, mgmt_password, org_name, env_name, artifact_type, artifact_name):

    rev_url = mgmt_url+'/v1/organizations/'+org_name+'/'+artifact_type+'/'+artifact_name+'/revisions'

    response = make_get_call(rev_url, mgmt_username, mgmt_password)

    if response.ok:
        rev_array = json.loads(response.content)
        if len(rev_array)!=0:
            return max(rev_array)
        else:
            return 0
    else:
        print("revision call failed with code "+str(response.status_code)+", message: "+response.text);



def download_artifact(artifact_type, artifact_name, mgmt_username, mgmt_password, branch_name, planet_config):
    print(planet_config)
    mgmt_url=planet_config['mgmt_url']

    org_name = ''
    env_name = ''
    for branch in planet_config['branch']:
        if branch_name == 'develop':
            org_name=branch['develop']['source_org']
            env_name=branch['develop']['source_env']

    revision_num = get_highest_revnum(mgmt_url,mgmt_username,mgmt_password,org_name,env_name,artifact_type,artifact_name)
    if revision_num != None and revision_num !=0:
        print('Downloading bundle for '+artifact_name+' --> '+revision_num)
        rev_url = mgmt_url+'/v1/organizations/'+org_name+'/'+artifact_type+'/'+artifact_name+'/revisions/'+revision_num
        params = {'format':'bundle'}
        headers = {
            'authorization': "Basic " + get_base64(mgmt_username, mgmt_password)
        }

        response = requests.request("GET", rev_url,params=params, headers=headers, verify=False)

        if response.ok:
            bundle_name=os.getcwd()+os.sep+artifact_name+'.zip'

            with open(bundle_name, 'wb') as bundle_zip:
                bundle_zip.write(response.content)
                bundle_zip.close()
    else:
        print('No revisions found for proxy: '+artifact_name+", Hence can't download")


def deploy_artifact(artifact_name, mgmt_username, mgmt_password, branch_name, planet_config):
    mgmt_url = planet_config['mgmt_url']

    #read target env details.
    org_name = ''
    env_name = ''
    mvn_profile = ''
    for branch in planet_config['branch']:
        if branch_name == 'develop':
            org_name = branch['develop']['target_org']
            env_name = branch['develop']['target_env']
            mvn_profile = branch['develop']['mvn_profile']

    zip_file_name = os.getcwd()+os.sep+artifact_name+'.zip'
    if os.path.exists(zip_file_name):
        with ZipFile(zip_file_name,'r') as zip:
            zip.extractall(os.getcwd()+os.sep+artifact_name)

        #change pom xml with proxy name
        datafile = os.getcwd()+os.sep+'pom.xml'

        new_lines = []
        with open(datafile, 'r') as f:
            for line in f.readlines():
                if 'edge-bundle' in line:
                    line = line.replace('edge-bundle',artifact_name)
                new_lines.append(line)

            outfile = os.getcwd()+os.sep+artifact_name+os.sep+'pom.xml'

            with open(outfile, 'w') as of:
                of.writelines(new_lines)

        # invoke deployment
        os.chdir(os.getcwd()+os.sep+artifact_name)

        mvn_command = 'mvn install -P '+mvn_profile+' -Dprofile='+env_name+' -Dorgname='+org_name+' -Denv='+env_name+' -Dmgmturl='+mgmt_url+' -Dusername='+mgmt_username+' -Dpassword='+mgmt_password+' -Doptions=override -Ddelay=10'
        os.system(mvn_command)
    else:
        print("Artifact "+artifact_name+".zip doesn't exist, hence cannot deploy")


def main():
    requests.packages.urllib3.disable_warnings()
    parser = argparse.ArgumentParser(description="Apigee CI CD utility.")
    parser.add_argument('--planet_name', required=True, help="Please provide planet name with flag --planet_name")
    parser.add_argument('--action_name', required=True, help="Please provide action name with flag --action_name")
    parser.add_argument('--artifact_type', required=True, help="Please provide artifact name with flag --artifact_type")
    parser.add_argument('--artifact_name', required=True, help="Please provide artifact name with flag --artifact_name")
    parser.add_argument('--mgmt_username', required=True, help="Please provide mgmt username with flag --mgmt_username")
    parser.add_argument('--mgmt_password', required=True, help="Please provide mgmt password with flag --mgmt_password")
    parser.add_argument('--branch_name',  required=True, help="Please provide branch name with flag --branch_name")

    args = parser.parse_args()

    planet_name=args.planet_name
    action_name = args.action_name
    artifact_type = args.artifact_type
    artifact_name = args.artifact_name
    mgmt_username = args.mgmt_username
    mgmt_password = args.mgmt_password
    branch_name = args.branch_name

    if planet_name is not None and action_name is not None and artifact_type is not None and artifact_name is not None and mgmt_username is not None and mgmt_password is not None and branch_name is not None:
        config_json = read_config_from_yml('config.yml')['edge_config_data']

        planet_config = config_json[planet_name]

        action_names = action_name.split(',')

        for act_name in action_names:

            if act_name == 'download' and branch_name == 'develop':
                download_artifact(artifact_type,artifact_name,mgmt_username,mgmt_password,branch_name,planet_config)

            if act_name == 'deploy':
                deploy_artifact(artifact_name, mgmt_username, mgmt_password, branch_name, planet_config)
    else:
        print("Issue with input params, please check")


if __name__ == "__main__":
    main()
