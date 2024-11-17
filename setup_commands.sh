#!/bin/bash

# Create main directory structure
mkdir -p src/{app/{routes},models,services,chains,tools,utils,tests}

# Create files in app directory
touch src/app/__init__.py
touch src/app/config.py
touch src/app/main.py

# Create route files
touch src/app/routes/__init__.py
touch src/app/routes/auth.py
touch src/app/routes/data.py
touch src/app/routes/analysis.py
touch src/app/routes/reports.py

# Create model files
touch src/models/__init__.py
touch src/models/user.py
touch src/models/data_source.py
touch src/models/analysis.py
touch src/models/report.py
touch src/models/policy.py

# Create service files
touch src/services/__init__.py
touch src/services/gemini_service.py
touch src/services/data_service.py
touch src/services/cache_service.py

# Create chain files
touch src/chains/__init__.py
touch src/chains/analysis_chain.py
touch src/chains/policy_chain.py

# Create tool files
touch src/tools/__init__.py
touch src/tools/unicef_tool.py
touch src/tools/who_tool.py
touch src/tools/worldbank_tool.py

# Create utils files
touch src/utils/__init__.py
touch src/utils/validators.py
touch src/utils/helpers.py

# Create test files
touch src/tests/__init__.py
touch src/tests/test_routes.py
touch src/tests/test_models.py
touch src/tests/test_chains.py 