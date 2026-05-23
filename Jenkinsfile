
pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command: ["sleep"]
    args: ["infinity"]
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker
  - name: tools
    image: python:3.12-slim
    command: ["sleep"]
    args: ["infinity"]
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["sleep"]
    args: ["infinity"]
  volumes:
  - name: docker-config
    emptyDir: {}
'''
    }
  }

  environment {
    IMAGE_NAME = "docker.io/sivanext/netflixclone:${BUILD_NUMBER}"
    LATEST_IMAGE = "docker.io/sivanext/netflixclone:latest"
    DOCKER_REGISTRY = "docker.io"
    DOCKER_AUTH_REGISTRY = "https://index.docker.io/v1/"
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
        container('tools') {
          sh 'pip install -r requirements.txt'
        }
      }
    }

    stage('Unit Test') {
      steps {
        container('tools') {
          sh 'python -m pytest'
        }
      }
    }

    stage('Build and Push Image') {
      steps {
        container('kaniko') {
          withCredentials([usernamePassword(credentialsId: 'netflixclone-docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
            sh '''
              mkdir -p /kaniko/.docker
              cat > /kaniko/.docker/config.json <<EOF
{"auths":{"${DOCKER_AUTH_REGISTRY}":{"username":"${DOCKER_USER}","password":"${DOCKER_PASSWORD}"}}}
EOF
            '''
            sh '/kaniko/executor --context=${WORKSPACE} --dockerfile=${WORKSPACE}/Dockerfile --destination=${IMAGE_NAME} --destination=${LATEST_IMAGE}'
          }
        }
      }
    }



    stage('Deploy') {
      steps {
        container('kubectl') {
          timeout(time: 3, unit: 'MINUTES') {
            withCredentials([string(credentialsId: 'netflixclone-kubeconfig', variable: 'KUBECONFIG_CONTENT')]) {
              writeFile file: 'kubeconfig.generated.yaml', text: KUBECONFIG_CONTENT
              sh '''
                set -eux
                trap 'rm -f kubeconfig.generated.yaml' EXIT
                kubectl version --client=true
                kubectl --kubeconfig kubeconfig.generated.yaml --request-timeout=30s config current-context
                kubectl --kubeconfig kubeconfig.generated.yaml --request-timeout=30s get namespace ${NAMESPACE} || kubectl --kubeconfig kubeconfig.generated.yaml --request-timeout=30s create namespace ${NAMESPACE}
                kubectl --kubeconfig kubeconfig.generated.yaml --request-timeout=30s apply -n ${NAMESPACE} --validate=false -f k8s/generated/
              '''
            }
          }
        }
      }
    }
  }
}
