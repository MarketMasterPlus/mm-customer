// mm-customer/pact/tests/providerPactVerification.spec.js
import { Verifier } from '@pact-foundation/pact';
import dotenv from 'dotenv';
import { getCurrentGitBranch } from '../utils/git.js';

dotenv.config();

// Use this function in your Pact setup
describe('Pact Verification for mm-customer', () => {
    it('should validate the expectations of mm-shopping-cart', async () => {
      const currentBranch = getCurrentGitBranch();
      const opts = {
        provider: 'mm-customer',
        providerBaseUrl: process.env.PACT_PROVIDER_BASE_URL,
        pactBrokerUrl: process.env.PACT_BROKER_URL,
        pactBrokerUsername: process.env.PACT_BROKER_USERNAME,
        pactBrokerPassword: process.env.PACT_BROKER_PASSWORD,
        publishVerificationResult: true,
        providerVersion: process.env.APP_VERSION,
        providerVersionBranch: currentBranch, // Dynamically set to current Git branch
        consumerVersionSelectors: [{ latest: true }],
        enablePending: true,
        stateHandlers: {
          'it has customer details': async () => {
            console.log('Setting up customer state for inventory item details');
            // Setup your state here
          },
        },
        requestFilter: (req, res, next) => {
          console.log(`Request to provider: ${req.method} ${req.path}`);
          next();
        },
        logLevel: 'INFO',
      };
  
      try {
        const verifier = new Verifier(opts);
        const output = await verifier.verifyProvider();
        console.log('Pact Verification Complete!');
        console.log(output);
      } catch (err) {
        console.error('Pact Verification Failed:', err);
        throw err;
      }
    });
  });