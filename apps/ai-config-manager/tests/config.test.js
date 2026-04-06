const fs = require('fs-extra');
const path = require('path');
const yaml = require('js-yaml');

describe('AI Config Tests', () => {
  // Правильный путь к корневому .ai-config/
  const configPath = path.join(__dirname, '../../../.ai-config/master-config.yaml');
  
  test('master-config.yaml exists', () => {
    expect(fs.existsSync(configPath)).toBe(true);
  });
  
  test('master-config.yaml is valid YAML', () => {
    expect(() => {
      yaml.load(fs.readFileSync(configPath, 'utf8'));
    }).not.toThrow();
  });
  
  test('config has models', () => {
    const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
    expect(config.models.length).toBeGreaterThan(0);
  });
  
  test('each model has required fields', () => {
    const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
    
    config.models.forEach(model => {
      expect(model).toHaveProperty('id');
      expect(model).toHaveProperty('name');
      expect(model).toHaveProperty('provider');
      expect(model.provider).toHaveProperty('type');
      expect(model).toHaveProperty('capabilities');
    });
  });
  
  test('ollama models have correct format', () => {
    const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
    
    config.models
      .filter(m => m.provider.type === 'ollama')
      .forEach(model => {
        expect(model.provider).toHaveProperty('baseUrl');
        expect(model.provider.baseUrl).toMatch(/^http:\/\/localhost/);
      });
  });
});