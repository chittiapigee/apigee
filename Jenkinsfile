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
                
				sh "python apigeecicd.py --planet_name saas --action_name download --artifact_type apis --artifact_name ${env.JOB_NAME} --mgmt_username icicibank-apigee@freshgravity.com --mgmt_password Fresh@1234 --branch_name develop"
            }
        } 
		 stage('Deploy Bundle') {
            steps {
                
				sh "python apigeecicd.py --planet_name saas --action_name deploy --artifact_type apis --artifact_name ${env.JOB_NAME} --mgmt_username icicibank-apigee@freshgravity.com --mgmt_password Fresh@1234 --branch_name develop"
            }
        } 
    }
}