/**
 * Composable for IQ recording functionality.
 * 
 * Manages:
 * - Starting and stopping recordings
 * - Tracking recording status
 * - API communication with backend
 */

import { ref, computed, reactive } from 'vue'
import { spectrumService } from '@/services/spectrumService'

interface RecordingState {
  recording_id?: string
  status?: string
  elapsed_seconds?: number
  estimated_remaining_seconds?: number
  progress_percent?: number
  file_size_mb?: number
  filename?: string
  error?: string
}

interface StartRecordingParams {
  center_frequency_hz: number
  bandwidth_hz: number
  sample_rate_sps: number
  duration_seconds: number
  location_name?: string
  operator_name?: string
  notes?: string
}

export function useRecording() {
  const recording = reactive<RecordingState>({})
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Start a new IQ recording.
   */
  async function startRecording(params: StartRecordingParams): Promise<string> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/recordings/iq/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          center_frequency_hz: params.center_frequency_hz,
          bandwidth_hz: params.bandwidth_hz,
          sample_rate_sps: params.sample_rate_sps,
          duration_seconds: params.duration_seconds,
          location_name: params.location_name,
          operator_name: params.operator_name,
          notes: params.notes,
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to start recording')
      }

      const data = await response.json()
      
      recording.recording_id = data.recording_id
      recording.status = 'recording'
      recording.elapsed_seconds = 0
      recording.progress_percent = 0
      
      console.log('[useRecording] Recording started:', data.recording_id)
      
      return data.recording_id
    } catch (err: any) {
      const message = err.message || 'Failed to start recording'
      error.value = message
      recording.status = 'error'
      recording.error = message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Stop the current IQ recording.
   */
  async function stopRecording(): Promise<string> {
    if (!recording.recording_id) {
      throw new Error('No active recording')
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await fetch('/api/recordings/iq/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recording_id: recording.recording_id,
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to stop recording')
      }

      const data = await response.json()
      
      recording.status = 'stopped'
      recording.filename = data.file_path.split('/').pop()
      
      console.log('[useRecording] Recording stopped:', data.file_path)
      
      return data.file_path
    } catch (err: any) {
      const message = err.message || 'Failed to stop recording'
      error.value = message
      recording.error = message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get status of a recording.
   */
  async function getRecordingStatus(): Promise<void> {
    if (!recording.recording_id) {
      return
    }

    try {
      const response = await fetch(
        `/api/recordings/iq/${recording.recording_id}/status`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to get status')
      }

      const data = await response.json()
      
      // Update recording state
      recording.status = data.status
      recording.elapsed_seconds = data.elapsed_seconds
      recording.estimated_remaining_seconds = data.estimated_remaining_seconds
      recording.file_size_mb = data.file_size_mb
      
      // Estimate progress based on expected duration
      if (recording.estimated_remaining_seconds !== undefined) {
        const total = (recording.elapsed_seconds || 0) + recording.estimated_remaining_seconds
        if (total > 0) {
          recording.progress_percent = ((recording.elapsed_seconds || 0) / total) * 100
        }
      }
    } catch (err: any) {
      console.error('[useRecording] Error getting status:', err)
      // Don't throw, just log
    }
  }

  /**
   * List all recordings.
   */
  async function listRecordings(limit: number = 100): Promise<any[]> {
    try {
      const response = await fetch(`/api/recordings/list?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to list recordings')
      }

      const data = await response.json()
      return data.recordings || []
    } catch (err: any) {
      console.error('[useRecording] Error listing recordings:', err)
      return []
    }
  }

  /**
   * Get metadata for a specific recording.
   */
  async function getRecordingMetadata(filename: string): Promise<any> {
    try {
      const response = await fetch(`/api/recordings/${filename}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to get metadata')
      }

      return await response.json()
    } catch (err: any) {
      console.error('[useRecording] Error getting metadata:', err)
      throw err
    }
  }

  /**
   * Delete a recording.
   */
  async function deleteRecording(filename: string): Promise<void> {
    try {
      const response = await fetch(`/api/recordings/${filename}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to delete recording')
      }

      console.log('[useRecording] Recording deleted:', filename)
    } catch (err: any) {
      console.error('[useRecording] Error deleting recording:', err)
      throw err
    }
  }

  /**
   * Get acquisition system status.
   */
  async function getAcquisitionStatus(): Promise<any> {
    try {
      const response = await fetch('/api/recordings/status', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Failed to get status')
      }

      return await response.json()
    } catch (err: any) {
      console.error('[useRecording] Error getting acquisition status:', err)
      throw err
    }
  }

  return {
    // State
    recording,
    isLoading,
    error,

    // Methods
    startRecording,
    stopRecording,
    getRecordingStatus,
    listRecordings,
    getRecordingMetadata,
    deleteRecording,
    getAcquisitionStatus,
  }
}
