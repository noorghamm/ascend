function Toast({ toast, onClose }) {
  if (!toast) return null;
  return (
    <div className={`toast toast-${toast.kind}`} role="status">
      <span>{toast.text}</span>
      <button type="button" className="toast-x" onClick={onClose} aria-label="Dismiss">×</button>
    </div>
  );
}

export default Toast;
