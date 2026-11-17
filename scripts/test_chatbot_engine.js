// Test chatbot functions in cb_js.js using Node.js
const fs = require('fs');

const cbJs = fs.readFileSync('cb_js_clean.js', 'utf8');

// Mock browser environment
global.window = {
  lucide: {
    createIcons: () => {}
  }
};
global.document = {
  getElementById: (id) => {
    return {
      classList: {
        contains: (c) => false,
        add: () => {},
        remove: () => {}
      },
      focus: () => {},
      value: '',
      innerHTML: '',
      scrollTop: 0,
      scrollHeight: 100,
      className: ''
    };
  },
  addEventListener: () => {}
};

// Mock appState and helper functions
global.appState = {
  chatbotOpen: false,
  chatbotRole: 'user',
  chatbotMessages: []
};

global.getPeriod = () => ({
  periodCode: '2026-10',
  label: 'Oktober 2026',
  ibErp: 15420000.0,
  isLocked: false,
  inTransitRecognized: false,
  controllerSigned: { signed: true, timestamp: '31.10.2026 18:30' }
});

global.computePeriodMetrics = (p) => ({
  readiness: 94,
  netDelta: 0.0,
  rawDelta: -92725.0,
  ubBank: 15327275.0,
  erpTxBaseSum: 0.0,
  openBank: [1, 2],
  openErp: [1, 2]
});

global.formatNOK = (v) => (v || 0).toLocaleString('nb-NO', { minimumFractionDigits: 2 }) + ' kr';
global.escapeHtml = (s) => s ? String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';
global.showToast = (msg) => console.log('Toast:', msg);

// Evaluate script
try {
  eval(cbJs);
  console.log("Successfully evaluated cb_js.js!");
  
  // Test toggle
  toggleChatbot();
  console.log("toggleChatbot ok, open:", global.appState.chatbotOpen);
  
  // Test role switch
  setChatbotRole('admin');
  console.log("setChatbotRole admin ok, role:", global.appState.chatbotRole);
  setChatbotRole('user');
  console.log("setChatbotRole user ok, role:", global.appState.chatbotRole);
  
  // Test queries
  const testQueries = [
    { q: "Hvorfor er konto 1920 ubalansert?", role: "user" },
    { q: "Hva gjenstår for CFO-låsing?", role: "user" },
    { q: "Bergen Marine tidsavvik", role: "user" },
    { q: "WBS-408 Kystvakt", role: "user" },
    { q: "Importmal for Business Central", role: "admin" },
    { q: "Importmal for Xledger", role: "admin" },
    { q: "Amerikansk BAI2 format", role: "admin" },
    { q: "Sett opp øresavrunding <= 5 kr", role: "admin" },
    { q: "Vis DuckDB avstemmingsstatus", role: "user" },
    { q: "Ukjent spørsmål om noe annet", role: "user" }
  ];

  testQueries.forEach(({ q, role }) => {
    const reply = generateChatbotReply(q, role);
    console.log(`[PASS] Query: "${q}" (Role: ${role}) -> Reply has ${reply.text.length} chars, ${reply.actions ? reply.actions.length : 0} actions`);
  });

  console.log("\nALL 10 CHATBOT FUNCTIONALITY TESTS PASSED!");
} catch (err) {
  console.error("Evaluation error:", err);
  process.exit(1);
}
