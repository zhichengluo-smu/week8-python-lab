# Week 8 Lab: Continuous Integration and Deployment to the Cloud (AWS)

## Before Class (Individual)

1. Register for an AWS Free Tier Account
   - Be aware that some AWS services (like ECS) might incur charges once you exceed the free tier.   
2. (Optional) Install Docker Desktop (only if you want to build containers locally)
   - **Windows**: [Install Docker for Windows](https://docs.docker.com/docker-for-windows/install/). Choose **WSL 2** or **Hyper-V** backend depending on your OS version.
   - **macOS**: [Install Docker for Mac](https://docs.docker.com/docker-for-mac/install/).  
   - Verify Docker is running: follow the [Get Started tutorial](https://docs.docker.com/get-started/).  
3. Create a Docker Hub Account
   - (Optional) Sign in to Docker Desktop with your Docker Hub credentials to link the account.

## Activity 1: Continuous Integration with GitHub Workflows
In this part, we will be implementing CI with GitHub Worfklows. The CI will run when code is merged into the main branch.
All tests will run as part of the CI pipeline. If all tests pass, a Docker container image will be built and automatically pushed to your Docker Hub repository. You do not need to build and push the Docker image locally.

Download and extract the code for Week 8 from eLearn. Open the code in your VS Code as usual.

Note: you do not need to create the virtual environment or install dependencies as usual, unless you want to run the code locally.

### Push the code to your GitHub account
In VS Code's version control interface, choose `Publish to GitHub` and select the private repository option. Your VS Code should already be linked to your GitHub account (Week 2, refer to https://code.visualstudio.com/docs/sourcecontrol/github).

You might see the CI pipeline running right away on GitHub (under the repository, visit `Actions` to see the worfklows) and then it fails. It is not a problem for now, as we need to complete the configuration below before it can run properly.

### Add your secret environment variables and Docker Hub credentials to GitHub
In the GitHub repository for the code you just pushed, click on `Settings`, then go to `Secrects and variables`, then `Actions`, then `New repository secret`. Enter the name, e.g., `OPENAI_API_KEY`, as in your `.env` file in the lab of Week 6, and the corresponding value. Repeat the process for each secret. These are needed to run the tests in the CI pipeline.

Remember to also include your Docker Hub login information, i.e., `DOCKER_PASSWORD` and `DOCKER_USERNAME`, so that GitHub Workflow can automatically push the container image to your account.

### Dockerfile 
Study and understand the content of the given `Dockerfile`.

### Docker Hub repository creation
Login to your Docker Hub on the web. From the home page (https://hub.docker.com/), click `Create a repository`. Give the new repository a name, e.g., `book_app_backend`. Select the option to make the repository public.

### Github Worfklow configuration
Study and understand the content of the `ci-docker-image.yml` file, which is under the folder `.github\workflows`.
Modify the file with your own values for `DOCKER_IMAGE`. This specifies where the CI will push the Docker image of your app.

### Commit and push the latest changes to GitHub
You should commit and push the latest changes to the yml file to GitHub. The pipeline will run automatically. You can check the status under `Actions` in your repository on GitHub.

When the pipeline can run successfully, you can check if a new Docker image with the tag `latest` has been pushed to your Docker Hub repository. To change the tag, you can explore the usage of Git tagging (for example, using `git tag v1.0.0` command), and push the new tag to GitHub repository (using `git push origin v1.0.0`). The CI pipeline will run and build a Docker image tagged with the latest Git tag instead of `latest`, e.g., `donta/book_app_backend:1.0.0`.

If the pipeline fails, you can look at the output of each stage to fix the issues, before committing/pushing again.

### Optional: pull the Docker image and test locally
If you have Docker Desktop running, you can pull the image that GitHub Workflow just created, and run a Docker container locally to test. In the `Optional settings` when choosing to run a Docker image, you will need to provide all environment variables for the OpenAI key, AWS Cognito, etc., for the local container to work.

You can also build a Docker image locally with the given Dockerfile, and push to your Docker Hub repository manually. Note: NEVER include your `.env` in the build.


## Activity 2: Deploy on AWS Elastic Container Service
### Create app secrets in AWS Secret Manager
   - In the AWS Console, search for “Secret Manager” and open **AWS Secret Manager**.
   - Click `Store a new secret`, then choose `Other type of secret`.
   - Enter the key/value pair for each app secret, e.g., `OPENAI_API_KEY`, `COGNITO_CLIENT_SECRET`, `COGNITO_USER_ROLE`, etc.
   - Click `Next` when you're done, and enter a `Secret name`, e.g., `prod/bookapp`.
   - Click `Next` to skip `Configure rotation`.
   - Click `Store`. Your app secret has been created.
   - Click on `Secrets` to see the list of secrets. Click on the secret's name to see its details.
   - Copy the `Secret ARN` which is to be used later in the ECS container task definition. The secret specified by the ARN will be passed as environment variables to your running application later by ECS. This is more secure than including an `.env` in the container image.

### Deploy on ECS
   - In the AWS Console, search for “ECS” and open **Amazon Elastic Container Service**.

#### Create a Cluster
   - Click on the top left icon before `Amazon Elastic Container Service` to reveal the left panel menu.
   - Click `Clusters` on the left, then `Create Cluster`.
   - Give the cluster a name, e.g., `book_cluster`.
   - Under `Infrastructure`, choose `AWS Fargate (serverless)`
   - Leave all optional parts as default values.
   - Click `Create`.  
   - You should see a success message that your cluster is created.

#### Create a Task Definition
   - Click on the top left icon before `Amazon Elastic Container Service` to reveal the left panel menu.
   - Click the `Task definitions`, then the drop down triangle on `Create new task definition` and select `Create new task definition`.
   - Enter a name of your choice for `Task definition family`.
   - Under `Infrastructure requirements`, select `AWS Fargate`.
   - Under `Operating system/Architecture`, select `Linux/X86_64`.
   - Under `Task size`, choose `1 vCPU` for `CPU`, `3 GB` for `Memory`.
   - Leave `Task role` empty. Select `Create new role` for `Task execution role`.
   - Under `Container`, give it a name, e.g., `bookcontainer`. 
   - Under `Image URI`, specify your Docker Hub image in the form `docker.io/<your Docker username>/<your Docker repository>:latest`, e.g., `docker.io/donta/book_backend:latest`.
   - Under `Port mappings`, enter `8000` and `container-port` for `Container port` and `Port name`, respectively. Leave the protocols as default values which should be `TCP` and `HTTP`.
   - Under `Environment variables`, add your app's required environment variables. For example, `Key` should be `OPENAI_API_KEY`, `Value type` should be `ValueFrom`, and `Value` should be your AWS secret's ARN obtained earlier in the form of `<Secret ARN>:<Key>::`. An example for `Value` is `arn:aws:secretsmanager:ap-southeast-1:352703104689:secret:prod/book_app-3TklMs:OPENAI_API_KEY::`. Continue to add all the required secrets (there are 7 of them).
   - Leave all other optional parts as default.
   - Click `Create`. Your ECS task to run a container image containing your app has been created.
   - Under `Task definitions`, click on the name of the newly created task. Click on the name of the role under `Task execution role`. This brings you to the `Identity and Access Management` service, as we need to customize the role's permission to read secrets from `Secret Manager`.
   - Under `Permission policies` for the role, you should see `AmazonECSTaskExecutionRolePolicy`.
   - Click `Add permissions` and then `Create inline policy`. In the `Policy editor`, select `JSON`. Remove all JSON content in the editor.
   - Copy and paste the following policy, which enables the role to read secrets, into the editor. Change `<your secret ARN here>` to the secret ARN obtained earlier. Then click `Next`.
      ```json
         {
         "Version": "2012-10-17",
         "Statement": [
            {
               "Effect": "Allow",
               "Action": [
                  "secretsmanager:GetSecretValue"
               ],
               "Resource": [
                  "<your secret ARN here>"
               ]
            }
         ]
      } 

      ```
   - Give the policy a name, e.g., `SecretAccess`, and click `Create policy`.
   - Your ECS task execution role is now with the permission to read environment variables from the Secret Manager.

  
#### Create a Service to deploy and run the task
   - Under `Cluster`, click on the cluster you have created earlier.
   - Under `Services`, click `Create`.
   - Under `Compute configuration`, select `Launch type`. Leave the `Launch type` as `FARGATE`, and `Platform version` as `LATEST`.
   - Under `Deployment configuration`, select `Service`.
   - Under `Task definition`, `Family`, select the task you have created earlier. Choose the latest `Revision`.
   - Provide a service name, e.g., `bookservice`. 
   - Under `Deployment options`, choose `Rolling update`. Leave the rest as default.
   - Under `Networking`, leave the default VPC, subnets, and security group. Default subnets, security groups, along with the default VPC, etc., are designed to help you get started quickly with AWS services without having to configure networking components from scratch. Ensure that `Public IP` is turned on so that Internet users can access your service.
   - Leave the rest of the options as default. Click `Create`. The newly created service will run the task automatically, which may take a while to be ready.

#### Check the running app
   - Click on your cluster, and on the service name.
   - Click on the tab `Tasks`. You should see the task running. Click on the task ID.
   - Click on the tab `Networking` under the task ID. You should see the public IP address. Copy it for the next step.
   - Enter the URL in the form of `<public ID address>:8000/docs` into a web browser. You should see the Swagger UI docs of your app.
   - Congratulations! Your app is now deployed and visible publicly to anyone on the Internet.

#### Tear down the ECS cluster
   - You can stop the task when you're done to avoid being charged for ECS usage.
   - You can also delete the service and cluster to avoid further charges.
