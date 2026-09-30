SKILLS = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Scala", "R",
        "C", "C++", "C#", "Rust", "Kotlin", "Swift", "Ruby", "PHP",
        "MATLAB", "Julia", "Bash", "Shell", "Perl", "Haskell",
    ],
    "web_frontend": [
        "React", "Angular", "Vue.js", "Next.js", "Svelte", "HTML", "CSS",
        "SASS", "LESS", "Tailwind CSS", "Bootstrap", "jQuery", "Redux",
        "GraphQL", "REST", "WebSockets", "Webpack", "Vite",
    ],
    "web_backend": [
        "Node.js", "Django", "Flask", "FastAPI", "Spring Boot", "Express.js",
        "NestJS", "Ruby on Rails", "Laravel", "ASP.NET", "Gin", "Echo",
        "gRPC", "Celery", "Gunicorn",
    ],
    "data_and_ml": [
        "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
        "XGBoost", "LightGBM", "CatBoost", "Matplotlib", "Seaborn", "Plotly",
        "NLTK", "spaCy", "Hugging Face", "OpenCV", "SciPy", "Statsmodels",
        "Langchain", "LangGraph", "LlamaIndex",
    ],
    "big_data": [
        "Apache Spark", "Kafka", "Airflow", "dbt", "Hadoop", "Flink",
        "Hive", "Presto", "Trino", "Databricks", "Delta Lake",
        "Apache Beam", "NiFi", "Luigi",
    ],
    "mlops": [
        "MLflow", "Kubeflow", "DVC", "Weights & Biases", "Neptune",
        "Seldon", "BentoML", "Feast", "Great Expectations",
    ],
    "cloud": [
        "AWS", "Azure", "GCP", "EC2", "S3", "Lambda", "RDS", "EMR",
        "Glue", "Redshift", "Athena", "SageMaker", "EKS", "ECS",
        "CloudFormation", "Azure DevOps", "Azure ML", "BigQuery",
        "Cloud Run", "Cloud Functions", "Vertex AI", "GKE",
    ],
    "devops": [
        "Docker", "Kubernetes", "Terraform", "Jenkins", "GitHub Actions",
        "GitLab CI", "Ansible", "Helm", "ArgoCD", "CircleCI", "Travis CI",
        "Prometheus", "Grafana", "ELK Stack", "Datadog", "New Relic",
    ],
    "databases": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra",
        "DynamoDB", "Elasticsearch", "Neo4j", "Snowflake", "BigQuery",
        "Oracle", "SQL Server", "ClickHouse", "CockroachDB",
    ],
    "version_control": [
        "Git", "GitHub", "GitLab", "Bitbucket", "SVN",
    ],
}

# Flat list used for matching
ALL_SKILLS = sorted({skill for category in SKILLS.values() for skill in category})
