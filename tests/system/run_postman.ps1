$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$collection = Join-Path $projectRoot "postman\CareerFlow.postman_collection.json"
$environment = Join-Path $projectRoot "postman\CareerFlow.postman_environment.json"
$results = Join-Path $PSScriptRoot "postman-results.xml"

npx --yes newman run $collection `
    --environment $environment `
    --reporters cli,junit `
    --reporter-junit-export $results
