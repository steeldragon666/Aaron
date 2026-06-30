/**
 * Smoke tests for IndustryRedirect — verifies legacy /industries/:slug
 * deep links redirect to the matching /services/:slug path (or fall
 * through to /services when the slug doesn't map cleanly).
 *
 * Uses wouter's memoryLocation in mutable mode so navigate() calls actually
 * flip the location and we can observe the final path.
 */

import { render, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Route, Router, Switch } from 'wouter';
import { memoryLocation } from 'wouter/memory-location';
import IndustryRedirect from './IndustryRedirect';

function renderAt(path: string) {
  const { hook, history } = memoryLocation({ path, record: true });
  const utils = render(
    <Router hook={hook}>
      <Switch>
        <Route path="/industries/:slug" component={IndustryRedirect} />
        <Route path="/industries" component={IndustryRedirect} />
      </Switch>
    </Router>,
  );
  return { ...utils, history };
}

describe('IndustryRedirect', () => {
  it('maps /industries/healthcare to /services/mental-health', async () => {
    const { history } = renderAt('/industries/healthcare');
    await waitFor(() => {
      expect(history[history.length - 1]).toBe('/services/mental-health');
    });
  });

  it('falls through to /services for an unmapped slug', async () => {
    const { history } = renderAt('/industries/manufacturing');
    await waitFor(() => {
      expect(history[history.length - 1]).toBe('/services');
    });
  });

  it('falls through to /services for a slug that never existed', async () => {
    const { history } = renderAt('/industries/does-not-exist');
    await waitFor(() => {
      expect(history[history.length - 1]).toBe('/services');
    });
  });
});
