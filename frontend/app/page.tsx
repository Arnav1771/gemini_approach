'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Camera, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'
import axios from 'axios'

interface InsightResponse {
  chart_type: string
  summary: string
  trends: string[]
  anomalies: string[]
  recommendations: string[]
  extracted_data: Array<{ category: string; value: number }>
}

export default function Home() {
  const [insights, setInsights] = useState<InsightResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/api/analyze/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setInsights(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze the graph')
    } finally {
      setLoading(false)
    }
  }, [API_URL])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    },
    multiple: false
  })

  const captureScreen = async () => {
    try {
      setLoading(true)
      setError(null)

      // Request screen capture
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { mediaSource: 'screen' }
      })

      // Create video element to capture frame
      const video = document.createElement('video')
      video.srcObject = stream
      video.play()

      video.onloadedmetadata = () => {
        const canvas = document.createElement('canvas')
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        const ctx = canvas.getContext('2d')!
        
        ctx.drawImage(video, 0, 0)
        
        // Stop the stream
        stream.getTracks().forEach(track => track.stop())

        // Convert to base64
        const imageData = canvas.toDataURL('image/png')

        // Send to API
        axios.post(`${API_URL}/api/analyze/screencap`, {
          image_data: imageData
        }).then(response => {
          setInsights(response.data)
        }).catch(err => {
          setError(err.response?.data?.detail || 'Failed to analyze the screen capture')
        }).finally(() => {
          setLoading(false)
        })
      }
    } catch (err: any) {
      setError('Screen capture not supported or permission denied')
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Graph Analysis AI
          </h1>
          <p className="text-xl text-gray-600">
            Upload or capture graphs to get AI-powered insights and recommendations
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* File Upload */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Upload Graph Image
            </h3>
            <p className="text-gray-600">
              {isDragActive
                ? 'Drop the image here...'
                : 'Drag & drop an image here, or click to select'}
            </p>
          </div>

          {/* Screen Capture */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Capture Screen
            </h3>
            <p className="text-gray-600 mb-4">
              Capture a portion of your screen containing a graph
            </p>
            <button
              onClick={captureScreen}
              disabled={loading}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              Start Capture
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
              <p className="text-blue-800">Analyzing your graph...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="flex items-center">
              <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {insights && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Analysis Results
            </h2>

            {/* Chart Type */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Chart Type
              </h3>
              <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                {insights.chart_type}
              </span>
            </div>

            {/* Summary */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Summary
              </h3>
              <p className="text-gray-700">{insights.summary}</p>
            </div>

            {/* Trends */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                Key Trends
              </h3>
              <ul className="space-y-2">
                {insights.trends.map((trend, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{trend}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Anomalies */}
            {insights.anomalies.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mr-2" />
                  Anomalies
                </h3>
                <ul className="space-y-2">
                  {insights.anomalies.map((anomaly, index) => (
                    <li key={index} className="flex items-start">
                      <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{anomaly}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Recommendations
              </h3>
              <ul className="space-y-3">
                {insights.recommendations.map((recommendation, index) => (
                  <li key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <span className="text-green-800">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Extracted Data */}
            {insights.extracted_data.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  Extracted Data
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-gray-50 border border-gray-200 rounded-lg">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="px-4 py-2 text-left text-gray-800">Category</th>
                        <th className="px-4 py-2 text-left text-gray-800">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {insights.extracted_data.map((data, index) => (
                        <tr key={index} className="border-t border-gray-200">
                          <td className="px-4 py-2 text-gray-700">{data.category}</td>
                          <td className="px-4 py-2 text-gray-700">{data.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
