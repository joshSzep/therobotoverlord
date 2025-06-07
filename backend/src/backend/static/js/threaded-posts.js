/**
 * Toggle visibility of reply forms in threaded posts
 */
function toggleReplyForm(formId) {
  const form = document.getElementById(formId);
  if (form) {
    // Toggle display between 'none' and 'block'
    if (form.style.display === 'none') {
      form.style.display = 'block';
    } else {
      form.style.display = 'none';
    }
  }
}
