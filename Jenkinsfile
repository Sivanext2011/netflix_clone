
pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: default
  automountServiceAccountToken: true
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
    image: alpine:3.20
    command: ["sleep"]
    args: ["infinity"]
  volumes:
  - name: docker-config
    emptyDir: {}
'''
    }
  }

  environment {
    IMAGE_NAME = "docker.io/sivanext/payments-api:${BUILD_NUMBER}"
    LATEST_IMAGE = "docker.io/sivanext/payments-api:latest"
    DOCKER_REGISTRY = "docker.io"
    DOCKER_AUTH_REGISTRY = "https://index.docker.io/v1/"
    NAMESPACE = "devsecops"
    TRIVY_SEVERITY = "HIGH,CRITICAL"
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
          withCredentials([usernamePassword(credentialsId: 'payments-api-docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD')]) {
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
            sh '''
              set -eux
              trap 'rm -f kubeconfig.incluster.yaml' EXIT
              apk add --no-cache kubectl
              SA_DIR=/var/run/secrets/kubernetes.io/serviceaccount
              kubectl config --kubeconfig kubeconfig.incluster.yaml set-cluster in-cluster --server=https://kubernetes.default.svc --certificate-authority=${SA_DIR}/ca.crt --embed-certs=true
              kubectl config --kubeconfig kubeconfig.incluster.yaml set-credentials jenkins-agent --token="$(cat ${SA_DIR}/token)"
              kubectl config --kubeconfig kubeconfig.incluster.yaml set-context in-cluster --cluster=in-cluster --user=jenkins-agent
              kubectl config --kubeconfig kubeconfig.incluster.yaml use-context in-cluster
              kubectl --kubeconfig kubeconfig.incluster.yaml version --client=true
              kubectl --kubeconfig kubeconfig.incluster.yaml --request-timeout=30s get namespace ${NAMESPACE} || kubectl --kubeconfig kubeconfig.incluster.yaml --request-timeout=30s create namespace ${NAMESPACE}
              kubectl --kubeconfig kubeconfig.incluster.yaml --request-timeout=30s apply -n ${NAMESPACE} --validate=false -f k8s/generated/
            '''
          }
        }
      }
    }
  }
}
