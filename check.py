from app.backend.reporting.azurewiki.azureport import azureport

az = azureport("default", "demo")

az.generateReport("R014")