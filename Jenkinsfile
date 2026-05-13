
pipeline {
  agent any

  environment {
    IMAGE_NAME = "docker.io/sivanext/netflix_clone:${BUILD_NUMBER}"
    LATEST_IMAGE = "docker.io/sivanext/netflix_clone:latest"
    DOCKER_REGISTRY = "docker.io"
    NAMESPACE = "devsecops"
    TRIVY_SEVERITY = "MEDIUM,HIGH,CRITICAL"
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

    stage('Dependency Scan') {
      steps {
        sh 'trivy fs --exit-code 1 --severity ${TRIVY_SEVERITY} .'
      }
    }

    stage('Container Scan') {
      steps {
        sh 'trivy image --exit-code 1 --severity ${TRIVY_SEVERITY} ${IMAGE_NAME}'
      }
    }

    stage('SBOM') {
      steps {
        sh 'syft ${IMAGE_NAME} -o spdx-json=sbom.spdx.json'
        archiveArtifacts artifacts: 'sbom.spdx.json', fingerprint: true
      }
    }

    stage('IaC Scan') {
      steps {
        sh 'checkov -d k8s --quiet'
      }
    }

    stage('Push') {
      when {
        branch 'main'
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'netflixclone-docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
          sh 'echo "$DOCKER_PASSWORD" | docker login ${DOCKER_REGISTRY} -u "$DOCKER_USER" --password-stdin'
          sh 'docker push ${IMAGE_NAME}'
          sh 'docker push ${LATEST_IMAGE}'
        }
      }
    }

    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        withCredentials([string(credentialsId: 'netflixclone-kubeconfig', variable: 'KUBECONFIG_CONTENT')]) {
          writeFile file: 'kubeconfig.generated.yaml', text: KUBECONFIG_CONTENT
          sh 'kubectl --kubeconfig kubeconfig.generated.yaml create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl --kubeconfig kubeconfig.generated.yaml apply -f -'
          sh 'kubectl --kubeconfig kubeconfig.generated.yaml apply -n ${NAMESPACE} -f k8s/'
        }
      }
    }
  }
}
