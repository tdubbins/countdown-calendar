<template>
  <ion-page>
    <ion-header>
      <ion-toolbar color="primary">
        <!-- Desktop only: Back button -->
        <ion-buttons v-if="!isMobile()" slot="start">
          <ion-button @click="goBack" color="light">
            <ion-icon :icon="arrowBack" slot="start"></ion-icon>
            Back
          </ion-button>
        </ion-buttons>
        <ion-title>Help & Support</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="help-content">
      <div class="help-container">
        <!-- Hero Section -->
        <div class="help-hero">
          <h1>How can we help you?</h1>
          <p>Everything you need to know about creating and sharing countdown calendars</p>
        </div>

        <!-- Getting Started -->
        <section class="help-section">
          <h2 class="section-title">Getting Started</h2>

          <ion-accordion-group>
            <ion-accordion value="create-calendar">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I create my first calendar?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <ol>
                  <li>Click the "New" button or the plus icon on your dashboard</li>
                  <li>Enter a title for your calendar (e.g., "Christmas 2025")</li>
                  <li>Choose the number of days (1-31)</li>
                  <li>Select start and end dates</li>
                  <li>Add an optional description (this will be visible to everyone viewing your calendar)</li>
                  <li>Choose a theme (Christmas or Birthday)</li>
                  <li>Set door ordering (sequential or random)</li>
                  <li>Click "Create Calendar" to save</li>
                </ol>
                <p><strong>Tip:</strong> Use the description to add a personal message, explain the occasion, or give instructions to your viewers.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="calendar-duration">
              <ion-item slot="header">
                <ion-label>
                  <h3>What calendar durations are supported?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>You can create calendars with 1 to 31 days. Common examples:</p>
                <ul>
                  <li><strong>Advent Calendar:</strong> 24 days (December 1-24)</li>
                  <li><strong>Birthday Countdown:</strong> 7-14 days before a birthday</li>
                  <li><strong>Holiday Countdown:</strong> Any custom duration</li>
                  <li><strong>Event Preparation:</strong> Days leading up to an event</li>
                </ul>
              </div>
            </ion-accordion>

            <ion-accordion value="themes">
              <ion-item slot="header">
                <ion-label>
                  <h3>What themes are available?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Currently, two beautiful themes are available:</p>
                <ul>
                  <li><strong>Christmas:</strong> Wooden cabin doors with falling snow and festive decorations</li>
                  <li><strong>Birthday:</strong> Gift-wrapped doors with floating balloons and celebration colors</li>
                </ul>
                <p>You can select your theme when creating or editing a calendar.</p>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- Account Management -->
        <section class="help-section">
          <h2 class="section-title">Account Management</h2>

          <ion-accordion-group>
            <ion-accordion value="access-profile">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I access my profile?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>To access your profile:</p>
                <ol>
                  <li>Click on the user icon in the top-right corner of the header</li>
                  <li>Select "Profile" from the menu</li>
                </ol>
                <p>Your profile page shows:</p>
                <ul>
                  <li>Your email address</li>
                  <li>Your display name</li>
                  <li>Account creation date</li>
                  <li>Email verification status</li>
                  <li>Number of calendars you've created</li>
                </ul>
              </div>
            </ion-accordion>

            <ion-accordion value="change-display-name">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I change my display name?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Your display name is shown to viewers of your shared calendars. To change it:</p>
                <ol>
                  <li>Go to your Profile page</li>
                  <li>Click "Edit Profile"</li>
                  <li>Update your display name</li>
                  <li>Click "Save Changes"</li>
                </ol>
                <p><strong>Tip:</strong> Choose a name that helps recipients identify who the calendar is from.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="change-password">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I change my password?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>To update your password:</p>
                <ol>
                  <li>Go to your Profile page</li>
                  <li>Click "Change Password"</li>
                  <li>Enter your current password</li>
                  <li>Enter your new password (minimum 8 characters)</li>
                  <li>Confirm your new password</li>
                  <li>Click "Change Password" to save</li>
                </ol>
                <p><strong>Note:</strong> You will be logged out after changing your password and need to log in again with your new credentials.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="verification-email">
              <ion-item slot="header">
                <ion-label>
                  <h3>I didn't receive my verification email</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>If you haven't received your verification email:</p>
                <ol>
                  <li>Check your spam or junk folder</li>
                  <li>Wait a few minutes - emails can sometimes be delayed</li>
                  <li>On the verification page, click "Resend verification email"</li>
                  <li>Check that your email address was entered correctly</li>
                </ol>
                <p>If you still don't receive it, contact support at <a :href="`mailto:${supportEmail}?subject=Verification Email Issue`">{{ supportEmail }}</a></p>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- Video Management -->
        <section class="help-section">
          <h2 class="section-title">Video Management</h2>

          <ion-accordion-group>
            <ion-accordion value="video-formats">
              <ion-item slot="header">
                <ion-label>
                  <h3>What video formats are supported?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Supported video formats:</p>
                <ul>
                  <li>MP4 (recommended)</li>
                  <li>WebM</li>
                  <li>MOV</li>
                  <li>AVI</li>
                </ul>
                <p><strong>File size limit:</strong> 1GB per video</p>
                <p><strong>Duration limit:</strong> 3 minutes maximum</p>
              </div>
            </ion-accordion>

            <ion-accordion value="video-upload">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I upload videos?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <ol>
                  <li>Open your calendar in edit mode</li>
                  <li>Click on any day card</li>
                  <li>Click the "Upload Video" button</li>
                  <li>Select your video file</li>
                  <li>Wait for the upload and compression to complete</li>
                  <li>The video will automatically be assigned to that day</li>
                </ol>
                <p><strong>Note:</strong> Videos are automatically compressed in the background to optimize playback performance.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="video-compression">
              <ion-item slot="header">
                <ion-label>
                  <h3>Why is my video being compressed?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>All uploaded videos are automatically compressed to ensure:</p>
                <ul>
                  <li>Fast loading times for viewers</li>
                  <li>Smooth playback on all devices</li>
                  <li>Reduced storage and bandwidth usage</li>
                  <li>Optimal viewing experience</li>
                </ul>
                <p>The compression happens in the background, so you can continue working while your videos are being processed.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="video-drag-drop">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I move videos between days?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>You can easily rearrange videos using drag and drop:</p>
                <p><strong>To move a video to an empty day:</strong></p>
                <ol>
                  <li>Click and hold on a day card that has a video</li>
                  <li>Drag it to an empty day</li>
                  <li>Release to drop the video in its new location</li>
                </ol>
                <p><strong>To swap videos between two days:</strong></p>
                <ol>
                  <li>Click and hold on a day card that has a video</li>
                  <li>Drag it onto another day that also has a video</li>
                  <li>Release to swap the videos between the two days</li>
                </ol>
                <p><strong>Visual feedback:</strong></p>
                <ul>
                  <li>The card you're dragging becomes semi-transparent</li>
                  <li>Valid drop targets are highlighted as you hover</li>
                  <li>Empty days show a teal highlight (move)</li>
                  <li>Days with videos show an amber highlight (swap)</li>
                </ul>
                <p><strong>Note:</strong> Drag and drop works on desktop browsers. On mobile devices, use the delete and re-upload method to reassign videos.</p>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- Sharing Calendars -->
        <section class="help-section">
          <h2 class="section-title">Sharing Calendars</h2>

          <ion-accordion-group>
            <ion-accordion value="get-link">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I share my calendar?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <ol>
                  <li>Open your calendar in edit mode</li>
                  <li>Make sure your calendar is published (toggle the "Published" switch)</li>
                  <li>Click the "Share" button</li>
                  <li>Your unique sharing link will be displayed</li>
                  <li>Click "Copy Link" to copy it to your clipboard</li>
                  <li>Share the link via email, messaging apps, or social media</li>
                </ol>
              </div>
            </ion-accordion>

            <ion-accordion value="privacy">
              <ion-item slot="header">
                <ion-label>
                  <h3>Who can view my calendar?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Your calendar privacy is protected:</p>
                <ul>
                  <li><strong>Private by default:</strong> Only you can see unpublished calendars</li>
                  <li><strong>Secure sharing:</strong> Each calendar has a unique UUID-based link that's impossible to guess</li>
                  <li><strong>No public listing:</strong> Calendars are never listed publicly or searchable</li>
                  <li><strong>Link-only access:</strong> Only people with the exact sharing link can view your calendar</li>
                </ul>
              </div>
            </ion-accordion>

            <ion-accordion value="publish-unpublish">
              <ion-item slot="header">
                <ion-label>
                  <h3>What does publishing/unpublishing do?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p><strong>Published:</strong></p>
                <ul>
                  <li>Calendar is accessible via sharing link</li>
                  <li>Viewers can see unlocked days and videos</li>
                  <li>Daily unlock mechanism is active</li>
                </ul>
                <p><strong>Unpublished:</strong></p>
                <ul>
                  <li>Calendar is only visible to you</li>
                  <li>Sharing link shows "calendar not found"</li>
                  <li>Perfect for testing before sharing</li>
                </ul>
                <p>You can toggle publication status anytime without affecting your calendar data.</p>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- Calendar Features -->
        <section class="help-section">
          <h2 class="section-title">Calendar Features</h2>

          <ion-accordion-group>
            <ion-accordion value="daily-unlock">
              <ion-item slot="header">
                <ion-label>
                  <h3>How does the daily unlock work?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Days unlock automatically based on your calendar dates:</p>
                <ul>
                  <li><strong>Locked days:</strong> Show a decorative ribbon or lock icon and cannot be opened</li>
                  <li><strong>Unlocked days:</strong> Show an open ribbon and can be clicked to view the video</li>
                  <li><strong>Opened days:</strong> Show a checkmark and thumbnail after being viewed</li>
                </ul>
                <p><strong>Example:</strong> For a calendar starting December 1st, Day 1 unlocks on December 1st, Day 2 on December 2nd, etc.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="door-ordering">
              <ion-item slot="header">
                <ion-label>
                  <h3>What is door ordering?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>You can choose how days are displayed on your calendar:</p>
                <ul>
                  <li><strong>Sequential:</strong> Days appear in order (1, 2, 3, 4...)</li>
                  <li><strong>Random:</strong> Days appear in a shuffled order for a more traditional advent calendar feel</li>
                </ul>
                <p>The ordering is purely visual - unlocking still happens based on dates.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="preview-mode">
              <ion-item slot="header">
                <ion-label>
                  <h3>What is preview mode?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>As the calendar creator, you have two viewing modes:</p>
                <ul>
                  <li><strong>See All Doors:</strong> View all days regardless of lock status (creator preview)</li>
                  <li><strong>Viewer Mode:</strong> See exactly what your recipients see (respects unlock dates)</li>
                </ul>
                <p>Toggle between modes using the buttons at the top of your calendar to test the viewing experience.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="calendar-status">
              <ion-item slot="header">
                <ion-label>
                  <h3>What do calendar statuses mean?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <ul>
                  <li><strong>Upcoming:</strong> Calendar hasn't started yet (before start date)</li>
                  <li><strong>Ongoing:</strong> Calendar is currently active (between start and end dates)</li>
                  <li><strong>Expired:</strong> Calendar has ended (after end date)</li>
                </ul>
                <p>Status is displayed on your dashboard and automatically updates based on dates.</p>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- Technical Support -->
        <section class="help-section">
          <h2 class="section-title">Technical Support</h2>

          <ion-accordion-group>
            <ion-accordion value="browser-compatibility">
              <ion-item slot="header">
                <ion-label>
                  <h3>Which browsers are supported?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Countdown Calendar works best on modern browsers:</p>
                <ul>
                  <li>Chrome 90+ (recommended)</li>
                  <li>Firefox 88+</li>
                  <li>Safari 14+</li>
                  <li>Edge 90+</li>
                </ul>
                <p><strong>Mobile browsers:</strong></p>
                <ul>
                  <li>Chrome Mobile</li>
                  <li>Safari iOS</li>
                  <li>Samsung Internet</li>
                </ul>
              </div>
            </ion-accordion>

            <ion-accordion value="mobile-device">
              <ion-item slot="header">
                <ion-label>
                  <h3>Does it work on mobile devices?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Yes! Countdown Calendar is a Progressive Web App (PWA) that works seamlessly on:</p>
                <ul>
                  <li>iOS devices (iPhone, iPad)</li>
                  <li>Android devices (phones, tablets)</li>
                  <li>Desktop computers</li>
                </ul>
                <p>The interface automatically adapts to your screen size for the best experience on any device.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="troubleshooting">
              <ion-item slot="header">
                <ion-label>
                  <h3>Troubleshooting common issues</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p><strong>Video won't play:</strong></p>
                <ul>
                  <li>Check your internet connection</li>
                  <li>Try refreshing the page</li>
                  <li>Ensure the video format is supported</li>
                  <li>Wait for compression to complete if just uploaded</li>
                </ul>
                <p><strong>Calendar won't load:</strong></p>
                <ul>
                  <li>Check your internet connection</li>
                  <li>Clear browser cache and cookies</li>
                  <li>Try a different browser</li>
                  <li>Verify the sharing link is correct</li>
                </ul>
                <p><strong>Upload failed:</strong></p>
                <ul>
                  <li>Check file size (max 1GB)</li>
                  <li>Check video duration (max 3 minutes)</li>
                  <li>Ensure stable internet connection</li>
                  <li>Try uploading again</li>
                </ul>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- FAQ -->
        <section class="help-section">
          <h2 class="section-title">Frequently Asked Questions</h2>

          <ion-accordion-group>
            <ion-accordion value="edit-after-publish">
              <ion-item slot="header">
                <ion-label>
                  <h3>Can I edit a calendar after publishing?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Yes! You can edit your calendar anytime, whether it's published or not:</p>
                <ul>
                  <li>Change title, description, or theme</li>
                  <li>Upload or replace videos</li>
                  <li>Drag and drop videos to rearrange them between days</li>
                  <li>Modify dates or duration (affects unlock schedule)</li>
                  <li>Toggle door ordering</li>
                  <li>Publish or unpublish</li>
                </ul>
                <p>Changes are saved immediately and visible to viewers (if published).</p>
              </div>
            </ion-accordion>

            <ion-accordion value="delete-videos">
              <ion-item slot="header">
                <ion-label>
                  <h3>Can I delete or replace videos?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Yes, you have full control over your videos:</p>
                <ul>
                  <li><strong>Delete:</strong> Click on a day in edit mode and remove the video</li>
                  <li><strong>Replace:</strong> Upload a new video to the same day - it will replace the existing one</li>
                </ul>
                <p>Deleted videos are permanently removed and cannot be recovered.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="calendar-expires">
              <ion-item slot="header">
                <ion-label>
                  <h3>What happens when my calendar expires?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>When your calendar reaches its end date:</p>
                <ul>
                  <li>Status changes to "Expired" on your dashboard</li>
                  <li>All days remain unlocked for viewers</li>
                  <li>Sharing link continues to work</li>
                  <li>Videos remain accessible</li>
                  <li>You can still edit or delete the calendar</li>
                </ul>
                <p>Expired calendars are not automatically deleted - they remain until you choose to delete them.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="reuse-calendar">
              <ion-item slot="header">
                <ion-label>
                  <h3>Can I reuse the same calendar next year?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>You can edit an existing calendar to update its dates:</p>
                <ol>
                  <li>Open the calendar in edit mode</li>
                  <li>Update the start and end dates to the new year</li>
                  <li>Save changes</li>
                  <li>The unlock schedule will adjust to the new dates</li>
                </ol>
                <p><strong>Note:</strong> The sharing link remains the same, so previous recipients can still access it with updated dates.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="how-many-calendars">
              <ion-item slot="header">
                <ion-label>
                  <h3>How many calendars can I create?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>There is currently no limit on the number of calendars you can create. Create as many as you need for different occasions, recipients, or purposes!</p>
              </div>
            </ion-accordion>

            <ion-accordion value="account-deletion">
              <ion-item slot="header">
                <ion-label>
                  <h3>How do I delete my account?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>You can delete your account directly from the Profile page:</p>
                <ol>
                  <li>Click on your profile icon in the header</li>
                  <li>Navigate to Profile</li>
                  <li>Click the "Delete Account" button</li>
                  <li>Enter your password to confirm</li>
                  <li>Confirm the deletion</li>
                </ol>
                <p><strong>Warning:</strong> This will permanently delete your account and all associated calendars and videos. This action cannot be undone.</p>
              </div>
            </ion-accordion>

            <ion-accordion value="change-email">
              <ion-item slot="header">
                <ion-label>
                  <h3>Can I change my email address?</h3>
                </ion-label>
              </ion-item>
              <div class="accordion-content" slot="content">
                <p>Yes, you can update your email address:</p>
                <ol>
                  <li>Go to your Profile page</li>
                  <li>Click "Edit Profile"</li>
                  <li>Enter your new email address</li>
                  <li>Save changes</li>
                </ol>
                <p><strong>Note:</strong> You may need to verify your new email address before the change takes effect.</p>
              </div>
            </ion-accordion>
          </ion-accordion-group>
        </section>

        <!-- Contact Support -->
        <section class="help-section contact-section">
          <h2 class="section-title">Still Need Help?</h2>
          <div class="contact-card">
            <ion-icon :icon="mail" class="contact-icon"></ion-icon>
            <h3>Contact Support</h3>
            <p>Our support team is here to help. Send us an email and we'll get back to you as soon as possible.</p>
            <ion-button
              :href="`mailto:${supportEmail}?subject=Countdown Calendar Support Request`"
              expand="block"
              color="primary"
            >
              <ion-icon :icon="mail" slot="start"></ion-icon>
              {{ supportEmail }}
            </ion-button>
          </div>
        </section>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButtons,
  IonButton,
  IonIcon,
  IonAccordion,
  IonAccordionGroup,
  IonItem,
  IonLabel
} from '@ionic/vue';
import { arrowBack, mail } from 'ionicons/icons';
import { useResponsive } from '@/composables/useResponsive';

