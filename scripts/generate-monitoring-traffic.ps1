$BaseUrl = $env:APP_URL
if (-not $BaseUrl) {
    $BaseUrl = "http://localhost:8001"
}

$suffix = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

$user = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/users/" `
    -ContentType "application/json" `
    -Body (@{
        name = "Monitoring User"
        email = "monitoring-$suffix@example.com"
        password = "secret123"
        age = 21
    } | ConvertTo-Json)

$category = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/products/categories/" `
    -ContentType "application/json" `
    -Body (@{
        name = "Monitoring Category $suffix"
        description = "Category for Prometheus custom metrics"
    } | ConvertTo-Json)

$product = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/products/" `
    -ContentType "application/json" `
    -Body (@{
        name = "Monitoring Product $suffix"
        description = "Product for Grafana screenshots"
        price = "42.50"
        stock = 10
        category_id = $category.id
    } | ConvertTo-Json)

Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/api/v1/products/orders/" `
    -ContentType "application/json" `
    -Body (@{
        user_id = $user.id
        status = "new"
        items = @(
            @{
                product_id = $product.id
                quantity = 2
            }
        )
    } | ConvertTo-Json -Depth 4)

1..20 | ForEach-Object {
    Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/products/" | Out-Null
    Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/users/" | Out-Null
    Invoke-RestMethod -Method Get -Uri "$BaseUrl/metrics" | Out-Null
}

Write-Host "Monitoring traffic generated. Check Grafana and Prometheus for FastAPI and custom shop metrics."