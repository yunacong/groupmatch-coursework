document.addEventListener('DOMContentLoaded', () => {
  const columns = ['todo', 'doing', 'done'];
  const board = document.querySelector('.task-columns');
  const announcement = document.getElementById('statusAnnouncement');
  // Extract the CSRF token from the browser cookie.
  // Django's CsrfViewMiddleware rejects POST requests that omit this token.
  const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

  function columnElement(statusKey) { return board?.querySelector(`[data-column="${statusKey}"] .task-list`); }
  // Update the aria-live region so screen readers announce the status change
  // without requiring the user's focus to move to the notification element.
  function announce(message) { if (announcement) announcement.textContent = message; }

  function relabelButtons(card, statusKey) {
    card.dataset.status = statusKey;
    const idx = columns.indexOf(statusKey);
    const left = card.querySelector('.move-left');
    const right = card.querySelector('.move-right');
    if (left) left.disabled = idx === 0;
    if (right) right.disabled = idx === columns.length - 1;
  }

  function moveTask(card, direction) {
    const current = card.dataset.status;
    const currentIndex = columns.indexOf(current);
    const nextIndex = currentIndex + direction;
    if (nextIndex < 0 || nextIndex >= columns.length) return;
    const nextStatus = columns[nextIndex];
    fetch(`/tasks/${card.dataset.taskId}/update-status/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json','X-CSRFToken': csrftoken},
      body: JSON.stringify({ status: nextStatus }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.new_status_key) {
          const targetList = columnElement(data.new_status_key);
          if (targetList) targetList.appendChild(card);
          relabelButtons(card, data.new_status_key);
          announce(`Task moved to ${data.status}.`);
          card.focus();
        } else {
          announce('Unable to update task status.');
        }
      })
      .catch(() => announce('Unable to update task status.'));
  }

  document.querySelectorAll('.task-card').forEach(card => {
    relabelButtons(card, card.dataset.status);
    // ArrowLeft/ArrowRight keyboard support allows keyboard-only users
    // to move task cards between columns without using a mouse.
    card.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft') moveTask(card, -1);
      if (event.key === 'ArrowRight') moveTask(card, 1);
    });
    card.querySelector('.move-left')?.addEventListener('click', () => moveTask(card, -1));
    card.querySelector('.move-right')?.addEventListener('click', () => moveTask(card, 1));
  });
});
