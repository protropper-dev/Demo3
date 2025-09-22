// Debug script để kiểm tra chat data flow
// Chạy trong browser console hoặc node

const testChatDataFlow = async () => {
  console.log('🔍 Testing Chat Data Flow...');
  
  try {
    // 1. Test chats endpoint
    const chatsResponse = await fetch('http://localhost:8000/api/v1/rag/chats?page=1&per_page=5');
    
    if (chatsResponse.ok) {
      const chatsData = await chatsResponse.json();
      console.log('✅ Chats API response:', chatsData);
      
      const chats = chatsData.chats || [];
      console.log(`📊 Found ${chats.length} chats`);
      
      if (chats.length > 0) {
        const firstChat = chats[0];
        console.log('🔍 First chat raw data:', firstChat);
        
        // Simulate formatChatsForUI
        const userMessages = firstChat.stats?.message_stats?.user || 0;
        const assistantMessages = firstChat.stats?.message_stats?.assistant || 0;
        const messageCount = userMessages + assistantMessages;
        
        const formattedChat = {
          id: firstChat.id,
          title: firstChat.title,
          messageCount: messageCount,
          sourcesUsed: firstChat.stats?.sources_used || 0,
          avgConfidence: firstChat.stats?.avg_confidence || 0
        };
        
        console.log('✅ Formatted chat:', formattedChat);
        
        // Test messages endpoint
        if (formattedChat.id) {
          console.log(`🔍 Testing messages for chat ${formattedChat.id}...`);
          
          const messagesResponse = await fetch(`http://localhost:8000/api/v1/rag/chats/${formattedChat.id}/messages?page=1&per_page=10`);
          
          if (messagesResponse.ok) {
            const messagesData = await messagesResponse.json();
            console.log('✅ Messages API response:', messagesData);
            console.log(`📝 Found ${messagesData.messages?.length || 0} messages`);
          } else {
            console.log('❌ Messages API failed:', messagesResponse.status, await messagesResponse.text());
          }
        }
      }
      
    } else {
      console.log('❌ Chats API failed:', chatsResponse.status, await chatsResponse.text());
    }
    
  } catch (error) {
    console.error('❌ Test error:', error);
  }
};

// Export for browser use
if (typeof window !== 'undefined') {
  window.testChatDataFlow = testChatDataFlow;
}

// Run if in node
if (typeof window === 'undefined') {
  testChatDataFlow();
}
