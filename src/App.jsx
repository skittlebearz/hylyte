import { useState } from 'react'
import './App.css'

function App() {
  const [videoUrl, setVideoUrl] = useState('')
  const [userPrompt, setUserPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setResponse(null)

    try {
      const response = await fetch('http://localhost:5000/api/highlight-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: videoUrl,
          prompt: userPrompt || undefined // Only send if not empty
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResponse(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>Video Hylyte Generator</h1>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label htmlFor="videoUrl">Video URL:</label>
          <input
            type="url"
            id="videoUrl"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            placeholder="Enter video URL here..."
            required
            className="input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="userPrompt">User Prompt (optional):</label>
          <textarea
            id="userPrompt"
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="Enter your prompt here..."
            rows="4"
            className="textarea"
          />
        </div>

        <button 
          type="submit" 
          disabled={isLoading || !videoUrl.trim()}
          className="submit-button"
        >
          {isLoading ? 'Processing...' : 'Generate Highlights'}
        </button>
      </form>

      {error && (
        <div className="error">
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}

      {response && (
        <div className="response">
          <h3>Response:</h3>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

export default App
