# Remove __pycache__ directories recursively
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Remove everything from instance/ directory
rm -rf instance/*

# Remove everything from uploads/* directories
rm -rf uploads/*/