/**
 * Vitest setup for React client tests.
 *
 * Wires jest-dom matchers (`toBeInTheDocument`, `toHaveClass`, etc.) and
 * cleans up rendered DOM after each test. Referenced from vitest.config.ts.
 */

import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
