// Test script để kiểm tra kết nối giữa Frontend1 và Backend1
// Chạy: node test-connection.js

const API_URL = 'http://localhost:8000';

async function testConnection() {
  console.log('🧪 Testing connection between Frontend1 and Backend1...\n');
  
  const tests = [
    {
      name: 'Root Health Check',
      url: `${API_URL}/`,
      method: 'GET'
    },
    {
      name: 'Basic Health Check',
      url: `${API_URL}/api/v1/health/`,
      method: 'GET'
    },
    {
      name: 'Detailed Health Check',
      url: `${API_URL}/api/v1/health/detailed`,
      method: 'GET'
    },
    {
      name: 'Readiness Check',
      url: `${API_URL}/api/v1/health/ready`,
      method: 'GET'
    },
    {
      name: 'Liveness Check',
      url: `${API_URL}/api/v1/health/live`,
      method: 'GET'
    },
    {
      name: 'Chatbot Health',
      url: `${API_URL}/api/v1/chatbot/health`,
      method: 'GET'
    },
    {
      name: 'Enhanced Status',
      url: `${API_URL}/api/v1/chatbot/status/enhanced`,
      method: 'GET'
    },
    {
      name: 'Device Info',
      url: `${API_URL}/api/v1/chatbot/device/enhanced`,
      method: 'GET'
    },
    {
      name: 'Categories',
      url: `${API_URL}/api/v1/chatbot/categories`,
      method: 'GET'
    }
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    try {
      console.log(`Testing: ${test.name}`);
      console.log(`URL: ${test.url}`);
      
      const response = await fetch(test.url, {
        method: test.method,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ PASSED (${response.status})`);
        console.log(`Response:`, JSON.stringify(data, null, 2));
        passed++;
      } else {
        console.log(`❌ FAILED (${response.status})`);
        console.log(`Error: ${response.statusText}`);
        failed++;
      }
    } catch (error) {
      console.log(`❌ ERROR: ${error.message}`);
      failed++;
    }
    
    console.log('---\n');
  }

  console.log('📊 Test Results:');
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`📈 Success Rate: ${((passed / (passed + failed)) * 100).toFixed(1)}%`);

  if (failed === 0) {
    console.log('\n🎉 All tests passed! Frontend1 can connect to Backend1 successfully.');
  } else {
    console.log('\n⚠️  Some tests failed. Please check Backend1 is running and accessible.');
  }
}

async function testChatFunctionality() {
  console.log('\n🤖 Testing Chat Functionality...\n');
  
  try {
    // Test basic chat
    console.log('Testing Basic Chat...');
    const chatResponse = await fetch(`${API_URL}/api/v1/chatbot/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: 'Xin chào, bạn có thể giúp tôi không?',
        chat_history: null,
        filter_category: null
      })
    });

    if (chatResponse.ok) {
      const chatData = await chatResponse.json();
      console.log('✅ Basic Chat Test Passed');
      console.log('Response:', chatData.response);
      console.log('Sources:', chatData.sources?.length || 0);
    } else {
      console.log('❌ Basic Chat Test Failed:', chatResponse.status);
    }

    // Test enhanced chat
    console.log('\nTesting Enhanced Chat...');
    const enhancedResponse = await fetch(`${API_URL}/api/v1/chatbot/enhanced`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: 'Hãy giải thích về an toàn thông tin',
        max_tokens: 256,
        temperature: 0.7,
        top_k: 50,
        top_p: 0.95
      })
    });

    if (enhancedResponse.ok) {
      const enhancedData = await enhancedResponse.json();
      console.log('✅ Enhanced Chat Test Passed');
      console.log('Response:', enhancedData.response);
      console.log('Status:', enhancedData.status);
    } else {
      console.log('❌ Enhanced Chat Test Failed:', enhancedResponse.status);
    }

  } catch (error) {
    console.log('❌ Chat Test Error:', error.message);
  }
}

// Run tests
async function runAllTests() {
  await testConnection();
  await testChatFunctionality();
  
  console.log('\n🏁 Test completed!');
  console.log('\n📋 Next Steps:');
  console.log('1. Start Frontend1: npm run dev');
  console.log('2. Open http://localhost:5173');
  console.log('3. Check Connection Status panel');
  console.log('4. Try sending a message in the chat');
}

runAllTests().catch(console.error);
