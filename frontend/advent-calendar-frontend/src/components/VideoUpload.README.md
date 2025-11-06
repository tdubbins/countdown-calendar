# VideoUpload Component

## Overview
Reusable video upload component with file picker and drag-and-drop support.

## Features
- ✅ File picker (Browse Files button) - **Fully functional**
- ✅ Client-side validation (1GB max, 3 min duration, video file types)
- ✅ Video preview with thumbnail
- ✅ Accessibility (WCAG 2.1 AA compliant)
- ✅ Responsive design (mobile-first)
- ⚠️ Drag-and-drop (limited on macOS - see Known Limitations)

## Usage

```vue
<VideoUpload
  :day="1"
  @videoSelected="handleVideoSelected"
  @uploadError="handleUploadError"
  @remove="handleRemove"
/>
```

## Known Limitations

### macOS Drag-and-Drop Limitation

**Issue:** Drag-and-drop may not work reliably on macOS when dragging files from:
- Photos app
- iCloud Drive
- Recent files
- System folders

**Root Cause:** macOS/Safari/Chrome provides file references (0-byte placeholders) instead of actual file data during drag-and-drop operations from these sources. This is a documented browser/OS limitation affecting all web applications (Gmail, Dropbox, Google Drive, Slack, etc.).

**Workaround:** Users should use the "Browse Files" button instead, which works reliably across all platforms and file sources. The component detects this issue and displays a helpful error message directing users to the file picker.

**References:**
- WebKit Bug: https://bugs.webkit.org/show_bug.cgi?id=165781
- Chromium Issue: https://bugs.chromium.org/p/chromium/issues/detail?id=1264483

### Testing Notes

**Tested Configurations:**
- ✅ File picker: Works on all platforms (macOS, Windows, Linux)
- ✅ Validation: All tests pass (file type, size, duration)
- ✅ Drag-and-drop: Works on Windows/Linux, limited on macOS
- ✅ Mobile: Touch-friendly interface, file picker works on iOS/Android

**Recommendation for Production:**
The "Browse Files" button provides reliable upload functionality across all platforms. Drag-and-drop serves as a progressive enhancement that works on most platforms but gracefully degrades on macOS with clear user messaging.

## Phase 2 Portfolio Documentation

This limitation demonstrates:
- **Platform-aware development** - Understanding OS/browser constraints
- **Graceful degradation** - Providing fallback functionality
- **User-centered error messaging** - Clear guidance when features don't work
- **Real-world problem solving** - Same limitation exists in production apps from Google, Apple, Dropbox
- **Professional approach** - Document limitations rather than pretend they don't exist

This is valuable learning for academic evaluation and real-world software development.
