<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Video Upload Component Test</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <div class="test-container">
        <h1>VideoUpload Component Test</h1>
        <p class="test-description">
          Test the video upload component with drag-and-drop, file picker, and validation.
        </p>

        <!-- VideoUpload Component -->
        <VideoUpload
          :day="1"
          @videoSelected="handleVideoSelected"
          @uploadError="handleUploadError"
          @remove="handleRemove"
        />

        <!-- Test Results Display -->
        <div v-if="selectedVideo" class="test-result success-result">
          <h3>✅ Video Selected Successfully!</h3>
          <div class="result-details">
            <p><strong>File Name:</strong> {{ selectedVideo.name }}</p>
            <p><strong>File Size:</strong> {{ formatBytes(selectedVideo.size) }}</p>
            <p><strong>File Type:</strong> {{ selectedVideo.type }}</p>
            <p><strong>Duration:</strong> {{ formatDuration(videoDuration) }}</p>
          </div>
        </div>

        <div v-if="errorMsg" class="test-result error-result">
          <h3>❌ Validation Error</h3>
          <p>{{ errorMsg }}</p>
        </div>

        <!-- Console Log Display -->
        <div class="console-log">
          <h3>Event Log:</h3>
          <div class="log-entries">
            <div
              v-for="(log, index) in eventLogs"
              :key="index"
              class="log-entry"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>

        <!-- Test Instructions -->
        <div class="test-instructions">
          <h3>Test Cases:</h3>
          <ol>
            <li><strong>Valid Upload:</strong> Upload a video file &lt;50MB and &lt;3 minutes</li>
            <li><strong>File Too Large:</strong> Upload a file &gt;50MB (should show error)</li>
            <li><strong>Video Too Long:</strong> Upload a video &gt;3 minutes (should show error)</li>
            <li><strong>Wrong Type:</strong> Try uploading an image or PDF (should show error)</li>
            <li><strong>Drag & Drop:</strong> Drag a video file over the drop zone</li>
            <li><strong>Remove File:</strong> After upload, click the red remove button</li>
          </ol>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent
} from '@ionic/vue';
import VideoUpload from '@/components/VideoUpload.vue';

// State
const selectedVideo = ref<File | null>(null);
const videoDuration = ref<number>(0);
const errorMsg = ref<string>('');
const eventLogs = ref<Array<{ time: string; message: string }>>([]);

// Utility functions
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const formatDuration = (seconds: number): string => {
  if (seconds === 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const addLog = (message: string) => {
  const now = new Date();
  const time = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;
  eventLogs.value.unshift({ time, message });

  // Keep only last 10 logs
  if (eventLogs.value.length > 10) {
    eventLogs.value.pop();
  }
};

// Event handlers
const handleVideoSelected = (file: File, duration: number) => {
  console.log('✅ Video selected:', file.name, 'Duration:', duration);
  selectedVideo.value = file;
  videoDuration.value = duration;
  errorMsg.value = '';
  addLog(`✅ Video selected: ${file.name} (${formatBytes(file.size)}, ${formatDuration(duration)})`);
};

const handleUploadError = (error: string) => {
  console.error('❌ Upload error:', error);
  errorMsg.value = error;
  addLog(`❌ Error: ${error}`);
};

const handleRemove = () => {
  console.log('🗑️ Video removed');
  selectedVideo.value = null;
  videoDuration.value = 0;
  errorMsg.value = '';
  addLog('🗑️ Video removed by user');
};
</script>

<style scoped>
.test-container {
  max-width: 900px;
  margin: 0 auto;
  padding: clamp(1rem, 4vw, 2rem);
}

h1 {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.test-description {
  font-size: clamp(0.9rem, 2vw, 1rem);
  color: var(--color-text-secondary);
  margin-bottom: 2rem;
}

/* Test Results */
.test-result {
  margin-top: 2rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  border-radius: var(--radius-lg);
  animation: fadeIn 0.3s ease-in;
}

.success-result {
  background: rgba(var(--ion-color-success-rgb), 0.1);
  border: 2px solid var(--ion-color-success);
}

.error-result {
  background: rgba(var(--ion-color-danger-rgb), 0.1);
  border: 2px solid var(--ion-color-danger);
}

.test-result h3 {
  margin: 0 0 1rem 0;
  font-size: clamp(1.1rem, 2.5vw, 1.3rem);
}

.result-details p {
  margin: 0.5rem 0;
  font-size: clamp(0.9rem, 2vw, 1rem);
}

.result-details strong {
  color: var(--color-text-primary);
}

/* Console Log */
.console-log {
  margin-top: 2rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  background: var(--color-background-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.console-log h3 {
  margin: 0 0 1rem 0;
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  color: var(--color-text-primary);
}

.log-entries {
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: clamp(0.8rem, 1.8vw, 0.9rem);
}

.log-entry {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  gap: 1rem;
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  color: var(--color-text-tertiary);
  min-width: 70px;
}

.log-message {
  color: var(--color-text-primary);
  flex: 1;
}

/* Test Instructions */
.test-instructions {
  margin-top: 2rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  background: rgba(var(--ion-color-primary-rgb), 0.05);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(var(--ion-color-primary-rgb), 0.2);
}

.test-instructions h3 {
  margin: 0 0 1rem 0;
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  color: var(--ion-color-primary);
}

.test-instructions ol {
  margin: 0;
  padding-left: 1.5rem;
}

.test-instructions li {
  margin: 0.75rem 0;
  font-size: clamp(0.9rem, 2vw, 1rem);
  line-height: 1.5;
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .log-entry {
    flex-direction: column;
    gap: 0.25rem;
  }

  .log-time {
    min-width: auto;
  }
}
</style>
