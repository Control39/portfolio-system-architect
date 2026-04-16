import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Мок для electron
jest.mock('electron', () => ({
  ipcRenderer: {
    invoke: jest.fn(),
    on: jest.fn()
  }
}));

describe('Renderer Components', () => {
  test('placeholder - add actual tests', () => {
    expect(true).toBe(true);
  });
});
