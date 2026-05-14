
pipeline {
  agent any

  environment {
    IMAGE_NAME = "docker.io/sivanext/netflix_clone:${BUILD_NUMBER}"
    LATEST_IMAGE = "docker.io/sivanext/netflix_clone:latest"
    DOCKER_REGISTRY = "docker.io"
    NAMESPACE = "devsecops"
    TRIVY_SEVERITY = "HIGH,CRITICAL"
    KUBECONFIG = "/var/jenkins_home/.kube/config"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }

    stage('Unit Test') {
      steps {
        sh 'python -m pytest'
      }
    }

    stage('Build Image') {
      steps {
        sh 'docker build -t ${IMAGE_NAME} .'
        sh 'docker tag ${IMAGE_NAME} ${LATEST_IMAGE}'
      }
    }



    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'netflixclone-docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
          sh 'echo "$DOCKER_PASSWORD" | docker login ${DOCKER_REGISTRY} -u "$DOCKER_USER" --password-stdin'
          sh 'docker push ${IMAGE_NAME}'
          sh 'docker push ${LATEST_IMAGE}'
        }
      }
    }

    stage('Deploy') {
      steps {
        sh 'kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply --validate=false -f -'
        sh 'kubectl apply -n ${NAMESPACE} -f k8s/generated/'
      }
    }
  }
}
