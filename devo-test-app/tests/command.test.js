const { test, expect } = require('@jest/globals');

// Mock fetch for testing
global.fetch = jest.fn();

// Test cases that simulate different scenarios
describe('TestDevoApp Command Tests', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('should pass with normal command', async () => {
    // Simulate successful response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        message: 'Command processed successfully',
        type: 'success',
        command: 'hello'
      })
    });

    const response = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'hello' })
    });

    const data = await response.json();
    expect(response.ok).toBe(true);
    expect(data.type).toBe('success');
    console.log('✅ Normal command test passed');
  });

  test('should show warning with warn command', async () => {
    // Simulate warning response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        message: 'Command processed with warning',
        type: 'warning',
        command: 'warn'
      })
    });

    const response = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'warn' })
    });

    const data = await response.json();
    expect(response.ok).toBe(true);
    expect(data.type).toBe('warning');
    console.warn('⚠️  Warning command test - this should show in CI logs');
  });

  test('should fail with fail command', async () => {
    // Check for INTENTIONAL_FAIL environment variable to control test behavior
    if (process.env.INTENTIONAL_FAIL === 'true') {
      console.error('❌ INTENTIONAL FAILURE: This test is designed to fail for CI/CD testing');
      throw new Error('Intentional test failure for Devo CI/CD pipeline testing');
    }

    // Simulate error response
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({
        error: 'Intentional failure triggered for CI/CD testing'
      })
    });

    const response = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'fail' })
    });

    expect(response.ok).toBe(false);
    expect(response.status).toBe(500);
    console.log('✅ Fail command test completed (controlled failure)');
  });

  test('should validate input requirements', async () => {
    // Test empty command
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        error: 'Command is required'
      })
    });

    const response = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: '' })
    });

    expect(response.ok).toBe(false);
    expect(response.status).toBe(400);
    console.log('✅ Input validation test passed');
  });
});

// Simulate different test scenarios based on environment
describe('Environment-based Tests', () => {
  test('CI Environment Detection', () => {
    const isCI = process.env.CI === 'true';
    console.log(`🔍 Running in CI environment: ${isCI}`);
    
    if (isCI) {
      console.log('📊 CI-specific logging for Devo collection');
      console.log('🏗️  Build environment detected');
    }
    
    expect(true).toBe(true); // Always pass
  });

  test('Trigger Failure Based on Input', () => {
    // This test will fail if the TRIGGER_FAIL env var is set
    // This allows us to control failures from GitHub Actions
    const shouldFail = process.env.TRIGGER_FAIL === 'true';
    
    if (shouldFail) {
      console.error('❌ TRIGGERED FAILURE: Environment variable TRIGGER_FAIL is set to true');
      console.error('🔧 This failure is intentional for testing Devo log collection');
      throw new Error('Environment-triggered test failure for CI/CD pipeline');
    }
    
    console.log('✅ No failure trigger detected');
    expect(true).toBe(true);
  });
});
