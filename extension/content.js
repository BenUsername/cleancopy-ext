let currentSessionId = crypto.randomUUID()

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    const nodes = Array.from(mutation.addedNodes)
    for (const node of nodes) {
      if (node.classList?.contains('group')) {
        const role = node.classList.contains('w-full') ? 'assistant' : 'user'
        const content = node.textContent.trim()
        
        sendMessage({
          session_id: currentSessionId,
          role,
          content,
          timestamp: new Date().toISOString()
        })
      }
    }
  }
})

observer.observe(document.body, {
  childList: true,
  subtree: true
})

async function sendMessage(data) {
  try {
    const response = await fetch(
      'https://your-app-name.ondigitalocean.app/api/chat',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api-key': 'chatgpt-history-2024'
        },
        body: JSON.stringify(data)
      }
    )
    if (!response.ok) throw new Error('Failed to send message')
  } catch (error) {
    console.error('Error sending message:', error)
  }
}

function addCopyCleanButton() {
  const targetNodes = document.querySelectorAll('.group.w-full')
  targetNodes.forEach(node => {
    if (!node.querySelector('.copy-clean-btn')) {
      const copyBtn = node.querySelector('button[aria-label="Copy message"]')
      if (copyBtn) {
        const cleanBtn = copyBtn.cloneNode(true)
        cleanBtn.classList.add('copy-clean-btn')
        cleanBtn.setAttribute('aria-label', 'Copy clean message')
        cleanBtn.onclick = () => copyCleanMessage(node)
        copyBtn.parentNode.insertBefore(cleanBtn, copyBtn.nextSibling)
      }
    }
  })
}

function copyCleanMessage(node) {
  const text = node.textContent.trim()
  navigator.clipboard.writeText(text)
}

document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'c') {
    const selectedNode = window.getSelection().anchorNode?.closest('.group.w-full')
    if (selectedNode) {
      e.preventDefault()
      copyCleanMessage(selectedNode)
    }
  }
})

setInterval(addCopyCleanButton, 1000) 