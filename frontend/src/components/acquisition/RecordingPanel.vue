<template>
  <div class="recording-panel">
    <h2>IQ Recorder</h2>
    
    <div class="status-section" v-if="recording.status">
      <div class="status-badge" :class="recording.status">
        {{ statusLabel }}
      </div>
      <p v-if="recording.elapsed_seconds" class="elapsed-time">
        Elapsed: {{ formatTime(recording.elapsed_seconds) }}
      </p>
      <p v-if="recording.estimated_remaining_seconds" class="remaining-time">
        Remaining: {{ formatTime(recording.estimated_remaining_seconds) }}
      </p>
      <div v-if="recording.progress_percent !== undefined" class="progress-bar">
        <div class="progress-fill" :style="{ width: recording.progress_percent + '%' }"></div>
      </div>
    </div>

    <div class="config-section">
      <div class="input-group">
        <label>Center Frequency (MHz)</label>
        <input 
          v-model.number="config.center_frequency_mhz"
          type="number"
          :disabled="isRecording"
          min="9"
          max="6400"
        >
      </div>

      <div class="input-group">
        <label>Bandwidth (MHz)</label>
        <input
          v-model.number="config.bandwidth_mhz"
          type="number"
          :disabled="isRecording"
          min="1"
          max="40"
        >
      </div>

      <div class="input-group">
        <label>Sample Rate (MSps)</label>
        <input
          v-model.number="config.sample_rate_msps"
          type="number"
          :disabled="isRecording"
          min="1"
          max="125"
        >
      </div>

      <div class="input-group">
        <label>Duration (seconds)</label>
        <input
          v-model.number="config.duration_seconds"
          type="number"
          :disabled="isRecording"
          min="1"
          max="3600"
        >
      </div>

      <div class="input-group">
        <label>Location (optional)</label>
        <input
          v-model="config.location_name"
          type="text"
          :disabled="isRecording"
          placeholder="e.g., Office, Field A, etc."
        >
      </div>

      <div class="input-group">
        <label>Operator Name (optional)</label>
        <input
          v-model="config.operator_name"
          type="text"
          :disabled="isRecording"
          placeholder="Your name"
        >
      </div>

      <div class="input-group">
        <label>Notes (optional)</label>
        <textarea
          v-model="config.notes"
          :disabled="isRecording"
          placeholder="Additional notes about this recording"
          rows="3"
        ></textarea>
      </div>

      <div class="estimated-size">
        <strong>Estimated file size:</strong> {{ estimatedSizeGb.toFixed(2) }} GB
      </div>
    </div>

    <div class="control-section">
      <button
        @click="startRecording"
        :disabled="isRecording"
        class="btn btn-primary"
      >
        <span v-if="!isRecording">START RECORDING</span>
        <span v-else>Recording...</span>
      </button>

      <button
        @click="stopRecording"
        :disabled="!isRecording"
        class="btn btn-danger"
      >
        STOP RECORDING
      </button>
    </div>

    <div class="info-section" v-if="isRecording">
      <p class="info-text">
        Recording in progress... Do not disconnect device or close application.
      </p>
    </div>

    <div class="error-section" v-if="error">
      <p class="error-text">{{ error }}</p>
      <button @click="error = ''" class="btn btn-small">Clear</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRecording } from '@/composables/useRecording'

interface RecordingConfig {
  center_frequency_mhz: number
  bandwidth_mhz: number
  sample_rate_msps: number
  duration_seconds: number
  location_name?: string
  operator_name?: string
  notes?: string
}

interface RecordingStatus {
  recording_id?: string
  status?: string
  elapsed_seconds?: number
  estimated_remaining_seconds?: number
  progress_percent?: number
  filename?: string
  error?: string
}

