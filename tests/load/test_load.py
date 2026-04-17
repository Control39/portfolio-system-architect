from locust import HttpUser, task, between
import random
import string

class PortfolioSystemUser(HttpUser):
    """
    Load test for Portfolio System Architect API
    Simulates realistic user behavior across different components
    """
    
    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)
    
    # Base URLs for different services
    host = "http://localhost:8000"  # API Gateway
    
    def on_start(self):
        """
        Executed when a user starts
        """
        # Authenticate user
        self.login()
    
    def login(self):
        """
        Simulate user login
        """
        try:
            response = self.client.post(
                "/auth/login",
                json={
                    "username": "testuser",
                    "password": "testpass"
                }
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
        except Exception as e:
            print(f"Login failed: {e}")
    
    @task(3)
    def get_arch_compass_analysis(self):
        """
        Task: Get architectural analysis
        Weight: 3 (frequent)
        """
        try:
            response = self.client.get(
                "/arch-compass/analyze",
                headers=self.headers,
                params={
                    "project_type": random.choice(["microservice", "monolith", "serverless"])
                }
            )
            if response.status_code != 200:
                print(f"GET /arch-compass/analyze failed: {response.status_code}")
        except Exception as e:
            print(f"GET /arch-compass/analyze exception: {e}")
    
    @task(2)
    def get_cloud_reasoning(self):
        """
        Task: Get cloud reasoning response
        Weight: 2 (common)
        """
        try:
            response = self.client.post(
                "/cloud-reason/reason",
                headers=self.headers,
                json={
                    "prompt": "How to design a scalable microservice architecture?",
                    "context": "cloud_infrastructure"
                }
            )
            if response.status_code != 200:
                print(f"POST /cloud-reason/reason failed: {response.status_code}")
        except Exception as e:
            print(f"POST /cloud-reason/reason exception: {e}")
    
    @task(1)
    def get_it_compass_skills(self):
        """
        Task: Get IT skills assessment
        Weight: 1 (less frequent)
        """
        try:
            response = self.client.get(
                "/it-compass/skills",
                headers=self.headers,
                params={
                    "domain": random.choice(["ai", "cloud", "security", "devops"])
                }
            )
            if response.status_code != 200:
                print(f"GET /it-compass/skills failed: {response.status_code}")
        except Exception as e:
            print(f"GET /it-compass/skills exception: {e}")
    
    @task(1)
    def create_portfolio_project(self):
        """
        Task: Create a new portfolio project
        Weight: 1 (less frequent)
        """
        try:
            # Generate random project name
            project_name = "project_" + "".join(random.choices(string.ascii_lowercase, k=8))
            
            response = self.client.post(
                "/portfolio-organizer/projects",
                headers=self.headers,
                json={
                    "name": project_name,
                    "description": f"Automated test project {project_name}",
                    "tags": random.sample(["ai", "cloud", "security", "devops", "ml", "data"], k=3)
                }
            )
            if response.status_code != 201:
                print(f"POST /portfolio-organizer/projects failed: {response.status_code}")
        except Exception as e:
            print(f"POST /portfolio-organizer/projects exception: {e}")
    
    @task(2)
    def get_ml_model_registry(self):
        """
        Task: Get ML model registry entries
        Weight: 2 (common)
        """
        try:
            response = self.client.get(
                "/ml-model-registry/models",
                headers=self.headers,
                params={
                    "status": random.choice(["active", "deprecated", "experimental"])
                }
            )
            if response.status_code != 200:
                print(f"GET /ml-model-registry/models failed: {response.status_code}")
        except Exception as e:
            print(f"GET /ml-model-registry/models exception: {e}")
    
    @task(1)
    def get_career_development_plan(self):
        """
        Task: Get career development plan
        Weight: 1 (less frequent)
        """
        try:
            response = self.client.get(
                "/career-development/plan",
                headers=self.headers,
                params={
                    "level": random.choice(["junior", "middle", "senior", "lead"])
                }
            )
            if response.status_code != 200:
                print(f"GET /career-development/plan failed: {response.status_code}")
        except Exception as e:
            print(f"GET /career-development/plan exception: {e}")

# Configuration for locust
# This can be overridden by command line arguments
class Config:
    HOST = "http://localhost:8000"
    USERS = 100  # Number of simulated users
    SPAWN_RATE = 10  # Users spawned per second
    RUN_TIME = "1h"  # Duration of the test

# To run this test:
# locust -f tests/load/test_load.py --host=http://localhost:8000 -u 100 -r 10 --run-time=1h --headless
# 
# Or with web interface:
# locust -f tests/load/test_load.py --host=http://localhost:8000
