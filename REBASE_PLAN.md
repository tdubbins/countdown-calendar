# Interactive Rebase Plan

## Goal: Squash 26 commits → 9 clean commits

### Proposed Final Commits

1. **feat: Implement Christmas theme with wooden cabin doors and snowfall**
   - Keep c9b2ffc (main theme implementation)

2. **refactor: Make doors more realistic with handles and wooden locks**
   - Keep 508b35a

3. **refactor: Strip DoorCard to minimal structural CSS, themes control all styling**
   - Keep 9b4b5f2

4. **feat: Add winter scene background image with proper asset resolution**
   - Squash: 38402a8 + 189ad06 + 7b495bf + 7d3c196 + 528ec4c
   - (All background image and sizing fixes)

5. **feat: Add animated snowfall with multiple layers and varied sizes**
   - Squash: 4aec635 + 8ea8d9e + 36097c5
   - (All snowfall iterations)

6. **feat: Add glowing Christmas text styling for title and description**
   - Keep 41fa811

7. **feat: Replace wooden door texture with Christmas wreath door image**
   - Squash: 60d9b87 + 58cb292
   - (Door image + lock icon fix)

8. **feat: Add Christmas tree decorations to video letterbox**
   - Squash: 64cc480 + 55c961d + 16286de + c61d8ed + 9878ae4 + dca3a29 + bd1d2ee + a725c08 + e8caf8f
   - (All 9 tree decoration iterations)

9. **fix: Improve mobile video playback and responsive layout**
   - Squash: 0d5acf8 + a690f1d + dc333ac
   - (Mobile video component + responsive grid + platform API)

---

## How to Execute Interactive Rebase

### Commands to run:

```bash
# Start interactive rebase from origin/main
git rebase -i origin/main
```

### In the editor, mark commits like this:

```
pick c9b2ffc feat: Implement Christmas theme with wooden cabin doors and snowfall
pick 508b35a refactor: Make doors more realistic with handles and wooden locks
pick 9b4b5f2 refactor: Strip DoorCard to minimal structural CSS, themes control all styling

# Background image group
pick 38402a8 feat: Add winter scene background image to Christmas theme
fixup 189ad06 fix: Correct CSS path for Christmas background image
fixup 7b495bf fix: Move background image to src/assets for proper Webpack resolution
fixup 7d3c196 fix: Make background span entire screen while keeping content centered

# Snowfall group
pick 4aec635 feat: Make snowflakes bigger and more frequent
fixup 8ea8d9e feat: Create continuous snowfall with staggered layers
fixup 36097c5 feat: Add mixed snowflake sizes and opacity within each layer

pick 41fa811 feat: Add glowing Christmas text styling for title and description

# Door image group
pick 60d9b87 feat: Replace wooden door texture with Christmas wreath door image
fixup 58cb292 fix: Center lock icon and show clean thumbnails on opened doors

# Tree decorations group (all 9 commits)
pick 64cc480 feat: Add subtle Christmas tree decorations to video letterbox
fixup 55c961d feat: Create dark forest silhouette in video letterbox with CSS trees
fixup 16286de fix: Increase visibility of dark forest trees in letterbox
fixup c61d8ed feat: Replace CSS trees with actual Christmas tree silhouette images
fixup 9878ae4 fix: Make tree silhouettes visible in letterbox
fixup dca3a29 feat: Replace with cleaner tree1.png silhouette
fixup bd1d2ee feat: Show 4 large visible trees on each side with varied shades
fixup a725c08 fix: Use invert filter to make black trees visible on black background
fixup e8caf8f feat: Add 4 naturally-shaded tree images for letterbox decoration

# Mobile video + responsive layout group
pick 0d5acf8 fix: Separate mobile and desktop video playback for native experience
fixup a690f1d fix: Use fluid viewport units for orientation-responsive door grid layout
fixup dc333ac fix: Use Ionic Platform API for mobile detection and enable autoplay on all devices

# CSS fix
pick 528ec4c fix: Correct background viewport sizing for full screen coverage
```

### After marking commits:

1. **Save and close the editor**
2. Git will automatically squash the commits
3. You may need to edit commit messages (git will open editor for each "pick")
4. If conflicts occur, resolve them and run: `git rebase --continue`

### Recommended Commit Message Updates:

When git opens editor for combined commits, use these improved messages:

**Commit 4 (Background):**
```
feat: Add winter scene background image with proper asset resolution

Add winter scene background to Christmas theme with proper Webpack asset
loading and full viewport coverage.

Changes:
- Add christmas-background.png (winter scene)
- Configure background-size: cover with center positioning
- Fix asset path for Webpack resolution (public → src/assets)
- Ensure full screen coverage with min-height: 100vh
- Add background-attachment: fixed for parallax effect

Benefits:
- Professional winter atmosphere
- Proper asset bundling
- Full viewport coverage on all devices
```

**Commit 5 (Snowfall):**
```
feat: Add animated snowfall with multiple layers and varied sizes

Create continuous snowfall animation with three staggered layers for depth
effect. Uses pure CSS animations with snowflake characters.

Features:
- Three animation layers (slow, medium, fast)
- Mixed snowflake sizes (20px-36px)
- Varied opacity (0.5-0.7) for depth
- Staggered timing for continuous effect
- Reduced motion support

Performance:
- Pure CSS (no JavaScript)
- Mobile optimized (fewer snowflakes on small screens)
```

**Commit 8 (Trees):**
```
feat: Add Christmas tree decorations to video letterbox

Add subtle Christmas tree silhouettes to letterbox areas on sides of
vertical videos. Uses 4 separate tree images with natural shade variation.

Implementation:
- 4 tree PNG images (tree1-4.png) in different grey shades
- Positioned in letterbox areas (30% width on each side)
- 150% size for fuller forest effect
- Opacity: 0.3 for subtle, non-distracting appearance
- Only visible with vertical videos (covered by horizontal)
- Video z-index: 1 prevents trees showing through

Benefits:
- Festive touch without distraction
- Natural variation with multiple tree shades
- Only appears in empty letterbox space
- Maintains professional appearance
```

**Commit 9 (Mobile/Responsive):**
```
fix: Improve mobile video playback and responsive layout

Extract mobile video to dedicated component for native playback. Improve
responsive grid with fluid viewport units. Use Ionic Platform API for
reliable device detection.

Changes:
- Create MobileVideoOverlay component for mobile/tablet devices
- Use Ionic's isPlatform() instead of user agent sniffing
- Replace fixed pixels with fluid viewport units (vmin, cqi)
- Enable autoplay on all devices (browser may still block)
- Automatic orientation adaptation without media queries

Benefits:
- Native fullscreen player on mobile/tablet/iPad
- Cleaner separation of mobile vs desktop concerns
- Reliable iOS 13+ iPad detection
- Smooth rotation handling
- Simpler, more maintainable code

NFR Compliance:
- [U1] Mobile responsive - Optimized for all devices
- [U2] Touch-friendly - 44px minimum touch targets
- [U5] WCAG 2.1 AA - Accessible with ARIA labels
- [SC3] Modular - Reusable components
```

---

## If You Need to Abort

If something goes wrong during rebase:
```bash
git rebase --abort
```

This will return you to the state before the rebase started.

---

## After Successful Rebase

```bash
# Verify commit history
git log --oneline origin/main..HEAD

# You should see exactly 9 commits
```

Then you're ready to push to remote!