export default defineComponent({
  name: 'RecordingPanel',
  setup() {
    const {
      recording,
      startRecording: composableStart,
      stopRecording: composableStop,
      getRecordingStatus,
    } = useRecording()

    return {
      recording,
      composableStart,
      composableStop,
      getRecordingStatus,
    }
  },
  data() {
    return {
      config: {
        center_frequency_mhz: 118.0,
        bandwidth_mhz: 28.0,
        sample_rate_msps: 40.0,
        duration_seconds: 10,
        location_name: '',
        operator_name: '',
        notes: '',
      } as RecordingConfig,
      isRecording: false,
      error: '',
      statusPollingInterval: null as any,
    }
  },
  computed: {
    estimatedSizeGb(): number {
      const samples = (this.config.duration_seconds * this.config.sample_rate_msps * 1e6)
      const bytesPerSample = 8  // complex64 = 8 bytes
      const uncompressed = samples * bytesPerSample
      const compressed = uncompressed * 0.5  // ~50% compression
      return compressed / (1024 ** 3)
    },
    statusLabel(): string {
      const status = this.recording.status
      const map: Record<string, string> = {
        'initializing': 'Initializing...',
        'recording': 'Recording',
        'stopping': 'Stopping...',
        'stopped': 'Stopped',
        'saved': 'Saved',
        'error': 'Error',
      }
      return map[status] || 'Unknown'
    }
  },
  methods: {
    async startRecording() {
      try {
        this.error = ''
        
        await this.composableStart({
          center_frequency_hz: this.config.center_frequency_mhz * 1e6,
          bandwidth_hz: this.config.bandwidth_mhz * 1e6,
          sample_rate_sps: this.config.sample_rate_msps * 1e6,
          duration_seconds: this.config.duration_seconds,
          location_name: this.config.location_name || undefined,
          operator_name: this.config.operator_name || undefined,
          notes: this.config.notes || undefined,
        })
        
        this.isRecording = true
        
        // Poll status every 500ms
        this.statusPollingInterval = setInterval(() => {
          this.getRecordingStatus()
        }, 500)
        
      } catch (err: any) {
        this.error = err.message || 'Failed to start recording'
        this.isRecording = false
      }
    },
    async stopRecording() {
      try {
        if (this.statusPollingInterval) {
          clearInterval(this.statusPollingInterval)
        }
        
        await this.composableStop()
        this.isRecording = false
        
      } catch (err: any) {
        this.error = err.message || 'Failed to stop recording'
      }
    },
    formatTime(seconds: number): string {
      const h = Math.floor(seconds / 3600)
      const m = Math.floor((seconds % 3600) / 60)
      const s = Math.floor(seconds % 60)
      
      if (h > 0) {
        return `${h}h ${m}m ${s}s`
      }
      if (m > 0) {
        return `${m}m ${s}s`
      }
      return `${s}s`
    }
  },
  beforeUnmount() {
    if (this.statusPollingInterval) {
      clearInterval(this.statusPollingInterval)
    }
  }
})
</script>

<style scoped>
.recording-panel {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  margin: 20px 0;
}

h2 {
  margin-top: 0;
  color: #333;
}

.status-section {
  background: white;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
  border-left: 4px solid #3498db;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 10px;
}

.status-badge.recording {
  background: #27ae60;
  color: white;
}

.status-badge.stopped {
  background: #95a5a6;
  color: white;
}

.status-badge.error {
  background: #e74c3c;
  color: white;
}

.elapsed-time, .remaining-time {
  margin: 5px 0;
  color: #555;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #27ae60, #2ecc71);
  transition: width 0.2s ease;
}

.config-section {
  background: white;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.input-group {
  margin-bottom: 15px;
}

.input-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
  font-size: 14px;
}

.input-group input,
.input-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  box-sizing: border-box;
}

.input-group input:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
}

.input-group textarea:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
}

.estimated-size {
  padding: 10px;
  background: #ecf0f1;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 15px;
}

.control-section {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  flex: 1;
}

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #229954;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn-danger:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
  flex: none;
}

.info-section {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 15px;
}

.info-text {
  margin: 0;
  color: #155724;
  font-size: 14px;
}

.error-section {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 15px;
}

.error-text {
  margin: 0 0 10px 0;
  color: #721c24;
  font-size: 14px;
}
</style>
