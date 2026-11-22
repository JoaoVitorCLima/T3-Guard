(() => {
  const stages = window.integrityTrace;
  const controls = document.querySelector('#integrity-controls');
  const messages = {
    1: 'Origem e integridade verificadas. A última leitura aceita chega ao supervisório.',
    3: 'O gateway rejeitou a alteração. A pressão aceita e a rodada do RTL foram preservadas.',
    4: 'O gateway rejeitou a repetição. A pressão aceita e a rodada do RTL foram preservadas.',
  };
  const display = (id, value) => {
    document.querySelector('#' + id).textContent = value;
  };
  function render(index) {
    const stage = stages[index];
    const [, , a, b, c, discrep, , , authentication, replay, status, , mode, trip] = stage.registers;
    const result = document.querySelector('#integrity-result');
    result.textContent = stage.stage;
    result.dataset.status = status === 1 && !discrep ? 'ok' : 'warning';
    display('integrity-detail', discrep
      ? 'B enviou uma leitura autenticada. O RTL confirmou a divergência e passou ao modo degradado.'
      : messages[status]);
    const pressure = document.querySelector('#integrity-pressure');
    pressure.replaceChildren(...[a, b, c].map((reading, channel) => {
      const card = document.createElement('div');
      card.className = 'sensor';
      card.dataset.fault = Boolean(discrep & (1 << channel));
      const label = document.createElement('span');
      label.textContent = 'Canal ' + 'ABC'[channel];
      const value = document.createElement('strong');
      value.textContent = reading + ' kPa';
      const note = document.createElement('span');
      note.textContent = card.dataset.fault === 'true' ? 'Discrepante' : 'Em concordância';
      card.append(label, value, note);
      return card;
    }));
    display('integrity-auth', authentication);
    display('integrity-replay', replay);
    display('integrity-rounds', stage.rounds);
    display('integrity-rtl', ['Normal', 'Degradado', 'Seguro'][mode] + ' · trip ' + trip);
    for (const [i, button] of Array.from(controls.children).entries()) {
      button.setAttribute('aria-pressed', String(i === index));
    }
  }
  for (const [i, stage] of stages.entries()) {
    const button = document.createElement('button');
    button.textContent = stage.stage;
    button.type = 'button';
    button.addEventListener('click', () => render(i));
    controls.append(button);
  }
  render(0);
})();
