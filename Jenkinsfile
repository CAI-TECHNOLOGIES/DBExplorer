pipeline {
    agent {
        label 'k8agent'
    }
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Clone repository') {
            steps {
                script {
                    container('build-agent') {
                        checkout scm
                    }
                }
            }
        }
        stage('Build docker image') {
            steps {
                script {
                    container('build-agent') {
                        app = docker.build('db-explorer')
                    }
                }
            }
        }
        stage('Push to ECR') {
            steps {
                script {
                    container('build-agent') {
                        docker.withRegistry("${env.IMAGE_REGISTRY_URL}", "${env.IMAGE_REGISTRY_CREDS}") {
                            app.push("${env.GIT_COMMIT[0..7]}")
                            app.push('latest')
                        }
                    }
                }
            }
        }
    }
}
