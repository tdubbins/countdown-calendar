# Frontend Accessibility Checklist

This checklist must be completed for all frontend GitHub issues before moving to "Done" status.

## 🎯 Core Accessibility Requirements (WCAG 2.1 AA)

### ✅ Keyboard Navigation
- [ ] All interactive elements accessible via keyboard
- [ ] Logical tab order maintained
- [ ] Visible focus indicators (2px outline minimum)
- [ ] No keyboard traps
- [ ] Skip links provided where needed

### ✅ Screen Reader Support
- [ ] Semantic HTML elements used correctly
- [ ] Form labels properly associated with inputs
- [ ] ARIA attributes added where needed:
  - [ ] `aria-label` for buttons without text
  - [ ] `aria-describedby` for error messages
  - [ ] `aria-invalid` for validation states
  - [ ] `role` attributes for custom components
- [ ] Dynamic content has live regions (`aria-live`)
- [ ] Decorative icons marked `aria-hidden="true"`

### ✅ Visual Accessibility
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] Color contrast ratio ≥ 3:1 for large text
- [ ] Information not conveyed by color alone
- [ ] Text can be zoomed to 200% without horizontal scroll
- [ ] Touch targets ≥ 44px (NFR U2)

### ✅ Form Accessibility
- [ ] All form fields have labels
- [ ] Required fields clearly marked
- [ ] Error messages announced to screen readers
- [ ] Validation states properly communicated
- [ ] Autocomplete attributes added where appropriate
- [ ] Fieldsets and legends for grouped inputs

### ✅ Content Structure
- [ ] Proper heading hierarchy (h1, h2, h3...)
- [ ] Lists use proper list markup
- [ ] Tables have headers and captions
- [ ] Images have meaningful alt text
- [ ] Language of page declared

## 🧪 Testing Procedures

### Manual Testing Checklist
- [ ] **Keyboard Test**: Navigate entire component using only Tab, Shift+Tab, Enter, Space, Arrow keys
- [ ] **Screen Reader Test**: Test with VoiceOver (Mac) or NVDA (Windows)
- [ ] **Focus Test**: Verify all interactive elements have visible focus
- [ ] **Zoom Test**: Test at 200% zoom level
- [ ] **Contrast Test**: Use browser developer tools color contrast checker

### Browser Testing
- [ ] Chrome DevTools Lighthouse accessibility audit (score ≥ 90)
- [ ] Firefox accessibility inspector
- [ ] Safari VoiceOver compatibility

### Mobile Accessibility
- [ ] Touch targets ≥ 44px
- [ ] Gestures work with assistive technology
- [ ] Content readable at mobile zoom levels
- [ ] iOS VoiceOver / Android TalkBack compatible

## 📋 Issue Integration

### GitHub Issue Template Addition
```markdown
## Accessibility Acceptance Criteria
- [ ] Keyboard navigation working
- [ ] Screen reader announcements correct
- [ ] ARIA attributes implemented
- [ ] Color contrast compliant
- [ ] Touch targets ≥ 44px
- [ ] Accessibility checklist completed
```

### Definition of Done Updates
A frontend issue cannot be moved to "Done" until:
1. ✅ All functional requirements met
2. ✅ All NFRs verified
3. ✅ **Accessibility checklist completed**
4. ✅ Accessibility testing performed

## 🎯 Quick Reference

### Essential ARIA Attributes
```html
<!-- Form validation -->
<input aria-invalid="true" aria-describedby="error-id">
<div id="error-id" role="alert">Error message</div>

<!-- Dynamic content -->
<div aria-live="polite" aria-atomic="true">Status updates</div>
<div aria-live="assertive">Critical alerts</div>

<!-- Interactive elements -->
<button aria-label="Close dialog">×</button>
<div role="button" tabindex="0">Custom button</div>

<!-- Form structure -->
<label for="email">Email Address</label>
<input id="email" type="email" required>
```

### CSS Focus Indicators
```css
/* Visible focus for all interactive elements */
button:focus,
input:focus,
[tabindex]:focus {
  outline: 2px solid var(--ion-color-primary);
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .form-element {
    border-width: 3px;
  }
}
```

## 🏆 Accessibility Levels

### Level 1: Essential (All Issues)
- Keyboard navigation
- Screen reader basics
- Form accessibility
- Color contrast

### Level 2: Enhanced (User-facing Components)
- Advanced ARIA patterns
- Custom component accessibility
- Animation considerations
- Progressive enhancement

### Level 3: Advanced (Complex Interactions)
- Live regions for dynamic content
- Focus management
- Accessibility testing automation
- Performance + accessibility optimization

---

## 📚 Resources
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Ionic Accessibility Guide](https://ionicframework.com/docs/developing/accessibility)
- [Vue.js Accessibility Guide](https://vuejs.org/guide/best-practices/accessibility.html)
- [WebAIM Screen Reader Testing](https://webaim.org/articles/screenreader_testing/)