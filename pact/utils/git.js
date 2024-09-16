// mm-inventory/pact/utils/git.js

import { execSync } from 'child_process';

export const getCurrentGitBranch = () => {
    try {
        const branch = execSync('git rev-parse --abbrev-ref HEAD').toString().trim();
        return branch;
      } catch (error) {
        console.error('Failed to fetch Git branch:', error);
        return 'unknown';  // Return a default or handle the error appropriately
      }
}
