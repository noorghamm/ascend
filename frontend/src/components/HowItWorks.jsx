const STEPS = [
  ["Post", "Say which zone and level you're on, and how long you'll be there."],
  ["Click the link", "We email your student address. One click puts you on the board."],
  ["Get found", "Your card stays up until you leave or your time runs out."],
];

function HowItWorks({ onDismiss }) {
  return (
    <section className="howto" aria-label="How it works">
      <ol className="howto-steps">
        {STEPS.map(([title, body], i) => (
          <li key={title}>
            <span className="howto-n">{i + 1}</span>
            <div>
              <b>{title}</b>
              <p>{body}</p>
            </div>
          </li>
        ))}
      </ol>
      <button type="button" className="howto-x" onClick={onDismiss} aria-label="Dismiss">
        Got it
      </button>
    </section>
  );
}

export default HowItWorks;
