const fs = require('fs-extra');
const path = require('path');

class AzureAdapter {
  constructor(config) {
    this.config = config;
    this.endpoint = process.env.AZURE_ENDPOINT;
    this.apiKey = process.env.AZURE_API_KEY;
  }

  async testConnection() {
    try {
      const response = await fetch(`${this.endpoint}/health`, {
        headers: { 'api-key': this.apiKey }
      });
      return { success: response.ok, status: response.status };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async generateConfig() {
    const config = {
      version: "1.0",
      provider: "azure",
      endpoint: this.endpoint,
      services: {
        textAnalytics: { enabled: true },
        speechToText: { enabled: false },
        translator: { enabled: true }
      }
    };

    const configPath = path.join(__dirname, '../../.azure-config.json');
    await fs.writeJson(configPath, config, { spaces: 2 });
    return config;
  }
}

module.exports = AzureAdapter;
