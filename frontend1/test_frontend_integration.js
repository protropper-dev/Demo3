// Test script để kiểm tra frontend integration
// Chạy: node test_frontend_integration.js

const testEndpoints = async () => {
  console.log('🧪 Testing Frontend Integration...');
  
  const endpoints = [
    'http://localhost:8000/api/v1/health/',
    'http://localhost:8000/api/v1/rag/health',
    'http://localhost:8000/api/v1/rag/files/uploaded',
    'http://localhost:8000/api/v1/rag/chats'
  ];

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(endpoint, { 
        method: 'GET',
        timeout: 5000 
      });
      
      console.log(`${response.ok ? '✅' : '❌'} ${endpoint} - ${response.status}`);
      
      if (response.ok && endpoint.includes('/files/uploaded')) {
        const data = await response.json();
        console.log(`   📁 Files: ${data.total || 0}`);
      }
      
    } catch (error) {
      console.log(`❌ ${endpoint} - Error: ${error.message}`);
    }
  }

  // Test chat API
  console.log('\n🤖 Testing Chat API...');
  try {
    const chatResponse = await fetch('http://localhost:8000/api/v1/rag/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: 'An toàn thông tin là gì?',
        user_id: 1,
        top_k: 3
      })
    });

    if (chatResponse.ok) {
      const data = await chatResponse.json();
      console.log('✅ Chat API working!');
      console.log(`   📊 Sources: ${data.total_sources}`);
      console.log(`   🎯 Confidence: ${data.confidence?.toFixed(3)}`);
      console.log(`   💬 Chat ID: ${data.chat_id}`);
    } else {
      console.log(`❌ Chat API failed: ${chatResponse.status}`);
    }
    
  } catch (error) {
    console.log(`❌ Chat API error: ${error.message}`);
  }
};

// Run test
testEndpoints().catch(console.error);
