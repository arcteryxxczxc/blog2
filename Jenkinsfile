pipeline {
    // This pipeline can run on any available agent (e.g., Jenkins slave)
    agent any

    // Define environment variables for Docker credentials and image details
    environment {
        DOCKER_IMAGE = 'arcteryxxc/blog_mirka'  // Name of your Docker image
        DOCKER_TAG = "${BUILD_NUMBER}"       // Use build number for image tag
        DOCKER_USERNAME = 'arcteryxxc'          // Username for Docker Hub
        DOCKER_PASSWORD = 'dckr_pat_mzXJ-Y72rzdJA5OHsqmRU3PRTzo' // Docker Hub access token (replace with PAT)
    }

    // Define stages in the pipeline
    stages {
        // Checkout code from the Git repository
        stage('Checkout') {
            steps {
                // Clean workspace before checkout
                cleanWs()
                // Checkout code from 'main' branch of the specified repository URL
                git branch: 'main', url: 'https://github.com/arcteryxxczxc/blog_mirka.git'
            }
        }

        // Run tests on the checked out code
        stage('Test') {
            steps {
                // Install test dependencies using pip
                sh '''
                    python -m pip install -r requirements.txt
                '''
                // Run tests using pytest on 'tests.py' file
                sh '''
                    python -m pytest tests.py
                '''
            }
        }

        // Build Docker image for the application
        stage('Build Docker Image') {
            steps {
                script {
                    // Clean up unnecessary files before building the image (optional)
                    sh '''
                        if [ -d "__pycache__" ]; then rm -rf __pycache__; fi
                        if [ -d ".idea" ]; then rm -rf .idea; fi
                        if [ -d ".venv" ]; then rm -rf .venv; fi
                    '''
                    // Build the Docker image with the build number tag
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    // Create an additional "latest" tag for the image
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }

        // Push the built Docker image to the registry
        stage('Push Docker Image') {
            steps {
                script {
                    // Login to Docker Hub using stored credentials (**WARNING:** Security risk, consider using PAT)
                    sh "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin"

                    // Push both the tagged and latest versions of the image
                    sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        // Deploy the application using Docker Compose (**REPLACE with your deployment steps)
        stage('Deploy') {
            steps {
                script {
                    // Stop any existing Docker containers (ignore errors if not running)
                    sh 'docker-compose down || true'
                    // Update docker-compose.yml to use the built image with the build number tag
                    sh "sed -i 's|build: .|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|' docker-compose.yml"
                    // Start the application containers in detached mode
                    sh 'docker-compose up -d'
                }
            }
        }
    }

    // Post-build actions (always run after all stages)
    post {
        always {
            // Clean up unused Docker resources
            sh 'docker system prune -f'
            // Logout from Docker Hub
            sh 'docker logout'
            // Clean workspace
            cleanWs()
        }
    }
}