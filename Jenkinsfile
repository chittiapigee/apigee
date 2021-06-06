pipeline {
    agent any

    stages {
		stage('Python setup'){
		
			steps{
				sh "pip install requests"
				sh "pip install PyYAML"
			}
		}
        stage('Download Bundle') {
            steps {
                
				withCredentials([usernamePassword(credentialsId: 'APIG_SAAS_MGMT_CRED_ID', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
				sh "python apigeecicd.py --planet_name saas --action_name download --artifact_type apis --artifact_name ${env.JOB_NAME} --mgmt_username ${USERNAME} --mgmt_password ${PASSWORD} --branch_name develop"
				}
            }
        } 
		 stage('Deploy Bundle') {
            steps {
                
				withCredentials([usernamePassword(credentialsId: 'APIG_SAAS_MGMT_CRED_ID', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
				sh "python apigeecicd.py --planet_name saas --action_name deploy --artifact_type apis --artifact_name ${env.JOB_NAME} --mgmt_username ${USERNAME} --mgmt_password ${PASSWORD} --branch_name develop"
				}
			}
        } 
    }
}
