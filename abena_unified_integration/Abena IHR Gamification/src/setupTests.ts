// Mock the service worker
const mockServiceWorker = {
  register: jest.fn().mockResolvedValue({
    active: {
      dispatchEvent: jest.fn(),
    },
    showNotification: jest.fn(),
    unregister: jest.fn(),
  }),
  ready: Promise.resolve(),
};

// Mock the cache API
const mockCache = {
  open: jest.fn().mockResolvedValue({
    keys: jest.fn().mockResolvedValue([
      { url: '/index.html' },
      { url: '/offline.html' },
    ]),
    match: jest.fn().mockResolvedValue(new Response()),
    put: jest.fn(),
  }),
};

// Mock the fetch API
const mockFetch = jest.fn().mockResolvedValue(new Response());

// Mock the Clients API
const mockClients = {
  matchAll: jest.fn().mockResolvedValue([
    {
      focused: true,
      focus: jest.fn(),
    },
  ]),
  openWindow: jest.fn(),
};

// Add mocks to the global object
Object.defineProperty(window, 'navigator', {
  value: {
    serviceWorker: mockServiceWorker,
  },
});

Object.defineProperty(window, 'caches', {
  value: mockCache,
});

Object.defineProperty(window, 'fetch', {
  value: mockFetch,
});

Object.defineProperty(window, 'clients', {
  value: mockClients,
});

// Mock the service worker global scope
const mockSelf = {
  registration: {
    showNotification: jest.fn(),
  },
  clients: mockClients,
};

// Add self to global scope
Object.defineProperty(global, 'self', {
  value: mockSelf,
});

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
}); 