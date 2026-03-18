# OmniscientAI Google Cloud Deployment Script

echo "Checking gcloud authentication..."
try {
    $token = gcloud auth print-access-token --quiet
}
catch {
    $token = $null
}

if (-not $token) {
    echo "Authentication expired or missing. Initiating gcloud login..."
    gcloud auth login
}

echo "Building application..."
pnpm install
pnpm run build

echo "Deploying to Google App Engine..."
gcloud app deploy app.yaml --project=omniscientai --promote --quiet

echo "Deployment complete! Visit your Google Cloud Console to map omniscientai.io"