const router = useRouter();
const { isMobile } = useResponsive();
const supportEmail = 'countdown-calendars@dubbins.de';

const goBack = () => {
  router.back();
};
</script>

<style scoped>
.help-content {
  --background: var(--color-background);
}

.help-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

/* Hero Section */
.help-hero {
  text-align: center;
  padding: var(--spacing-2xl) var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.help-hero h1 {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.help-hero p {
  font-size: clamp(1rem, 3vw, 1.25rem);
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 600px;
  margin: 0 auto;
}

/* Help Sections */
.help-section {
  margin-bottom: var(--spacing-2xl);
}

.section-title {
  font-size: 1.5rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
  padding-left: var(--spacing-xs);
}

/* Accordion Styling */
ion-accordion-group {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

ion-accordion {
  background: var(--color-surface);
  margin-bottom: var(--spacing-xs);
  border-radius: var(--radius-md);
  overflow: hidden;
}

ion-accordion ion-item {
  --background: var(--color-surface);
  --padding-start: var(--spacing-md);
  --padding-end: var(--spacing-md);
  --min-height: 60px;
}

ion-accordion ion-item h3 {
  font-size: 1rem;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
}

.accordion-content {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-background);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.accordion-content p {
  margin: 0 0 var(--spacing-md) 0;
}

.accordion-content p:last-child {
  margin-bottom: 0;
}

.accordion-content ul,
.accordion-content ol {
  margin: var(--spacing-sm) 0;
  padding-left: var(--spacing-lg);
}

.accordion-content li {
  margin-bottom: var(--spacing-xs);
}

.accordion-content strong {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
}

.accordion-content a {
  color: var(--ion-color-primary);
  text-decoration: none;
}

.accordion-content a:hover {
  text-decoration: underline;
}

/* Contact Section */
.contact-section {
  margin-top: var(--spacing-3xl);
  margin-bottom: var(--spacing-3xl);
}

.contact-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  text-align: center;
  box-shadow: var(--shadow-md);
}

.contact-icon {
  font-size: 3rem;
  color: var(--ion-color-primary);
  margin-bottom: var(--spacing-md);
}

.contact-card h3 {
  font-size: 1.5rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.contact-card p {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-lg) 0;
  line-height: 1.6;
}

.contact-card ion-button {
  margin-top: var(--spacing-md);
  font-weight: var(--font-weight-medium);
}

/* Responsive Design */
@media (max-width: 640px) {
  .help-container {
    padding: var(--spacing-sm);
  }

  .help-hero {
    padding: var(--spacing-xl) var(--spacing-sm);
  }

  .accordion-content {
    padding: var(--spacing-md);
  }

  .contact-card {
    padding: var(--spacing-xl) var(--spacing-md);
  }
}

@media (min-width: 768px) {
  .help-container {
    padding: var(--spacing-xl) var(--spacing-lg);
  }
}
</style>
