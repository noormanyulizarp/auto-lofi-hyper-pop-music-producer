const nextJest = require('next/jest')

const createJestConfig = (nextConfig = {}) => {
  const jestConfig = {
    ...nextConfig,
    moduleDirectories: ['node_modules', '<rootDir>/'],
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
    moduleNameMapping: {
      '^@/(.*)$': '<rootDir>/src/$1',
    },
    collectCoverageFrom: [
      'src/**/*.{js,jsx,ts,tsx}',
      '!src/**/*.d.ts',
      '!src/main.tsx',
      '!src/vite-env.d.ts',
    ],
    coveragePathIgnorePatterns: [
      '/node_modules/',
      '/.vite/',
      '/dist/',
    ],
  }

  return jestConfig
}

// createJestConfig is exported this way to ensure that next/jest can load the Jest configuration asynchronously
module.exports = createJestConfig()