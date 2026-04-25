const fs = require('fs-extra');
const path = require('path');
const https = require('https');

class HuggingFaceAdapter {
  constructor(config) {
    this.config = config;
    this.apiKey = process.env.HUGGINGFACE_API_KEY;
  }

  async getAvailableModels() {
    return new Promise((resolve, reject) => {
      https.get('https://huggingface.co/api/models?sort=downloads&limit=20', {
        headers: { 'Authorization': `Bearer ${this.apiKey}` }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data).map(m => ({
              id: m.modelId,
              name: m.modelId.split('/')[1] || m.modelId,
              downloads: m.downloads
            })));
          } catch (e) { reject(e); }
        });
      }).on('error', reject);
    });
  }

  async generateConfig() {
    const models = await this.getAvailableModels();
    const config = {
      version: "1.0",
      provider: "huggingface",
      models: models.slice(0, 10)
    };
    await fs.writeJson(path.join(__dirname, '../../.hf-config.json'), config, { spaces: 2 });
    return config;
  }
}

module.exports = HuggingFaceAdapter;
